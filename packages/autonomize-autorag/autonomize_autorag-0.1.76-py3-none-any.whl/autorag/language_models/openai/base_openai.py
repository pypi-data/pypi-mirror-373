"""OpenAI Language Model module implementation"""

# pylint: disable=line-too-long, duplicate-code, too-many-locals

import os
from typing import Any, Dict, List, Optional, Union, override

try:
    from openai import AsyncOpenAI, OpenAI
    from openai._types import NOT_GIVEN
    from openai.types.chat.chat_completion import ChatCompletion
    from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate openai package. "
        'Please install it with `pip install "autonomize-autorag[openai]"`.'
    ) from err

from autorag.language_models.base import LanguageModel
from autorag.types.language_models import (
    Generation,
    Logprobs,
    ParsedGeneration,
    ToolCall,
    Usage,
)
from autorag.types.language_models.generation import ResponseFormatT


class OpenAILanguageModel(LanguageModel):
    """
    Implementation of the LanguageModel abstract base class using OpenAI's API.

    This class utilizes OpenAI's API to generate text data. It supports different models
    provided by OpenAI for text generation tasks like conversation and RAG systems.

    Example:
    .. code-block:: python

        from autorag.language_models import OpenAILanguageModel

        model_name = "gpt-4o"
        llm = OpenAILanguageModel()

        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
        )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the OpenAI language model client.

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

    def get_usage(self, response: Union[ChatCompletion, ParsedChatCompletion]) -> Usage:
        """
        Extracts the usage information from the response.

        Args:
            response (Union[ChatCompletion, ParsedChatCompletion]): The response object from the chat completion.

        Returns:
            Usage: An object containing the usage information.
        """
        return Usage(
            completion_tokens=(
                response.usage.completion_tokens
                if response.usage and response.usage.completion_tokens is not None
                else None
            ),
            prompt_tokens=(
                response.usage.prompt_tokens
                if response.usage and response.usage.prompt_tokens is not None
                else None
            ),
            total_tokens=(
                response.usage.total_tokens
                if response.usage and response.usage.total_tokens is not None
                else None
            ),
        )

    def convert_to_generation(self, response: ChatCompletion) -> Generation:
        """
        Converts the OpenAI ChatCompletion response to a Generation object.

        Args:
            response (ChatCompletion): The response object from the chat completion.

        Returns:
            Generation: An object containing the generated content and metadata.
        """
        usage = self.get_usage(response)
        return Generation(
            content=response.choices[0].message.content,
            finish_reason=response.choices[0].finish_reason,
            role=response.choices[0].message.role,
            usage=usage,
            # If tool is used, then return its name and arguments, otherwise None
            tool_call=(
                ToolCall(
                    name=response.choices[0].message.tool_calls[0].function.name,
                    arguments=response.choices[0]
                    .message.tool_calls[0]
                    .function.arguments,
                )
                if response.choices[0].message.tool_calls
                and len(response.choices[0].message.tool_calls) > 0
                else None
            ),
            logprobs=(
                [
                    Logprobs(**item.model_dump())
                    for item in response.choices[0].logprobs.content
                ]
                if response.choices[0].logprobs
                and response.choices[0].logprobs.content
                and len(response.choices[0].logprobs.content) > 0
                else None
            ),
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
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
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
            logprobs (Optional[bool]): Include log probabilities for each token.
            top_logprobs (Optional[int]): Include log probabilities for the top n tokens.
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            Generation: Generated response based on the input messages and model parameters.
        """

        # Base args that are always required
        payload: dict[str, Any] = {
            "messages": messages,
            "model": model,
        }

        # Optional, but needs light massaging
        if tool is not None:  # the SDK wants a *list* here
            payload["tools"] = [tool]

        # All the plain scalars that can be dropped if None
        optionals = dict(  # pylint: disable=use-dict-literal
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            temperature=temperature,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
            **kwargs,
        )

        # Keep only entries whose value is *not* None
        payload.update({k: v for k, v in optionals.items() if v is not None})

        response: ChatCompletion = self._client.chat.completions.create(**payload)
        output = self.convert_to_generation(response)
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
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
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
            logprobs (Optional[bool]): Include log probabilities for each token.
            top_logprobs (Optional[int]): Include log probabilities for the top n tokens.
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            Generation: Generated response based on the input messages and model parameters.
        """

        # Base args that are always required
        payload: dict[str, Any] = {
            "messages": messages,
            "model": model,
        }

        # Optional, but needs light massaging
        if tool is not None:  # the SDK wants a *list* here
            payload["tools"] = [tool]

        # All the plain scalars that can be dropped if None
        optionals = dict(  # pylint: disable=use-dict-literal
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            temperature=temperature,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
            **kwargs,
        )

        # Keep only entries whose value is *not* None
        payload.update({k: v for k, v in optionals.items() if v is not None})

        response: ChatCompletion = await self._aclient.chat.completions.create(
            **payload
        )
        output = self.convert_to_generation(response)
        return output

    def convert_to_parsed_generation(
        self, response: ParsedChatCompletion[ResponseFormatT]
    ) -> ParsedGeneration[ResponseFormatT]:
        """
        Converts the OpenAI ParsedChatCompletion response to a ParsedGeneration object.

        Args:
            response (ParsedChatCompletion[ResponseFormatT]): The response object from the parsed chat completion.

        Returns:
            ParsedGeneration[ResponseFormatT]: An object containing the generated content and metadata.
        """
        usage = self.get_usage(response)
        return ParsedGeneration(
            content=response.choices[0].message.content,
            finish_reason=response.choices[0].finish_reason,
            role=response.choices[0].message.role,
            usage=usage,
            tool_call=None,  # Tool calls are not supported in parsed responses
            parsed=response.choices[0].message.parsed,
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
        """
        response: ParsedChatCompletion[ResponseFormatT] = self._client.beta.chat.completions.parse(  # type: ignore[call-overload]
            messages=messages,  # type: ignore[arg-type]
            model=model,
            response_format=response_format,
            seed=seed if seed else NOT_GIVEN,
            temperature=temperature if temperature else NOT_GIVEN,
            **kwargs,
        )
        output: ParsedGeneration[ResponseFormatT] = self.convert_to_parsed_generation(
            response
        )
        return output

    @override
    async def aparse(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        response_format: type[ResponseFormatT],
        seed: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ParsedGeneration[ResponseFormatT]:
        """
        Asynchronously generates a response based on the provided messages and model settings.

        Args:
            messages (List[Dict[str, Any]]): A list of dictionaries containing the conversation history or prompts.
            model (str): The model identifier to use for text generation.
            response_format (type[ResponseFormatT]): An object specifying the format that the model must output.
            seed (Optional[int]): Random seed for reproducibility of results.
            temperature (Optional[float]): Controls randomness in the generation. Higher values (e.g., 1.0) make output more random, lower values (e.g., 0.2) make it more deterministic.
            **kwargs (Any): Additional optional arguments for further customization.

        Returns:
            ParsedGeneration[ResponseFormatT]: Generated response based on the input messages and model parameters.
        """
        response: ParsedChatCompletion[ResponseFormatT] = await self._aclient.beta.chat.completions.parse(  # type: ignore[call-overload]
            messages=messages,  # type: ignore[arg-type]
            model=model,
            response_format=response_format,
            seed=seed if seed else NOT_GIVEN,
            temperature=temperature if temperature else NOT_GIVEN,
            **kwargs,
        )
        output: ParsedGeneration[ResponseFormatT] = self.convert_to_parsed_generation(
            response
        )
        return output
