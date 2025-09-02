"""Modelhub Language Model module implementation"""

# pylint: disable=line-too-long, duplicate-code

from typing import Any, Dict, List, Literal, Optional, Union, override

from autonomize.core.credential import ModelhubCredential

from autorag.language_models.base import LanguageModel
from autorag.language_models.ollama import OllamaLanguageModel
from autorag.types.language_models import Generation, ParsedGeneration
from autorag.types.language_models.generation import ResponseFormatT
from autorag.utilities.logger import get_logger

logger = get_logger()


class ModelhubLanguageModel(LanguageModel):
    """
    Implementation of the LanguageModel abstract base class using Modelhub hosted models.

    This class utilizes Modelhubs's deployed language models' API to generate text data.
    It supports different models served using modelhub for text generation tasks like conversation
    and RAG systems.

    Example:
    .. code-block:: python

        from autonomize.core.credential import ModelhubCredential
        from autorag.language_models import ModelhubLanguageModel

        credential = ModelhubCredential()
        provider_name = "ollama"
        llm = ModelhubLanguageModel(credential=credential, provider="ollama")

        model_name = "llama3.1:8b-instruct-q8_0"
        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
        )
    """

    def __init__(
        self,
        credential: ModelhubCredential,
        provider_name: Literal["ollama"] = "ollama",
        **kwargs: Any,
    ):
        """
        Initialize the ModelhubEmbedding instance.

        Args:
            credential ModelhubCredential: The credential object for authorizing with Modelhub.
            provider str: Which community provider to use for the language model.
            **kwargs (Any): Additional optional arguments for further customization.

        Raises:
            ValueError: If neither (client_id and client_secret) nor token is provided.
        """

        self._credential = credential
        self._get_provider(provider_name=provider_name, **kwargs)

    def _get_provider(
        self, provider_name: Literal["ollama"] = "ollama", **kwargs: Any
    ) -> None:
        """
        Given the provider's name this method creates an instance of the provider deployed using modelhub.

        Args:
            provider_name (str): The name of the provider, for example: "ollama".
            **kwargs (Any): Additional optional arguments for further customization.
        """
        if provider_name == "ollama":
            self._provider = OllamaLanguageModel(self._credential, **kwargs)

    def _generate(  # pylint: disable=too-many-locals
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tool: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        temperature: Optional[float] = None,
        num_ctx: Optional[int] = 8096,
        **kwargs: Any,
    ) -> Generation:
        """
        Generates a response based on the provided messages and model settings.

        Args:
            messages (List[Dict[str, Any]]): A list of dictionaries containing the conversation history or prompts.
            model (str): The model identifier to use for text generation.
            tool (Optional[Dict[str, Any]]): A dictionary containing tool definition, if applicable.
            max_tokens (Optional[int]): Maximum number of tokens to generate. Defaults to no limit.
            frequency_penalty (Optional[float]): Penalizes new tokens based on their frequency in the generated text.
            presence_penalty (Optional[float]): Penalizes new tokens based on whether they appear in the generated text.
            seed (Optional[int]): Random seed for reproducibility of results.
            stop (Optional[Union[str, List[str]]]): String or list of strings to end the generation when encountered.
            temperature (Optional[float]): Controls randomness in the generation.
            Higher values (e.g., 1.0) make output more random, lower values (e.g., 0.2) make it more deterministic.
            num_ctx (Optional[int]): Sets the size of the context window used to generate the next token.
            (Default: 8096)
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            Generation: Generated response based on the input messages and model parameters.
        """
        output = self._provider.generate(
            messages,
            model,
            tool,
            max_tokens,
            frequency_penalty,
            presence_penalty,
            seed,
            stop,
            temperature,
            num_ctx=num_ctx,
            **kwargs,
        )

        return output

    @override
    async def agenerate(  # pylint: disable=too-many-locals
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tool: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        temperature: Optional[float] = None,
        num_ctx: Optional[int] = 8096,
        **kwargs: Any,
    ) -> Generation:
        """
        Asynchronously generates a response based on the provided messages and model settings.

        Args:
            messages (List[Dict[str, Any]]): A list of dictionaries containing the conversation history or prompts.
            model (str): The model identifier to use for text generation.
            tool (Optional[Dict[str, Any]]): A dictionary containing tool definition, if applicable.
            max_tokens (Optional[int]): Maximum number of tokens to generate. Defaults to no limit.
            frequency_penalty (Optional[float]): Penalizes new tokens based on their frequency in the generated text.
            presence_penalty (Optional[float]): Penalizes new tokens based on whether they appear in the generated text.
            seed (Optional[int]): Random seed for reproducibility of results.
            stop (Optional[Union[str, List[str]]]): String or list of strings to end the generation when encountered.
            temperature (Optional[float]): Controls randomness in the generation.
            Higher values (e.g., 1.0) make output more random, lower values (e.g., 0.2) make it more deterministic.
            num_ctx (Optional[int]): Sets the size of the context window used to generate the next token.
            (Default: 8096)
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            Generation: Generated response based on the input messages and model parameters.
        """
        output = await self._provider.agenerate(
            messages,
            model,
            tool,
            max_tokens,
            frequency_penalty,
            presence_penalty,
            seed,
            stop,
            temperature,
            num_ctx=num_ctx,
            **kwargs,
        )
        return output

    def _parse(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        response_format: type[ResponseFormatT],
        seed: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ParsedGeneration[ResponseFormatT]:
        """
        Generates a response based on the provided messages and model settings.

        Args:
            messages (List[Dict[str, Any]]): A list of dictionaries containing the conversation history or prompts.
            model (str): The model identifier to use for text generation.
            response_format (type[ResponseFormatT]): An object specifying the format that the model must output.
            seed (Optional[int]): Random seed for reproducibility of results.
            temperature (Optional[float]): Controls randomness in the generation. Higher values (e.g., 1.0) make output more random, lower values (e.g., 0.2) make it more deterministic.
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            ParsedGeneration[ResponseFormatT]: Generated response based on the input messages and model parameters.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_parse'."
        )
