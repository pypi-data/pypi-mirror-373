from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from seekrai import (
    abstract,
    client,
    constants,
    error,
    filemanager,
    resources,
    seekrflow_response,
    types,
    utils,
)
from seekrai.version import VERSION


version = VERSION

log: str | None = None  # Set to either 'debug' or 'info', controls console logging

if TYPE_CHECKING:
    import requests

requestssession: "requests.Session" | Callable[[], "requests.Session"] | None = None

from seekrai.client import AsyncClient, AsyncSeekrFlow, Client, SeekrFlow


api_key: str | None = None  # To be deprecated in the next major release

__all__ = [
    "constants",
    "version",
    "SeekrFlow",
    "AsyncSeekrFlow",
    "Client",
    "AsyncClient",
    "resources",
    "types",
    "abstract",
    "filemanager",
    "error",
    "seekrflow_response",
    "client",
    "utils",
]
