from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import Field

from seekrai.types.abstract import BaseModel
from seekrai.types.common import (
    ObjectType,
)


class FinetuneJobStatus(str, Enum):
    """
    Possible fine-tune job status
    """

    STATUS_PENDING = "pending"
    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    # STATUS_COMPRESSING = "compressing"
    # STATUS_UPLOADING = "uploading"
    STATUS_CANCEL_REQUESTED = "cancel_requested"
    STATUS_CANCELLED = "cancelled"
    STATUS_FAILED = "failed"
    STATUS_COMPLETED = "completed"
    STATUS_DELETED = "deleted"


class FinetuneEventLevels(str, Enum):
    """
    Fine-tune job event status levels
    """

    NULL = ""
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    LEGACY_INFO = "info"
    LEGACY_IWARNING = "warning"
    LEGACY_IERROR = "error"


class FinetuneEventType(str, Enum):
    """
    Fine-tune job event types
    """

    JOB_PENDING = "JOB_PENDING"
    JOB_START = "JOB_START"
    JOB_STOPPED = "JOB_STOPPED"
    MODEL_DOWNLOADING = "MODEL_DOWNLOADING"
    MODEL_DOWNLOAD_COMPLETE = "MODEL_DOWNLOAD_COMPLETE"
    TRAINING_DATA_DOWNLOADING = "TRAINING_DATA_DOWNLOADING"
    TRAINING_DATA_DOWNLOAD_COMPLETE = "TRAINING_DATA_DOWNLOAD_COMPLETE"
    VALIDATION_DATA_DOWNLOADING = "VALIDATION_DATA_DOWNLOADING"
    VALIDATION_DATA_DOWNLOAD_COMPLETE = "VALIDATION_DATA_DOWNLOAD_COMPLETE"
    WANDB_INIT = "WANDB_INIT"
    TRAINING_START = "TRAINING_START"
    CHECKPOINT_SAVE = "CHECKPOINT_SAVE"
    BILLING_LIMIT = "BILLING_LIMIT"
    EPOCH_COMPLETE = "EPOCH_COMPLETE"
    TRAINING_COMPLETE = "TRAINING_COMPLETE"
    MODEL_COMPRESSING = "COMPRESSING_MODEL"
    MODEL_COMPRESSION_COMPLETE = "MODEL_COMPRESSION_COMPLETE"
    MODEL_UPLOADING = "MODEL_UPLOADING"
    MODEL_UPLOAD_COMPLETE = "MODEL_UPLOAD_COMPLETE"
    JOB_COMPLETE = "JOB_COMPLETE"
    JOB_ERROR = "JOB_ERROR"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    JOB_RESTARTED = "JOB_RESTARTED"
    REFUND = "REFUND"
    WARNING = "WARNING"


class FineTuneType(str, Enum):
    STANDARD = "STANDARD"
    DPO = "DPO"
    GRPO = "GRPO"


class FinetuneEvent(BaseModel):
    """
    Fine-tune event type
    """

    # object type
    object: Literal[ObjectType.FinetuneEvent]
    # created at datetime stamp
    created_at: datetime | None = None
    # metrics that we expose
    loss: float | None = None
    epoch: float | None = None


class TrainingConfig(BaseModel):
    # training file ID
    training_files: List[str]
    # base model string
    model: str
    # number of epochs to train for
    n_epochs: int
    # training learning rate
    learning_rate: float
    # number of checkpoints to save
    n_checkpoints: int | None = None
    # training batch size
    batch_size: int = Field(..., ge=1, le=1024)
    # up to 40 character suffix for output model name
    experiment_name: str | None = None
    # sequence length
    max_length: int = 2500
    # # weights & biases api key
    # wandb_key: str | None = None
    # IFT by default
    pre_train: bool = False
    # fine-tune type
    fine_tune_type: FineTuneType = FineTuneType.STANDARD


class AcceleratorType(str, Enum):
    GAUDI2 = "GAUDI2"
    GAUDI3 = "GAUDI3"
    A100 = "A100"
    A10 = "A10"
    H100 = "H100"
    MI300X = "MI300X"


class InfrastructureConfig(BaseModel):
    accel_type: AcceleratorType
    n_accel: int


class FinetuneRequest(BaseModel):
    """
    Fine-tune request type
    """

    project_id: int
    training_config: TrainingConfig
    infrastructure_config: InfrastructureConfig


class FinetuneResponse(BaseModel):
    """
    Fine-tune API response type
    """

    # job ID
    id: str | None = None
    # fine-tune type
    fine_tune_type: FineTuneType = FineTuneType.STANDARD
    # training file id
    training_files: List[str] | None = None
    # validation file id
    # validation_files: str | None = None TODO
    # base model name
    model: str | None = None
    accel_type: AcceleratorType
    n_accel: int
    # number of epochs
    n_epochs: int | None = None
    # number of checkpoints to save
    # n_checkpoints: int | None = None # TODO
    # training batch size
    batch_size: int | None = None
    # training learning rate
    learning_rate: float | None = None
    # number of steps between evals
    # eval_steps: int | None = None TODO
    # is LoRA finetune boolean
    # lora: bool | None = None
    # lora_r: int | None = None
    # lora_alpha: int | None = None
    # lora_dropout: int | None = None
    # created/updated datetime stamps
    created_at: datetime | None = None
    # updated_at: str | None = None
    # up to 40 character suffix for output model name
    experiment_name: str | None = None
    # job status
    status: FinetuneJobStatus | None = None
    deleted_at: datetime | None = None

    # list of fine-tune events
    events: List[FinetuneEvent] | None = None
    inference_available: bool = False
    project_id: Optional[int] = None  # TODO - fix this
    completed_at: datetime | None = None
    description: str | None = None

    # dataset token count
    # TODO
    # token_count: int | None = None
    # # model parameter count
    # param_count: int | None = None
    # # fine-tune job price
    # total_price: int | None = None
    # # number of epochs completed (incrementing counter)
    # epochs_completed: int | None = None
    # # place in job queue (decrementing counter)
    # queue_depth: int | None = None
    # # weights & biases project name
    # wandb_project_name: str | None = None
    # # weights & biases job url
    # wandb_url: str | None = None
    # # training file metadata
    # training_file_num_lines: int | None = Field(None, alias="TrainingFileNumLines")
    # training_file_size: int | None = Field(None, alias="TrainingFileSize")


class FinetuneList(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune job objects
    data: List[FinetuneResponse] | None = None


class FinetuneListEvents(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune events
    data: List[FinetuneEvent] | None = None


class FinetuneDownloadResult(BaseModel):
    # object type
    object: Literal["local"] | None = None
    # fine-tune job id
    id: str | None = None
    # checkpoint step number
    checkpoint_step: int | None = None
    # local path filename
    filename: str | None = None
    # size in bytes
    size: int | None = None
