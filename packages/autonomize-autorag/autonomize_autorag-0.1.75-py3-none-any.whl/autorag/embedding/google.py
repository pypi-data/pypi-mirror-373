"""Google Embedding module implementation"""

# pylint: disable=line-too-long

import os
import warnings
from typing import Any, List, Literal, Optional, Union, override

try:
    from google.genai import Client  # type: ignore[import-untyped]
    from google.genai.types import (  # type: ignore[import-untyped]
        EmbedContentConfig,
        HttpOptions,
    )
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate google-genai package. "
        'Please install it with `pip install "autonomize-autorag[google-genai]"`.'
    ) from err

from autorag.embedding import Embedding


class GoogleEmbedding(Embedding):
    """
    Implementation of the Embedding abstract base class using Google API.

    This class utilizes Google SDK to generate embeddings for text data. It
    supports different models provided by Google, allowing flexible and scalable
    embedding generation.

    Example:
    .. code-block:: python

        from autorag.embedding import GoogleEmbedding

        model_name = "text-embedding-004"
        client = GoogleEmbedding()

        client.create_embedding(
            texts=["Sample text"],
            model_name=model_name
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        vertexai: Optional[bool] = False,
    ):
        """
        Initializes the Google embedding client.

        Args:
            api_key (Optional[str]): API key for Gemini access if not using ADC. Defaults to None.
            project (Optional[str]): Google Cloud project ID. Defaults to env var or None.
            location (Optional[str]): Google Cloud location. Defaults to env var or None.
            vertexai (Optional[bool]): Whether to use Vertex AI backend. Defaults to False.

        Raises:
            ValueError: If the project or location is not provided and cannot be found in the environment
                when using Vertex AI.
        """
        self._project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self._location = location or os.getenv("GOOGLE_CLOUD_LOCATION")
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        use_vertexai = (
            vertexai
            or os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
        )
        self._vertexai = use_vertexai
        common_args = {
            "vertexai": use_vertexai,
            "project": self._project,
            "location": self._location,
        }

        if use_vertexai and self._api_key:
            warnings.warn(
                "The `api_key` argument is ignored when using Vertex AI.", stacklevel=2
            )

        if vertexai:
            if not self._project or not self._location:
                raise ValueError(
                    "Google Cloud `project` and `location` must be provided when using Vertex AI."
                )
        elif self._api_key:
            common_args["api_key"] = self._api_key
        else:
            raise ValueError(
                "Missing key inputs argument! "
                "To use the Google AI API, provide (`api_key`) argument. "
                "To use the Google Cloud API, provide (`vertexai`, `project` & `location`) arguments."
            )

        self._client = Client(**common_args)

    def _create_embedding(
        self,
        texts: List[str],
        model_name: Literal[
            "embedding-001",
            "gemini-embedding-exp-03-07",
            "text-embedding-004",
        ] = "text-embedding-004",
        task_type: Literal[
            "SEMANTIC_SIMILARITY",
            "CLASSIFICATION",
            "CLUSTERING",
            "RETRIEVAL_DOCUMENT",
            "RETRIEVAL_QUERY",
            "QUESTION_ANSWERING",
            "FACT_VERIFICATION",
            "CODE_RETRIEVAL_QUERY",
        ] = "CLUSTERING",
        **kwargs: Any
    ) -> List[List[float]]:
        """
        Creates embeddings for the provided text(s) using Google.

        Args:
            texts (List[str]): The input text or list of texts to generate embeddings for.
            model_name (str): Google embedding model name. Defaults to "text-embedding-004".
                Refer to: https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """

        config = EmbedContentConfig(
            http_options=HttpOptions(api_version="v1"), task_type=task_type
        )
        response = self._client.models.embed_content(
            model=model_name, contents=texts, config=config
        )
        output = [result.values for result in response.embeddings]
        return output

    @override
    async def acreate_embedding(
        self,
        texts: Union[str, List[str]],
        model_name: Literal[
            "embedding-001",
            "gemini-embedding-exp-03-07",
            "text-embedding-004",
        ] = "text-embedding-004",
        task_type: Literal[
            "SEMANTIC_SIMILARITY",
            "CLASSIFICATION",
            "CLUSTERING",
            "RETRIEVAL_DOCUMENT",
            "RETRIEVAL_QUERY",
            "QUESTION_ANSWERING",
            "FACT_VERIFICATION",
            "CODE_RETRIEVAL_QUERY",
        ] = "CLUSTERING",
        **kwargs: Any
    ) -> List[List[float]]:
        """
        Asynchronously creates embeddings for the provided text(s) using Google.

        Args:
            texts (Union[str, List[str]]): The input text or list of texts to generate embeddings for.
            model_name (str): Google embedding model name. Defaults to "text-embedding-004".
                Refer to: https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """

        config = EmbedContentConfig(
            http_options=HttpOptions(api_version="v1"), task_type=task_type
        )
        response = await self._client.aio.models.embed_content(
            model=model_name, contents=texts, config=config
        )
        output = [result.values for result in response.embeddings]
        return output
