"""
Azure AI Search Vector Store Module.

This module provides a concrete implementation of the VectorStore abstract base class,
using Azure AI Search for managing collections of vectors and their associated metadata.
"""

# pylint: disable=line-too-long, duplicate-code, too-many-instance-attributes, arguments-differ

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Dict, List, override

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
    from azure.identity import DefaultAzureCredential
    from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
    from azure.search.documents import SearchClient, SearchIndexingBufferedSender
    from azure.search.documents.aio import SearchClient as AsyncSearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.aio import (
        SearchIndexClient as AsyncSearchIndexClient,
    )
    from azure.search.documents.indexes.models import (
        ComplexField,
        ExhaustiveKnnAlgorithmConfiguration,
        ExhaustiveKnnParameters,
        HnswAlgorithmConfiguration,
        HnswParameters,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SimpleField,
        VectorSearch,
        VectorSearchAlgorithmKind,
        VectorSearchAlgorithmMetric,
        VectorSearchProfile,
    )
    from azure.search.documents.models import VectorizedQuery
except ImportError as err:  # pragma: no cover
    raise ImportError(
        "Unable to locate azure-search-documents package. "
        'Please install it with `pip install "autonomize-autorag[azure-ai-search]"`.'
    ) from err

from autorag.exceptions.vector_stores import (
    VectorStoreCollectionAlreadyExistsException,
    VectorStoreCollectionNotFoundException,
    VectorStoreDataMismatchException,
)
from autorag.types.vector_stores import DistanceType, VectorStoreQueryResult
from autorag.vector_stores.base import VectorStore


