"""Anthropic Language Model module implementation"""

# pylint: disable=line-too-long, duplicate-code, logging-fstring-interpolation

import os
from typing import Any, Dict, List, Optional, Union, override

try:
    from anthropic import Anthropic, AsyncAnthropic
    from anthropic._types import NOT_GIVEN
    from anthropic.types.message import Message
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate anthropic package. "
        'Please install it with `pip install "autonomize-autorag[anthropic]"`.'
    ) from err

from autorag.language_models.base import LanguageModel
from autorag.types.language_models import Generation, ParsedGeneration, ToolCall, Usage
from autorag.types.language_models.generation import ResponseFormatT
from autorag.utilities.logger import get_logger

logger = get_logger()


class AnthropicLanguageModel(LanguageModel):
    """
    Implementation of the LanguageModel abstract base class using Anthropic's API.

    This class utilizes Anthropic's API to generate text data. It supports different models
    provided by Anthropic for text generation tasks like conversation and RAG systems.

    Example:
    .. code-block:: python

        from autorag.language_models import AnthropicLanguageModel

        model_name = "claude-3-7-sonnet-latest"
        llm = AnthropicLanguageModel()

        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
        )
    """

    DEFAULT_MAX_TOKENS = 1024
    UNSUPPORTED_PARAMETERS = {"frequency_penalty", "presence_penalty", "seed"}
    FINISH_REASONS = {
        "end_turn": "stop",
        "max_tokens": "length",
        "stop_sequence": "stop",
        "tool_use": "tool_calls",
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the Anthropic language model client.

        Args:
            api_key (Optional[str]): Anthropic API key. If not provided, the key is read from the environment variable 'ANTHROPIC_API_KEY'.

        Raises:
            ValueError: If the API key is not provided and cannot be found in the environment.
        """
        super().__init__()

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "The api_key client option must be set either by passing api_key to the client or by setting the ANTHROPIC_API_KEY environment variable."
            )

        self._client = Anthropic(
            api_key=self.api_key,
        )
        self._aclient = AsyncAnthropic(
            api_key=self.api_key,
        )

    def _generate(
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
            temperature (Optional[float]): Controls randomness in the generation. Higher values (e.g., 1.0) make output more random, lower values (e.g., 0.2) make it more deterministic.
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            Generation: Generated response based on the input messages and model parameters.
        """

        if not max_tokens:
            logger.warning(
                f"`max_tokens` is not provided. Setting the value of `max_tokens` is set to {self.DEFAULT_MAX_TOKENS}."
            )
        max_tokens = max_tokens if max_tokens else self.DEFAULT_MAX_TOKENS

        # Anthropic API does not send system messages as a part of `messages` parameter
        # Instead, it is sent using another parameter `system`.
        # So, we need to separate the system message from the messages list.
        system_message = None
        if messages[0]["role"] == "system":
            system_message = messages.pop(0)

        # Check for unsupported parameters
        self._warn_unsupported_params(
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
        )

        response: Message = self._client.messages.create(  # type: ignore[call-overload]
            messages=messages,
            model=model,
            system=system_message["content"] if system_message else NOT_GIVEN,
            tools=[tool] if tool else NOT_GIVEN,
            max_tokens=max_tokens,
            stop_sequences=stop if stop else NOT_GIVEN,
            temperature=temperature if temperature else NOT_GIVEN,
            **kwargs,
        )

        tool_use = next(
            (item for item in response.content if item.type == "tool_use"), None
        )

        output = Generation(
            content=next(
                (item.text for item in response.content if item.type == "text"), None
            ),
            finish_reason=(
                self.FINISH_REASONS[response.stop_reason]  # type: ignore[arg-type]
                if response.stop_reason
                else None
            ),
            role=response.role,
            # To calculate usage for prompt and response
            usage=self._calculate_usage(response),
            # If tool is used, then return its name and arguments, otherwise None
            tool_call=(
                ToolCall(
                    name=tool_use.name,
                    arguments=str(tool_use.input),
                )
                if tool_use
                else None
            ),
        )
        return output

    @override
    async def agenerate(
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
            temperature (Optional[float]): Controls randomness in the generation. Higher values (e.g., 1.0) make output more random, lower values (e.g., 0.2) make it more deterministic.
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            Generation: Generated response based on the input messages and model parameters.
        """

        if not max_tokens:
            logger.warning(
                f"`max_tokens` is not provided. Setting the value of `max_tokens` is set to {self.DEFAULT_MAX_TOKENS}."
            )
        max_tokens = max_tokens if max_tokens else self.DEFAULT_MAX_TOKENS

        # Anthropic API does not send system messages as a part of `messages` parameter
        # Instead, it is sent using another parameter `system`.
        # So, we need to separate the system message from the messages list.
        system_message = None
        if messages[0]["role"] == "system":
            system_message = messages.pop(0)

        # Check for unsupported parameters
        self._warn_unsupported_params(
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
        )

        response: Message = await self._aclient.messages.create(  # type: ignore[call-overload]
            messages=messages,
            model=model,
            system=system_message["content"] if system_message else NOT_GIVEN,
            tools=[tool] if tool else NOT_GIVEN,
            max_tokens=max_tokens,
            stop_sequences=stop if stop else NOT_GIVEN,
            temperature=temperature if temperature else NOT_GIVEN,
            **kwargs,
        )

        tool_use = next(
            (item for item in response.content if item.type == "tool_use"), None
        )

        output = Generation(
            content=next(
                (item.text for item in response.content if item.type == "text"), None
            ),
            finish_reason=(
                self.FINISH_REASONS[response.stop_reason]  # type: ignore[arg-type]
                if response.stop_reason
                else None
            ),
            role=response.role,
            # To calculate usage for prompt and response
            usage=self._calculate_usage(response),
            # If tool is used, then return its name and arguments, otherwise None
            tool_call=(
                ToolCall(
                    name=tool_use.name,
                    arguments=str(tool_use.input),
                )
                if tool_use
                else None
            ),
        )
        return output

    @staticmethod
    def _warn_unsupported_params(**params):
        """
        Logs warnings for any Anthropic API unsupported parameters.

        Args:
            params: Dictionary of parameters to check for support.
        """
        for param, value in params.items():
            if (
                value is not None
                and param in AnthropicLanguageModel.UNSUPPORTED_PARAMETERS
            ):
                logger.warning(
                    "Anthropic API does not support '%s'; It will be ignored.", param
                )

    def _calculate_usage(self, response: Message) -> Usage:
        """
        Calculates token usage from the Anthropic API response.

        Args:
            response (Message): Anthropic API response.

        Returns:
            Usage: Calculated usage metrics.
        """

        return Usage(
            completion_tokens=(
                response.usage.output_tokens
                if response.usage and response.usage.output_tokens is not None
                else None
            ),
            prompt_tokens=(
                response.usage.input_tokens
                if response.usage and response.usage.output_tokens is not None
                else None
            ),
            total_tokens=(
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage
                and response.usage.input_tokens is not None
                and response.usage.output_tokens is not None
                else None
            ),
        )

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
