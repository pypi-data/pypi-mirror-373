from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal

from seekrai.types.abstract import BaseModel
from seekrai.types.common import ObjectType


class ModelType(str, Enum):
    CHAT = "chat"
    LANGUAGE = "language"
    EMBEDDING = "embedding"
    OBJECT_DETECTION = "object_detection"
    IMAGE_CLASSIFICATION = "image_classification"


# class PricingObject(BaseModel):
#     input: float | None = None
#     output: float | None = None
#     hourly: float | None = None
#     base: float | None = None
#     finetune: float | None = None


class ModelResponse(BaseModel):
    # model id
    id: str
    # object type
    object: Literal[ObjectType.Model]
    created: int | None = None
    created_at: datetime | None = None
    # model type
    type: ModelType | None = None
    name: str | None = None
    bytes: int | None = None
    model_type: str | None = None
    # # model creator organization
    # organization: str | None = None
    # # link to model resource
    # link: str | None = None
    # license: str | None = None
    # context_length: int | None = None
    # pricing: PricingObject


class ModelList(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune job objects
    data: List[ModelResponse] | None = None
