from __future__ import annotations

from seekrai.types import SeekrFlowClient


class ResourceBase:
    """Base class for resources."""

    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client
