"""OpenAI Embedding module implementation"""

# pylint: disable=line-too-long

import os
from typing import Any, List, Literal, Optional, Union, override

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate openai package. "
        'Please install it with `pip install "autonomize-autorag[openai]"`.'
    ) from err

from autorag.embedding.base import Embedding


class OpenAIEmbedding(Embedding):
    """
    Implementation of the Embedding abstract base class using OpenAI's API.

    This class utilizes OpenAI's API to generate embeddings for text data. It
    supports different models provided by OpenAI, allowing flexible and scalable
    embedding generation.

    Example:
    .. code-block:: python

        from autorag.embedding import OpenAIEmbedding

        model_name = "text-embedding-3-small"
        client = OpenAIEmbedding()

        client.create_embedding(
            texts=["Sample text"],
            model_name=model_name
        )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the OpenAI embedding client.

        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, the key is read from the environment variable 'OPENAI_API_KEY'.

        Raises:
            ValueError: If the API key is not provided and cannot be found in the environment.
        """
        super().__init__()

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable."
            )

        self._client = OpenAI(
            api_key=self.api_key,
        )
        self._aclient = AsyncOpenAI(
            api_key=self.api_key,
        )

    def _create_embedding(
        self,
        texts: List[str],
        model_name: Literal[
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002",
        ] = "text-embedding-ada-002",
        **kwargs: Any
    ) -> List[List[float]]:
        """
        Creates embeddings for the provided text(s) using OpenAI.

        Args:
            texts (List[str]): The input text or list of texts to generate embeddings for.
            model_name (str): OpenAI embedding model name. Defaults to "text-embedding-ada-002".
                Refer to: https://platform.openai.com/docs/guides/embeddings/embedding-models
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """
        response = self._client.embeddings.create(
            input=texts, model=model_name, **kwargs
        )

        embedding = [item.embedding for item in response.data]
        return embedding

    @override
    async def acreate_embedding(
        self,
        texts: Union[str, List[str]],
        model_name: Literal[
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002",
        ] = "text-embedding-ada-002",
        **kwargs: Any
    ) -> List[List[float]]:
        """
        Asynchronously creates embeddings for the provided text(s) using OpenAI.

        Args:
            texts (Union[str, List[str]]): The input text or list of texts to generate embeddings for.
            model_name (str): OpenAI embedding model name. Defaults to "text-embedding-ada-002".
                Refer to: https://platform.openai.com/docs/guides/embeddings/embedding-models
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """

        if isinstance(texts, str):
            texts = [texts]

        response = await self._aclient.embeddings.create(
            input=texts, model=model_name, **kwargs
        )

        embedding = [item.embedding for item in response.data]
        return embedding
