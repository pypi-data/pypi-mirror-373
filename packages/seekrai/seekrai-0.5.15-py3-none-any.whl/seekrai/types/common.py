from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import ConfigDict, Field

from seekrai.types.abstract import BaseModel


# Generation finish reason
class FinishReason(str, Enum):
    Length = "length"
    StopSequence = "stop"
    EOS = "eos"
    ToolCalls = "tool_calls"


class UsageData(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ObjectType(str, Enum):
    Completion = "text.completion"
    CompletionChunk = "completion.chunk"
    ChatCompletion = "chat.completion"
    ChatCompletionChunk = "chat.completion.chunk"
    Embedding = "embedding"
    FinetuneEvent = "fine-tune-event"
    File = "file"
    Model = "model"


class LogProbs(BaseModel):  # OpenAI style
    text_offset: List[int] = Field(default_factory=list)
    token_logprobs: List[Optional[float]] = Field(default_factory=list)
    tokens: List[str] = Field(default_factory=list)
    top_logprobs: List[Optional[Dict[str, float]]] = Field(default_factory=list)


class LogprobsPart(BaseModel):
    # token list
    tokens: List[str | None] | None = None
    # token logprob list
    token_logprobs: List[float | None] | None = None


class PromptPart(BaseModel):
    # prompt string
    text: str | None = None
    # list of prompt logprobs
    logprobs: LogprobsPart | None = None


class DeltaContent(BaseModel):
    content: str | None = None


class DeltaLogProbs(BaseModel):
    text_offset: int | None = None
    token_logprob: float | None = None
    token: str | None = None
    top_logprobs: Dict[str, float] | None = None


class SeekrFlowRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str
    url: str
    headers: Dict[str, str] | None = None
    params: Dict[str, Any] | None = None
    files: (
        Dict[str, Any]
        | List[Tuple[str, Tuple[str, Any, Optional[str]]]]
        | List[Tuple[str, Any]]
        | None
    ) = None
    allow_redirects: bool = True
    override_headers: bool = False
