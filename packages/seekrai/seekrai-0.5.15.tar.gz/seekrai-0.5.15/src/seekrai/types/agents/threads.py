import datetime
from enum import Enum
from typing import Any, Literal, Optional, Sequence, Union
from uuid import uuid4

from pydantic import Field

from seekrai.types.abstract import BaseModel


class ThreadCreateRequest(BaseModel):
    """Pydantic model for creating a thread request.

    Attributes:
        meta_data (Optional[dict[str, Any]]): Optional metadata dictionary.
    """

    meta_data: Optional[dict[str, Any]] = None


class MessageUpdateRequest(BaseModel):
    """Pydantic model for updating a message request.

    Attributes:
        content (Optional[str]): Optional content of the message.
        meta_data (Optional[dict[str, Any]]): Optional metadata dictionary.
    """

    content: Optional[str] = None
    meta_data: Optional[dict[str, Any]] = None


class ThreadStatus(str, Enum):
    """Available status for a thread."""

    AVAILABLE = "available"
    LOCKED = "locked"


class Thread(BaseModel):
    """A thread is a top-level conversation container.

    Threads can contain multiple messages from various assistants and users,
    providing a complete history of an interaction sequence.
    """

    id: str
    object: str = "thread"
    created_at: datetime.datetime
    status: ThreadStatus = ThreadStatus.AVAILABLE
    active_run_id: Optional[str] = None
    meta_data: dict[str, Any] = Field(default_factory=dict)


class StreamReasoningChunk(BaseModel):
    """A chunk of reasoning output from a streaming tool."""

    type: Literal["stream_reasoning"]
    reasoning: str
    meta_data: dict[str, Any]


class StreamTextChunk(BaseModel):
    """A chunk of text output from a streaming tool."""

    text: str
    type: Literal["streaming_chunk"]
    meta_data: dict[str, Any]


class StreamingToolChunk(BaseModel):
    """A chunk of output from a streaming tool."""

    type: Literal["streaming_tool"]
    tool_id: str
    tool_name: str
    tool_output: dict[str, Any]
    meta_data: dict[str, Any]


class StreamingToolRequest(BaseModel):
    """A chunk of output from a streaming tool."""

    type: Literal["streaming_tool_request"]
    tool_id: str
    tool_args: dict[str, Any]
    meta_data: dict[str, Any]
    tool_name: str


class StreamingToolResponse(BaseModel):
    """A chunk of output from a streaming tool."""

    type: Literal["streaming_tool_response"]
    tool_id: str
    tool_output: dict[str, Any]
    meta_data: dict[str, Any]


class StreamNodeHeaderChunk(BaseModel):
    """Represents a special 'header' announcement that we're at a particular Node."""

    type: Literal["node_header"]
    node_type: str  # e.g. "ModelRequestNode" or "CallToolsNode"
    description: str  # e.g. "streaming partial request tokens"
    meta_data: dict[str, Any]


class StreamUserPromptChunk(BaseModel):
    """Represents the user prompt node."""

    type: Literal["user_prompt"]
    user_prompt: Union[str, Sequence[Any]]
    meta_data: dict[str, Any]


class StreamPartStartEventChunk(BaseModel):
    """Represents a PartStartEvent."""

    type: Literal["part_start_event"]
    part_index: int
    part_content: str  # whatever event.part!r is
    meta_data: dict[str, Any]


class StreamToolCallPartDeltaChunk(BaseModel):
    """Represents a ToolCallPartDelta."""

    type: Literal["tool_call_part_delta"]
    part_index: int
    args_delta: Any  # or dict[str, Any] depending on your usage
    meta_data: dict[str, Any]


class StreamFinalResultEventChunk(BaseModel):
    """Represents a FinalResultEvent."""

    type: Literal["final_result_event"]
    tool_name: Optional[str]
    meta_data: dict[str, Any]


class StreamEndNodeChunk(BaseModel):
    """Represents the final agent output at the EndNode."""

    type: Literal["end_node"]
    final_output: str
    meta_data: dict[str, Any]


class StreamTextDeltaChunk(BaseModel):
    """Represents partial text tokens returned by the model (TextPartDelta)."""

    type: Literal["text_delta"]
    text: str  # chunk of partial text
    meta_data: dict[str, Any]


StreamChunkDataTypes = Union[
    StreamReasoningChunk,
    StreamTextChunk,
    StreamingToolRequest,
    StreamingToolResponse,
    StreamNodeHeaderChunk,
    StreamUserPromptChunk,
    StreamPartStartEventChunk,
    StreamToolCallPartDeltaChunk,
    StreamFinalResultEventChunk,
    StreamEndNodeChunk,
    StreamTextDeltaChunk,
]


class StreamChunk(BaseModel):
    """A single chunk of streaming output from a tool."""

    data: StreamChunkDataTypes
    type: Literal["streaming_chunk"]
    meta_data: dict[str, Any]


class InputText(BaseModel):
    """A text input to be sent to the model."""

    text: str
    type: Literal["input_text"]


class InputImage(BaseModel):
    """An image input to be sent to the model."""

    detail: Literal["high", "low", "auto"]
    """The detail level of the image to be sent to the model.
    One of `high`, `low`, or `auto`. Defaults to `auto`.
    """

    type: Literal["input_image"]

    file_id: Optional[str]
    """The ID of the file to be sent to the model."""

    image_url: Optional[str]
    """The URL of the image to be sent to the model.

    A fully qualified URL or base64 encoded image in a data URL.
    """


class InputFile(BaseModel):
    """A file input to be sent to the model."""

    type: Literal["input_file"]
    """The type of the input item. Always `input_file`."""

    file_id: str
    """The ID of the file to be sent to the model."""


InputMessage = Union[InputText, InputImage, InputFile]


class OutputText(BaseModel):
    """A text output from the model."""

    text: str
    type: Literal["output_text"]
    annotations: list[str]


class OutputGuardrail(BaseModel):
    """A guardrail output from the model."""

    type: Literal["output_guardrail"]
    text: str
    guardrail: list[dict[str, Any]]


OutputMessage = Union[OutputText, OutputGuardrail]


ThreadMessageContentType = Union[str, list[InputMessage], list[OutputMessage]]


class ThreadMessage(BaseModel):
    """A single piece of content within a thread.

    Messages can be either requests to a model (user prompts, system prompts,
    or tool returns) or responses from the model. Each message is associated
    with a specific thread and optionally with an assistant and run.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    object: str = "thread.message"
    thread_id: str  # FK to Thread
    role: str  # e.g. 'user', 'assistant', 'system', 'tool'

    # content can be either
    # - a single string (for text messages)
    # - a list of InputMessage objects (for model inputs)
    # - a list of OutputMessage objects (for model outputs)
    content: ThreadMessageContentType

    agent_id: Optional[str] = None  # If this message was sent by an assistant
    run_id: Optional[str] = None  # If it's part of a Run
    meta_data: dict[str, Any] = Field(default_factory=dict)
