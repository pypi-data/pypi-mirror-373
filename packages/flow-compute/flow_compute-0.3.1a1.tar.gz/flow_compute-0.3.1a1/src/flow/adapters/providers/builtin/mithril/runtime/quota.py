"""Quota-aware instance selection for the Mithril provider.

Implements basic quota checks that fail fast with clear errors and offer
suggested alternatives.
"""

from dataclasses import dataclass


@dataclass
class QuotaInfo:
    """Simple quota information."""

    instance_type: str
    available: int
    total: int

    @property
    def is_available(self) -> bool:
        return self.available > 0


class QuotaChecker:
    """Check quota and suggest alternatives."""

    # Instance type aliases and their actual Mithril names
    INSTANCE_ALIASES = {
        "h100": "8x NVIDIA H100 80GB SXM5",
        "h100-pcie": "8x NVIDIA H100 80GB PCIe",
        "a100": "1x NVIDIA A100 80GB SXM4",
        "8xa100": "8x NVIDIA A100 80GB SXM4",
    }

    @staticmethod
    def check_quota_url() -> str:
        """Return the quota check URL."""
        from flow.utils.links import WebLinks

        return WebLinks.quotas_instances()

    @staticmethod
    def format_quota_error(requested: str, suggestion: str | None = None) -> str:
        """Format a clear quota error message."""
        msg = f"No quota available for {requested}"
        if suggestion:
            msg += f". Try: {suggestion}"
        msg += f"\nCheck quota: {QuotaChecker.check_quota_url()}"
        return msg
