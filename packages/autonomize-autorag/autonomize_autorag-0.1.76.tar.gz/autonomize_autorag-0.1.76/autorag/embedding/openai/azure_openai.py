"""OpenAI Embedding module implementation"""

# pylint: disable=line-too-long, duplicate-code

import os
from typing import Optional

try:
    from openai import AsyncAzureOpenAI, AzureOpenAI
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate openai package. "
        'Please install it with `pip install "autonomize-autorag[openai]"`.'
    ) from err

from autorag.embedding.openai.base_openai import OpenAIEmbedding


class AzureOpenAIEmbedding(OpenAIEmbedding):
    """
    Azure OpenAI Embedding implementation using the OpenAI client for Azure.

    This class utilizes Azure's OpenAI API to generate embeddings for text data.
    It allows specifying the API key, base URL, and version, either directly or via
    environment variables.

    Example:
    .. code-block:: python

        from autorag.embedding import AzureOpenAIEmbedding

        model_name = "text-embedding-3-small"
        client = AzureOpenAIEmbedding()

        client.create_embedding(
            texts=["Sample text"],
            model_name=model_name
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        """
        Initializes the Azure OpenAI client.

        Args:
            api_key (Optional[str]): Azure OpenAI API key. If not provided, it will be read from the 'OPENAI_API_KEY' environment variable.
            azure_endpoint (Optional[str]): Azure endpoint deployed. If not provided, it will be read from the 'AZURE_OPENAI_ENDPOINT' environment variable.
            api_version (Optional[str]): Azure OpenAI API version. If not provided, it will be read from the 'OPENAI_API_VERSION' environment variable.
        """
        super().__init__(api_key=api_key)

        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version or os.getenv("OPENAI_API_VERSION")

        if not self.azure_endpoint:
            raise ValueError(
                "The Azure endpoint URL must be set either by passing 'azure_endpoint' or by setting the 'AZURE_OPENAI_ENDPOINT' environment variable."
            )

        if not self.api_version:
            raise ValueError(
                "The API version must be set either by passing 'api_version' or by setting the 'OPENAI_API_VERSION' environment variable."
            )

        self._client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
        )
        self._aclient = AsyncAzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
        )
