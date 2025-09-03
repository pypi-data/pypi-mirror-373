"""Error mapper for converting adapter exceptions to Flow errors.

Provides a centralized mapping from various third-party exceptions to the
canonical Flow error classes in ``flow.errors`` for consistent handling.
"""

from collections.abc import Callable

from flow.errors import (
    FlowError,
    NetworkError,
    ProviderError,
    ResourceNotFoundError,
    ValidationError,
)

# Global exception mapping registry
_exception_map: dict[type[Exception], Callable[[Exception], FlowError]] = {}


def register_exception_mapper(
    exception_type: type[Exception], mapper: Callable[[Exception], FlowError]
) -> None:
    """Register a mapper for a specific exception type.

    Args:
        exception_type: Exception class to map
        mapper: Function that converts the exception to a FlowError
    """
    _exception_map[exception_type] = mapper


def map_exception(exc: Exception, correlation_id: str | None = None) -> FlowError:
    """Map an exception to a FlowError.

    Args:
        exc: Exception to map
        correlation_id: Optional correlation ID for tracing

    Returns:
        Mapped FlowError with appropriate code and context
    """
    # Check for exact type match first
    mapper = _exception_map.get(type(exc))
    if mapper:
        return mapper(exc)

    # Check for subclass matches
    for exc_type, mapper in _exception_map.items():
        if isinstance(exc, exc_type):
            return mapper(exc)

    # Default mapping for unknown exceptions (preserve original as cause via chaining)
    return FlowError(
        "An unexpected error occurred. Please check logs for details.",
        suggestions=[],
    )


# Common exception mappers
def _map_value_error(exc: ValueError) -> FlowError:
    """Map ValueError to ValidationError."""
    return ValidationError(str(exc), suggestions=["Check input parameters and try again."])


def _map_key_error(exc: KeyError) -> FlowError:
    """Map KeyError to ValidationError."""
    return ValidationError(
        f"Missing required field: {exc}", suggestions=["Ensure all required fields are provided."]
    )


def _map_timeout_error(exc: TimeoutError) -> FlowError:
    """Map TimeoutError to NetworkError."""
    return NetworkError(
        str(exc), suggestions=["The operation timed out. Check network connectivity and retry."]
    )


def _map_connection_error(exc: ConnectionError) -> FlowError:
    """Map ConnectionError to NetworkError."""
    return NetworkError(
        str(exc), suggestions=["Failed to establish connection. Check network settings."]
    )


def _map_permission_error(exc: PermissionError) -> FlowError:
    """Map PermissionError to a provider/resource error."""
    return ProviderError(
        "Permission denied", suggestions=["Check file permissions and access rights."]
    )


def _map_file_not_found(exc: FileNotFoundError) -> FlowError:
    """Map FileNotFoundError to ResourceNotFoundError."""
    return ResourceNotFoundError(
        str(exc), suggestions=["Ensure the file or resource exists and the path is correct."]
    )


# Register default mappers
register_exception_mapper(ValueError, _map_value_error)
register_exception_mapper(KeyError, _map_key_error)
register_exception_mapper(TimeoutError, _map_timeout_error)
register_exception_mapper(ConnectionError, _map_connection_error)
register_exception_mapper(PermissionError, _map_permission_error)
register_exception_mapper(FileNotFoundError, _map_file_not_found)


# Provider-specific mappers (to be extended by adapters)
def register_provider_exceptions():
    """Register provider-specific exception mappings.

    This function should be called by provider adapters to register
    their specific exception types.
    """
    # Example for httpx exceptions (if httpx is used)
    try:
        import httpx

        def _map_httpx_timeout(exc: httpx.TimeoutException) -> FlowError:
            return NetworkError(
                f"HTTP request timed out: {exc}",
                suggestions=["Increase timeout or check server responsiveness."],
            )

        def _map_httpx_network(exc: httpx.NetworkError) -> FlowError:
            return NetworkError(
                f"Network error: {exc}",
                suggestions=["Check network connectivity and DNS resolution."],
            )

        register_exception_mapper(httpx.TimeoutException, _map_httpx_timeout)
        register_exception_mapper(httpx.NetworkError, _map_httpx_network)
    except ImportError:
        pass  # httpx not installed

    # Example for paramiko exceptions (if paramiko is used)
    try:
        import paramiko

        def _map_ssh_exception(exc: paramiko.SSHException) -> FlowError:
            return NetworkError(
                f"SSH error: {exc}", suggestions=["Check SSH credentials and server configuration."]
            )

        def _map_auth_exception(exc: paramiko.AuthenticationException) -> FlowError:
            from flow.errors import AuthenticationError

            return AuthenticationError(
                f"SSH authentication failed: {exc}", suggestions=["Verify SSH keys or password."]
            )

        register_exception_mapper(paramiko.SSHException, _map_ssh_exception)
        register_exception_mapper(paramiko.AuthenticationException, _map_auth_exception)
    except ImportError:
        pass  # paramiko not installed
