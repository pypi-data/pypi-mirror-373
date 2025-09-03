"""Mithril provider-specific errors with proper hierarchy.

This module defines a clean error hierarchy for Mithril operations,
providing specific error types for different failure scenarios.
"""

from flow.errors import FlowError


class MithrilError(FlowError):
    """Base error for all Mithril provider operations."""

    pass


class MithrilAPIError(MithrilError):
    """Error communicating with Mithril API."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        request_id: str | None = None,
        suggestions: list[str] | None = None,
    ):
        super().__init__(message, suggestions=suggestions)
        self.status_code = status_code
        self.response_body = response_body
        self.request_id = request_id


class MithrilAuthenticationError(MithrilAPIError):
    """Authentication failed with Mithril API."""

    pass


class MithrilResourceNotFoundError(MithrilAPIError):
    """Requested resource not found in Mithril."""

    pass


class MithrilQuotaExceededError(MithrilAPIError):
    """Quota or limit exceeded in Mithril."""

    pass


class MithrilValidationError(MithrilError):
    """Invalid parameters provided to Mithril operation."""

    pass


class MithrilTimeoutError(MithrilError):
    """Operation timed out."""

    pass


class MithrilInstanceError(MithrilError):
    """Error related to instance operations."""

    pass


class MithrilBidError(MithrilError):
    """Error related to bid operations."""

    pass


class MithrilVolumeError(MithrilError):
    """Error related to volume operations."""

    pass