class AsyncKeyCredential:
    "Wraper Around Key Credential to make it usable with async with"

    def __init__(self, sync_obj: AzureKeyCredential):
        self._sync_obj = sync_obj

    async def __aenter__(self):
        """Async enter - returns the wrapped object"""
        return self._sync_obj

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async exit - clean up if needed"""


class FieldDataType(str, Enum):
    """
    Enum class for valid data types for vector indexes.
    """

    # We don't have `single` or `single_list` here because
    # Azure doesn't support single precision outside vectors.
    # Please use `double` or `double_list` in its place.

    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    DOUBLE = "double"
    BOOLEAN = "boolean"

    STRING_LIST = "string_list"
    INT32_LIST = "int32_list"
    INT64_LIST = "int64_list"
    DOUBLE_LIST = "double_list"
    BOOLEAN_LIST = "boolean_list"

    @classmethod
    def from_str(cls, value: str) -> FieldDataType:
        """
        Converts a string to FieldDataType
        Args:
            value (str): raw string value

        Returns:
            FieldDataType: FieldDataType object corresponding to the string
        """

        try:
            return cls(value)
        except ValueError:
            return cls.STRING

    def get_azure_data_type(self) -> str:
        """
        Convert FieldDataType to the corresponding Azure datatype string.

        Returns:
            str : Coresponding Azure Search Field data type for FieldDataType
        """

        mapping = {
            FieldDataType.STRING: SearchFieldDataType.String,
            FieldDataType.INT32: SearchFieldDataType.Int32,
            FieldDataType.INT64: SearchFieldDataType.Int64,
            FieldDataType.DOUBLE: SearchFieldDataType.Double,
            FieldDataType.BOOLEAN: SearchFieldDataType.Boolean,
            FieldDataType.STRING_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.String
            ),
            FieldDataType.INT32_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Int32
            ),
            FieldDataType.INT64_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Int64
            ),
            FieldDataType.DOUBLE_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Double
            ),
            FieldDataType.BOOLEAN_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Boolean
            ),
        }
        return mapping.get(self, SearchFieldDataType.String)


class AzureAISearchVectorStore(VectorStore):
    """
    Azure AI Search vector store implementation.

    This class provides an interface for interacting with an Azure AI Search vector database,
    utilizing the Azure SDK for Python for different operations.

    Args:
        endpoint (str): The endpoint of your Azure AI Search service.
        api_key (str): The API key for your Azure AI Search service.
        use_managed_identity (bool): If True, uses the managed identity for authentication. Default is False.

    Attributes:
        _m (int): Number of edges per node in the HNSW index graph.
                  Larger values lead to more accurate searches but require more space.
                  Default is 10.
        _ef_construct (int): Number of neighbors considered during the index building process.
                             Larger values improve accuracy but increase indexing time.
                             Default is 512.
        _ef_search (int): Size of the beam during a beam-search operation.
                          Larger values lead to more accurate search results but require more time.
                          Recommended to be the same as `_ef_construct`. Default is 512.

    Example:

    .. code-block:: python

        from autorag.vector_stores import AzureAISearchVectorStore
        from autorag.types.vector_stores import DistanceType

        client = AzureAISearchVectorStore(
            endpoint='https://<your-service-name>.search.windows.net',
            api_key='<your-api-key>'
        )

        client.create_collection(
            collection_name="test_collection",
            embedding_dimensions=768,
            distance=DistanceType.COSINE,
            metadata_fields=["content"]
        )
    """

    def __init__(
        self, endpoint: str, api_key: str | None, use_managed_identity: bool = False
    ) -> None:

        self._credential = self._get_sync_credential(
            api_key=api_key, use_managed_identity=use_managed_identity
        )
        self._api_key = api_key
        self._endpoint = endpoint
        self._use_managed_identity = use_managed_identity

        self._index_client = SearchIndexClient(
            endpoint=self._endpoint, credential=self._credential
        )

        # Initialize collection parameters for HNSW
        self._m = (
            10  # Max allowed value is 10 for some reason, I wanted to set it to 16.
        )
        self._ef_construct = 512
        self._ef_search = self._ef_construct

        # Embedding field name
        # Fixed name for the field in the vector db to store embeddings.
        self._embedding_field_name = "embedding"

    def _get_sync_credential(
        self, api_key: str | None, use_managed_identity: bool
    ) -> AzureKeyCredential | DefaultAzureCredential:

        if use_managed_identity:
            return DefaultAzureCredential()
        if api_key:
            return AzureKeyCredential(key=api_key)

        raise ValueError(
            "No authentication method was provided. "
            "Pass an `api_key` (str) or set `use_managed_identity=True` "
            "to authenticate using the managed identity."
        )

    async def _get_async_credential(
        self, api_key: str | None, use_managed_identity: bool
    ) -> AsyncDefaultAzureCredential | AsyncKeyCredential:
        if use_managed_identity:
            return AsyncDefaultAzureCredential()
        if api_key:
            return AsyncKeyCredential(sync_obj=AzureKeyCredential(key=api_key))

        raise ValueError(
            "No authentication method was provided. "
            "Pass an `api_key` (str) or set `use_managed_identity=True` "
            "to authenticate using the managed identity."
        )

    def _schema_to_field(self, name: str, spec: Any) -> SearchField:
        """
        Turn a user schema spec into an Azure Search field, recursively.

        Args:
            name (str): The name of the field.
            spec (Any): The schema specification for the field.

        Supported:
            - "string", "int32", "double_list", ... (primitive or *_list)
            - {"type": "complex", "field": { ... }}
            - {"type": "complex_list", "field": { ... }}
            - Arbitrary nesting via the same pattern.

        Also accepts (optional) synonyms for flexibility:
            - "fields" instead of "field"
            - "object" instead of "complex"

        Args:
            name (str): The name of the field.
            spec (Any): The schema specification for the field.

        Returns:
            SearchField: The corresponding Azure Search field.

        """
        # 1) Primitive
        if isinstance(spec, str):
            # Uses your FieldDataType to map primitives and *_list to Azure types
            t_enum = FieldDataType.from_str(spec)
            return SimpleField(
                name=name,
                type=t_enum.get_azure_data_type(),
            )

        # 2) Complex / Complex list
        if isinstance(spec, dict):
            t = (spec.get("type") or "").lower()

            # Allow synonyms
            if t == "object":
                t = "complex"

            # pull child map from "field", falling back to "fields" for convenience
            child_map = spec.get("field", spec.get("fields"))
            if t in {"complex", "complex_list"}:
                if not isinstance(child_map, dict):
                    raise VectorStoreDataMismatchException(
                        f"Complex field '{name}' must have a dict under 'field'."
                    )

                child_fields: List[SearchField] = [
                    self._schema_to_field(child_name, child_spec)
                    for child_name, child_spec in child_map.items()
                ]

                return ComplexField(
                    name=name,
                    fields=child_fields,
                    collection=(t == "complex_list"),
                )

        raise VectorStoreDataMismatchException(
            f"Unsupported schema spec for field '{name}': {spec!r}"
        )

    async def _get_async_search_index_client(
        self, credential
    ) -> AsyncSearchIndexClient:
        return AsyncSearchIndexClient(endpoint=self._endpoint, credential=credential)

    def _create_fields(
        self,
        embedding_dimensions: int,
        metadata_fields: List[str],
        metadata_field_to_type_mapping: Dict[str, str],
    ) -> List[SearchField]:  # SimpleField instantiates SearchField class
        """
        Creates a list of fields for the collection, including metadata and embedding fields.

        Args:
            embedding_dimensions (int): Number of dimensions for the embeddings.
            metadata_fields (List[str]): List of metadata field names.

        Returns:
            List[SearchField]: List of SearchFields for the collection schema.
        """

        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            )  # Default id field as key
        ]

        for metadata_field in metadata_fields:
            spec = metadata_field_to_type_mapping.get(metadata_field, "string")
            fields.append(self._schema_to_field(metadata_field, spec))

        fields.append(
            SearchField(
                name=self._embedding_field_name,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=embedding_dimensions,
                vector_search_profile_name="myHnswProfile",
            )
        )

        return fields

    def _create_vector_search_config(
        self, vector_distance: VectorSearchAlgorithmMetric
    ) -> VectorSearch:
        """
        Creates vector search configurations using HNSW and KNN algorithms.

        Args:
            vector_distance (VectorSearchAlgorithmMetric): The distance metric to use.

        Returns:
            VectorSearch: The vector search configuration for the collection.
        """
        return VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw",
                    kind=VectorSearchAlgorithmKind.HNSW,
                    parameters=HnswParameters(
                        m=self._m,
                        ef_construction=self._ef_construct,
                        ef_search=self._ef_search,
                        metric=vector_distance,
                    ),
                ),
                ExhaustiveKnnAlgorithmConfiguration(
                    name="myExhaustiveKnn",
                    kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                    parameters=ExhaustiveKnnParameters(metric=vector_distance),
                ),
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                ),
                VectorSearchProfile(
                    name="myExhaustiveKnnProfile",
                    algorithm_configuration_name="myExhaustiveKnn",
                ),
            ],
        )

    def _get_distance_metric(
        self, distance: DistanceType
    ) -> VectorSearchAlgorithmMetric:
        """
        Converts DistanceType to the corresponding `VectorSearchAlgorithmMetric`
        metric as per the configurations required by the Azure AI Search Vector Store.

        Args:
            distance (DistanceType): The type of distance metric to use.

        Returns:
            str: The matching distance metric for the Qdrant configuration.
        """
        if distance == DistanceType.EUCLIDEAN:
            return VectorSearchAlgorithmMetric.EUCLIDEAN
        if distance == DistanceType.COSINE:
            return VectorSearchAlgorithmMetric.COSINE
        return VectorSearchAlgorithmMetric.DOT_PRODUCT

    def _create_collection(  # type: ignore[override]
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> None:
        """
        Creates a new collection (index) in Azure AI Search.

        Args:
            collection_name (str): The name of the index to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            metadata_fields (List[str]): A list of fields to define the schema of the collection.
            kwargs (Any): Any additional arguments to be used.
        """

        if "id" in metadata_fields:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata_fields."
            )

        vector_distance = self._get_distance_metric(distance=distance)

        metadata_field_to_type_mapping: Dict[str, str] = kwargs.pop(
            "metadata_field_to_type_mapping", {}
        )

        fields = self._create_fields(
            embedding_dimensions=embedding_dimensions,
            metadata_fields=metadata_fields,
            metadata_field_to_type_mapping=metadata_field_to_type_mapping,
        )

        vector_search = self._create_vector_search_config(
            vector_distance=vector_distance
        )

        index = SearchIndex(
            name=collection_name,
            fields=fields,
            vector_search=vector_search,
        )

        self._index_client.create_index(index, **kwargs)

    def _delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection (index) in Azure AI Search.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.
        """
        self._index_client.delete_index(collection_name, **kwargs)

    def _upsert(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Upserts embeddings and metadata into the collection (index).

        Args:
            collection_name (str): The name of the collection to upsert into.
            embeddings (List[List[float]]): A list of vectors to be upserted.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the embeddings.
            kwargs (Any): Any additional arguments to be used.
        """

        use_client_provided_id: bool = False

        if "use_client_provided_id" in kwargs:
            # for idempotency when ExactlyOnceProcessing cannot be guaranteed
            use_client_provided_id_value_in_kwargs: bool = kwargs[
                "use_client_provided_id"
            ]
            kwargs.pop("use_client_provided_id")
            if "id" in metadatas[0] and use_client_provided_id_value_in_kwargs:
                use_client_provided_id = True

        if not use_client_provided_id and "id" in metadatas[0]:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata."
            )

        documents = []
        for embedding, metadata in zip(embeddings, metadatas):
            if use_client_provided_id:
                doc = {
                    self._embedding_field_name: embedding,
                    **metadata,
                }
            else:
                doc = {
                    "id": str(uuid.uuid4()),
                    self._embedding_field_name: embedding,
                    **metadata,
                }

            documents.append(doc)

        try:
            # `SearchIndexingBufferedSender` is preferred when batching uploading requests
            with SearchIndexingBufferedSender(
                endpoint=self._endpoint,
                index_name=collection_name,
                credential=self._credential,
            ) as batch_client:
                batch_client.upload_documents(documents=documents, **kwargs)

                # Manually flushing any remaining documents
                batch_client.flush()
        except HttpResponseError as e:  # pragma: no cover
            raise ValueError(f"Error occurred when uploading documents: {e}") from e

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

        search_client = SearchClient(
            endpoint=self._endpoint,
            index_name=collection_name,
            credential=self._credential,
        )  # type: ignore

        vector = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields=self._embedding_field_name,
        )

        results = search_client.search(
            search_text="",
            vector_queries=[vector],
            filter=filter_conditions,
            select=metadata_fields,
            top=top_k,
            **kwargs,
        )
        result_list = list(results)

        return self._convert_to_model(results=result_list)

    def _convert_to_model(
        self, results: List[Dict[str, Any]]
    ) -> List[VectorStoreQueryResult]:
        """
        Converts a list of the search results to VectorStoreQueryResult models.

        Args:
            results (List[Dict[str, Any]]): A list of search results from Azure AI Search.

        Returns:
            List[VectorStoreQueryResult]: A list of converted VectorStoreQueryResult models.
        """
        return [
            VectorStoreQueryResult(
                score=result.get("@search.score", 0.0),
                metadata={
                    k: v for k, v in result.items() if k not in {"@search.score"}
                },
            )
            for result in results
        ]

    def _build_query_filter(self, metadata_filter: Dict[str, Any]) -> str:
        """
        Constructs a query filter for the Azure AI Search vector store based on the provided metadata.

        The function translates a dictionary of metadata filters into a string format suitable for querying
        the vector store. Each key-value pair in the metadata_filter dictionary is converted
        into a corresponding OData filter condition needed for Azure AI Search.

        Supported filter conditions:
        - Equality
        - IN (as in checking all values in a list)

        Note:
            Additional filter conditions to be added later.

        Args:
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.

        Returns:
            str: A filter string formatted for Azure AI Search's API.
        """

        field_conditions = []

        for key, value in metadata_filter.items():
            if isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    # List of strings
                    or_conditions = " or ".join(
                        [f"{key} eq '{item}'" for item in value]
                    )
                elif all(isinstance(item, bool) for item in value):
                    # List of booleans
                    or_conditions = " or ".join(
                        [f"{key} eq {str(item).lower()}" for item in value]
                    )
                elif all(isinstance(item, (int, float)) for item in value):
                    # List of numbers (int, float)
                    or_conditions = " or ".join([f"{key} eq {item}" for item in value])
                else:
                    raise VectorStoreDataMismatchException(
                        f"Unsupported list type for key for filtering: {key}"
                    )

                or_conditions = f"({or_conditions})"
                field_conditions.append(or_conditions)

            # Non-list elements
            elif isinstance(value, str):
                condition = f"{key} eq '{value}'"
                field_conditions.append(condition)
            elif isinstance(value, bool):
                condition = f"{key} eq {str(value).lower()}"
                field_conditions.append(condition)
            elif isinstance(value, (int, float)):
                condition = f"{key} eq {value}"
                field_conditions.append(condition)
            else:
                raise VectorStoreDataMismatchException(
                    f"Unsupported data type for key for filtering: {key}"
                )

        return " and ".join(field_conditions)

    def _delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Deletes items from a collection (index) that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection (index) to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.
        """

        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        search_client = SearchClient(
            endpoint=self._endpoint,
            index_name=collection_name,
            credential=self._credential,
        )  # type: ignore

        # Collect all matching ids
        results = search_client.search(
            search_text="",
            filter=filter_conditions,
            select=["id"],
            **kwargs,
        )

        ids_to_delete: List[str] = [doc["id"] for doc in results]  # type: ignore[index]

        documents = [{"id": _id} for _id in ids_to_delete]

        try:
            # Buffered sender handles batching and retries.
            with SearchIndexingBufferedSender(
                endpoint=self._endpoint,
                index_name=collection_name,
                credential=self._credential,
            ) as batch_client:
                batch_client.delete_documents(documents=documents, **kwargs)
                batch_client.flush()
        except HttpResponseError as e:  # pragma: no cover
            raise ValueError(f"Error occurred when deleting documents: {e}") from e

    def _collection_exists(self, collection_name: str, **kwargs: Any) -> bool:
        """
        Checks if a collection (index) exists in Azure AI Search.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        try:
            self._index_client.get_index(collection_name)
            return True
        except ResourceNotFoundError:
            return False

    @override
    async def acreate_collection(  # type: ignore[override]
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> None:
        """
        Asynchronously creates a new collection (index) in Azure AI Search.

        Args:
            collection_name (str): The name of the index to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            metadata_fields (List[str]): A list of fields to define the schema of the collection.
            kwargs (Any): Any additional arguments to be used.
        """

        if "id" in metadata_fields:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata_fields."
            )

        if await self._acollection_exists(collection_name):
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' already exists."
            )

        vector_distance = self._get_distance_metric(distance=distance)

        metadata_field_to_type_mapping: Dict[str, str] = kwargs.pop(
            "metadata_field_to_type_mapping", {}
        )

        fields = self._create_fields(
            embedding_dimensions=embedding_dimensions,
            metadata_fields=metadata_fields,
            metadata_field_to_type_mapping=metadata_field_to_type_mapping,
        )

        vector_search = self._create_vector_search_config(
            vector_distance=vector_distance
        )

        index = SearchIndex(
            name=collection_name,
            fields=fields,
            vector_search=vector_search,
        )

        async with await self._get_async_credential(
            self._api_key, self._use_managed_identity
        ) as credential:
            async with await self._get_async_search_index_client(
                credential=credential
            ) as async_index_client:
                await async_index_client.create_index(index, **kwargs)

    @override
    async def adelete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Asynchronously deletes an existing collection in the vector store.

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

        async with await self._get_async_credential(
            self._api_key, self._use_managed_identity
        ) as credential:
            async with await self._get_async_search_index_client(
                credential=credential
            ) as async_index_client:

                await async_index_client.delete_index(collection_name, **kwargs)

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
        Asynchronously queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the embeddings and their corresponding metadatas.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        async with await self._get_async_credential(
            self._api_key, self._use_managed_identity
        ) as credential:
            async with AsyncSearchClient(
                endpoint=self._endpoint,
                index_name=collection_name,
                credential=credential,  # type: ignore[arg-type]
            ) as search_client:  # type: ignore[arg-type]

                vector = VectorizedQuery(
                    vector=query_embedding,
                    k_nearest_neighbors=top_k,
                    fields=self._embedding_field_name,
                )

                results = await search_client.search(
                    search_text="",
                    vector_queries=[vector],
                    filter=filter_conditions,
                    select=metadata_fields,
                    top=top_k,
                    **kwargs,
                )
                result_list = [result async for result in results]

                return self._convert_to_model(results=result_list)

    async def _acollection_exists(self, collection_name: str) -> bool:
        """
        Asynchronously checks if a collection (index) exists in Azure AI Search.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        try:
            async with await self._get_async_credential(
                self._api_key, self._use_managed_identity
            ) as credential:
                async with await self._get_async_search_index_client(
                    credential=credential
                ) as async_index_client:

                    await async_index_client.get_index(collection_name)

            return True
        except ResourceNotFoundError:
            return False
