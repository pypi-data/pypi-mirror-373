from __future__ import annotations

import email.utils
import json
import sys
import threading
import time
from json import JSONDecodeError
from random import random
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    overload,
)
from urllib.parse import urlencode, urlsplit, urlunsplit

from seekrai.abstract.response_parsing import (
    parse_raw_response,
    parse_raw_response_async,
)


if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

import httpx

from seekrai import error, utils
from seekrai.constants import (
    BASE_URL,
    INITIAL_RETRY_DELAY,
    MAX_RETRIES,
    MAX_RETRY_DELAY,
    TIMEOUT_SECS,
)
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowClient, SeekrFlowRequest


# Has one attribute per thread, 'session'.
_thread_context = threading.local()


def _build_api_url(url: str, query: str) -> str:
    scheme, netloc, path, base_query, fragment = urlsplit(url)
    if base_query:
        query = "%s&%s" % (base_query, query)
    return str(urlunsplit((scheme, netloc, path, query, fragment)))


def check_response_edge_cases(result: httpx.Response) -> Optional[SeekrFlowResponse]:
    """Logs, Raises, or Returns any specially-handled HTTP responses."""
    headers = dict(result.headers.items())
    request_id = headers.get("cf-ray")
    code = result.status_code
    if 500 <= code < 600 or code == 429:
        utils.log_debug(
            f"Encountered httpx.HTTPError. Error code: {result.status_code}"
        )
    if code >= 500:
        raise httpx.HTTPError("Error communicating with API: {}".format(result))
    if code == 204:
        return SeekrFlowResponse({}, headers)
    if code == 503:
        raise error.ServiceUnavailableError(
            "The server is overloaded or not ready yet.",
            http_status=code,
            headers=headers,
        )
    if code == 429:
        raise error.RateLimitError(
            result.read().decode("utf-8"),
            http_status=code,
            headers=headers,
            request_id=request_id,
        )
    elif code in [400, 403, 404, 415]:
        raise error.InvalidRequestError(
            result.read().decode("utf-8"),
            http_status=code,
            headers=headers,
            request_id=request_id,
        )
    elif code == 401:
        raise error.AuthenticationError(
            result.read().decode("utf-8"),
            http_status=code,
            headers=headers,
            request_id=request_id,
        )
    if not 200 <= code < 300:
        utils.log_info(
            "SeekrFlow API error received",
            error_code=code,
            error_message=result.read(),
        )
        raise error.APIError(
            result.content.decode("utf-8"),
            http_status=code,
            headers=headers,
            request_id=headers.get("cf-ray"),
        )
    if 300 < code < 500:
        raise httpx.HTTPError(result.read().decode())

    return None  # No errors, no special-case response


async def acheck_response_edge_cases(
    result: httpx.Response,
) -> Optional[SeekrFlowResponse]:
    """Same as check_response_edge_cases(), but async."""
    if result.status_code != 200:  # Only synchronize for errors
        synced_result = httpx.Response(
            status_code=result.status_code,
            headers=result.headers,
            content=await result.aread(),
        )
        return check_response_edge_cases(synced_result)

    return None  # No errors, no special-case response. Carry on asynchronously...


