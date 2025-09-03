from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional, Union

from seekrai.types.abstract import BaseModel
from seekrai.types.common import (
    ObjectType,
)


class FilePurpose(str, Enum):
    ReinforcementFineTune = "reinforcement-fine-tune"
    FineTune = "fine-tune"
    PreTrain = "pre-train"
    Alignment = "alignment"


class TrainingFileType(str, Enum):
    jsonl = "jsonl"
    parquet = "parquet"
    pytorch = "pt"  # TODO - this doesnt belong here


class AlignmentFileType(str, Enum):
    HTML = "html"
    MD = "md"
    RST = "rst"
    RTF = "rtf"
    TXT = "txt"
    XML = "xml"
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    DOC = "doc"
    DOCX = "docx"
    PDF = "pdf"
    PPT = "ppt"
    PPTX = "pptx"


FileType = Union[TrainingFileType, AlignmentFileType]


class AlignFileMetadataValidationReq(BaseModel):
    purpose: str
    suffix: str
    size: int


class AlignFileMetadataValidationResp(BaseModel):
    is_valid: bool
    errors: Optional[str] = None


class FileRequest(BaseModel):
    """
    Files request type
    """

    # # training file ID
    # training_file: str
    # # base model string
    # model: str
    # # number of epochs to train for
    # n_epochs: int
    # # training learning rate
    # learning_rate: float
    # # number of checkpoints to save
    # n_checkpoints: int | None = None
    # # training batch size
    # batch_size: int | None = None
    # # up to 40 character suffix for output model name
    # suffix: str | None = None
    # # weights & biases api key
    # wandb_api_key: str | None = None
    purpose: FilePurpose
    filetype: FileType
    filename: str


class FileResponse(BaseModel):
    """
    Files API response type
    """

    id: str
    object: Literal[ObjectType.File]
    # created timestamp
    created_at: datetime | None = None
    type: FileType | None = None
    purpose: FilePurpose | None = None
    filename: str | None = None
    # file byte size
    bytes: int | None = None
    created_by: str | None = None  # TODO - fix this later
    original_file_id: str | None = None
    deleted: bool | None = None


class FileList(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune job objects
    data: List[FileResponse] | None = None


class FileDeleteResponse(BaseModel):
    # file id
    id: str
    # object type
    object: Literal[ObjectType.File]
    # is deleted
    deleted: bool


class FileObject(BaseModel):
    # object type
    object: Literal["local"] | None = None
    # fine-tune job id
    id: str | None = None
    # local path filename
    filename: str | None = None
    # size in bytes
    size: int | None = None
