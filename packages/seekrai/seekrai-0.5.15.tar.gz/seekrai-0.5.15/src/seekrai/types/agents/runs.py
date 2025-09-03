import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

import pydantic
from pydantic import Field

from seekrai.types.abstract import BaseModel


class ModelSettings(BaseModel):
    """Settings to use when calling an LLM.

    This class holds optional model configuration parameters (e.g. temperature,
    top_p, penalties, truncation, etc.).

    Not all models/providers support all of these parameters, so please check the API documentation
    for the specific model and provider you are using.
    """

    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    max_tokens: Optional[int] = None


class ResponseFormat(BaseModel):
    """Specifies a JSON schema for the response format.

    When provided, the LLM will be constrained to return a JSON response
    that matches the specified schema.

    Can be instantiated with:
    - A JSON schema dictionary
    - A Pydantic model class
    - An existing ResponseFormat instance
    """

    json_schema: Dict[str, Any]

    @classmethod
    def from_value(cls, value: Any) -> "ResponseFormat":
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(json_schema=value)
        if isinstance(value, type) and issubclass(value, pydantic.BaseModel):
            return cls(json_schema=value.model_json_schema())
        raise ValueError(
            "ResponseFormat configuration is invalid. Expected ResponseFormat, a valid schema or a Pydantic BaseModel."
        )


class RunRequest(BaseModel):
    """Request model for creating a run."""

    agent_id: str = Field(default="default_agent")
    model_settings: ModelSettings = ModelSettings()
    response_format: Optional[Union[ResponseFormat, Dict[str, Any], type]] = None
    group: Optional[str] = None


class RunResponse(BaseModel):
    """Response model for run creation."""

    run_id: str
    thread_id: str
    status: str
    group: Optional[str] = None


class RunStatus(str, Enum):
    """Available status for a run."""

    QUEUED = "queued"
    IN_PROGRESS = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class RunUsage(BaseModel):
    """Aggregated usage metrics for a complete run execution.

    Tracks token consumption for both prompts and completions.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class RunStepUsage(BaseModel):
    """Usage metrics for a single step within a run.

    Tracks token consumption at the individual step level.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Run(BaseModel):
    """Represents a single execution within a thread.

    A run encompasses the entire lifecycle of processing, from receiving
    the initial prompt to delivering the final response. Runs track
    execution status, timing, model parameters, and resource usage.
    """

    id: str
    object: str = "thread.run"
    created_at: datetime.datetime
    agent_id: str
    thread_id: str
    status: RunStatus  # e.g. queued, in_progress, completed, failed, canceled
    is_active: bool = False  # Indicates if this run is actively executing on its thread

    started_at: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime] = None
    cancelled_at: Optional[datetime.datetime] = None
    failed_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    model: str
    instructions: Optional[str] = None
    tools: list[dict[str, Any]] = Field(default_factory=list)
    meta_data: dict[str, Any] = Field(default_factory=dict)

    usage: Optional[RunUsage] = None

    temperature: float
    top_p: float
    max_completion_tokens: Optional[int] = None
    truncation_strategy: dict[str, Any] = Field(default_factory=dict)
    response_format: Union[str, dict[str, Any]] = "auto"
    tool_choice: Union[str, dict[str, Any]] = "auto"
    parallel_tool_calls: bool


class RunStep(BaseModel):
    """A single atomic operation within a run.

    Steps can include message creation, tool calls, or other internal actions.
    Each step is associated with a specific run, assistant, and thread, and
    includes details about its type, status, and resource usage.
    """

    id: str
    object: str = "thread.run.step"
    created_at: datetime.datetime
    run_id: str
    agent_id: str
    thread_id: str

    # E.g. 'message_creation', 'tool_call', etc.
    type: str

    # E.g. 'completed', 'failed', etc.
    status: str

    completed_at: Optional[datetime.datetime] = None
    meta_data: dict[str, Any] = Field(default_factory=dict)
    usage: Optional[RunStepUsage] = None
