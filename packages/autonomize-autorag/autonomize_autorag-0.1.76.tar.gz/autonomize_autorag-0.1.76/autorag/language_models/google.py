"""Google Language Model module implementation"""

# pylint: disable=too-many-locals, line-too-long, too-many-instance-attributes, duplicate-code

import base64
import mimetypes
import os
import re
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union, override

try:
    from google.genai import Client  # type: ignore[import-untyped]
    from google.genai.types import (  # type: ignore[import-untyped]
        Content,
        FinishReason,
        FunctionCallingConfig,
        FunctionCallingConfigMode,
        GenerateContentConfigDict,
        GenerateContentResponse,
        ModelContent,
        Part,
        Tool,
        ToolConfig,
        UserContent,
    )
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate google-genai package. "
        'Please install it with `pip install "autonomize-autorag[google-genai]"`.'
    ) from err

import httpx

from autorag.language_models import LanguageModel
from autorag.types.language_models import Generation, ParsedGeneration, ToolCall, Usage
from autorag.types.language_models.generation import ResponseFormatT

FINISH_REASON_MAP = {
    FinishReason.STOP: "stop",
    FinishReason.MAX_TOKENS: "length",
    FinishReason.SAFETY: "content_filter",
    FinishReason.BLOCKLIST: "content_filter",
    FinishReason.PROHIBITED_CONTENT: "content_filter",
    FinishReason.SPII: "content_filter",
    FinishReason.IMAGE_SAFETY: "content_filter",
    FinishReason.MALFORMED_FUNCTION_CALL: "function_call",
    FinishReason.RECITATION: "content_filter",
    FinishReason.OTHER: "content_filter",
    FinishReason.FINISH_REASON_UNSPECIFIED: "stop",
}

DATA_URL_RE = re.compile(r"data:(?P<mime>[^;]+);base64,(?P<b64>.+)", re.I)


