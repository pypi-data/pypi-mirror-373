# pylint: disable=missing-class-docstring, missing-module-docstring

from typing import Generic, List, Literal, Optional

from pydantic import BaseModel
from typing_extensions import TypeVar

ResponseFormatT = TypeVar("ResponseFormatT", bound=BaseModel)


class ToolCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


class Usage(BaseModel):
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class Logprob(BaseModel):
    token: Optional[str] = None
    bytes: Optional[List[int]] = None
    logprob: Optional[float] = None


class Logprobs(Logprob):
    top_logprobs: Optional[List[Logprob]] = None


class Generation(BaseModel):
    content: Optional[str] = None
    finish_reason: Optional[
        Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
    ] = None
    role: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    usage: Optional[Usage] = None
    logprobs: Optional[List[Logprobs]] = None


class ParsedGeneration(Generation, Generic[ResponseFormatT]):
    parsed: Optional[ResponseFormatT] = None
