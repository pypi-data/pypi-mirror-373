# pylint: disable=line-too-long, duplicate-code, too-many-instance-attributes, arguments-differ, too-many-locals, logging-fstring-interpolation
"""
Vertex AI Vector Search Vector Store Module.

This module provides a concrete implementation of the VectorStore abstract base class,
using Vertex AI Vector Search for managing collections of vectors and their associated metadata.
"""

import hashlib
import json
import os
import uuid
from typing import Any, Dict, List, Optional, override

try:
    from google.auth import default as google_auth_default
    from google.auth.credentials import Credentials
    from google.cloud import aiplatform  # type: ignore[attr-defined]
    from google.cloud.aiplatform.matching_engine import (
        MatchingEngineIndex,
        MatchingEngineIndexEndpoint,
    )
    from google.cloud.aiplatform.matching_engine.matching_engine_index_config import (
        DistanceMeasureType,
    )
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
        Namespace,
    )
    from google.cloud.aiplatform_v1.types import IndexDatapoint
    from google.oauth2 import service_account

except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate google-cloud-aiplatform package. "
        'Please install it with `pip install "autonomize-autorag[vertex-ai-vector-search]"`.'
    ) from err

from autorag.exceptions.vector_stores import (
    VectorStoreCollectionAlreadyExistsException,
    VectorStoreCollectionNotFoundException,
)
from autorag.types.vector_stores import DistanceType, VectorStoreQueryResult
from autorag.utilities.concurrency import run_async
from autorag.utilities.logger import get_logger
from autorag.vector_stores import VectorStore

logger = get_logger(__name__)


