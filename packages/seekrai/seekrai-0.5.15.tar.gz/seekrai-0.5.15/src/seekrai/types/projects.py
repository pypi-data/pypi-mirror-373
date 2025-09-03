from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    user_id: int
    created_at: datetime
    updated_at: datetime


class ProjectWithRuns(Project):
    runs: int
    runs_deployed: int
    last_modified: datetime


class GetProjectsResponse(BaseModel):
    data: list[ProjectWithRuns]


class PostProjectRequest(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=5, max_length=1000)
