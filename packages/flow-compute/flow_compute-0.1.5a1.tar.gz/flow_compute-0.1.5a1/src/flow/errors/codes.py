"""Error codes and exception hierarchy.

This module defines structured error codes and typed exceptions
for consistent error handling across the Flow platform.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorCode(Enum):
    """Standardized error codes for Flow platform."""

    # General errors (1xxx)
    UNKNOWN = "FLOW-1000"
    INVALID_INPUT = "FLOW-1001"
    CONFIGURATION_ERROR = "FLOW-1002"
    VALIDATION_ERROR = "FLOW-1003"

    # Resource errors (2xxx)
    RESOURCE_NOT_FOUND = "FLOW-2001"
    RESOURCE_UNAVAILABLE = "FLOW-2002"
    INSUFFICIENT_RESOURCES = "FLOW-2003"
    QUOTA_EXCEEDED = "FLOW-2004"

    # Provider errors (3xxx)
    PROVIDER_NOT_FOUND = "FLOW-3001"
    PROVIDER_ERROR = "FLOW-3002"
    PROVIDER_TIMEOUT = "FLOW-3003"
    PROVIDER_AUTH_FAILED = "FLOW-3004"

    # Task errors (4xxx)
    TASK_NOT_FOUND = "FLOW-4001"
    TASK_FAILED = "FLOW-4002"
    TASK_TIMEOUT = "FLOW-4003"
    TASK_CANCELLED = "FLOW-4004"

    # Network errors (5xxx)
    NETWORK_ERROR = "FLOW-5001"
    CONNECTION_FAILED = "FLOW-5002"
    CONNECTION_TIMEOUT = "FLOW-5003"
    SSH_FAILED = "FLOW-5004"

    # Storage errors (6xxx)
    STORAGE_ERROR = "FLOW-6001"
    VOLUME_NOT_FOUND = "FLOW-6002"
    MOUNT_FAILED = "FLOW-6003"
    UPLOAD_FAILED = "FLOW-6004"
    DOWNLOAD_FAILED = "FLOW-6005"


@dataclass(frozen=True)
class ErrorContext:
    """Context information for an error."""

    code: ErrorCode
    message: str
    hint: str | None = None
    doc_url: str | None = None
    metadata: dict[str, Any] | None = None
    correlation_id: str | None = None


class FlowError(Exception):
    """Base exception for Flow platform errors."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        hint: str | None = None,
        doc_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        cause: Exception | None = None,
    ):
        """Initialize a Flow error.

        Args:
            code: Error code
            message: Human-readable error message
            hint: Hint for resolving the error
            doc_url: URL to documentation about this error
            metadata: Additional error metadata
            correlation_id: Request correlation ID for tracing
            cause: Original exception that caused this error
        """
        self.context = ErrorContext(
            code=code,
            message=message,
            hint=hint,
            doc_url=doc_url,
            metadata=metadata,
            correlation_id=correlation_id,
        )
        self.__cause__ = cause
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "code": self.context.code.value,
            "message": self.context.message,
            "hint": self.context.hint,
            "doc_url": self.context.doc_url,
            "metadata": self.context.metadata,
            "correlation_id": self.context.correlation_id,
        }


# Specific error types
class ValidationError(FlowError):
    """Validation error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(code=ErrorCode.VALIDATION_ERROR, message=message, **kwargs)


class ResourceError(FlowError):
    """Resource-related error."""

    def __init__(self, code: ErrorCode, message: str, **kwargs):
        if not code.value.startswith("FLOW-2"):
            raise ValueError(f"Invalid resource error code: {code}")
        super().__init__(code=code, message=message, **kwargs)


class ProviderError(FlowError):
    """Provider-related error."""

    def __init__(self, code: ErrorCode, message: str, **kwargs):
        if not code.value.startswith("FLOW-3"):
            raise ValueError(f"Invalid provider error code: {code}")
        super().__init__(code=code, message=message, **kwargs)


class TaskError(FlowError):
    """Task-related error."""

    def __init__(self, code: ErrorCode, message: str, **kwargs):
        if not code.value.startswith("FLOW-4"):
            raise ValueError(f"Invalid task error code: {code}")
        super().__init__(code=code, message=message, **kwargs)


class NetworkError(FlowError):
    """Network-related error."""

    def __init__(self, code: ErrorCode, message: str, **kwargs):
        if not code.value.startswith("FLOW-5"):
            raise ValueError(f"Invalid network error code: {code}")
        super().__init__(code=code, message=message, **kwargs)


class StorageError(FlowError):
    """Storage-related error."""

    def __init__(self, code: ErrorCode, message: str, **kwargs):
        if not code.value.startswith("FLOW-6"):
            raise ValueError(f"Invalid storage error code: {code}")
        super().__init__(code=code, message=message, **kwargs)
