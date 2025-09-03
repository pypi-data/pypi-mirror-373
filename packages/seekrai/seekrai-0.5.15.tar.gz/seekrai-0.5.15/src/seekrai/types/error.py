from __future__ import annotations

from pydantic import Field

from seekrai.types.abstract import BaseModel


class SeekrFlowErrorResponse(BaseModel):
    # error message
    message: str | None = None
    # error type
    type_: str | None = Field(None, alias="type")
    # param causing error
    param: str | None = None
    # error code
    code: str | None = None
