"""Centralized links for web, docs, and status URLs.

All downstream code should import from this module instead of hard-coding
URLs. Base hosts are configurable via environment variables.

This module intentionally avoids importing provider adapter constants to keep
utils provider-agnostic. Defaults mirror the Mithril provider values.
"""

from __future__ import annotations

import os
from typing import Final

# Read base URLs from environment, falling back to Mithril defaults
MITHRIL_WEB_BASE_URL = os.getenv("MITHRIL_WEB_URL", "https://app.mithril.ai")
MITHRIL_DOCS_URL = os.getenv("MITHRIL_DOCS_URL", "https://docs.mithril.ai")
MITHRIL_STATUS_URL = os.getenv("MITHRIL_STATUS_URL", "https://status.mithril.ai")
MITHRIL_MARKETING_URL = os.getenv("MITHRIL_MARKETING_URL", "https://mithril.ai")


def _join(base: str, *parts: str) -> str:
    base = (base or "").rstrip("/")
    path = "/".join(p.strip("/") for p in parts if p)
    return f"{base}/{path}" if path else base


class WebLinks:
    """Dashboard/console links under the Mithril web app."""

    @staticmethod
    def root() -> str:
        return MITHRIL_WEB_BASE_URL

    @staticmethod
    def api_keys() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "account", "apikeys")

    @staticmethod
    def ssh_keys() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "account", "ssh-keys")

    @staticmethod
    def billing_settings() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "settings", "billing")

    @staticmethod
    def projects_settings() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "settings", "projects")

    @staticmethod
    def instances() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "instances")

    @staticmethod
    def instances_spot() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "instances", "spot")

    @staticmethod
    def price_chart() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "price-chart")

    @staticmethod
    def quotas_instances() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "instances", "quotas")

    @staticmethod
    def quotas_storage() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "storage", "quotas")


class DocsLinks:
    """Documentation links."""

    @staticmethod
    def root() -> str:
        return MITHRIL_DOCS_URL

    @staticmethod
    def compute_quickstart() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "compute-quickstart")

    @staticmethod
    def startup_scripts() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "startup-scripts")

    @staticmethod
    def regions() -> str:
        # Some deployments may not host a dedicated regions page; prefer instance types/specs
        return _join(
            MITHRIL_DOCS_URL,
            "compute-and-storage",
            "instance-types-and-specifications",
        )

    @staticmethod
    def instance_types_and_specs() -> str:
        return _join(
            MITHRIL_DOCS_URL,
            "compute-and-storage",
            "instance-types-and-specifications",
        )

    @staticmethod
    def spot_auction_mechanics() -> str:
        return _join(
            MITHRIL_DOCS_URL,
            "compute-and-storage",
            "spot-bids",
            "spot-auction-mechanics",
        )

    @staticmethod
    def spot_bids() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "spot-bids")

    @staticmethod
    def compute_api_reference() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-api", "compute-api-reference")

    @staticmethod
    def compute_api_overview() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-api", "api-overview-and-quickstart")

    @staticmethod
    def ephemeral_storage() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "ephemeral-storage")

    @staticmethod
    def persistent_storage() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "persistent-storage")


class MarketingLinks:
    """Public marketing site links (e.g., pricing)."""

    @staticmethod
    def pricing() -> str:
        return _join(MITHRIL_MARKETING_URL, "pricing")


def status_page() -> str:
    """Service status page."""
    return MITHRIL_STATUS_URL


# Back-compat short aliases
web: Final[type[WebLinks]] = WebLinks
docs: Final[type[DocsLinks]] = DocsLinks
