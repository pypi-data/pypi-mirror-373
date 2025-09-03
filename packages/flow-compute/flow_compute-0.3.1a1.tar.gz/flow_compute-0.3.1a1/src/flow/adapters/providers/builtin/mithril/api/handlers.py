"""Error handling utilities for the Mithril provider.

Decorators and utilities for consistent error handling across Mithril operations.
"""

import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from flow.adapters.providers.builtin.mithril.core.errors import (
    MithrilAPIError,
    MithrilAuthenticationError,
    MithrilError,
    MithrilQuotaExceededError,
    MithrilResourceNotFoundError,
    MithrilTimeoutError,
)
from flow.errors import FlowError
from flow.errors import TimeoutError as FlowTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_mithril_errors(operation: str = "Mithril operation") -> Callable:
    """Decorator to handle Mithril-specific errors with proper logging and conversion.

    Args:
        operation: Description of the operation for error messages

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except MithrilError:
                # Already a specific Mithril error (including MithrilAPIError, MithrilInstanceError, etc), re-raise
                raise
            except (TimeoutError, FlowTimeoutError) as e:
                # Handle timeout errors first (before FlowError)
                raise MithrilTimeoutError(f"{operation} timed out") from e
            except FlowError as e:
                # Check if this is an HTTP error we can convert
                if hasattr(e, "status_code"):
                    status_code = e.status_code
                    response_body = getattr(e, "response_body", None)
                    request_id = getattr(e, "request_id", None)
                    suggestions = getattr(e, "suggestions", None)

                    # Convert to specific Mithril errors based on status code
                    if status_code == 401:
                        raise MithrilAuthenticationError(
                            f"{operation} failed: Authentication required",
                            status_code=status_code,
                            response_body=response_body,
                            request_id=request_id,
                            suggestions=suggestions,
                        ) from e
                    elif status_code == 404:
                        raise MithrilResourceNotFoundError(
                            str(e) or f"{operation} failed: Resource not found",
                            status_code=status_code,
                            response_body=response_body,
                            request_id=request_id,
                            suggestions=suggestions,
                        ) from e
                    elif status_code == 429:
                        raise MithrilQuotaExceededError(
                            f"{operation} failed: Rate limit or quota exceeded",
                            status_code=status_code,
                            response_body=response_body,
                            request_id=request_id,
                            suggestions=suggestions,
                        ) from e
                    elif status_code and status_code >= 500:
                        # Preserve original error details (status and message) for better UX
                        original_message = str(e) or "Server error"
                        raise MithrilAPIError(
                            f"{operation} failed: {original_message}",
                            status_code=status_code,
                            response_body=response_body,
                            request_id=request_id,
                            suggestions=suggestions,
                        ) from e

                # Re-raise other Flow errors
                raise
            except Exception as e:
                # Prefer re-raising native httpx network errors so external retry logic
                # that explicitly catches httpx exceptions (as used in tests) can work.
                try:
                    import httpx  # type: ignore

                    if isinstance(e, httpx.RequestError):
                        raise
                except Exception:
                    pass

                # Handle httpx network errors by name if direct isinstance wasn't possible
                if hasattr(e, "__class__") and e.__class__.__name__ in [
                    "NetworkError",
                    "ConnectError",
                    "ConnectTimeout",
                ]:
                    from flow.errors import NetworkError

                    raise NetworkError(
                        f"{operation} failed: {e!s}",
                        suggestions=[
                            "Check your internet connection",
                            "Verify the API endpoint is correct",
                            "Check if you're behind a firewall or proxy",
                            "Try again in a few moments",
                        ],
                    ) from e

                # Handle httpx HTTP status errors
                if hasattr(e, "__class__") and e.__class__.__name__ == "HTTPStatusError":
                    # httpx.HTTPStatusError - extract status code
                    status_code = None
                    if hasattr(e, "response") and hasattr(e.response, "status_code"):
                        status_code = e.response.status_code

                    # Map specific status codes to SDK-level exceptions
                    if status_code == 429 or status_code == 503:
                        from flow.errors import APIError

                        raise APIError(
                            f"{operation} failed: {e!s}",
                            status_code=status_code,
                            response_body=(
                                getattr(e.response, "text", None)
                                if hasattr(e, "response")
                                else None
                            ),
                        ) from e

                # Log unexpected errors
                logger.error(f"{operation} failed with unexpected error: {e}", exc_info=True)
                raise MithrilAPIError(
                    f"{operation} failed: {e!s}",
                    suggestions=[
                        "Try again in a few moments",
                        "If the problem persists, enable diagnostics with FLOW_CLI_DIAGNOSTICS=1 and retry",
                    ],
                ) from e

        return wrapper

    return decorator


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values.

    Args:
        data: Dictionary to extract from
        keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Value at the key path or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def validate_response(response: Any, required_fields: list[str]) -> dict:
    """Validate API response has required fields.

    Args:
        response: API response to validate
        required_fields: List of required field names

    Returns:
        Response as dict

    Raises:
        MithrilAPIError: If response is invalid
    """
    if not isinstance(response, dict):
        raise MithrilAPIError(f"Invalid response type: expected dict, got {type(response)}")

    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise MithrilAPIError(f"Missing required fields in response: {', '.join(missing_fields)}")

    return response
