"""Vector Store abstraction module."""

# pylint: disable=line-too-long

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from autorag.exceptions.vector_stores import (
    VectorStoreCollectionAlreadyExistsException,
    VectorStoreCollectionNotFoundException,
    VectorStoreDataMismatchException,
)
from autorag.types.vector_stores import DistanceType, VectorStoreQueryResult
from autorag.utilities.concurrency import run_async


class VectorStore(ABC):
    """
    Abstract base class for Vector Store.

    This class defines the interface for vector store implementations. A vector store is
    responsible for managing collections of vectors, which are crucial in machine learning
    and retrieval-augmented generation (RAG) systems.
    """

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
        if self._collection_exists(collection_name, **kwargs):
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' already exists."
            )

        self._create_collection(
            collection_name=collection_name,
            embedding_dimensions=embedding_dimensions,
            distance=distance,
            **kwargs,
        )

    @abstractmethod
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

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_create_collection'."
        )

    def delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        if not self._collection_exists(collection_name, **kwargs):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        self._delete_collection(collection_name=collection_name, **kwargs)

    @abstractmethod
    def _delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_delete_collection'."
        )

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

        Raises:
            VectorStoreCollectionNotFoundException: If the collection doesn't exist.
            VectorStoreDataMismatchException: If the number of embeddings and metadatas do not match.
        """
        if not self._collection_exists(collection_name, **kwargs):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        # Check whether len of embeddings and metadatas are same or not.
        self._validate_embeddings_and_metadata(
            embeddings=embeddings, metadatas=metadatas
        )

        self._upsert(
            collection_name=collection_name,
            embeddings=embeddings,
            metadatas=metadatas,
            **kwargs,
        )

    @abstractmethod
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

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_upsert'."
        )

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

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        if not self._collection_exists(collection_name, **kwargs):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        return self._query(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
            metadata_fields=metadata_fields,
            **kwargs,
        )

    @abstractmethod
    def _query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs,
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

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_query'."
        )

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
        """
        if not self._collection_exists(collection_name, **kwargs):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        self._delete_by_metadata(
            collection_name=collection_name,
            metadata_filter=metadata_filter,
            **kwargs,
        )

    @abstractmethod
    def _delete_by_metadata(
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
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_delete_by_metadata'."
        )

    @abstractmethod
    def _collection_exists(self, collection_name: str, **kwargs: Any) -> bool:
        """
        Checks if a collection exists in the vector store.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_collection_exists'."
        )

    def _validate_embeddings_and_metadata(
        self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Validates that the number of embeddings matches the number of metadata entries.

        Args:
            embeddings (List[List[float]]): A list of vectors to be upserted.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the embeddings.

        Raises:
            VectorStoreDataMismatchException: If the number of embeddings and metadatas do not match.
        """
        if len(embeddings) != len(metadatas):
            raise VectorStoreDataMismatchException(
                f"The number of metadatas must match the number of embeddings."
                f" Got {len(metadatas)} metadatas and {len(embeddings)} embeddings."
            )

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

        await run_async(
            lambda: self.create_collection(
                collection_name=collection_name,
                embedding_dimensions=embedding_dimensions,
                distance=distance,
                **kwargs,
            )
        )

    async def adelete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Asyncronously deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        await run_async(
            lambda: self.delete_collection(collection_name=collection_name, **kwargs)
        )

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
        await run_async(
            lambda: self.upsert(
                collection_name=collection_name,
                embeddings=embeddings,
                metadatas=metadatas,
                **kwargs,
            )
        )

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
            List[VectorStoreQueryResult]: A list of dictionaries containing the embeddings and their corresponding metadatas.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """

        return await run_async(
            lambda: self.query(
                collection_name=collection_name,
                query_embedding=query_embedding,
                top_k=top_k,
                metadata_filter=metadata_filter,
                metadata_fields=metadata_fields,
                **kwargs,
            )
        )

    async def adelete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Asyncronously deletes items from a collection that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        return await run_async(
            lambda: self.delete_by_metadata(
                collection_name=collection_name,
                metadata_filter=metadata_filter,
                **kwargs,
            )
        )
