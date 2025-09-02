"""
Qdrant Vector Store Module.

This module provides a concrete implementation of the VectorStore abstract base class,
using Qdrant Vector Store for managing collections of vectors and their associated metadata.
"""

# pylint: disable=line-too-long, duplicate-code

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional, override

try:
    from qdrant_client import AsyncQdrantClient, QdrantClient, models
    from qdrant_client.conversions.common_types import ScoredPoint
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate qdrant_client package. "
        'Please install it with `pip install "autonomize-autorag[qdrant]"`.'
    ) from err

from tqdm import tqdm

from autorag.exceptions.vector_stores import (
    VectorStoreCollectionAlreadyExistsException,
    VectorStoreCollectionNotFoundException,
    VectorStoreDataMismatchException,
)
from autorag.types.vector_stores import DistanceType, VectorStoreQueryResult
from autorag.utilities.concurrency import run_async
from autorag.vector_stores.base import VectorStore


class QdrantVectorStore(VectorStore):
    """
    Qdrant vector store implementation.

    This class provides an interface for interacting with a Qdrant vector database,
    utilizing both REST and gRPC clients for different operations.

    Args:
        host (Optional[str]): Hostname of the Qdrant service for REST API.
        grpc_host (Optional[str]): Hostname of the Qdrant service for gRPC. Defaults to `host` if not provided.
        port (int): Port for the REST API interface. Defaults to 6333.
        grpc_port (int): Port for the gRPC interface. Defaults to 6334.
        api_key (Optional[str]): API key for authentication with Qdrant Cloud.
        prefer_grpc (bool): If True, gRPC interface is preferred for custom methods. Defaults to True.
        kwargs (Any): Any other arguments to be passed to the constructor.

    Note:
        The gRPC client is used for upsertion operations, while the REST client handles all other operations.

    Attributes:
        _m (int): Number of edges per node in the HNSW index graph.
                  Larger values lead to more accurate searches but require more space.
                  Default is 16.
        _ef_construct (int): Number of neighbors considered during the index building process.
                             Larger values improve accuracy but increase indexing time.
                             Default is 512.
        _ef_search (int): Size of the beam during a beam-search operation.
                          Larger values lead to more accurate search results but require more time.
                          Recommended to be the same as `_ef_construct`. Default is 512.

    Example:

    .. code-block:: python

        from autorag.vector_stores import QdrantVectorStore
        from autorag.types.vector_stores import DistanceType

        client = QdrantVectorStore(
            host='localhost',
            port=6333,
            grpc_port=6334,
            api_key='xxx'
        )

        client.create_collection(
            collection_name="test_collection",
            embedding_dimensions=768,
            distance=DistanceType.COSINE
        )
    """

    def __init__(
        self,
        host: Optional[str] = None,
        grpc_host: Optional[str] = None,
        port: int = 6333,
        grpc_port: int = 6334,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Enable gRPC fork support and configure poll strategy
        os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "true"
        os.environ["GRPC_POLL_STRATEGY"] = "epoll,poll"

        # Fallback to 'host' if 'grpc_host' is not provided
        grpc_host = grpc_host or host

        # Initialize all Qdrant clients
        self._initialize_clients(
            host=host,
            grpc_host=grpc_host,
            port=port,
            grpc_port=grpc_port,
            api_key=api_key,
            **kwargs,
        )

        # Initialize collection parameters for HNSW
        self._m = 16
        self._ef_construct = 512
        self._ef_search = self._ef_construct
        self._max_value_for_integer_id: int = 2**64

    def _initialize_clients(
        self,
        host: Optional[str],
        grpc_host: Optional[str],
        port: int,
        grpc_port: int,
        api_key: Optional[str],
        **kwargs: Any,
    ) -> None:
        """
        Initialize Qdrant clients for both REST and gRPC.

        Args:
            host (Optional[str]): Hostname for the REST client.
            grpc_host (Optional[str]): Hostname for the gRPC client.
            port (int): Port for the REST API.
            grpc_port (int): Port for the gRPC interface.
            api_key (Optional[str]): API key for authentication with Qdrant Cloud.
            kwargs (Any): Any other arguments to be passed to the constructor.
        """

        self._client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            api_key=api_key,
            prefer_grpc=False,
            **kwargs,
        )
        self._grpc_client = QdrantClient(
            host=grpc_host,
            port=port,
            grpc_port=grpc_port,
            api_key=api_key,
            prefer_grpc=True,
            **kwargs,
        )
        self._aclient = AsyncQdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            api_key=api_key,
            prefer_grpc=False,
            **kwargs,
        )

    def _get_distance_metric(self, distance: DistanceType) -> models.Distance:
        """
        Converts DistanceType to the corresponding `models.Distance`
        metric as per the configurations required by the Qdrant Vector Store.

        Args:
            distance (DistanceType): The type of distance metric to use.

        Returns:
            models.Distance: The matching distance metric for the Qdrant configuration.
        """
        if distance == DistanceType.EUCLIDEAN:
            return models.Distance.EUCLID
        if distance == DistanceType.COSINE:
            return models.Distance.COSINE
        return models.Distance.DOT

    def _is_valid_qdrant_id(self, input_id):
        """
        Check if the given value is either:
        - An integer that fits in 64-bit unsigned range [0, 2^64), or
        - A string that is a valid UUID.

        Args:
            value: The value to check.

        Returns:
            True if the value is a valid 64-bit unsigned int or a valid UUID string, else False.
        """
        if isinstance(input_id, int):
            # Check if integer falls in the unsigned 64-bit range.
            return 0 <= input_id < self._max_value_for_integer_id
        if isinstance(input_id, str):
            try:
                # Attempt to create a UUID from the string.
                _ = uuid.UUID(input_id)
                return True
            except ValueError:
                return False
        return False

    def _create_collection(
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        **kwargs: Any,
    ) -> None:
        """
        Creates a new collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            kwargs (Any): Any additional arguments to be used.
        """

        vector_distance = self._get_distance_metric(distance=distance)

        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_dimensions, distance=vector_distance
            ),
            hnsw_config=models.HnswConfigDiff(
                m=self._m,
                ef_construct=self._ef_construct,
            ),
            **kwargs,
        )

    def _delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.
        """
        self._client.delete_collection(collection_name=collection_name, **kwargs)

    def _upsert(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Upserts embeddings and metadata into the collection.

        Args:
            collection_name (str): The name of the collection to upsert into.
            embeddings (List[List[float]]): A list of vectors to be upserted.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the embeddings.
            kwargs (Any): Any additional arguments to be used.
        """

        # Whether to use id in the payload or let qdrant generate a unique 64 bit integer id
        use_client_provided_id: bool = kwargs.pop("use_client_provided_id", False)

        # Check if client ID is allowed and "id" is present in metadata
        has_id_in_metadata = "id" in metadatas[0]

        if not use_client_provided_id and has_id_in_metadata:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata."
            )

        ids: Optional[List] = None

        if use_client_provided_id:
            ids = []
            for metadata in metadatas:
                input_id = metadata.pop("id", None)
                if not input_id or not self._is_valid_qdrant_id(input_id):
                    raise VectorStoreDataMismatchException(
                        "Error in `id` field. "
                        "If client provided id is to be used for Qdrant points, "
                        "it should be unsigned 64 bit integer or UUID string"
                    )
                ids.append(input_id)

        # Wrapping the metadata with tqdm allows us
        # to view the upsertion progression on the terminal.
        payload = tqdm(metadatas)

        # If we upload more than 256 data points in a single request,
        # then we are dividing it into batches of 256, and uploading
        # them in parallel. At a single point of time, we can upload
        # 1024 data points due to 4 parallel upload processes.
        self._grpc_client.upload_collection(
            collection_name=collection_name,
            vectors=embeddings,
            ids=ids,
            payload=payload,
            batch_size=256,
            parallel=4,
            max_retries=3,
            **kwargs,
        )

    def _query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> List[VectorStoreQueryResult]:
        """
        Queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.
        """

        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        results = self._client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=filter_conditions,
            # exact - Search without approximation
            search_params=models.SearchParams(
                hnsw_ef=self._ef_search,
                exact=False,  # If set to true, search may run long but with exact results, usually not recommended to set True.
            ),
            limit=top_k,
            with_payload=models.PayloadSelectorInclude(include=metadata_fields),
            **kwargs,
        )

        return self._convert_to_model(results=results)

    def _convert_to_model(self, results: List[ScoredPoint]):
        """
        Converts a list of scored points from the search results to VectorStoreQueryResult models.

        Args:
            results (List[ScoredPoint]): A list of search results from Qdrant.

        Returns:
            List[VectorStoreQueryResult]: A list of converted VectorStoreQueryResult models.
        """
        return [
            VectorStoreQueryResult(
                score=result.score,
                # result.payload can be None in some unique cases.
                # In such events, we will simply use an empty dict in its place.
                metadata={
                    k: v for k, v in (result.payload or {}).items() if k != "score"
                },
            )
            for result in results
        ]

    def _build_query_filter(self, metadata_filter: Dict[str, Any]) -> models.Filter:
        """
        Constructs a query filter for the Qdrant vector store based on the provided metadata.

        The function translates a dictionary of metadata filters into a format suitable for querying
        the Qdrant vector store. Each key-value pair in the metadata_filter dictionary is converted
        into a corresponding Qdrant filter condition.

        Supported filter conditions:
        - Equality
        - IN (as in checking all values in a list)

        Note:
            Additional filter conditions to be added later.

        Args:
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.

        Returns:
            models.Filter: A `Filter` object formatted for Qdrant's search API.
        """

        field_conditions = []

        for key, value in metadata_filter.items():
            if isinstance(value, list):
                # In case you want to check if the stored value is one of multiple values,
                # you can use the Match Any condition.
                # Match Any works as a logical OR for the given values.
                # It can also be described as a `IN` operator
                field_condition = models.FieldCondition(
                    key=key, match=models.MatchAny(any=value)
                )
            else:
                field_condition = models.FieldCondition(
                    key=key, match=models.MatchValue(value=value)
                )
            field_conditions.append(field_condition)

        return models.Filter(must=field_conditions)  # type: ignore

    def _delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Deletes points from a collection that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.
        """
        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        # Delete by filter. Qdrant will remove all matching points.
        self._client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(filter=filter_conditions),
            **kwargs,
        )

    def _collection_exists(self, collection_name: str, **kwargs: Any) -> bool:
        """
        Checks if a collection exists in the vector store.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return self._client.collection_exists(collection_name=collection_name)

    @override
    async def acreate_collection(
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        **kwargs: Any,
    ) -> None:
        """
        Asyncronously creates a new collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionAlreadyExistsException: If the collection already exists.
        """

        if await self._acollection_exists(collection_name):
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' already exists."
            )

        await self._acreate_collection(
            collection_name=collection_name,
            embedding_dimensions=embedding_dimensions,
            distance=distance,
            **kwargs,
        )

    async def _acreate_collection(
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        **kwargs: Any,
    ) -> None:
        """
        Asyncronously creates a new collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            kwargs (Any): Any additional arguments to be used.
        """

        vector_distance = self._get_distance_metric(distance=distance)

        await self._aclient.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_dimensions, distance=vector_distance
            ),
            hnsw_config=models.HnswConfigDiff(
                m=self._m,
                ef_construct=self._ef_construct,
            ),
            **kwargs,
        )

    @override
    async def adelete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Asyncronously deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        await self._adelete_collection(collection_name=collection_name, **kwargs)

    async def _adelete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Asyncronously deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.
        """
        await self._aclient.delete_collection(collection_name=collection_name, **kwargs)

    @override
    async def aupsert(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Asyncronously upserts embeddings and metadata into the collection.

        Args:
            collection_name (str): The name of the collection to upsert into.
            embeddings (List[List[float]]): A list of vectors to be upserted.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the embeddings.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection doesn't exist or if the number of embeddings and metadatas do not match.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        # Check whether len of embeddings and metadatas are same or not.
        self._validate_embeddings_and_metadata(
            embeddings=embeddings, metadatas=metadatas
        )

        # Qdrant doesn't provide async method for upload_collection,
        # so, we'll just run it in a separate awaitable thread.
        await run_async(
            lambda: self._upsert(
                collection_name=collection_name,
                embeddings=embeddings,
                metadatas=metadatas,
                **kwargs,
            )
        )

    @override
    async def aquery(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> List[VectorStoreQueryResult]:
        """
        Asyncronously queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """

        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        return await self._aquery(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
            metadata_fields=metadata_fields,
            **kwargs,
        )

    async def _aquery(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> List[VectorStoreQueryResult]:
        """
        Asyncronously queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.
        """

        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        results = await self._aclient.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=filter_conditions,
            # exact - Search without approximation
            search_params=models.SearchParams(
                hnsw_ef=self._ef_search,
                exact=False,  # If set to true, search may run long but with exact results, usually not recommended to set True.
            ),
            limit=top_k,
            with_payload=models.PayloadSelectorInclude(include=metadata_fields),
            **kwargs,
        )

        return self._convert_to_model(results=results)

    @override
    async def adelete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Asynchronously deletes points from a collection that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        await self._aclient.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(filter=filter_conditions),
            **kwargs,
        )

    async def _acollection_exists(self, collection_name: str) -> bool:
        """
        Asyncronously checks if a collection exists in the vector store.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return await self._aclient.collection_exists(collection_name=collection_name)
