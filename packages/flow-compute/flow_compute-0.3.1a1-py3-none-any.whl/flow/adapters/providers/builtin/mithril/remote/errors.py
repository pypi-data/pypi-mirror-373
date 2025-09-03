from __future__ import annotations

from flow.errors import FlowError


class RemoteExecutionError(FlowError):
    """Raised when remote command execution fails."""

    pass


class TaskNotFoundError(FlowError):
    """Raised when task cannot be found."""

    pass


class SshConnectionError(RemoteExecutionError):
    """Specific error for SSH connection/setup issues."""

    pass


def make_error(
    message: str,
    request_id: str,
    suggestions: list | None = None,
    cls: type[RemoteExecutionError] = RemoteExecutionError,
) -> RemoteExecutionError:
    """Create a FlowError-derived error object with an attached request ID.

    Attaches the correlation ID to the exception object for CLI surfacing.
    """
    err = cls(message, suggestions=suggestions)  # type: ignore[arg-type]
    try:
        err.request_id = request_id
    except Exception:
        pass
    return err
