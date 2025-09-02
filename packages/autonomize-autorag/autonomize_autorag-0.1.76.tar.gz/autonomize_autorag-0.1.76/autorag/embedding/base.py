"Embedding abstraction module"

# pylint: disable=line-too-long

from abc import ABC, abstractmethod
from typing import Any, List, Union

from autorag.utilities.concurrency import run_async


class Embedding(ABC):
    """
    Abstract base class for Embedding.

    This class defines the interface for embedding model implementations. It provides
    a structure to create embeddings using various models, making it easier to switch
    between different embedding models.
    """

    def create_embedding(
        self, texts: Union[str, List[str]], **kwargs: Any
    ) -> List[List[float]]:
        """
        Creates embeddings for the provided text(s).

        Args:
            texts (Union[str, List[str]]): The input text or list of texts to generate embeddings for.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """

        if isinstance(texts, str):
            texts = [texts]

        return self._create_embedding(texts=texts, **kwargs)

    @abstractmethod
    def _create_embedding(self, texts: List[str], **kwargs: Any) -> List[List[float]]:
        """
        Creates embeddings for the provided text(s).

        Args:
            texts (List[str]): The input list of texts to generate embeddings for.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input texts.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_create_embedding'."
        )

    async def acreate_embedding(
        self, texts: Union[str, List[str]], **kwargs: Any
    ) -> List[List[float]]:
        """
        Asynchronously creates embeddings for the provided text(s).

        Args:
            texts (Union[str, List[str]]): The input text or list of texts to generate embeddings for.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """

        return await run_async(lambda: self.create_embedding(texts=texts, **kwargs))