class GoogleLanguageModel(LanguageModel):
    """
    Google language model integration for handling LLM prompts using Google SDK.

    Provides synchronous and asynchronous content generation, system/user message processing,
    and function/tool invocation handling.

    Example:
    .. code-block:: python

        from autorag.language_models import GoogleLanguageModel

        model_name = "gemini-2.0-flash"
        llm = GoogleLanguageModel()

        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
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
        Initializes the Google language model client.

        Args:
            api_key (Optional[str]): API key for gemini access if not using ADC. Defaults to None.
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
            warnings.warn("The `api_key` argument is ignored when using Vertex AI.")

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

    @staticmethod
    def _part_from_base64(base64_url: str) -> Part:
        """
        Convert a data-URL (`data:image/jpeg;base64,...`) to Part.

        Args:
            base64_url: Base64 url of the image.

        Returns:
            Part: Byte part from the base64 url.

        Raises:
            ValueError: If base64_url is malformed.
        """
        m = DATA_URL_RE.fullmatch(base64_url)
        if not m:
            raise ValueError("Malformed data: Base64 URL")
        mime = m.group("mime")
        raw = base64.b64decode(m.group("b64"))
        return Part.from_bytes(data=raw, mime_type=mime)

    @staticmethod
    def _part_from_url(url: str) -> Part:
        """
        Download the image and wrap the bytes in Part.from_bytes.

        Args:
            url: URL of the image.

        Returns:
            Part: Byte part from the url.
        """
        r = httpx.get(url, timeout=None)
        r.raise_for_status()
        mime = (
            r.headers.get("content-type")
            or mimetypes.guess_type(url)[0]
            or "application/octet-stream"
        )
        return Part.from_bytes(data=r.content, mime_type=mime)

    def _create_contents(
        self, messages: List[Dict[str, Any]]
    ) -> Tuple[List[Content], Optional[Content]]:
        """
        Creates the conversation history compatible with Google SDK.

        Args:
            messages (List[Dict[str, Any]]): A list of dictionaries containing the conversation history or prompts.

        Returns:
            Tuple[List[Content], Optional[Content]]: Conversation history and system prompt.
        """
        contents = []
        system_instruction = None
        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    user_content = UserContent(
                        parts=[Part.from_text(text=message["content"])]
                    )
                elif isinstance(message["content"], list):
                    parts = []
                    for cnt in message["content"]:
                        if cnt["type"] == "text":
                            parts.append(Part.from_text(text=cnt["text"]))
                        elif cnt["type"] == "image_url":
                            image_url: str = cnt["image_url"]["url"]
                            part = (
                                self._part_from_base64(image_url)
                                if image_url.startswith("data:")
                                else self._part_from_url(image_url)
                            )
                            parts.append(part)
                    user_content = UserContent(parts=parts)
                else:
                    raise ValueError("Malformed data.")
                contents.append(user_content)
            elif message["role"] == "assistant":
                model_content = ModelContent(
                    parts=[Part.from_text(text=message["content"])]
                )
                contents.append(model_content)
            elif message["role"] == "system":
                system_instruction = Content(
                    role="system", parts=[Part.from_text(text=message["content"])]
                )

        return contents, system_instruction

    def _convert_to_function_declaration(self, tool: Dict[str, Any]) -> List[Tool]:
        """
        Converts the tool dictionary to Function Declaration format required by the Google SDK.

        Args:
            tool (Dict[str, Any]): A dictionary containing information about the tool.

        Returns:
            List[Tool]: A list of Tool objects containing the function declaration.
        """
        tools: List[Tool] = []
        function: Dict = tool.get("function")  # type: ignore
        if function:
            # Create a Tool object with a single function declaration
            tools = [Tool(function_declarations=[function])]
        return tools

    def _build_tool_config(
        self, tools: Optional[List[Tool]], tool_choice: str
    ) -> Optional[ToolConfig]:
        """
        Create ToolConfig with appropriate function calling mode.

        Args:
            tools: List of Tool objects.
            tool_choice: Tool invocation mode or tool name.

        Returns:
            ToolConfig or None.
        """
        if not tools:
            return None

        if isinstance(tool_choice, dict):
            raise ValueError("Dict tool_choice is not supported.")

        mode = {
            "auto": FunctionCallingConfigMode.AUTO,
            "none": FunctionCallingConfigMode.NONE,
        }.get(tool_choice, FunctionCallingConfigMode.ANY)

        config = FunctionCallingConfig(mode=mode)

        if tool_choice not in ["auto", "none"]:
            tool_names = [tool.function_declarations[0].name for tool in tools]
            config.allowed_function_names = (
                [tool_choice] if tool_choice in tool_names else tool_names
            )

        return ToolConfig(function_calling_config=config)

    def _parse_response(self, response: GenerateContentResponse) -> Generation:
        """
        Convert SDK response to internal Generation format.

        Args:
            response: Raw response object from SDK.

        Returns:
            A `Generation` instance with structured output.
        """
        candidate = response.candidates[0]
        part = candidate.content.parts[0] if candidate.content.parts else None

        tool_call = (
            ToolCall(
                name=part.function_call.name, arguments=str(part.function_call.args)
            )
            if part and part.function_call
            else None
        )

        return Generation(
            content=response.text,
            finish_reason=FINISH_REASON_MAP.get(candidate.finish_reason.value, "stop"),  # type: ignore[arg-type]
            role=(
                "assistant"
                if candidate.content.role == "model"
                else candidate.content.role
            ),
            usage=Usage(
                completion_tokens=getattr(
                    response.usage_metadata, "candidates_token_count", None
                ),
                prompt_tokens=getattr(
                    response.usage_metadata, "prompt_token_count", None
                ),
                total_tokens=getattr(
                    response.usage_metadata, "total_token_count", None
                ),
            ),
            tool_call=tool_call,
            logprobs=None,
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
    ):
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

        Raises:
            ValueError: If the tool_choice is equal to `dict` which is not supported by Gemini.

        """

        contents, system_instruction = self._create_contents(messages=messages)
        tools = self._convert_to_function_declaration(tool=tool) if tool else None  # type: ignore[arg-type]
        tool_config = self._build_tool_config(
            tools=tools, tool_choice=kwargs.get("tool_choice", "auto")
        )

        config = GenerateContentConfigDict(
            system_instruction=system_instruction,
            frequency_penalty=frequency_penalty,
            max_output_tokens=max_tokens,
            presence_penalty=presence_penalty,
            seed=seed,
            stop_sequences=stop,
            temperature=temperature,
            tools=tools,
            tool_config=tool_config,
            **kwargs,
        )

        response = self._client.models.generate_content(
            model=model, contents=contents, config=config
        )
        return self._parse_response(response)

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
    ):
        """
        Asynchronously Generates a response based on the provided messages and model settings.

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

        Raises:
            ValueError: If the tool_choice is equal to `dict` which is not supported by Gemini.
            ValueError: tool calling is only supported by vertex ai.

        """

        contents, system_instruction = self._create_contents(messages=messages)
        tools = self._convert_to_function_declaration(tool=tool) if tool else None  # type: ignore[arg-type]
        tool_config = self._build_tool_config(
            tools=tools, tool_choice=kwargs.get("tool_choice", "auto")
        )

        config = GenerateContentConfigDict(
            frequency_penalty=frequency_penalty,
            max_output_tokens=max_tokens,
            presence_penalty=presence_penalty,
            seed=seed,
            stop_sequences=stop,
            temperature=temperature,
            system_instruction=system_instruction,
            tools=tools,
            tool_config=tool_config,
            **kwargs,
        )

        response = await self._client.aio.models.generate_content(
            model=model, contents=contents, config=config
        )
        return self._parse_response(response)

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
        contents, system_instruction = self._create_contents(messages=messages)

        config = GenerateContentConfigDict(
            system_instruction=system_instruction,
            temperature=temperature,
            seed=seed,
            response_mime_type="application/json",
            response_schema=response_format,
            **kwargs,
        )

        response = self._client.models.generate_content(
            model=model, contents=contents, config=config
        )

        candidate = response.candidates[0]

        output: ParsedGeneration[ResponseFormatT] = ParsedGeneration(
            content=response.text,
            finish_reason=FINISH_REASON_MAP.get(candidate.finish_reason.value, "stop"),  # type: ignore[arg-type]
            role=(
                "assistant"
                if candidate.content.role == "model"
                else candidate.content.role
            ),
            # To calculate usage for prompt and response
            usage=Usage(
                completion_tokens=getattr(
                    response.usage_metadata, "candidates_token_count", None
                ),
                prompt_tokens=getattr(
                    response.usage_metadata, "prompt_token_count", None
                ),
                total_tokens=getattr(
                    response.usage_metadata, "total_token_count", None
                ),
            ),
            tool_call=None,
            parsed=response.parsed,
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
        contents, system_instruction = self._create_contents(messages=messages)

        config = GenerateContentConfigDict(
            system_instruction=system_instruction,
            temperature=temperature,
            seed=seed,
            response_mime_type="application/json",
            response_schema=response_format,
            **kwargs,
        )

        response = await self._client.aio.models.generate_content(
            model=model, contents=contents, config=config
        )

        candidate = response.candidates[0]

        output: ParsedGeneration[ResponseFormatT] = ParsedGeneration(
            content=response.text,
            finish_reason=FINISH_REASON_MAP.get(candidate.finish_reason.value, "stop"),  # type: ignore[arg-type]
            role=(
                "assistant"
                if candidate.content.role == "model"
                else candidate.content.role
            ),
            # To calculate usage for prompt and response
            usage=Usage(
                completion_tokens=getattr(
                    response.usage_metadata, "candidates_token_count", None
                ),
                prompt_tokens=getattr(
                    response.usage_metadata, "prompt_token_count", None
                ),
                total_tokens=getattr(
                    response.usage_metadata, "total_token_count", None
                ),
            ),
            tool_call=None,
            parsed=response.parsed,
        )
        return output
