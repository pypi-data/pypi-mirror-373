"""Ollama Language Model module implementation"""

# pylint: disable=line-too-long, duplicate-code, invalid-name

import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union, override

import httpx
from autonomize.core.credential import ModelhubCredential

from autorag.language_models.base import LanguageModel
from autorag.types.language_models import Generation, ParsedGeneration, ToolCall, Usage
from autorag.types.language_models.generation import ResponseFormatT
from autorag.utilities.logger import get_logger

logger = get_logger()


class OllamaLanguageModel(LanguageModel):
    """
    Implementation of the LanguageModel abstract base class using Ollama's API.

    This class utilizes Ollama's deployed instance API to generate text data. It supports different models
    provided by Ollama for text generation tasks like conversation and RAG systems.

    Example:
    .. code-block:: python

        from autonomize.core.credential import ModelhubCredential
        from autorag.language_models import OllamaLanguageModel

        credential = ModelhubCredential()
        llm = OllamaLanguageModel(credential=credential)

        model_name = "llama3.1:8b-instruct-q8_0"
        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
        )
    """

    MODEL_URL = "https://ollama.modelhub.sprint.autonomize.dev/api/chat"

    def __init__(
        self,
        credential: ModelhubCredential,
        model_url: Optional[str] = None,
    ):
        """
        Initialize the ModelhubEmbedding instance.

        Args:
            credential ModelhubCredential: The credential object for authorizing with Modelhub.
            model_url (Optional[str]): The Modelhub URL for the language model. Defaults to None.

        Raises:
            ValueError: If neither (client_id and client_secret) nor token is provided.
        """

        # Use the provided modelhub URL if available.
        if model_url is not None:
            self.MODEL_URL = model_url

        self._credential = credential

    def _prepare_payload(
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
    ) -> Dict[str, Any]:
        """
        Creates the payload for Ollama modelhub API request.

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
            Dict[str, Any]: Payload for Ollama API request.
        """

        if frequency_penalty:
            logger.warning(
                "`frequency_penalty` argument is not supported by Ollama, and will be ignored."
            )

        if presence_penalty:
            logger.warning(
                "`presence_penalty` argument is not supported by Ollama, and will be ignored."
            )

        payload: dict = defaultdict(dict)

        payload["model"] = model
        payload["messages"] = messages
        payload["stream"] = False
        payload["options"]["num_ctx"] = num_ctx
        payload["keep_alive"] = (
            -1
        )  # -1 means that model is always in the memory and doesn't unload itself.

        # Conditionally add the optional parameters if they are not None
        if tool is not None:
            payload["tools"] = [tool]
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        if seed is not None:
            payload["options"]["seed"] = seed
        if stop is not None:
            if isinstance(stop, str):
                stop = [stop]
            payload["options"]["stop"] = stop
        if temperature is not None:
            payload["options"]["temperature"] = temperature

        # Include any additional arguments passed through kwargs
        payload.update(kwargs)

        return dict(payload)

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
        token = self._credential.get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = self._prepare_payload(
            messages=messages,
            model=model,
            tool=tool,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            temperature=temperature,
            num_ctx=num_ctx,
            **kwargs,
        )

        # timeout=None is to disable request getting timedout, i.e., infinite timeout limit.
        if temperature == 0:
            with httpx.Client(verify=False, timeout=None) as client:
                # Calling the endpoint twice is intentional. The second call results in deterministic response.
                # Do NOT remove the second call.
                client.post(self.MODEL_URL, headers=headers, json=payload)
                response = client.post(self.MODEL_URL, headers=headers, json=payload)
        else:
            with httpx.Client(verify=False, timeout=None) as client:
                response = client.post(self.MODEL_URL, json=payload)

        response.raise_for_status()
        response_json = response.json()

        output = Generation(
            content=(
                response_json["message"]["content"]
                if response_json["message"]["content"]
                else None
            ),
            finish_reason=response_json["done_reason"],
            role=response_json["message"]["role"],
            # To calculate usage for prompt and response
            usage=Usage(
                completion_tokens=(
                    response_json["eval_count"]
                    if "eval_count" in response_json
                    else None
                ),
                prompt_tokens=(
                    response_json["prompt_eval_count"]
                    if "prompt_eval_count" in response_json
                    else None
                ),
                total_tokens=None,  # Ollama doesn't return total counts
            ),
            # If tool is used, then return its name and arguments, otherwise None
            tool_call=(
                ToolCall(
                    name=response_json["message"]["tool_calls"][0]["function"]["name"],
                    arguments=json.dumps(
                        response_json["message"]["tool_calls"][0]["function"][
                            "arguments"
                        ]
                    ),
                )
                if "tool_calls" in response_json["message"]
                else None
            ),
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
        token = await self._credential.aget_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = self._prepare_payload(
            messages=messages,
            model=model,
            tool=tool,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            temperature=temperature,
            num_ctx=num_ctx,
            **kwargs,
        )

        # timeout=None is to disable request getting timedout, i.e., infinite timeout limit.
        if temperature == 0:
            async with httpx.AsyncClient(verify=False, timeout=None) as client:
                # Calling the endpoint twice is intentional. The second call results in deterministic response.
                # Do NOT remove the second call.
                await client.post(self.MODEL_URL, headers=headers, json=payload)
                response = await client.post(
                    self.MODEL_URL, headers=headers, json=payload
                )
        else:
            async with httpx.AsyncClient(verify=False, timeout=None) as client:
                response = await client.post(
                    self.MODEL_URL, headers=headers, json=payload
                )

        response.raise_for_status()
        response_json = response.json()

        output = Generation(
            content=(
                response_json["message"]["content"]
                if response_json["message"]["content"]
                else None
            ),
            finish_reason=response_json["done_reason"],
            role=response_json["message"]["role"],
            # To calculate usage for prompt and response
            usage=Usage(
                completion_tokens=(
                    response_json["eval_count"]
                    if "eval_count" in response_json
                    else None
                ),
                prompt_tokens=(
                    response_json["prompt_eval_count"]
                    if "prompt_eval_count" in response_json
                    else None
                ),
                total_tokens=None,  # Ollama doesn't return total counts
            ),
            # If tool is used, then return its name and arguments, otherwise None
            tool_call=(
                ToolCall(
                    name=response_json["message"]["tool_calls"][0]["function"]["name"],
                    arguments=json.dumps(
                        response_json["message"]["tool_calls"][0]["function"][
                            "arguments"
                        ]
                    ),
                )
                if "tool_calls" in response_json["message"]
                else None
            ),
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
            Generation: Generated response based on the input messages and model parameters.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_parse'."
        )
