import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeploymentType(str, enum.Enum):
    # Matches UI
    FINE_TUNED_RUN = "Fine-tuned Run"
    BASE_MODEL = "Base Model"  # TODO - clean up spacing, capital, etc.


class DeploymentStatus(str, enum.Enum):
    # dedicated
    INACTIVE = "Inactive"  # Shared with serverless.
    PENDING = "Pending"
    ACTIVE = "Active"  # Shared with serverless.
    FAILED = "Failed"
    STARTED = "Started"
    SUCCESS = "Success"


class HardwareType(str, enum.Enum):
    # Matches UI
    SERVERLESS = "Serverless"
    DEDICATED = "Dedicated"


class DeploymentProcessor(str, enum.Enum):
    GAUDI2 = "GAUDI2"
    GAUDI3 = "GAUDI3"
    A100 = "A100"
    A10 = "A10"
    H100 = "H100"
    XEON = "XEON"
    NVIDIA = "NVIDIA"  # TODO - this doesnt make sense with A100, etc.
    AMD = "AMD"


class NewDeploymentRequest(BaseModel):
    model_type: DeploymentType
    model_id: str
    name: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=5, max_length=1000)
    n_instances: int = Field(..., ge=1, le=50)


class Deployment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_type: DeploymentType
    model_id: str
    name: str
    description: str
    status: DeploymentStatus
    memory: Optional[str] = None
    hardware_type: HardwareType = HardwareType.DEDICATED
    total_input_tokens: int
    total_output_tokens: int
    created_at: datetime
    last_deployed_at: Optional[datetime] = None
    updated_at: datetime
    processor: DeploymentProcessor = DeploymentProcessor.GAUDI2
    n_instances: int
    user_id: int


class GetDeploymentsResponse(BaseModel):
    data: list[Deployment]
