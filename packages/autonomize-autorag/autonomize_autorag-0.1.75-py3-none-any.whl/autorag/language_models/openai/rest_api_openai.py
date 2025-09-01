# pylint: disable=R0801, duplicate-code, R0914, too-many-instance-attributes

"""
HTTPX-based OpenAI Language Model module implementation

This module implements the LanguageModel interface using direct REST
calls to the OpenAI API via httpx. It replicates the functionality of the
SDK‑based modules, supporting both synchronous and asynchronous methods.

"""

from typing import Any, Dict, List, Optional, Type, Union

import httpx

from autorag.language_models.base import LanguageModel
from autorag.types.language_models import (
    Generation,
    Logprobs,
    ParsedGeneration,
    ToolCall,
    Usage,
)
from autorag.types.language_models.generation import ResponseFormatT

# Define a type variable for response_format parameter


class RestApiOpenAILanguageModel(LanguageModel):
    """
    OpenAI Language Model implementation using REST API with httpx.

    This class implements the interface of the SDK-based OpenAILanguageModel
    but uses httpx to make HTTP requests directly to the OpenAI API.
    """

    def __init__(
        self,
        api_version: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_header: dict[str, str] | None = None,
        timeouts: dict[str, float] | None = None,
        verify_ssl: bool = True,
        pass_model_name_in_payload: bool = True,
    ) -> None:
        """
        Initializes the HTTPX OpenAI client.

        Args:
            api_key (Optional[str]): Your OpenAI API key.
            base_url (Optional[str]): The API base URL.
        """
        super().__init__()
        self._api_version = api_version
        if not api_key and not auth_header:
            raise ValueError(
                "The api_key  or Auth Header via  must be provided by parameter"
            )
        self.base_url = base_url

        self._params = {"api-version": api_version}

        if not self.base_url:
            raise ValueError("The base_url must be proviced via parameter")

        default_headers = {"Content-Type": "application/json"}

        headers = {}

        if auth_header:
            headers = {**auth_header, **default_headers}
        elif api_key:
            headers = {"api-key": api_key, **default_headers}

        self._headers = headers

        timeout_dict: dict[str, float] = {}
        if timeouts is not None:
            timeout_dict = timeouts

        self._timeout_obj = httpx.Timeout(
            connect=timeout_dict.get("connect", 60),
            read=timeout_dict.get("read", 600),
            write=timeout_dict.get("write", 60),
            pool=timeout_dict.get("pool", 60),
        )

        self._client = httpx.Client(
            base_url=self.base_url,
            params=self._params,
            headers=headers,
            timeout=self._timeout_obj,
            verify=verify_ssl,
        )

        self._verify_ssl = verify_ssl

        self._pass_model_name_in_payload = pass_model_name_in_payload

    async def _get_async_client(self) -> httpx.AsyncClient:
        """
        Create an Async httpx client
        """
        return httpx.AsyncClient(
            base_url=self.base_url,  # type: ignore
            params=self._params,
            headers=self._headers,
            timeout=self._timeout_obj,
            verify=self._verify_ssl,
        )

    def _build_payload(
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
    ) -> Dict[str, Any]:
        """
        Helper function to build the JSON payload for the API request.
        Only non-None values are included.
        """
        payload: Dict[str, Any] = {"messages": messages}
        if self._pass_model_name_in_payload:
            payload["model"] = model

        if tool is not None:
            payload["tools"] = [tool]
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if seed is not None:
            payload["seed"] = seed
        if stop is not None:
            payload["stop"] = stop
        if temperature is not None:
            payload["temperature"] = temperature
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if top_logprobs is not None:
            payload["top_logprobs"] = top_logprobs

        # Include any additional keyword arguments
        payload.update(kwargs)
        return payload

    def _handle_response(self, data: Dict[str, Any]) -> Generation:
        """
        Converts the JSON response from the API into a Generation object.
        """
        choice = data["choices"][0]
        message = choice["message"]
        usage_data = data.get("usage", {})
        usage = Usage(
            completion_tokens=usage_data.get("completion_tokens"),
            prompt_tokens=usage_data.get("prompt_tokens"),
            total_tokens=usage_data.get("total_tokens"),
        )
        tool_call = None
        if (
            "tool_calls" in message
            and isinstance(message["tool_calls"], list)
            and message["tool_calls"]
        ):
            tc = message["tool_calls"][0]
            # Assume structure: {"function": {"name": ..., "arguments": ...}}
            tool_call = ToolCall(
                name=tc["function"]["name"],
                arguments=tc["function"]["arguments"],
            )
        logprobs_obj = None
        if (
            "logprobs" in choice
            and choice["logprobs"]
            and "content" in choice["logprobs"]
        ):
            content = choice["logprobs"]["content"]
            if content:
                logprobs_obj = [Logprobs(**item) for item in content]

        return Generation(
            content=message.get("content", ""),
            finish_reason=choice.get("finish_reason"),
            role=message.get("role"),
            usage=usage,
            tool_call=tool_call,
            logprobs=logprobs_obj,
        )

    def _handle_parsed_response(
        self, data: Dict[str, Any], response_format: Type[ResponseFormatT]
    ) -> ParsedGeneration:
        """
        Converts the JSON response into a ParsedGeneration object.
        """
        choice = data["choices"][0]
        message = choice["message"]
        usage_data = data.get("usage", {})
        usage = Usage(
            completion_tokens=usage_data.get("completion_tokens"),
            prompt_tokens=usage_data.get("prompt_tokens"),
            total_tokens=usage_data.get("total_tokens"),
        )
        return ParsedGeneration(
            content=message.get("content", ""),
            finish_reason=choice.get("finish_reason"),
            role=message.get("role"),
            usage=usage,
            tool_call=None,
            parsed=response_format.model_validate_json(message.get("content")),
        )

    def _create_response_format_schema(
        self, response_format: Type[ResponseFormatT]
    ) -> Dict[str, Any]:
        """
        Build the `response_format` dict for the OpenAI parse endpoint,
        using the JSON schema of the given Pydantic model.
        """
        # Grab the JSON Schema from the Pydantic model
        schema: Dict[str, Any] = response_format.model_json_schema()
        schema.update({"additionalProperties": False})
        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_format.__name__,
                "strict": True,
                "schema": schema,
            },
        }

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
        Synchronously generates a response using the OpenAI REST API.
        """
        payload = self._build_payload(
            messages=messages,
            model=model,
            tool=tool,
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
        url = "/chat/completions"
        response = self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return self._handle_response(data)

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
        Asynchronously generates a response using the OpenAI REST API.
        """
        payload = self._build_payload(
            messages=messages,
            model=model,
            tool=tool,
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
        url = "/chat/completions"
        async with await self._get_async_client() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return self._handle_response(data)

    def _parse(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        response_format: Type[ResponseFormatT],
        seed: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ParsedGeneration[ResponseFormatT]:
        """
        Synchronously generates a parsed response using the beta parse endpoint.
        The desired response format is passed as the name of the response_format class.
        """

        payload = self._build_payload(
            messages=messages,
            model=model,
            seed=seed,
            temperature=temperature,
            **kwargs,
        )

        response_format_schema = self._create_response_format_schema(
            response_format=response_format
        )

        payload.update({"response_format": response_format_schema})

        url = "/chat/completions"
        response = self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return self._handle_parsed_response(data, response_format)

    async def aparse(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        response_format: Type[ResponseFormatT],
        seed: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ParsedGeneration[ResponseFormatT]:
        """
        Asynchronously generates a parsed response using the beta parse endpoint.
        """
        payload = self._build_payload(
            messages=messages,
            model=model,
            seed=seed,
            temperature=temperature,
            **kwargs,
        )
        url = "/chat/completions"

        response_format_schema = self._create_response_format_schema(
            response_format=response_format
        )

        payload.update({"response_format": response_format_schema})

        async with await self._get_async_client() as client:
            resp = await client.post(
                url,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return self._handle_parsed_response(data, response_format)
