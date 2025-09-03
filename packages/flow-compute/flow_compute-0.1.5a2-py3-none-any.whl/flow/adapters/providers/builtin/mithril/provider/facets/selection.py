"""Selection facet - handles region and instance selection logic."""

from __future__ import annotations

import logging
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from flow.protocols.selection import SelectionOutcome
from flow.sdk.models import TaskConfig

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class SelectionFacet:
    """Handles region and instance selection logic."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize selection facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx

    def select_region_and_instance(
        self, *, adjusted_config: TaskConfig, instance_type: str, instance_fid: str
    ) -> SelectionOutcome:
        """Select optimal region and instance for task.

        Tries bid-based selection first, falls back to availability-based.

        Args:
            adjusted_config: Adjusted task configuration
            instance_type: User-friendly instance type
            instance_fid: Resolved instance type FID

        Returns:
            SelectionOutcome with region, auction, and metadata
        """
        # Try bids-based selection first
        with suppress(Exception):
            region, instance_type_id, auction = self.ctx.bids.select_region_and_instance(
                adjusted_config, instance_type
            )
            if region:
                logger.debug(f"Selected region {region} via bids service")
                return SelectionOutcome(
                    region=region,
                    auction=auction,
                    instance_type_id=instance_type_id,
                    candidate_regions=[region],
                    source="bids",
                )

        # Fallback to availability-based selection
        logger.debug("Falling back to availability-based region selection")
        availability = self.ctx.region.check_availability(instance_fid)
        region = self.ctx.region.select_best_region(availability, adjusted_config.region)
        candidates = list(availability.keys()) if availability else []
        auction = availability[region] if region and availability else None
        instance_type_id = instance_fid if region else None

        return SelectionOutcome(
            region=region,
            auction=auction,
            instance_type_id=instance_type_id,
            candidate_regions=candidates,
            source="availability",
        )

    def normalize_instance_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> dict[str, Any]:
        """Normalize GPU request to standard format.

        Args:
            gpu_count: Number of GPUs requested
            gpu_type: Optional GPU type (e.g., "a100", "h100")

        Returns:
            Normalized request dictionary
        """
        request = {"gpu_count": gpu_count}

        if gpu_type:
            # Normalize GPU type
            gpu_type_lower = gpu_type.lower()

            # Map common aliases
            gpu_aliases = {
                "a100": "a100",
                "a100-80": "a100.80gb",
                "a100-40": "a100.40gb",
                "h100": "h100",
                "h100-80": "h100.80gb",
                "a6000": "a6000",
                "a40": "a40",
                "l40": "l40",
                "l40s": "l40s",
            }

            normalized_type = gpu_aliases.get(gpu_type_lower, gpu_type)
            request["gpu_type"] = normalized_type

            # Build instance type string
            if gpu_count == 1:
                request["instance_type"] = normalized_type
            else:
                request["instance_type"] = f"{gpu_count}x{normalized_type}"

        return request

    def apply_instance_constraints(self, config: TaskConfig, instance_type: str) -> TaskConfig:
        """Apply provider-specific constraints based on instance type.

        Args:
            config: Original task configuration
            instance_type: Selected instance type

        Returns:
            Adjusted configuration with constraints applied
        """
        adjusted = config.model_copy()

        # High-end GPU constraints
        if any(gpu in instance_type.lower() for gpu in ["a100", "h100", "a6000"]):
            if not adjusted.memory:
                adjusted.memory = "32Gi"
            if not adjusted.disk:
                adjusted.disk = "100Gi"

        # Multi-GPU constraints
        if "8x" in instance_type:
            if not adjusted.cpu:
                adjusted.cpu = "32"
            if not adjusted.memory:
                adjusted.memory = "64Gi"
        elif "4x" in instance_type:
            if not adjusted.cpu:
                adjusted.cpu = "16"
            if not adjusted.memory:
                adjusted.memory = "32Gi"

        # Apply minimum requirements
        if adjusted.memory:
            # Ensure memory is in valid format
            if not any(adjusted.memory.endswith(suffix) for suffix in ["Mi", "Gi", "Ti"]):
                adjusted.memory = f"{adjusted.memory}Gi"

        if adjusted.disk:
            # Ensure disk is in valid format
            if not any(adjusted.disk.endswith(suffix) for suffix in ["Mi", "Gi", "Ti"]):
                adjusted.disk = f"{adjusted.disk}Gi"

        return adjusted
