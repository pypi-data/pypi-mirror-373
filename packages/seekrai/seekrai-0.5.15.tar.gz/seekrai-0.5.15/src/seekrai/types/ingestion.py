from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal

from pydantic import Field

from seekrai.types.abstract import BaseModel


class IngestionJobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionRequest(BaseModel):
    files: List[str] = Field(
        default=..., description="List of file ids to use for alignment"
    )
    method: str = Field(default="best", description="Method to use for ingestion")


class IngestionResponse(BaseModel):
    id: str = Field(default=..., description="Ingestion job ID")
    created_at: datetime
    status: IngestionJobStatus
    output_files: List[str]


class IngestionList(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune job objects
    data: List[IngestionResponse] | None = None
