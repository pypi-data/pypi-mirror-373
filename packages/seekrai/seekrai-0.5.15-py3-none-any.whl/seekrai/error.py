from __future__ import annotations

import json
from typing import Any, Dict

from requests import RequestException

from seekrai.types.error import SeekrFlowErrorResponse


class SeekrFlowException(Exception):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        headers: str | Dict[Any, Any] | None = None,
        request_id: str | None = None,
        http_status: int | None = None,
    ) -> None:
        _message = (
            json.dumps(message.model_dump())
            if isinstance(message, SeekrFlowErrorResponse)
            else message
        )
        self._message = f"Error code: {http_status} - {_message}"

        super(SeekrFlowException, self).__init__(self._message)

        self.http_status = http_status
        self.headers = headers or {}
        self.request_id = request_id

    def __repr__(self) -> str:
        repr_message = json.dumps(
            {
                "response": self._message,
                "status": self.http_status,
                "request_id": self.request_id,
                "headers": self.headers,
            }
        )
        return "%s(%r)" % (self.__class__.__name__, repr_message)


class AuthenticationError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class ResponseError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class JSONError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class InstanceError(SeekrFlowException):
    def __init__(self, model: str | None = "model", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.message = f"""No running instances for {model}."""


class RateLimitError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class FileTypeError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class AttributeError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class Timeout(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class APIConnectionError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class InvalidRequestError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class APIError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class ServiceUnavailableError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)


class DownloadError(SeekrFlowException):
    def __init__(
        self,
        message: (
            SeekrFlowErrorResponse | Exception | str | RequestException | None
        ) = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, **kwargs)
