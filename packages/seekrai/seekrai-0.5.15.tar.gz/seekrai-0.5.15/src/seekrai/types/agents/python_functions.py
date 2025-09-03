from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PythonFunctionBase(BaseModel):
    """Base model for a Python function, including metadata fields."""

    model_config = ConfigDict(from_attributes=True)
    id: str
    version: int
    name: str
    description: str
    active: bool


class PythonFunctionResponse(PythonFunctionBase):
    """Response model for a Python function, including code and user info."""

    code: str
    user_id: str
    created_at: datetime
    updated_at: datetime


class DeletePythonFunctionResponse(BaseModel):
    """Response model for Python function deletion."""

    deleted: bool
