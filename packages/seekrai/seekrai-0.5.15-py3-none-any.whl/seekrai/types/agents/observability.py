from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import field_serializer

from seekrai.types.abstract import BaseModel


class ObservabilitySpansRequest(BaseModel):
    """Request model for requesting observability spans."""

    min_start_datetime: Optional[datetime]
    max_start_datetime: Optional[datetime]
    agent_id: Optional[str]
    run_id: Optional[str]
    trace_id: Optional[str]
    thread_id: Optional[str]
    group: Optional[str]
    limit: int = 100
    order: str = "desc"
    offset: int = 0

    @field_serializer("min_start_datetime", "max_start_datetime")
    def serialize_dt(self, dt: Optional[datetime], _info: Any) -> Optional[str]:
        if dt is not None:
            return dt.isoformat()
        return None


class ObservabilitySpansResponse(BaseModel):
    """Response model for requesting observability spans."""

    spans: List[Dict[str, Any]]