class APIRequestor:
    def __init__(self, client: SeekrFlowClient):
        self.api_base = client.base_url or BASE_URL
        self.api_key = client.api_key or utils.default_api_key()
        self.retries = MAX_RETRIES if client.max_retries is None else client.max_retries
        self.supplied_headers = client.supplied_headers
        self.timeout = client.timeout or TIMEOUT_SECS

    def _parse_retry_after_header(
        self, response_headers: Dict[str, Any] | None = None
    ) -> float | None:
        """
        Returns a float of the number of seconds (not milliseconds)
        to wait after retrying, or None if unspecified.

        About the Retry-After header:
            https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After
        See also
            https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After#syntax
        """
        if response_headers is None:
            return None
        try:
            retry_ms_header = response_headers.get("retry-after-ms", None)
            return float(retry_ms_header) / 1000
        except (TypeError, ValueError):
            pass
        retry_header = str(response_headers.get("retry-after"))
        try:
            return float(retry_header)
        except (TypeError, ValueError):
            pass
        retry_date_tuple = email.utils.parsedate_tz(retry_header)
        if retry_date_tuple is None:
            return None
        retry_date = email.utils.mktime_tz(retry_date_tuple)
        return float(retry_date - time.time())

    def _calculate_retry_timeout(
        self,
        remaining_retries: int,
        response_headers: Dict[str, Any] | None = None,
    ) -> float:
        retry_after = self._parse_retry_after_header(response_headers)
        if retry_after is not None and 0 < retry_after <= 60:
            return retry_after
        nb_retries = self.retries - remaining_retries
        sleep_seconds = min(INITIAL_RETRY_DELAY * pow(2.0, nb_retries), MAX_RETRY_DELAY)
        jitter = 1 - 0.25 * random()
        timeout = sleep_seconds * jitter
        return timeout if timeout >= 0 else 0

    @overload
    def request(
        self,
        options: SeekrFlowRequest,
        stream: Literal[True],
        request_timeout: float | None = ...,
    ) -> Tuple[Iterator[SeekrFlowResponse], bool, str]: ...
    @overload
    def request(
        self,
        options: SeekrFlowRequest,
        stream: Literal[False] = ...,
        request_timeout: float | None = ...,
    ) -> Tuple[SeekrFlowResponse, bool, str]: ...
    @overload
    def request(
        self,
        options: SeekrFlowRequest,
        stream: bool = ...,
        request_timeout: float | None = ...,
    ) -> Tuple[SeekrFlowResponse | Iterator[SeekrFlowResponse], bool, str]: ...

    def request(
        self,
        options: SeekrFlowRequest,
        stream: bool = False,
        request_timeout: float | None = None,
    ) -> Tuple[
        SeekrFlowResponse | Iterator[SeekrFlowResponse],
        bool,
        str | None,
    ]:
        result = self.request_raw(options, stream, request_timeout)

        special_case = check_response_edge_cases(result)

        try:
            response = special_case or parse_raw_response(result, stream)
        except (JSONDecodeError, UnicodeDecodeError, ValueError) as e:
            raise error.APIError(
                f"Error code: {result.status_code} - {result.content!r}",
                http_status=result.status_code,
                headers=result.headers,
            ) from e

        return response, stream, self.api_key

    @overload
    async def arequest(
        self,
        options: SeekrFlowRequest,
        stream: Literal[True],
        request_timeout: float | None = ...,
    ) -> Tuple[AsyncGenerator[SeekrFlowResponse, None], bool, str]: ...
    @overload
    async def arequest(
        self,
        options: SeekrFlowRequest,
        *,
        stream: Literal[True],
        request_timeout: float | None = ...,
    ) -> Tuple[AsyncGenerator[SeekrFlowResponse, None], bool, str]: ...
    @overload
    async def arequest(
        self,
        options: SeekrFlowRequest,
        stream: Literal[False] = ...,
        request_timeout: float | None = ...,
    ) -> Tuple[SeekrFlowResponse, bool, str]: ...
    @overload
    async def arequest(
        self,
        options: SeekrFlowRequest,
        stream: bool = ...,
        request_timeout: float | None = ...,
    ) -> Tuple[
        SeekrFlowResponse | AsyncGenerator[SeekrFlowResponse, None], bool, str
    ]: ...

    async def arequest(
        self,
        options: SeekrFlowRequest,
        stream: bool = False,
        request_timeout: float | None = None,
    ) -> Tuple[
        SeekrFlowResponse | AsyncGenerator[SeekrFlowResponse, None], bool, str | None
    ]:
        abs_url, headers, data = self._prepare_request_raw(options, False)
        client = httpx.AsyncClient(http2=True)
        req = client.build_request(
            options.method,
            abs_url,
            headers=headers,
            data=data,  # type: ignore
            files=options.files,
            timeout=request_timeout or self.timeout,
        )
        try:
            result = await client.send(req, stream=stream)
        except httpx.TimeoutException as e:
            utils.log_debug("Encountered httpx.TimeoutException")
            raise error.Timeout("Request timed out: {}".format(e)) from e
        except httpx.RequestError as e:
            utils.log_debug("Encountered httpx.RequestError")
            raise error.APIConnectionError(
                "Error communicating with API: {}".format(e)
            ) from e

        utils.log_debug(
            "SeekrFlow API response",
            path=abs_url,
            response_code=result.status_code,
            processing_ms=result.headers.get("x-total-time"),
            request_id=result.headers.get("CF-RAY"),
        )

        special_case = await acheck_response_edge_cases(result)

        try:
            response = special_case or await parse_raw_response_async(result, stream)
        except (JSONDecodeError, UnicodeDecodeError, ValueError) as e:
            raise error.APIError(
                f"Error code: {result.status_code} - {result.content!r}",
                http_status=result.status_code,
                headers=result.headers,
            ) from e

        return response, stream, self.api_key

    @classmethod
    def _validate_headers(
        cls, supplied_headers: Dict[str, str] | None
    ) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if supplied_headers is None:
            return headers
        if not isinstance(supplied_headers, dict):
            raise TypeError("Headers must be a dictionary")
        for k, v in supplied_headers.items():
            if not isinstance(k, str):
                raise TypeError("Header keys must be strings")
            if not isinstance(v, str):
                raise TypeError("Header values must be strings")
            headers[k] = v
        return headers

    def _prepare_request_raw(
        self,
        options: SeekrFlowRequest,
        absolute: bool = False,
    ) -> Tuple[str, Dict[str, str], Mapping[str, Any] | None | str]:
        abs_url = options.url if absolute else "%s%s" % (self.api_base, options.url)
        headers = self._validate_headers(options.headers or self.supplied_headers)
        data: Mapping[str, Any] | None | str = None
        if options.method.lower() in {"get", "delete"}:
            if options.params:
                encoded_params = urlencode(
                    [(k, v) for k, v in options.params.items() if v is not None]
                )
                abs_url = _build_api_url(abs_url, encoded_params)
        elif options.method.lower() in {"post", "put", "patch"}:
            data = options.params
            if options.params and not options.files:
                data = json.dumps(data)
        else:
            raise error.APIConnectionError(
                "Unrecognized HTTP method %r. This may indicate a bug in the "
                "SeekrFlow SDK. Please contact us by filling out https://www.seekrflow.ai/contact for assistance."
                % (options.method,)
            )
        if not options.override_headers:
            headers = utils.get_headers(options.method, self.api_key, headers)
        utils.log_debug(
            "Request to SeekrFlow API",
            method=options.method,
            path=abs_url,
            post_data=data,
            headers=json.dumps(headers),
        )
        return abs_url, headers, data

    def request_raw(
        self,
        options: SeekrFlowRequest,
        stream: bool = False,
        request_timeout: float | None = None,
    ) -> httpx.Response:
        abs_url, headers, data = self._prepare_request_raw(options, False)
        client = httpx.Client(http2=True)
        req = client.build_request(
            options.method,
            abs_url,
            headers=headers,
            data=data,  # type: ignore
            files=options.files,
            timeout=request_timeout or self.timeout,
        )
        try:
            result = client.send(req, stream=stream)
        except httpx.TimeoutException as e:
            utils.log_debug("Encountered httpx.TimeoutException")
            raise error.Timeout("Request timed out: {}".format(e)) from e
        except httpx.RequestError as e:
            utils.log_debug("Encountered httpx.HTTPError")
            raise error.APIConnectionError(
                "Error communicating with API: {}".format(e)
            ) from e

        utils.log_debug(
            "SeekrFlow API response",
            path=abs_url,
            response_code=result.status_code,
            processing_ms=result.headers.get("x-total-time"),
            request_id=result.headers.get("CF-RAY"),
        )
        return result
