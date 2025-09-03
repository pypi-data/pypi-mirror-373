from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class VectorDatabaseCreate(BaseModel):
    """Request model for creating a new vector database."""

    name: str = Field(..., description="Name of the vector database")
    model: str = Field(..., description="Model used to generate the vectors")
    description: Optional[str] = Field(None, description="Optional description")


class VectorDatabaseResponse(BaseModel):
    """Response model for a vector database."""

    id: str
    name: str
    model: str
    dimension: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    file_count: int
    size_in_bytes: Optional[int] = None


class VectorDatabaseList(BaseModel):
    """Response model for a list of vector databases."""

    object: Literal["list"]
    data: List[VectorDatabaseResponse]


class VectorDatabaseIngestionRequest(BaseModel):
    """Request model for creating a new vector database ingestion job."""

    file_ids: List[str] = Field(..., description="List of file IDs to ingest")
    method: str = Field(..., description="Method to use for ingestion")
    token_count: int = Field(default=800, description="Token count for ingestion")
    overlap_tokens: int = Field(default=100, description="Overlap tokens for ingestion")


class VectorDatabaseIngestionResponse(BaseModel):
    """Response model for a vector database ingestion job."""

    id: str
    vector_database_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]
    file_ids: List[str]
    metaflow_run_id: Optional[str]


class VectorDatabaseIngestionList(BaseModel):
    """Response model for a list of vector database ingestion jobs."""

    object: Literal["list"]
    data: List[VectorDatabaseIngestionResponse]


class VectorDatabaseFileResponse(BaseModel):
    """Response model for a vector database file."""

    id: str
    vector_database_id: str
    filename: str
    created_at: datetime
    status: str
    error_message: Optional[str]


class VectorDatabaseFileList(BaseModel):
    """Response model for a list of vector database files."""

    object: Literal["list"]
    data: List[VectorDatabaseFileResponse]
