"""Hugging Face Embedding module implementation"""

# pylint: disable=line-too-long

from typing import Any, List

from autorag.embedding.base import Embedding


class HuggingFaceEmbedding(Embedding):
    """
    Hugging Face Embedding implementation.

    This class provides an implementation of the Embedding abstract class
    using the Hugging Face `SentenceTransformer` model to generate embeddings.

    Example:
    .. code-block:: python

        from autorag.embedding import HuggingFaceEmbedding

        model_name = "BAAI/bge-base-en-v1.5"
        model = HuggingFaceEmbedding(
            model_name=model_name
        )

        model.create_embedding("Sample text")
    """

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        """
        Initializes the Hugging Face embedding model.

        Args:
            model_name (str, optional): Hugging Face model name. Defaults to "BAAI/bge-base-en".
        """
        super().__init__()

        try:
            from sentence_transformers import (  # pylint: disable=import-outside-toplevel
                SentenceTransformer,
            )
        except ImportError as err:
            raise ImportError(
                "Unable to locate sentence_transformers package. "
                'Please install it with `pip install "autonomize-autorag[huggingface]"`.'
            ) from err

        self._model = SentenceTransformer(model_name)

    def _create_embedding(self, texts: List[str], **kwargs: Any) -> List[List[float]]:
        """
        Creates embeddings for the provided text(s).

        Args:
            texts (List[str]): The input list of texts to generate embeddings for.

        Returns:
            List[List[float]]: A list of embedding vectors for the input texts.
        """
        embedding = self._model.encode(texts, normalize_embeddings=True, **kwargs)

        if isinstance(embedding, list):
            return [e.tolist() for e in embedding]
        return embedding.tolist()
