from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal

from pydantic import Field

from seekrai.types.abstract import BaseModel


class InfluentialFinetuningDataResponse(BaseModel):
    results: List[Dict[str, Any]]
    version: str


class InfluentialFinetuningDataRequest(BaseModel):
    question: str
    answer: str = Field(
        default="",
        description="Response could be generated or given",
    )
    k: int


class ExplainabilityJobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    # TODO should titles along the following get added:
    # create_index
    # populate_index
    # delete_index
    # influential-finetuning-data


class ExplainabilityRequest(BaseModel):
    files: List[str] = Field(
        default=..., description="List of file ids to use for fine tuning"
    )
    method: str = Field(default="best", description="Method to use for explainability")


class ExplainabilityResponse(BaseModel):
    id: str = Field(default=..., description="Explainability job ID")
    created_at: datetime
    status: ExplainabilityJobStatus
    output_files: List[str]


class ExplainabilityList(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune job objects
    data: List[ExplainabilityResponse] | None = None
