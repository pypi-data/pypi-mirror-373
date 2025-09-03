"""Additional utility exceptions for Flow SDK."""

from flow.errors import FlowError, NetworkError


class TunnelCreationError(NetworkError):
    """Failed to create tunnel to GPU instance."""

    pass


class NotFoundError(FlowError):
    """Resource not found error."""

    pass
