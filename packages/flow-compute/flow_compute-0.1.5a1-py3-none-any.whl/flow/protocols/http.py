"""HTTP client protocol for external communication.

This port defines the contract for HTTP communication that the application layer
depends on. Adapters implement this interface to provide concrete HTTP functionality.
"""

from typing import Any, Protocol


class HttpClientProtocol(Protocol):
    """Port for HTTP client operations.

    This port abstracts HTTP communication for the application layer.
    Implementations must handle authentication, retries, and connection
    pooling transparently.

    Implementation requirements:
      - Automatic retry with exponential backoff for transient failures
      - Connection pooling for performance
      - Request/response logging for debugging
      - Timeout handling (30s default, configurable)
      - Error mapping to domain error types
      - Thread-safe operation for concurrent requests
    """

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        retry_server_errors: bool = True,
        timeout_seconds: float | None = None,
        verify: bool | str | None = None,
    ) -> dict[str, Any]:
        """Execute HTTP request with automatic retries.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            url: Full URL or path relative to base URL
            headers: Additional HTTP headers
            json: Request body for POST/PUT/PATCH
            params: URL query parameters
            retry_server_errors: Whether to retry 5xx responses
            timeout_seconds: Request timeout in seconds (None = client default)
            verify: TLS verification settings passed to the transport layer

        Returns:
            Parsed JSON response body

        Raises:
            Domain-specific errors mapped from HTTP status codes
        """
        ...

    def close(self) -> None:
        """Release HTTP client resources gracefully.

        Closes connection pools and frees resources.
        Safe to call multiple times.
        """
        ...
