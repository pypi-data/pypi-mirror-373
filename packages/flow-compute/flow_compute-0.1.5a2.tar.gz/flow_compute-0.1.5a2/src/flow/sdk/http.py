"""Thin SDK HTTP facade for CLI use.

Provides a stable import path for HTTP operations so the CLI does not import
adapter implementations directly. Internally delegates to the adapter client.
"""

from __future__ import annotations

import importlib
from typing import Any


class HttpClient:
    """HTTP client facade that delegates to the adapters layer lazily."""

    def __init__(
        self,
        *,
        base_url: str,
        headers: dict[str, str] | None = None,
        verify: bool | str | None = None,
        cert: str | tuple[str, str] | None = None,
        trust_env: bool = True,
        retry_server_errors_max: int = 3,
        backoff_base_seconds: float = 1.0,
        backoff_cap_seconds: float = 10.0,
        jitter_seconds: float = 0.25,
    ):
        mod = importlib.import_module("flow.adapters.http.client")
        _Http = mod.HttpClient
        self._impl = _Http(
            base_url=base_url,
            headers=headers,
            verify=verify,
            cert=cert,
            trust_env=trust_env,
            retry_server_errors_max=retry_server_errors_max,
            backoff_base_seconds=backoff_base_seconds,
            backoff_cap_seconds=backoff_cap_seconds,
            jitter_seconds=jitter_seconds,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
        verify: bool | str | None = None,
    ) -> Any:
        return self._impl.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=headers,
            timeout_seconds=timeout_seconds,
            verify=verify,
        )
