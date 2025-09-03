"""Storage capability data for Mithril by region.

Small data module used by the provider facade to assemble
`ProviderCapabilities` without hardcoding in the provider.
"""

from __future__ import annotations

from typing import Any

# Hardcoded capabilities based on Mithril documentation
ALL_CAPABILITIES: dict[str, dict[str, Any]] = {
    "us-central2-a": {
        "types": ["block", "file"],
        "max_gb": 15360,  # 15TB
        "available": True,
    },
    "us-central1-b": {"types": ["block", "file"], "max_gb": 7168, "available": True},  # 7TB
    "eu-central1-a": {"types": ["block"], "max_gb": 15360, "available": True},  # 15TB
    "eu-central1-b": {"types": ["block"], "max_gb": 15360, "available": True},  # 15TB
}


def get_storage_capabilities(location: str | None = None) -> dict[str, Any] | None:
    if location:
        return {
            location: ALL_CAPABILITIES.get(location, {"types": [], "max_gb": 0, "available": False})
        }
    return ALL_CAPABILITIES


class StorageCapabilitiesChecker:
    """Compute storage capability summary for the current context.

    The checker reads the provider's configured/default region (when available)
    and returns a normalized capability structure suitable for meta.facets.
    """

    def __init__(self, ctx: Any) -> None:
        self._ctx = ctx

    def check_capabilities(self) -> dict[str, Any]:
        try:
            region = getattr(getattr(self._ctx, "mithril_config", None), "region", None)
        except Exception:
            region = None
        data = get_storage_capabilities(region)
        return data or {}