class VertexAIVectorSearchVectorStore(VectorStore):
    """
    Vertex AI Vector Search vector store implementation.

    This class provides an interface for interacting with an Vertex AI Vector Search vector store,
    utilizing the Google SDK for Python for different operations.

    Args:
        use_application_default (bool):
            Whether to use the default authentication.
            To use default authentication, run `gcloud auth application-default login`
        project (Optional[str]): Project ID of the project on Vertex AI Studio.
        location (Optional[str]): Location of the project on Vertex AI Studio.
        credentials_path (Optional[str]): Path of service info file.
        credentials_dict (Optional[str]): JSON of service credentials
        explicit_credentials (Optional[Credentials]): Credentials created using Google SDK.

    Example:

    .. code-block:: python

        from autorag.vector_stores import VertexAIVectorSearchVectorStore
        from autorag.types.vector_stores import DistanceType

        client = VertexAIVectorSearchVectorStore(
            use_application_default=True
            project='<your-project-id>'
            location='<your-project-location>'
        )

        client.create_collection(
            collection_name="test_collection",
            embedding_dimensions=768,
            distance=DistanceType.DOT_PRODUCT,
        )
    """

    def __init__(
        self,
        use_application_default: bool = True,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials_path: Optional[str] = None,
        credentials_dict: Optional[dict] = None,
        explicit_credentials: Optional[Credentials] = None,
    ):
        self._project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self._location = location or os.getenv("GOOGLE_CLOUD_LOCATION")
        self._credentials_path = credentials_path or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self._credentials_dict = credentials_dict
        self._explicit_credentials = explicit_credentials
        self._use_application_default = use_application_default
        self._authenticate()

    def _authenticate(self):
        """
        Authenticates the Vertex AI for all incoming requests.

        Raises:
            ValueError: If no valid credentials are present to authenticate with google
        """

        if self._use_application_default:
            # Expects a .json file present at ~/.config/gcloud/
            self._credentials, _ = google_auth_default()

        elif self._explicit_credentials:
            self._credentials = self._explicit_credentials

        elif self._credentials_dict:
            self._credentials = service_account.Credentials.from_service_account_info(
                self._credentials_dict
            )

        elif self._credentials_path:
            # Path can be either a string JSON or a dict-like string from env var
            if os.path.exists(self._credentials_path):
                self._credentials = (
                    service_account.Credentials.from_service_account_file(
                        self._credentials_path
                    )
                )
            else:
                # Assume it's a JSON string in an env variable
                self._credentials = (
                    service_account.Credentials.from_service_account_info(
                        json.loads(self._credentials_path)
                    )
                )

        else:
            raise ValueError("No valid authentication method provided.")

        # Initialize the authentication
        aiplatform.init(
            project=self._project,
            location=self._location,
            credentials=self._credentials,
        )

    def _get_distance_metric(self, distance: DistanceType) -> DistanceMeasureType:
        """
        Converts DistanceType to the corresponding `DistanceMeasureType`
        metric as per the configurations required by the Vertex AI Vector Search.

        Args:
            distance (DistanceType): The type of distance metric to use.

        Returns:
            str: The matching distance metric for the Qdrant configuration.
        """
        if distance == DistanceType.EUCLIDEAN:
            return DistanceMeasureType.SQUARED_L2_DISTANCE
        if distance == DistanceType.COSINE:
            return DistanceMeasureType.COSINE_DISTANCE
        return DistanceMeasureType.DOT_PRODUCT_DISTANCE

    def _get_index(self, index_name: str) -> Optional[MatchingEngineIndex]:
        """
        Given the display name of the index, gets the index.

        Args:
            index_name (str): Display name of the index

        Returns:
            Optional[MatchingEngineIndex]: The index object.
        """
        indexes = MatchingEngineIndex.list(filter=f'display_name="{index_name}"')
        return indexes[0] if indexes else None  # type: ignore[return-value]

    def _get_index_endpoint(
        self, endpoint_name: str
    ) -> Optional[MatchingEngineIndexEndpoint]:
        """
        Given the display_name of index endpoint, returns the endpoint.

        Args:
            endpoint_name (str): Display name of index endpoint

        Returns:
            Optional[MatchingEngineIndexEndpoint]: Object of endpoint
        """
        endpoints = MatchingEngineIndexEndpoint.list(
            filter=f'display_name="{endpoint_name}"'
        )
        return MatchingEngineIndexEndpoint(index_endpoint_name=endpoints[0].resource_name) if endpoints else None  # type: ignore[return-value]

    def _is_index_deployed(
        self, endpoint: MatchingEngineIndexEndpoint, index_name: str
    ) -> bool:
        """
        Checks if the index is already deployed or not to the corresponding endpoint

        Args:
            endpoint (MatchingEngineIndexEndpoint): Index endpoint.
            index_name (str): Resource name of the index.

        Returns:
            bool: Flag identifying the deployment status of the index
        """
        return any(
            deployed.index == index_name for deployed in endpoint.deployed_indexes
        )

    def get_collection_status(
        self,
        collection_name: str,
    ):
        """
        Checks the status of collection creation and returns it.

        Args:
            collection_name (str): Name of the collection

        Returns:
            bool: The status of index creation
        """

        return self._collection_exists(collection_name=collection_name)

    def _create_deployed_index_id(self, collection_name: str) -> str:
        """
        Generate a deterministic, Vertex AI Vector Search-compliant index ID based on
        the collection name.

        The index ID:
        - Is derived deterministically using a fixed internal namespace and the collection name.
        - Always starts with a letter.
        - Contains only lowercase letters, numbers, and underscores.
        - Has a consistent format with underscores every 8 characters, up to 32 characters total.

        Args:
            collection_name (str): The name of the collection for which to generate the index ID.

        Returns:
            str: A valid index ID string suitable for use in Vertex AI.
        """
        # Combine namespace and name to ensure uniquenessxw
        namespace = "12345678-1234-5678-1234-567812345678"
        combined = f"{namespace}:{collection_name}"

        # Compute SHA-256 hash and convert to hex
        hash_str = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        # Vertex AI only supports deployed_index_id starting with a letter
        # and containing only letters, numbers and underscores.
        filtered = "".join(c for c in hash_str if c.isalnum())
        if not filtered[0].isalpha():
            filtered = "A" + filtered

        index_id = "_".join(filtered[i : i + 8] for i in range(0, 32, 8)).lower()
        return index_id

    @override
    def create_collection(
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

        Raises:
            VectorStoreCollectionAlreadyExistsException: If the collection already exists.
        """
        endpoint_name = kwargs.get("endpoint_name", collection_name)

        index = self._get_index(index_name=collection_name)
        index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)

        # If index or endpoint or a deployed index already exists, raise exception
        if index:
            if index_endpoint:
                is_index_deployed = self._is_index_deployed(
                    endpoint=index_endpoint, index_name=index.resource_name
                )
                if is_index_deployed:
                    raise VectorStoreCollectionAlreadyExistsException(
                        f"Collection '{collection_name}' already exists."
                    )
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' is currently being created. "
                "If you have recently created the collection, it may take up to an hour to be fully created."
            )

        self._create_collection(
            collection_name=collection_name,
            embedding_dimensions=embedding_dimensions,
            distance=distance,
            **kwargs,
        )

    def _create_collection(  # type: ignore[override]
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        **kwargs: Any,
    ) -> None:
        """
        Creates a new index (collection) in Vertex AI Vector Search. After creating the index, this function
        also deploys the index on the dedicated endpoint.

        Args:
            collection_name (str): The name of the index to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
        """
        endpoint_name = kwargs.get("endpoint_name", collection_name)
        deployed_index_id: str = kwargs.pop(
            "deployed_index_id", None
        ) or self._create_deployed_index_id(collection_name)

        distance_measure_type = self._get_distance_metric(distance=distance)

        # Set replica count
        min_replica_count = kwargs.pop("min_replica_count", 1)
        max_replica_count = kwargs.pop("max_replica_count", 1)

        # Create index
        index = MatchingEngineIndex.create_tree_ah_index(
            display_name=collection_name,
            dimensions=embedding_dimensions,
            contents_delta_uri=kwargs.pop("contents_delta_uri", None),
            approximate_neighbors_count=100,
            distance_measure_type=distance_measure_type,
            index_update_method="STREAM_UPDATE",
            shard_size=kwargs.pop("shard_size", None) or "SHARD_SIZE_SMALL",
        )

        # Check if endpoint already exists
        index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)

        # Create the index endpoint if it doesn't exist
        if not index_endpoint:
            index_endpoint = MatchingEngineIndexEndpoint.create(
                display_name=endpoint_name,
                public_endpoint_enabled=True,
            )
            index_endpoint.wait()

        # Deploy the index to the endpoint without waiting for LRO to complete
        deployed_index = (
            index_endpoint._build_deployed_index(  # pylint: disable=protected-access
                deployed_index_id=deployed_index_id,
                index_resource_name=index.resource_name,
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )
        )
        index_endpoint.api_client.deploy_index(
            index_endpoint=index_endpoint.resource_name,
            deployed_index=deployed_index,
            metadata=(),
            timeout=None,
        )
        logger.info(
            "The collection creation is in progress, check the status of your index "
            "using `get_collection_status` method. it may take up to an hour to be fully created."
        )

    @override
    def delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """

        endpoint_name = kwargs.pop("endpoint_name", collection_name)

        index = self._get_index(index_name=collection_name)
        index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)

        if not index or not index_endpoint:
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        is_index_deployed = self._is_index_deployed(
            endpoint=index_endpoint, index_name=index.resource_name
        )
        if not is_index_deployed:
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' is currently being created. "
                "If you have recently created the collection, it may take up to an hour to be fully created. "
                "Please wait until it's fully created before deleting it."
            )

        self._delete_collection(
            collection_name=collection_name,
            index=index,
            index_endpoint=index_endpoint,
            **kwargs,
        )

    def _delete_collection(  # type: ignore[override]
        self,
        collection_name: str,
        **kwargs: Any,
    ):
        """
        Deletes an existing collection (index) in Vertex AI Vector Search.
        It firsts undeploys the index from the corresponding endpoint and then deletes it.

        Args:
            collection_name (str): The display name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.
        """
        deployed_index_id = kwargs.pop(
            "deployed_index_id", None
        ) or self._create_deployed_index_id(collection_name)

        index: MatchingEngineIndex = kwargs.pop("index")  # type: ignore[assignment]
        index_endpoint: MatchingEngineIndexEndpoint = kwargs.pop("index_endpoint")  # type: ignore[assignment]

        # Undeploy the index from endpoint
        try:
            index_endpoint.undeploy_index(deployed_index_id=deployed_index_id)
        except Exception as e:
            raise ValueError(f"[Error] Failed to undeploy index: {e}") from e

        # Check if endpoint has any other deployed indexes
        # Refresh endpoint to get updated deployed_indexes
        index_endpoint: MatchingEngineIndexEndpoint = self._get_index_endpoint(  # type: ignore[no-redef]
            endpoint_name=index_endpoint.display_name
        )

        if len(index_endpoint.deployed_indexes) == 0:
            # Delete index endpoint if no indexes remain
            try:
                index_endpoint.delete()
            except Exception as e:
                raise ValueError(f"[Error] Failed to delete endpoint: {e}") from e

        # Delete index
        try:
            index.delete()
        except Exception as e:
            raise ValueError(f"[Error] Failed to delete index: {e}") from e

    def _generate_document_id(self, *args) -> str:
        """
        Generates a unique ID for the record.

        Returns:
            str: Unique ID of the record to be inserted
        """
        flattened_args: List[str] = []
        for arg in args:
            if isinstance(arg, list):
                flattened_args.extend(str(x) for x in arg)
            else:
                flattened_args.append(str(arg))

        name = "|".join(flattened_args)
        return str(
            uuid.uuid5(
                namespace=uuid.UUID("12345678-1234-5678-1234-567812345678"), name=name
            )
        )

    @override
    def upsert(
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
                endpoint_name (Optional[str]): Name of the endpoint.
                    Defaults to collection_name for backward compatibility.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection doesn't exist.
            VectorStoreDataMismatchException: If the number of embeddings and metadatas do not match.
        """
        # Check whether len of embeddings and metadatas are same or not.
        self._validate_embeddings_and_metadata(
            embeddings=embeddings, metadatas=metadatas
        )

        endpoint_name = kwargs.get("endpoint_name", collection_name)

        index = self._get_index(index_name=collection_name)
        index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)

        if not index:
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        if index_endpoint:
            is_index_deployed = self._is_index_deployed(
                endpoint=index_endpoint, index_name=index.resource_name
            )
            if not is_index_deployed:
                raise VectorStoreCollectionAlreadyExistsException(
                    f"Collection '{collection_name}' is currently being created. "
                    "If you have recently created the collection, it may take up to an hour to be fully created. "
                    "Please wait until it's fully created before using it."
                )

        self._upsert(
            collection_name=collection_name,
            embeddings=embeddings,
            metadatas=metadatas,
            index=index,
            **kwargs,
        )

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
            collection_name (str): Display name of the index
            embeddings (List[List[float]]): A list of vectors to be upserted.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the embeddings.
            kwargs (Any): Any additional arguments to be used.
        """
        index: MatchingEngineIndex = kwargs.pop("index", None) or self._get_index(  # type: ignore[assignment]
            index_name=collection_name
        )

        datapoints = []
        for embedding, metadata in zip(embeddings, metadatas):
            datapoint_id = str(
                metadata.get(
                    "id", self._generate_document_id(*metadata.values())
                )  # Create unique ID for the metadata
            )
            restricts = []
            for key, value in metadata.items():
                if key == "id":
                    continue
                allow_values = (
                    [str(value)]
                    if not isinstance(value, list)
                    else [str(v) for v in value]
                )
                restricts.append(
                    IndexDatapoint.Restriction(namespace=key, allow_list=allow_values)
                )

            datapoint = IndexDatapoint(
                datapoint_id=datapoint_id,
                feature_vector=embedding,
                crowding_tag=None,
                restricts=restricts,
            )
            datapoints.append(datapoint)
        index.upsert_datapoints(datapoints=datapoints)  # type: ignore

    @override
    def query(
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
                endpoint_name (Optional[str]): Name of the endpoint.
                    Defaults to collection_name for backward compatibility.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        endpoint_name = kwargs.get("endpoint_name", collection_name)

        index = self._get_index(index_name=collection_name)
        index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)

        if not index:
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        if not index_endpoint:
            raise VectorStoreCollectionNotFoundException(
                f"Endpoint '{endpoint_name}' does not exist."
            )

        is_index_deployed = self._is_index_deployed(
            endpoint=index_endpoint, index_name=index.resource_name
        )
        if not is_index_deployed:
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' is currently being created. "
                "If you have recently created the collection, it may take up to an hour to be fully created. "
                "Please wait until it's fully created before using it."
            )

        return self._query(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
            metadata_fields=metadata_fields,
            index=index,
            index_endpoint=index_endpoint,
            **kwargs,
        )

    def _query(  # type: ignore[override]
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
            collection_name (str): Display name of the index.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments required.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.
        """
        index: MatchingEngineIndex = kwargs.get("index")  # type: ignore[assignment]
        index_endpoint: MatchingEngineIndexEndpoint = kwargs.get("index_endpoint")  # type: ignore[assignment]

        # Get the deployed index ID for this specific index
        deployed_index_id = kwargs.pop(
            "deployed_index_id", None
        ) or self._create_deployed_index_id(collection_name)

        distance_metrics = index.to_dict()["metadata"]["config"]["distanceMeasureType"]

        filters = self._build_query_filter(metadata_filter=metadata_filter)
        response = index_endpoint.find_neighbors(
            deployed_index_id=deployed_index_id,
            num_neighbors=top_k,
            queries=[query_embedding],
            filter=filters,
            return_full_datapoint=True,
        )

        # Return empty list if no result returned.
        if not response:
            return []

        # Create the required metadata
        results = []
        neighbors = response[0]  # Expecting one query at a time
        for neighbor in neighbors:
            if neighbor.distance is not None:
                # If we get cosine distance, we convert it into cosine similarity
                # by using `1 - neighbor.distance`.
                if distance_metrics == "COSINE_DISTANCE":
                    score = 1 - neighbor.distance
                else:
                    score = neighbor.distance
            else:
                score = 0.0
            neighbor_restricts = neighbor.restricts
            neighbor_metadata = {}
            for restrict in neighbor_restricts:  # type: ignore[union-attr]
                if restrict.name in metadata_fields:
                    neighbor_metadata[restrict.name] = restrict.allow_tokens[0]
            results.append(
                VectorStoreQueryResult(
                    score=score, metadata={**neighbor_metadata, **({"id": neighbor.id} if "id" in metadata_fields else {})}  # type: ignore[arg-type]
                )
            )

        return results

    def _build_query_filter(self, metadata_filter: Dict[str, Any]) -> List[Namespace]:
        """
        Constructs a query filter for the Vertex AI Vector Search based on the provided metadata.

        The function translates a dictionary of metadata filters into a format suitable for querying
        the vector store. Each key-value pair in the metadata_filter dictionary is converted
        into a corresponding filter condition.

        Supported filter conditions:
        - Equality
        - IN (as in checking all values in a list)

        Note:
            Additional filter conditions to be added later.

        Args:
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.

        Returns:
            List[Namespace]: A list of namespaces with filters.
        """

        restricts = []
        for namespace, value in metadata_filter.items():
            allow = value if isinstance(value, list) else [value]
            restricts.append(
                Namespace(name=namespace, allow_tokens=[str(v) for v in allow])
            )
        return restricts

    @override
    def delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Deletes items from a collection that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.

        Note:
            Vertex AI Vector Search does not currently expose a server-side
            "delete by filter" using namespaces/restricts. To delete by metadata,
            you must know the datapoint IDs that were used at upsert time.
        """
        endpoint_name = kwargs.get("endpoint_name", collection_name)

        index = self._get_index(index_name=collection_name)
        index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)

        if not index:
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        if not index_endpoint:
            raise VectorStoreCollectionNotFoundException(
                f"Endpoint '{endpoint_name}' does not exist."
            )

        is_index_deployed = self._is_index_deployed(
            endpoint=index_endpoint, index_name=index.resource_name
        )
        if not is_index_deployed:
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' is currently being created. "
                "If you have recently created the collection, it may take up to an hour to be fully created. "
                "Please wait until it's fully created before using it."
            )

        return self._delete_by_metadata(
            collection_name=collection_name,
            metadata_filter=metadata_filter,
            index=index,
            index_endpoint=index_endpoint,
            **kwargs,
        )

    def _delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Deletes datapoints from a collection by datapoint ID.

        Args:
            collection_name (str): Display name of the index.
            metadata_filter (Dict[str, Any]): Must include key "id" (str or List[str]).
            kwargs (Any): Unused extras; accepted for API symmetry.

        Raises:
            ValueError: If no valid 'id' is provided in the filter.

        Note:
            Vertex AI Vector Search does not currently expose a server-side
            "delete by filter" using namespaces/restricts. To delete by metadata,
            you must know the datapoint IDs that were used at upsert time.
        """
        index: MatchingEngineIndex = kwargs.get("index", self._get_index(index_name=collection_name))  # type: ignore[assignment]

        index_dimension = int(index.to_dict()["metadata"]["config"]["dimensions"])

        query_embedding = [0.0] * index_dimension

        search_result = self.query(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=9999,
            metadata_fields=["id"],
            metadata_filter=metadata_filter,
        )

        datapoint_ids = [result.metadata["id"] for result in search_result]

        # Perform deletion
        index.remove_datapoints(datapoint_ids=datapoint_ids)  # type: ignore[arg-type]

    def _collection_exists(  # type: ignore[override]
        self, collection_name: str, **kwargs: Any
    ) -> bool:
        """
        Checks if a collection (index) exists in Vertex AI Vector Search and is deployed to an endpoint.

        Args:
            collection_name (str): The display name of the collection to check.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            bool: True if the collection exists and is deployed, False otherwise.
        """
        endpoint_name = kwargs.get("endpoint_name", collection_name)

        try:
            # Check if index already present.
            index = self._get_index(index_name=collection_name)
            if not index:
                logger.info(
                    f"The index with name: {collection_name} has not been created yet."
                )
                return False

            # Fetch the already existing endpoint
            index_endpoint = self._get_index_endpoint(endpoint_name=endpoint_name)
            if not index_endpoint:
                logger.info(
                    f"The endpoint with name: {endpoint_name} has not been created yet."
                )
                return False

            index_deployed = self._is_index_deployed(
                endpoint=index_endpoint, index_name=index.resource_name
            )
            if not index_deployed:
                logger.info(
                    "The index is currently being deployed to the endpoint. "
                    "Please wait some time for the deployment to complete."
                )
                return False
            logger.info("Index is deployed and ready to use.")
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    async def aget_collection_status(
        self,
        collection_name: str,
    ):
        """
        Asynchronously checks the status of collection creation and returns it.

        Args:
            collection_name (str): Name of the collection

        Returns:
            bool: The status of index creation
        """

        return await run_async(
            self.get_collection_status,
            collection_name=collection_name,
        )
