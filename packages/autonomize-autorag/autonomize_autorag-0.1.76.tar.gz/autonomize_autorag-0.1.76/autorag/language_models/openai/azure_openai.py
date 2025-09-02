"""Azure OpenAI Language Model module implementation"""

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

from autorag.language_models.openai.base_openai import OpenAILanguageModel


class AzureOpenAILanguageModel(OpenAILanguageModel):
    """
    Azure OpenAI Language Model implementation using the OpenAI client for Azure.

    This class utilizes Azure's OpenAI API to generate chat completions for text data.
    It allows specifying the API key, base URL, and version, either directly or via
    environment variables.

    Example:
    .. code-block:: python

        from autorag.language_models import AzureOpenAILanguageModel

        model_name = "gpt-4o"
        llm = AzureOpenAILanguageModel()

        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        use_managed_identity: bool = False,
        **kwargs
    ):
        """
        Initializes the Azure OpenAI client.

        Args:
            api_key (Optional[str]): Azure OpenAI API key. If not provided, it will be read from the 'OPENAI_API_KEY' environment variable.
            azure_endpoint (Optional[str]): Azure endpoint deployed. If not provided, it will be read from the 'AZURE_OPENAI_ENDPOINT' environment variable.
            api_version (Optional[str]): Azure OpenAI API version. If not provided, it will be read from the 'OPENAI_API_VERSION' environment variable.
            use_managed_identity (bool): If True, uses the managed identity for authentication. Default is False.
        """
        super().__init__(api_key=api_key)

        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version or os.getenv("OPENAI_API_VERSION")
        self.use_managed_identity = use_managed_identity

        if not self.azure_endpoint:
            raise ValueError(
                "The Azure endpoint URL must be set either by passing 'azure_endpoint' or by setting the 'AZURE_OPENAI_ENDPOINT' environment variable."
            )

        if not self.api_version:
            raise ValueError(
                "The API version must be set either by passing 'api_version' or by setting the 'OPENAI_API_VERSION' environment variable."
            )

        http_client = kwargs.pop("http_client", None)
        async_http_client = kwargs.pop("async_http_client", None)

        self._client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
            http_client=http_client,
        )
        self._aclient = AsyncAzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
            http_client=async_http_client,
        )
