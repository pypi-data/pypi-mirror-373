from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List

from pydantic import Field

from seekrai.types.abstract import BaseModel
from seekrai.types.common import (
    DeltaContent,
    DeltaLogProbs,
    FinishReason,
    LogProbs,
    ObjectType,
    PromptPart,
    UsageData,
)


class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class ResponseFormatType(str, Enum):
    JSON_OBJECT = "json_object"


class FunctionCall(BaseModel):
    name: str | None = None
    arguments: str | None = None


class ToolCalls(BaseModel):
    id: str | None = None
    type: str | None = None
    function: FunctionCall | None = None


class ChatCompletionMessage(BaseModel):
    role: MessageRole
    content: str | None = None
    # tool_calls: List[ToolCalls] | None = None


class ResponseFormat(BaseModel):
    type: ResponseFormatType
    schema_: Dict[str, Any] | None = Field(None, alias="schema")


class FunctionTool(BaseModel):
    description: str | None = None
    name: str
    parameters: Dict[str, Any] | None = None


class FunctionToolChoice(BaseModel):
    name: str


class Tools(BaseModel):
    type: str
    function: FunctionTool


class ToolChoice(BaseModel):
    type: str
    function: FunctionToolChoice


class ToolChoiceEnum(str, Enum):
    Auto = "auto"


class ChatCompletionRequest(BaseModel):
    # list of messages
    messages: List[ChatCompletionMessage]
    # model name
    model: str
    max_completion_tokens: int | None = None
    # stopping criteria: max tokens to generate
    max_tokens: int | None = None
    # stopping criteria: list of strings to stop generation
    stop: List[str] | None = None
    # sampling hyperparameters
    temperature: float = 0.7
    top_p: float = 1
    top_k: int = -1
    repetition_penalty: float = 1
    # stream SSE token chunks
    stream: bool = False
    # return logprobs
    logprobs: bool | None = False
    top_logprobs: int | None = 0
    # echo prompt.
    # can be used with logprobs to return prompt logprobs (is this supported in Seekr API/worker implementation?)
    echo: bool = False
    # number of output generations
    n: int = 1
    # moderation model
    safety_model: str | None = None
    # constraints
    response_format: ResponseFormat | None = None
    # tools: List[Tools] | None = None
    # tool_choice: ToolChoice | ToolChoiceEnum | None = None


class ChatCompletionChoicesData(BaseModel):
    index: int | None = None
    finish_reason: FinishReason | None = None
    message: ChatCompletionMessage | None = None
    logprobs: LogProbs | None = None


class ChatCompletionResponse(BaseModel):
    # request id
    id: str | None = None
    # object type
    object: ObjectType | None = None
    # created timestamp
    created: int | None = None
    # model name
    model: str | None = None
    # choices list
    choices: List[ChatCompletionChoicesData] | None = None
    # prompt list
    prompt: List[PromptPart] | List[None] | None = None
    # token usage data
    usage: UsageData | None = None


class ChatCompletionChoicesChunk(BaseModel):
    index: int | None = None
    finish_reason: FinishReason | None = None
    delta: DeltaContent | None = None
    logprobs: DeltaLogProbs | None = None


class ChatCompletionChunk(BaseModel):
    # request id
    id: str | None = None
    # object type
    object: ObjectType | None = None
    # created timestamp
    created: int | None = None
    # model name
    model: str | None = None
    # delta content
    choices: List[ChatCompletionChoicesChunk] | None = None
    # finish reason
    finish_reason: FinishReason | None = None
    # token usage data
    usage: UsageData | None = None
