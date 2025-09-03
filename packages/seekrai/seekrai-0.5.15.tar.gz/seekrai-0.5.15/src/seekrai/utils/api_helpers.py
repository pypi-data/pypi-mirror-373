from __future__ import annotations

import json
import os
import platform
from typing import TYPE_CHECKING, Any, Dict


if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem

import seekrai
from seekrai import error
from seekrai.utils._log import _console_log_level


def get_headers(
    method: str | None = None,
    api_key: str | None = None,
    extra: "SupportsKeysAndGetItem[str, Any] | None" = None,
) -> Dict[str, str]:
    """
    Generates request headers with API key, metadata, and supplied headers

    Args:
        method (str, optional): HTTP request type (POST, GET, etc.)
            Defaults to None.
        api_key (str, optional): API key to add as an Authorization header.
            Defaults to None.
        extra (SupportsKeysAndGetItem[str, Any], optional): Additional headers to add to request.
            Defaults to None.

    Returns:
        headers (Dict[str, str]): Compiled headers from data
    """

    user_agent = "SeekrFlow/v1 PythonBindings/%s" % (seekrai.version,)

    uname_without_node = " ".join(
        v for k, v in platform.uname()._asdict().items() if k != "node"
    )
    ua = {
        "bindings_version": seekrai.version,
        "httplib": "requests",
        "lang": "python",
        "lang_version": platform.python_version(),
        "platform": platform.platform(),
        "publisher": "seekrai",
        "uname": uname_without_node,
    }

    headers: Dict[str, Any] = {
        "X-SeekrFlow-Client-User-Agent": json.dumps(ua),
        "Authorization": default_api_key(api_key),
        "User-Agent": user_agent,
    }

    if _console_log_level():
        headers["SeekrFlow-Debug"] = _console_log_level()
    if extra:
        headers.update(extra)

    return headers


def default_api_key(api_key: str | None = None) -> str | None:
    """
    API key fallback logic from input argument and environment variable

    Args:
        api_key (str, optional): Supplied API key. This argument takes priority over env var

    Returns:
        seekrflow_api_key (str): Returns API key from supplied input or env var

    Raises:
        seekrai.error.AuthenticationError: if API key not found
    """
    if api_key:
        return api_key
    if os.environ.get("SEEKR_API_KEY"):
        return os.environ.get("SEEKR_API_KEY")

    raise error.AuthenticationError(seekrai.constants.MISSING_API_KEY_MESSAGE)
