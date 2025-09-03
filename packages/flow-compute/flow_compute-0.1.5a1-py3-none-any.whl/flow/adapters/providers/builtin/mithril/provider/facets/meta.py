"""Meta facet - handles metadata operations like users, projects, SSH keys, etc."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from flow.sdk.models import User

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class MetaFacet:
    """Handles metadata operations - users, projects, instance types, SSH keys, etc."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize meta facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx

    # ========== User Operations ==========

    def get_user(self, user_id: str) -> User:
        """Get user information.

        Args:
            user_id: User ID

        Returns:
            User object
        """
        # Check cache first
        if hasattr(self.ctx, "_user_cache"):
            cached = self.ctx._user_cache.get(user_id)
            if cached:
                return cached

        # Fetch from API
        user = self.ctx.users.get_user(user_id)

        # Cache the result
        if hasattr(self.ctx, "_user_cache"):
            self.ctx._user_cache.set(user_id, user)

        return user

    def get_user_teammates(self, user_id: str) -> Any:
        """Get teammates for a user.

        Args:
            user_id: User ID

        Returns:
            Teammates information
        """
        return self.ctx.users.get_teammates(user_id)

    # ========== Project Operations ==========

    def get_projects(self) -> list[dict[str, Any]]:
        """Get list of projects.

        Returns:
            List of project dictionaries
        """
        try:
            response = self.ctx.api.list_projects()
            if isinstance(response, dict):
                return response.get("data", response.get("projects", []))
            return response if isinstance(response, list) else []
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []

    def get_current_project(self) -> dict[str, Any]:
        """Get current project information.

        Returns:
            Current project dictionary
        """
        project_id = self.ctx.get_project_id()
        return {"id": project_id, "name": project_id}

    # ========== Instance Type Operations ==========

    def get_instance_types(self, region: str | None = None) -> list[dict[str, Any]]:
        """Get available instance types.

        Args:
            region: Optional region filter

        Returns:
            List of instance type dictionaries
        """
        try:
            params = {}
            if region:
                params["region"] = region

            response = self.ctx.api.list_instance_types(params)

            if isinstance(response, dict):
                return response.get("data", response.get("instance_types", []))
            return response if isinstance(response, list) else []
        except Exception as e:
            logger.error(f"Failed to get instance types: {e}")
            return []

    def resolve_instance_type(self, user_spec: str) -> str:
        """Resolve user-friendly instance spec to provider ID.

        Args:
            user_spec: User input like "a100", "4xa100", etc.

        Returns:
            Provider-specific instance type ID
        """
        return self.ctx.resolve_instance_type(user_spec)

    # ========== SSH Key Operations ==========

    def get_ssh_keys(self) -> list[dict[str, Any]]:
        """Get SSH keys for the project.

        Returns:
            List of SSH key dictionaries
        """
        try:
            keys = self.ctx.ssh_key_mgr.list_keys()
            return [
                {
                    "id": k.fid,
                    "name": k.name,
                    "public_key": k.public_key,
                    "required": getattr(k, "required", False),
                }
                for k in keys
            ]
        except Exception as e:
            logger.error(f"Failed to get SSH keys: {e}")
            return []

    def create_ssh_key(self, name: str, public_key: str) -> dict[str, Any]:
        """Create a new SSH key.

        Args:
            name: Key name
            public_key: Public key content

        Returns:
            Created SSH key dictionary
        """
        key_id = self.ctx.ssh_key_mgr.create_key(name, public_key)
        return {
            "id": key_id,
            "name": name,
            "public_key": public_key,
        }

    def delete_ssh_key(self, key_id: str) -> bool:
        """Delete an SSH key.

        Args:
            key_id: SSH key ID

        Returns:
            True if deletion successful
        """
        try:
            return self.ctx.ssh_key_mgr.delete_key(key_id)
        except Exception as e:
            logger.error(f"Failed to delete SSH key {key_id}: {e}")
            return False

    # ========== Capabilities ==========

    def get_capabilities(self) -> dict[str, Any]:
        """Get provider capabilities.

        Returns:
            Dictionary of provider capabilities
        """
        try:
            from flow.adapters.providers.builtin.mithril.domain.storage_capabilities import (
                StorageCapabilitiesChecker,
            )

            checker = StorageCapabilitiesChecker(self.ctx)  # type: ignore[arg-type]
            storage_caps = checker.check_capabilities()

            return {
                "provider": "mithril",
                "features": {
                    "multi_node": True,
                    "spot_instances": True,
                    "reservations": True,
                    "volumes": True,
                    "ssh_access": True,
                    "log_streaming": True,
                    "file_transfer": True,
                },
                "storage": storage_caps,
                "regions": self._get_available_regions(),
            }
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            return {
                "provider": "mithril",
                "features": {
                    "multi_node": True,
                    "spot_instances": True,
                    "reservations": True,
                    "volumes": True,
                    "ssh_access": True,
                    "log_streaming": True,
                    "file_transfer": True,
                },
            }

    # ========== Pricing/Regions Helpers (provider-agnostic surface) ==========
    def get_region_gpu_families(self, region: str) -> list[str]:
        """Return GPU families available in a given region (best-effort).

        Uses spot availability as a proxy for supply. Families currently probed:
        H100 and A100 using canonical instance IDs from constants. Returns a
        stable, user-facing order: H100, A100, then others.
        """
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import (
                INSTANCE_TYPE_MAPPINGS,
            )
            from flow.adapters.providers.builtin.mithril.domain.pricing import PricingService
            from flow.adapters.providers.builtin.mithril.domain.region import RegionSelector

            # Canonical representatives to probe per family
            fam_to_id: dict[str, str] = {}
            # Prefer explicit keys if present
            for key in ("h100", "8xh100"):
                if key in INSTANCE_TYPE_MAPPINGS:
                    fam_to_id["h100"] = INSTANCE_TYPE_MAPPINGS[key]
                    break
            for key in ("1xa100", "a100", "a100-80gb.sxm.1x"):
                if key in INSTANCE_TYPE_MAPPINGS:
                    fam_to_id["a100"] = INSTANCE_TYPE_MAPPINGS[key]
                    break

            selector = RegionSelector(self.ctx.api, PricingService(self.ctx.api))
            families: list[str] = []
            for fam, it_id in fam_to_id.items():
                try:
                    avail = selector.check_availability(it_id)
                    if region in avail:
                        families.append(fam)
                except Exception:
                    continue
            # Stable, readable order
            families = sorted(list(set(families)), key=lambda f: {"h100": 0, "a100": 1}.get(f, 10))
            return families
        except Exception:
            return []

    def get_region_price_samples(self, instance_spec_or_id: str) -> dict[str, float]:
        """Return a mapping of region -> current spot price for the instance.

        Args:
            instance_spec_or_id: Mithril instance type ID (it_...) or a user spec like 'a100', '8xh100'

        Returns:
            Dict of region -> price (float USD). Empty dict on failure.
        """
        try:
            # Resolve to an instance type ID if needed
            spec = str(instance_spec_or_id or "")
            if spec.startswith("it_"):
                it_id = spec
            else:
                it_id = self.ctx.resolve_instance_type(spec)

            from flow.adapters.providers.builtin.mithril.domain.pricing import PricingService
            from flow.adapters.providers.builtin.mithril.domain.region import RegionSelector

            selector = RegionSelector(self.ctx.api, PricingService(self.ctx.api))
            availability = selector.check_availability(it_id)
            prices: dict[str, float] = {}
            for region, auction in availability.items():
                try:
                    prices[region] = selector._pricing.parse_price(auction.last_instance_price)  # type: ignore[attr-defined]
                except Exception:
                    continue
            return prices
        except Exception:
            return {}

    def _get_available_regions(self) -> list[str]:
        """Return Mithril regions with a provider-accurate fallback.

        The previous implementation attempted to call a non-existent API client method
        (list_regions), which always raised and sometimes leaked AWS-style regions
        into the UX. Use the canonical constants instead.
        """
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import VALID_REGIONS

            return list(VALID_REGIONS)
        except Exception:
            # Final safety net: conservative known-good defaults for Mithril
            return ["us-central1-b", "us-central2-a", "eu-central1-a", "eu-central1-b"]
