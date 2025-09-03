"""Simple HTTP client for Flow SDK."""

import logging
import platform as _platform
import threading
import time
import uuid as _uuid
from contextlib import suppress
from typing import Any
from weakref import WeakValueDictionary

import httpx

from flow.errors import APIError, AuthenticationError, NetworkError, TimeoutError
from flow.errors.mapper import map_exception, register_provider_exceptions

logger = logging.getLogger(__name__)


class HttpClient:
    """Basic HTTP client with auto JSON handling."""

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        *,
        verify: bool | str | None = None,
        cert: str | tuple[str, str] | None = None,
        trust_env: bool = True,
        retry_server_errors_max: int = 3,
        backoff_base_seconds: float = 1.0,
        backoff_cap_seconds: float = 10.0,
        jitter_seconds: float = 0.25,
    ):
        """Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            headers: Default headers to include in all requests
        """
        # Store base_url as attribute for access by consumers
        self.base_url = base_url

        # Configure transport with built-in retries for connection errors
        transport = httpx.HTTPTransport(
            retries=3,  # Retry connection errors automatically
        )

        # Reasonable connection pool/HTTP2 settings for faster handshakes and reuse
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)

        # Enable HTTP/2 only if supported or explicitly requested. This avoids requiring 'h2'.
        http2_enabled = False
        try:
            # Centralized config
            from flow.application.config.runtime import settings as _settings  # local import

            http_cfg = _settings.http or {}
            if bool(http_cfg.get("http2", False)):
                http2_enabled = True
            else:
                # Best-effort detect if h2 is installed
                import h2  # type: ignore

                _ = h2  # silence linter
                http2_enabled = True
        except Exception:
            http2_enabled = False

        # Build a helpful User-Agent for debugging/support
        user_agent = "flow-compute/unknown"
        try:
            from flow._version import get_version as _get_version  # local import to avoid cycles

            user_agent = f"flow-compute/{_get_version()}"
        except Exception:
            pass
        with suppress(Exception):
            user_agent += f" ({_platform.system()} {_platform.release()}; Python { _platform.python_version() })"

        base_headers = dict(headers or {})
        # Do not override if caller sets a custom UA
        base_headers.setdefault("User-Agent", user_agent)

        # Ensure provider exception mappers (httpx, paramiko) are registered once
        try:  # pragma: no cover - registration is idempotent
            register_provider_exceptions()
        except Exception:
            pass

        self.client = httpx.Client(
            base_url=base_url,
            headers=base_headers,
            timeout=httpx.Timeout(30.0),
            transport=transport,
            follow_redirects=True,  # Follow redirects automatically
            http2=http2_enabled,
            limits=limits,
            verify=verify,
            cert=cert,
            trust_env=trust_env,
        )
        # Retry/backoff config and simple metrics
        self._retry_max = int(max(1, retry_server_errors_max))
        self._backoff_base = float(max(0.01, backoff_base_seconds))
        self._backoff_cap = float(max(0.1, backoff_cap_seconds))
        self._jitter = float(max(0.0, jitter_seconds))
        self.total_requests = 0
        self.retries_attempted = 0
        self.responses_5xx = 0
        self.responses_429 = 0

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        retry_server_errors: bool = True,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request and return JSON response.

        Transport layer handles connection retries automatically.
        This method only retries 5xx server errors if enabled.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL path (relative to base_url)
            headers: Additional headers for this request
            json: JSON body to send
            params: Query parameters
            retry_server_errors: Whether to retry 5xx errors (default: True)

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: For 401/403 responses
            ValidationAPIError: For 422 validation errors with details
            APIError: For other API errors
            TimeoutError: For request timeouts
            NetworkError: For connection errors
        """
        max_retries = self._retry_max if retry_server_errors else 1
        last_error = None

        for attempt in range(max_retries):
            try:
                # Generate a client-side correlation id to aid debugging if server doesn't provide one
                client_request_id = str(_uuid.uuid4())
                req_headers = dict(headers or {})
                req_headers.setdefault("X-Client-Request-Id", client_request_id)

                # Count attempts for coarse metrics
                self.total_requests += 1
                response = self.client.request(
                    method=method,
                    url=url,
                    headers=req_headers,
                    json=json,
                    params=params,
                    timeout=(
                        timeout_seconds if timeout_seconds is not None else httpx.USE_CLIENT_DEFAULT
                    ),
                )
                response.raise_for_status()

                # Handle 204 No Content response (e.g., from DELETE operations)
                if response.status_code == 204:
                    return {}

                # Parse JSON response
                return response.json()

            except httpx.HTTPStatusError as e:
                # Convert to specific errors
                if e.response.status_code == 401:
                    # Avoid implying the key is necessarily invalid; 401 can also mean
                    # missing auth context or insufficient permissions in some environments.
                    tips = [
                        "Run 'flow init' for interactive setup",
                        'Export MITHRIL_API_KEY: export MITHRIL_API_KEY="fkey_..."',
                        "Verify the key is active and has required permissions",
                    ]
                    try:
                        from flow.utils.links import WebLinks as _WebLinks  # local import

                        tips.append(f"Check billing/settings: {_WebLinks.billing_settings()}")
                    except Exception:
                        pass
                    raise AuthenticationError(
                        "Authentication failed (401). Verify API key and permissions.",
                        suggestions=tips,
                        error_code="AUTH_003",
                    ) from e
                elif e.response.status_code == 403:
                    raise AuthenticationError(
                        "Access denied. Check your API key permissions.",
                        suggestions=[
                            "Verify you have access to the project in the dashboard",
                            "Switch project: flow init --project <project>",
                            "Ask an admin to grant the necessary role",
                        ],
                        error_code="AUTH_004",
                    ) from e
                elif e.response.status_code == 404:
                    # Pass through the actual error message from the API
                    request_id = (
                        e.response.headers.get("x-request-id")
                        or e.response.headers.get("x-correlation-id")
                        or client_request_id
                    )
                    raise APIError(
                        f"Not found: {e.response.text}",
                        status_code=404,
                        response_body=e.response.text,
                        request_id=request_id,
                    ) from e
                elif e.response.status_code == 422:
                    # Validation error - parse and format the details
                    from flow.errors import ValidationAPIError

                    raise ValidationAPIError(e.response) from e
                elif e.response.status_code == 504:
                    # Gateway timeout
                    raise TimeoutError(f"Gateway timeout: {e.response.text}") from e
                elif e.response.status_code == 429:
                    # Rate limited (explicit path for better UX)
                    from flow.errors import RateLimitError

                    self.responses_429 += 1

                    retry_after_header = e.response.headers.get("retry-after")
                    retry_after = None
                    try:
                        if retry_after_header is not None:
                            retry_after = int(retry_after_header)
                    except Exception:
                        retry_after = None

                    request_id = (
                        e.response.headers.get("x-request-id")
                        or e.response.headers.get("x-correlation-id")
                        or client_request_id
                    )
                    err = RateLimitError(
                        "Rate limit exceeded",
                        retry_after=retry_after,
                        status_code=429,
                        response_body=e.response.text,
                        request_id=request_id,
                    )
                    # Attach helpful suggestions
                    err.suggestions = [
                        (
                            f"Wait {retry_after} seconds and retry"
                            if retry_after
                            else "Wait and retry shortly"
                        ),
                        "Reduce request frequency or batch operations",
                        "Consider exponential backoff between retries",
                    ]
                    raise err from e
                elif e.response.status_code >= 500:
                    # Server error - maybe retry
                    self.responses_5xx += 1
                    if attempt < max_retries - 1:
                        import random as _rand

                        base = self._backoff_base * (2**attempt)
                        delay = min(base, self._backoff_cap) + (_rand.random() * self._jitter)
                        # Demote noisy retry logs to debug; surfaced in higher-level UX instead
                        logger.debug(
                            f"Server error {e.response.status_code} (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {delay}s"
                        )
                        time.sleep(delay)
                        self.retries_attempted += 1
                        continue
                    # Build a cleaner server error with helpful suggestions
                    detail_text = None
                    try:
                        data = e.response.json()
                        detail_text = data.get("detail") if isinstance(data, dict) else None
                    except Exception:
                        detail_text = None
                    # Include provider detail string when available to avoid generic errors
                    message_text = (
                        f"Server error {e.response.status_code}: {detail_text}"
                        if detail_text
                        else f"Server error {e.response.status_code}"
                    )
                    request_id = (
                        e.response.headers.get("x-request-id")
                        or e.response.headers.get("x-correlation-id")
                        or client_request_id
                    )
                    last_error = APIError(
                        message_text,
                        status_code=e.response.status_code,
                        response_body=e.response.text,
                        request_id=request_id,
                    )
                    # Attach actionable suggestions for transient 5xx failures
                    with suppress(Exception):
                        last_error.suggestions = [
                            "This may be a transient provider issue. Try again in a minute",
                            "If it persists, try a different instance type or region",
                            "Check provider status dashboard",
                            "Run 'flow status' to verify if the request partially succeeded",
                        ]
                else:
                    # Other client errors - don't retry
                    error_text = e.response.text
                    suggestions: list[str] = []

                    # Try to parse JSON error for structured details
                    detail_text = None
                    try:
                        data = e.response.json()
                        if isinstance(data, dict):
                            detail_text = data.get("detail")
                    except Exception:
                        detail_text = None

                    # Normalize a lowercase aggregate for heuristics
                    combined_lower = " ".join(
                        s for s in [str(detail_text or ""), str(error_text or "")] if s
                    ).lower()

                    # Heuristic: billing/payment method not configured (Stripe)
                    # Detect via HTTP 402 or typical phrases and point users to billing settings
                    try:
                        from flow.utils.links import (
                            WebLinks as _WebLinks,
                        )  # local import to avoid cycles

                        _billing_url = _WebLinks.billing_settings()
                    except Exception:
                        _billing_url = None

                    _billing_indicators = (
                        "payment required",
                        "billing",
                        "payment method",
                        "payment_method",
                        "billing address",
                        "billing not configured",
                        "no default payment",
                        "stripe",
                    )
                    if e.response.status_code == 402 or any(
                        tok in combined_lower for tok in _billing_indicators
                    ):
                        if _billing_url:
                            error_text += (
                                f"\nBilling setup required. Add a payment method: {_billing_url}"
                            )
                            suggestions.extend(
                                [
                                    "Open the billing settings in the console",
                                    f"Add a payment method at: {_billing_url}",
                                    "Re-run the command after saving your payment method",
                                ]
                            )
                        else:
                            suggestions.extend(
                                [
                                    "Add a payment method in the console",
                                    "Re-run the command after completing billing setup",
                                ]
                            )

                    # Add helpful message for quota errors
                    if "quota" in combined_lower:
                        # Choose a more specific quotas page when possible
                        try:
                            request_path = url.lower() if isinstance(url, str) else ""
                            # Heuristics to classify storage vs instance quota issues
                            is_storage_context = (
                                "/volumes" in request_path
                                or "volume" in request_path
                                or "storage" in request_path
                                or "volume" in combined_lower
                                or "storage" in combined_lower
                                or "disk" in combined_lower
                            )

                            from flow.utils.links import WebLinks

                            if is_storage_context:
                                quota_url = WebLinks.quotas_storage()
                            else:
                                quota_url = WebLinks.quotas_instances()

                            error_text += f"\nCheck quota: {quota_url}"
                        except Exception:
                            # Fallback to instances quotas if detection fails
                            from flow.utils.links import WebLinks

                            error_text += f"\nCheck quota: {WebLinks.quotas_instances()}"

                    # Limit price too low - provide actionable remediation
                    limit_price_too_low = e.response.status_code == 400 and (
                        "limit price below minimum" in combined_lower
                        or "price below minimum" in combined_lower
                        or "bid price below minimum" in combined_lower
                    )
                    if limit_price_too_low:
                        # Best-effort: extract the requested limit price from the request body
                        requested_limit = None
                        try:
                            if isinstance(json, dict):
                                lp = json.get("limit_price")
                                if isinstance(lp, str) and lp.strip().startswith("$"):
                                    requested_limit = float(lp.strip().replace("$", ""))
                                elif isinstance(lp, int | float):
                                    requested_limit = float(lp)
                        except Exception:
                            requested_limit = None

                        # Suggest a higher limit price (simple 25% bump if we know the current)
                        if requested_limit:
                            recommended = round(requested_limit * 1.25, 2)
                            suggestions.extend(
                                [
                                    f"Your current limit price is ${requested_limit:.2f}/hour, which is below the minimum.",
                                    f"Increase the limit price and retry: flow run ... --max-price-per-hour {recommended:.2f}",
                                ]
                            )
                        else:
                            suggestions.append(
                                "Increase your limit price and retry (e.g., flow run ... --max-price-per-hour 100)"
                            )

                        # Additional general guidance
                        suggestions.extend(
                            [
                                "Use a higher priority tier to auto-set a higher limit price: flow run ... -p high",
                                "Re-run with --pricing to see the computed limit price in the config table",
                                "If you used 'flow example', export and edit the YAML: flow example <name> --show > job.yaml (add max_price_per_hour) then run: flow run job.yaml",
                            ]
                        )

                    # Add helpful message for name conflicts
                    elif e.response.status_code == 400 and "name already used" in combined_lower:
                        error_text += "\n\nHint: Add 'unique_name: true' to your config to automatically generate unique names."

                    # Missing required SSH keys (e.g., project requires a key)
                    if e.response.status_code == 400 and (
                        (
                            "ssh" in combined_lower
                            and "key" in combined_lower
                            and "required" in combined_lower
                        )
                        or ("no ssh keys" in combined_lower)
                    ):
                        suggestions.extend(
                            [
                                "List and sync your keys: flow ssh-keys get --sync",
                                "Upload a key: flow ssh-keys upload ~/.ssh/id_ed25519.pub",
                                "Mark a key as required (admin): flow ssh-keys require <sshkey_id>",
                                "Add the key id to your config under 'ssh_keys:'",
                            ]
                        )

                    request_id = (
                        e.response.headers.get("x-request-id")
                        or e.response.headers.get("x-correlation-id")
                        or client_request_id
                    )
                    api_error = APIError(
                        f"API error {e.response.status_code}: {error_text}",
                        status_code=e.response.status_code,
                        response_body=error_text,
                        request_id=request_id,
                    )
                    # Attach suggestions when available so CLI can render remediation steps
                    try:
                        if suggestions:
                            api_error.suggestions = suggestions
                        # Heuristic suggestions for 404 resources
                        if e.response.status_code == 404:
                            extra = [
                                "Verify the resource ID and project",
                                "List available resources, then retry",
                            ]
                            api_error.suggestions = list(set((api_error.suggestions or []) + extra))  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    raise api_error from e

            except httpx.TimeoutException as e:
                # Normalize to SDK TimeoutError (mapped further up the stack if needed)
                raise TimeoutError(f"Request timed out: {url}") from e
            except httpx.RequestError as e:
                # Network-level errors (DNS, connect, etc.)
                raise NetworkError(f"Network error: {e}") from e
            except Exception as e:
                # Map any unexpected exception via central mapper for consistency
                try:
                    mapped = map_exception(e, correlation_id=client_request_id)
                    raise mapped from e
                except Exception:
                    raise

        raise last_error

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        _ = (exc_type, exc_val, exc_tb)  # Unused but required by protocol
        self.close()


class HttpClientPool:
    """Singleton pool for HTTP clients to enable connection reuse.

    This pool maintains HTTP clients keyed by their base URL and headers,
    allowing multiple Flow instances to share the same underlying connections.
    Uses weak references to allow garbage collection when clients are no longer needed.
    """

    _clients: WeakValueDictionary[tuple, HttpClient] = WeakValueDictionary()
    _lock = threading.Lock()

    @classmethod
    def get_client(cls, base_url: str, headers: dict[str, str] | None = None) -> HttpClient:
        """Get or create a pooled HTTP client.

        Args:
            base_url: Base URL for the client
            headers: Default headers for the client

        Returns:
            Shared HttpClient instance
        """
        # Create a hashable key from base_url and headers
        headers = headers or {}
        key = (base_url, tuple(sorted(headers.items())))

        # Fast path - no lock needed for reads
        client = cls._clients.get(key)
        if client is not None:
            return client

        # Slow path - create new client outside lock
        new_client = HttpClient(base_url, headers)

        # Only lock for the minimal critical section
        with cls._lock:
            # Race condition check - another thread might have created it
            existing = cls._clients.get(key)
            if existing is not None:
                # Discard our client and use the existing one
                new_client.close()
                return existing

            # We won the race, store our client
            cls._clients[key] = new_client
            logger.debug(f"Created new HTTP client for {base_url}")
            return new_client

    @classmethod
    def clear_pool(cls) -> None:
        """Clear all pooled clients. Useful for testing."""
        cls._clients.clear()
