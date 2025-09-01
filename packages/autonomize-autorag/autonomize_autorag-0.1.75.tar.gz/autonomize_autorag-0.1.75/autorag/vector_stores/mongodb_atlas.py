"""
MongoDB Atlas Vector Store Module.

This module provides a concrete implementation of the VectorStore abstract base class,
using MongoDB Atlas for managing collections of vectors and their associated metadata.
"""

# pylint: disable=line-too-long, duplicate-code

from __future__ import annotations

from typing import Any, Dict, List, override

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
    from pymongo import MongoClient
    from pymongo.database import Database
    from pymongo.operations import SearchIndexModel
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate mongodb_altas package. "
        'Please install it with `pip install "autonomize-autorag[mongodb-atlas]"`.'
    ) from err

from autorag.exceptions.vector_stores import (
    VectorStoreCollectionAlreadyExistsException,
    VectorStoreCollectionNotFoundException,
    VectorStoreDataMismatchException,
)
from autorag.types.vector_stores import DistanceType, VectorStoreQueryResult
from autorag.utilities.concurrency import run_async
from autorag.vector_stores.base import VectorStore

EMBEDDING_INDEX = "embedding-index"


class MongoDBAtlasVectorStore(VectorStore):
    """
    MongoDB Atlas vector store implementation.

    This class provides an interface for interacting with a MongoDB Atlas database
    for storing and querying vector embeddings and their associated metadata.

    Args:
        connection_string (str): MongoDB Atlas connection string.
        database_name (str): Name of the database to use.

    Example:

    .. code-block:: python

        from autorag.vector_stores import MongoDBAtlasVectorStore
        from autorag.types.vector_stores import DistanceType

        client = MongoDBAtlasVectorStore(
            connection_string='xxx',
            database_name='my-db'
        )

        client.create_collection(
            collection_name="test_collection",
            embedding_dimensions=768,
            distance=DistanceType.COSINE
        )
    """

    def __init__(
        self,
        connection_string: str,
        database_name: str,
    ) -> None:

        # Initialize all MongoDB Atlas clients
        self._initialize_clients(
            connection_string=connection_string,
            database_name=database_name,
        )

    def _initialize_clients(
        self,
        connection_string: str,
        database_name: str,
    ) -> None:
        """
        Initialize MongoDB Atlas clients for both sync and async.

        Args:
            connection_string (str): MongoDB Atlas connection string.
            database_name (str): Name of the database to use.
        """
        self._client: Database = MongoClient(connection_string)[database_name]
        self._aclient: AsyncIOMotorDatabase = AsyncIOMotorClient(connection_string)[
            database_name
        ]

    def _get_distance_metric(self, distance: DistanceType) -> str:
        """
        Converts DistanceType to the corresponding string distance
        metric as per the configurations required by the MongoDB Atlas Vector Store.

        Args:
            distance (DistanceType): The type of distance metric to use.

        Returns:
            str: The matching distance metric for the MongoDB Atlas configuration.
        """
        if distance == DistanceType.EUCLIDEAN:
            return "euclidean"
        if distance == DistanceType.COSINE:
            return "cosine"
        return "dotProduct"

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

        self._client.create_collection(collection_name, **kwargs)
        self._create_search_index(
            collection_name=collection_name,
            embedding_dimensions=embedding_dimensions,
            distance=distance,
        )

    def _create_search_index(
        self,
        collection_name: str,  # pylint: disable=unused-argument
        embedding_dimensions: int,  # pylint: disable=unused-argument
        distance: DistanceType,  # pylint: disable=unused-argument
    ) -> None:
        """
        Creates a search index for vector similarity searches on a specified collection.
        Creating search index enables vector searching on a specified collection.

        Args:
            collection_name (str): The name of the collection where the index will be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use (EUCLIDEAN, COSINE, or DOT_PRODUCT).
        """

        similarity = self._get_distance_metric(distance=distance)

        # Create your index model, then create the search index
        search_index_model = self._get_search_index_model(
            embedding_dimensions=embedding_dimensions, similarity=similarity
        )
        self._client[collection_name].create_search_index(model=search_index_model)

    def _delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.
        """
        self._client.drop_collection(name_or_collection=collection_name, **kwargs)

    def _handle_client_provided_id_field_check(
        self, metadatas: List[Dict[str, Any]], **kwargs
    ) -> List[Dict[str, Any]]:

        use_client_provided_id: bool = False

        if "use_client_provided_id" in kwargs:
            # for idempotency when ExactlyOnceProcessing cannot be guaranteed
            use_client_provided_id_value_in_kwargs: bool = kwargs[
                "use_client_provided_id"
            ]
            kwargs.pop("use_client_provided_id")
            if "id" in metadatas[0] and use_client_provided_id_value_in_kwargs:
                use_client_provided_id = True

        if "_id" in metadatas[0]:
            raise VectorStoreDataMismatchException(
                "Field `_id` is a reserved keyword. Please use a different identifier in metadata."
            )

        if not use_client_provided_id and "id" in metadatas[0]:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata."
            )
        if use_client_provided_id:
            for metadata_dict in metadatas:
                id_field = metadata_dict.get("id")
                if id_field:
                    metadata_dict.pop("id")
                    metadata_dict["_id"] = id_field
                else:
                    raise VectorStoreDataMismatchException(
                        "Field `id` should be provided If Client Provided ID is set in Payload"
                    )
        return metadatas

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

        # if client provided id is to be used convert id to _id for mongo db
        self._handle_client_provided_id_field_check(metadatas, **kwargs)

        # Check for the existence of each metadata field index in the collection.
        # If the field index does not exist, create an index for it.
        metadata = metadatas[0]
        fields_to_index = self._get_metadata_fields_to_index(
            collection_name=collection_name, metadata=metadata
        )
        if fields_to_index:
            self._create_metadata_fields_index(
                collection_name=collection_name,
                fields=fields_to_index,
            )

        # Merge embeddings and metadata into a single list of dictionaries
        documents_to_upsert = MongoDBAtlasVectorStore.merge_embedding_and_metadata(
            embeddings=embeddings, metadatas=metadatas
        )

        # Upsert the merged list of embeddings and metadata into the collection
        self._client[collection_name].insert_many(documents_to_upsert, **kwargs)

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

        # Remove the _id field from the metadata fields list if it exists
        if "_id" in metadata_fields:
            metadata_fields.remove("_id")

        # Build the query filter based on the provided metadata filter
        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        # Query the collection using the provided query vector and filter conditions
        pipeline = self._create_query_pipeline(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_conditions=filter_conditions,
            metadata_fields=metadata_fields,
        )

        results = list(self._client[collection_name].aggregate(pipeline, **kwargs))

        return self._convert_to_model(results=results)

    def _convert_to_model(
        self, results: List[Dict[str, Any]]
    ) -> List[VectorStoreQueryResult]:
        """
        Converts a list of the search results to VectorStoreQueryResult models.

        Args:
            results (List[Dict[str, Any]]): A list of search results from MongoDB Atlas.

        Returns:
            List[VectorStoreQueryResult]: A list of converted VectorStoreQueryResult models.
        """
        return [
            VectorStoreQueryResult(
                score=result["score"],
                # result.payload can be None in some unique cases.
                # In such events, we will simply use an empty dict in its place.
                metadata={k: v for k, v in result.items() if k != "score"},
            )
            for result in results
        ]

    def _build_query_filter(self, metadata_filter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs a query filter for the MongoDB Atlas vector store based on the provided metadata.

        The function translates a dictionary of metadata filters into a format suitable for querying
        the MongoDB Atlas vector store. Each key-value pair in the metadata_filter dictionary is converted
        into a corresponding MongoDB Atlas filter condition.

        Supported filter conditions:
        - Equality
        - IN (as in checking all values in a list)

        Note:
            Additional filter conditions to be added later.

        Args:
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.

        Returns:
            Dict[str, Any]: A `Filter` object formatted for MongoDB Atlas' search API.
        """

        field_conditions = []

        for key, value in metadata_filter.items():
            if isinstance(value, list):
                # In case you want to check if the stored value is one of multiple values,
                # $in works as a logical OR for the given values.
                field_condition = {key: {"$in": value}}
            else:
                field_condition = {key: value}
            field_conditions.append(field_condition)

        return {"$and": field_conditions}

    def _delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Deletes documents from a collection that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.
        """

        filter_doc = self._build_query_filter(metadata_filter=metadata_filter)
        self._client[collection_name].delete_many(filter_doc, **kwargs)

    def _collection_exists(self, collection_name: str, **kwargs: Any) -> bool:
        """
        Checks if a collection exists in the vector store.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return collection_name in self._client.list_collection_names()

    def _get_metadata_fields_to_index(
        self, collection_name: str, metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Get the metadata fields that need to be indexed.

        Args:
            collection_name (str): The name of the collection to check.
            metadata (Dict[str, Any]): A dictionary of metadata fields.

        Returns:
            List[str]: A list of metadata fields that need to be indexed.
        """

        # Get the existing search index for the collection, only the first index is considered.
        search_index = list(
            self._client[collection_name].list_search_indexes(EMBEDDING_INDEX)
        )[0]
        indexed_fields = search_index["latestDefinition"]["fields"]

        fields_to_index = []

        for metadata_field in metadata.keys():
            # Check if the metadata_field is found in the 'path' of any dictionary in indexed_fields
            if not any(metadata_field in d["path"] for d in indexed_fields):
                fields_to_index.append(metadata_field)

        # If there is even a single field that is not indexed, we need all fields to index.
        if fields_to_index:
            indexed_paths = {d["path"] for d in indexed_fields if d["type"] == "filter"}
            fields_to_index = list(set(fields_to_index).union(indexed_paths))
        return fields_to_index

    def _create_metadata_fields_index(
        self,
        collection_name: str,
        fields: List[str],
    ) -> None:
        """
        Create an index for the metadata fields in the collection.

        Args:
            collection_name (str): The name of the collection to check.
            fields (List[str]): A list of metadata fields to create an index for.
        """

        # Get the similarity metric from the existing index
        indexes = list(
            self._client[collection_name].list_search_indexes(EMBEDDING_INDEX)
        )

        similarity = None

        for idx in indexes:
            if idx["name"] == EMBEDDING_INDEX:
                idx_fields = idx["latestDefinition"]["fields"]
                for idx_field in idx_fields:
                    if idx_field["type"] == "vector":
                        similarity = idx_field["similarity"]
                        num_dimensions = idx_field["numDimensions"]
                        break
                if similarity:
                    break

        # Create the index for each metadata field
        definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": num_dimensions,
                    "similarity": similarity,
                }
            ]
        }

        definition["fields"].extend(
            [{"type": "filter", "path": field} for field in fields]
        )

        self._client[collection_name].update_search_index(
            name=EMBEDDING_INDEX,
            definition=definition,
        )

    def _get_search_index_model(
        self, embedding_dimensions: int, similarity: str
    ) -> SearchIndexModel:
        """
        Get the search index model for a collection.

        Args:
            embedding_dimensions (int): The number of dimensions for the embeddings.
            similarity (str): The type of similarity metric to use.

        Returns:
            SearchIndexModel: The search index model for the collection.
        """

        return SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": embedding_dimensions,
                        "similarity": similarity,
                    }
                ]
            },
            name=EMBEDDING_INDEX,
            type="vectorSearch",
        )

    def _create_query_pipeline(
        self,
        query_embedding: List[float],
        top_k: int,
        filter_conditions: Dict[str, Any],
        metadata_fields: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Create a query pipeline for the MongoDB Atlas vector store.

        Args:
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            filter_conditions (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.

        Returns:
            List[Dict[str, Any]]: A list of query pipeline stages.
        """

        # Define a pipeline using the provided query embedding and filter conditions
        pipeline = [
            {
                "$vectorSearch": {
                    "index": EMBEDDING_INDEX,
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": top_k * 10,
                    "limit": top_k,
                    "filter": filter_conditions,
                }
            },
            {
                "$project": {
                    "_id": 0,  # Exclude _id field from the results.
                    # Convert all the elements of list into dict,
                    # with list element as key and `1` as value.
                    **{field: 1 for field in metadata_fields},
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        return pipeline

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

        await self._aclient.create_collection(collection_name, **kwargs)
        await self._acreate_search_index(
            collection_name=collection_name,
            embedding_dimensions=embedding_dimensions,
            distance=distance,
        )

    async def _acreate_search_index(
        self,
        collection_name: str,  # pylint: disable=unused-argument
        embedding_dimensions: int,  # pylint: disable=unused-argument
        distance: DistanceType,  # pylint: disable=unused-argument
    ) -> None:
        """
        Asyncronously creates a search index for vector similarity searches on a specified collection.
        Creating search index enables vector searching on a specified collection.

        Args:
            collection_name (str): The name of the collection where the index will be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use (EUCLIDEAN, COSINE, or DOT_PRODUCT).
        """

        similarity = self._get_distance_metric(distance=distance)

        # Create your index model, then create the search index
        search_index_model = self._get_search_index_model(
            embedding_dimensions=embedding_dimensions, similarity=similarity
        )
        await self._aclient[collection_name].create_search_index(
            model=search_index_model
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
        await self._aclient.drop_collection(
            name_or_collection=collection_name, **kwargs
        )

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
            VectorStoreCollectionNotFoundException: If the collection doesn't exist.
            VectorStoreDataMismatchException: If the number of embeddings and metadatas do not match.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        # will raise exception if validation fails
        # if use client provided id is set, will convert id to _id
        self._handle_client_provided_id_field_check(metadatas, **kwargs)

        # Check whether len of embeddings and metadatas are same or not.
        self._validate_embeddings_and_metadata(
            embeddings=embeddings, metadatas=metadatas
        )

        # Check for the existence of each metadata field index in the collection.
        # If the field index does not exist, create an index for it.
        metadata = metadatas[0]
        fields_to_index = await self._aget_metadata_fields_to_index(
            collection_name=collection_name, metadata=metadata
        )
        if fields_to_index:
            await self._acreate_metadata_fields_index(
                collection_name=collection_name,
                fields=fields_to_index,
            )

        # Merge embeddings and metadata into a single list of dictionaries
        # Moving it to another thread to avoid block event loop.
        documents_to_upsert = await run_async(
            lambda: MongoDBAtlasVectorStore.merge_embedding_and_metadata(
                embeddings=embeddings, metadatas=metadatas
            )
        )

        # Upsert the merged list of embeddings and metadata into the collection
        await self._aclient[collection_name].insert_many(documents_to_upsert)

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

        # Remove the _id field from the metadata fields list if it exists
        if "_id" in metadata_fields:
            metadata_fields.remove("_id")

        # Build the query filter based on the provided metadata filter
        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        # Query the collection using the provided query vector and filter conditions
        pipeline = self._create_query_pipeline(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_conditions=filter_conditions,
            metadata_fields=metadata_fields,
        )

        results = (
            await self._aclient[collection_name].aggregate(pipeline, **kwargs).to_list()
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
        Asynchronously deletes documents from a collection that match the given metadata filter.

        Returns:
            int: number of documents deleted.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        filter_doc = self._build_query_filter(metadata_filter=metadata_filter)
        await self._aclient[collection_name].delete_many(filter_doc, **kwargs)

    async def _acollection_exists(self, collection_name: str) -> bool:
        """
        Asyncronously checks if a collection exists in the vector store.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return collection_name in await self._aclient.list_collection_names()

    async def _aget_metadata_fields_to_index(
        self, collection_name: str, metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Asyncronously get the metadata fields that need to be indexed.

        Args:
            collection_name (str): The name of the collection to check.
            metadata (Dict[str, Any]): A dictionary of metadata fields.

        Returns:
            List[str]: A list of metadata fields that need to be indexed.
        """

        # Get the existing search index for the collection, only the first index is considered.
        search_index = (
            await self._aclient[collection_name]
            .list_search_indexes(EMBEDDING_INDEX)
            .to_list()
        )
        indexed_fields = search_index[0]["latestDefinition"]["fields"]

        fields_to_index = []

        for metadata_field in metadata.keys():
            # Check if the metadata_field is found in the 'path' of any dictionary in indexed_fields
            if not any(metadata_field in d["path"] for d in indexed_fields):
                fields_to_index.append(metadata_field)

        # If there is even a single field that is not indexed, we need all fields to index.
        if fields_to_index:
            indexed_paths = {d["path"] for d in indexed_fields if d["type"] == "filter"}
            fields_to_index = list(set(fields_to_index).union(indexed_paths))
        return fields_to_index

    async def _acreate_metadata_fields_index(
        self,
        collection_name: str,
        fields: List[str],
    ) -> None:
        """
        Create an index for the metadata fields in the collection.

        Args:
            collection_name (str): The name of the collection to check.
            fields (List[str]): A list of metadata fields to create an index for.
        """

        # Get the similarity metric from the existing index
        indexes = (
            await self._aclient[collection_name]
            .list_search_indexes(EMBEDDING_INDEX)
            .to_list()
        )

        similarity = None

        for idx in indexes:
            if idx["name"] == EMBEDDING_INDEX:
                idx_fields = idx["latestDefinition"]["fields"]
                for idx_field in idx_fields:
                    if idx_field["type"] == "vector":
                        similarity = idx_field["similarity"]
                        num_dimensions = idx_field["numDimensions"]
                        break
                if similarity:
                    break

        # Create the index for each metadata field
        definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": num_dimensions,
                    "similarity": similarity,
                }
            ]
        }

        definition["fields"].extend(
            [{"type": "filter", "path": field} for field in fields]
        )

        await self._aclient[collection_name].update_search_index(
            name=EMBEDDING_INDEX,
            definition=definition,
        )

    @staticmethod
    def merge_embedding_and_metadata(
        embeddings: List[List[float]], metadatas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merges embedding vectors with their respective metadata.

        This function takes a list of embedding vectors and a list of metadata dictionaries,
        and merges each embedding vector with its corresponding metadata dictionary. The
        result is a list of dictionaries where each dictionary contains both the embedding
        vector and the metadata.

        Args:
            embeddings (List[List[float]]): A list of embedding vectors, where each embedding is represented as a list of floats.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries, where each dictionary contains metadata corresponding to an embedding.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains an embedding vector and its associated metadata.
        """

        merged_list = []
        for embedding, metadata in zip(embeddings, metadatas):
            merged_entry = {"embedding": embedding}
            merged_entry.update(metadata)
            merged_list.append(merged_entry)

        return merged_list
