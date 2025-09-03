"""Bid building component for the Mithril provider.

Provides a small, testable helper for constructing bid payloads.
"""

import logging
from dataclasses import dataclass
from typing import Any

from flow.domain.pricing.calculator import (
    calculate_instance_price,
    get_pricing_table,
)
from flow.errors import FlowError
from flow.resources import get_gpu_pricing as get_pricing_data
from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)


class BidValidationError(FlowError):
    """Error validating bid parameters."""

    pass


@dataclass
class BidSpecification:
    """Complete specification for a bid request."""

    # Required fields
    project_id: str
    region: str
    name: str
    instance_quantity: int
    limit_price: str  # Dollar string format (e.g., "$25.60")

    # Instance targeting - must have auction_id OR instance_type (not both)
    auction_id: str | None = None
    instance_type: str | None = None

    # Launch specification
    ssh_keys: list[str] = None
    startup_script: str = ""
    volumes: list[dict[str, Any]] = None

    def __post_init__(self):
        """Validate the specification after initialization."""
        self._validate()

        # Set defaults
        if self.ssh_keys is None:
            self.ssh_keys = []
        if self.volumes is None:
            self.volumes = []

    def _validate(self):
        """Validate bid specification.

        Raises:
            BidValidationError: If specification is invalid
        """
        # Required fields
        if not self.project_id:
            raise BidValidationError("project_id is required")
        if not self.region:
            raise BidValidationError("region is required")
        if not self.name:
            raise BidValidationError("name is required")
        if self.instance_quantity < 1:
            raise BidValidationError("instance_quantity must be at least 1")

        # Price validation
        if not self.limit_price or not self.limit_price.startswith("$"):
            raise BidValidationError("limit_price must be in dollar format (e.g., '$25.60')")

        # Instance targeting validation
        # For spot bids (with auction_id), instance_type is also required by the API
        if self.auction_id and not self.instance_type:
            raise BidValidationError(
                "When auction_id is provided, instance_type is also required for spot bids"
            )
        if not self.auction_id and not self.instance_type:
            raise BidValidationError(
                "Must specify instance_type (and optionally auction_id for spot instances)"
            )

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to Mithril API payload format.

        Returns:
            Dict ready for API submission
        """
        # Build launch specification
        # Extract volume IDs from volume attachment specs
        volume_ids = [vol["volume_id"] for vol in self.volumes] if self.volumes else []

        launch_spec = {
            "ssh_keys": self.ssh_keys,
            "startup_script": self.startup_script,
            "volumes": volume_ids,  # Mithril API expects list of volume IDs, not attachment specs
        }

        # Build base payload
        payload = {
            "project": self.project_id,
            "region": self.region,
            "name": self.name,
            "instance_quantity": self.instance_quantity,
            "limit_price": self.limit_price,
            "launch_specification": launch_spec,
        }

        # Add instance targeting
        payload["instance_type"] = self.instance_type
        if self.auction_id:
            payload["auction_id"] = self.auction_id

        return payload


class BidBuilder:
    """Builds bid specifications from task configurations using domain services."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def build_specification(
        config: TaskConfig,
        project_id: str,
        region: str,
        auction_id: str | None = None,
        instance_type_id: str | None = None,
        ssh_keys: list[str] | None = None,
        startup_script: str = "",
        volume_attachments: list[dict[str, Any]] | None = None,
    ) -> BidSpecification:
        """Build a bid specification from task config and resolved components.

        Args:
            config: Task configuration
            project_id: Resolved project ID
            region: Target region
            auction_id: Optional auction ID for spot instances
            instance_type_id: Optional instance type ID for on-demand
            ssh_keys: List of SSH key IDs
            startup_script: Complete startup script
            volume_attachments: Volume attachment specifications

        Returns:
            Complete BidSpecification

        Raises:
            BidValidationError: If parameters are invalid
        """
        # Determine limit price based on priority or explicit setting
        if config.max_price_per_hour is not None:
            limit_price = f"${config.max_price_per_hour:.2f}"
        else:
            # Derive from pricing.json tiers using instance_type, GPU count, and priority.
            # Fall back to a conservative cap only if derivation fails.
            try:
                prio = (getattr(config, "priority", None) or "med").lower()
                # Prefer the user-specified instance type from config (human-friendly, e.g., "8xa100")
                inst = getattr(config, "instance_type", None)
                # Merge defaults with resource-based overrides
                table = get_pricing_table(overrides=get_pricing_data().get("gpu_pricing", {}))
                derived = calculate_instance_price(inst or "", priority=prio, pricing_table=table)
                # Guard against non-positive / None results
                if not isinstance(derived, (int, float)) or derived <= 0:
                    raise ValueError("Derived price invalid")
                limit_price = f"${float(derived):.2f}"
            except Exception:
                # Final safeguard: conservative default
                limit_price = "$100.00"

        # Basic validation
        if not project_id:
            raise BidValidationError("project_id is required")
        if not region:
            raise BidValidationError("region is required")
        if not config.name:
            raise BidValidationError("Task name is required")
        if not isinstance(config.num_instances, int) or config.num_instances < 1:
            raise BidValidationError("num_instances must be >= 1")
        if not limit_price.startswith("$"):
            raise BidValidationError("limit_price must be in dollar format (e.g., '$25.60')")
        if auction_id and not instance_type_id:
            raise BidValidationError("When auction_id is provided, instance_type is also required")
        if not auction_id and not instance_type_id:
            raise BidValidationError("Must specify instance_type (and optionally auction_id)")

        return BidSpecification(
            project_id=project_id,
            region=region,
            name=config.name,
            instance_quantity=config.num_instances,
            limit_price=limit_price,
            auction_id=auction_id,
            instance_type=instance_type_id,
            ssh_keys=ssh_keys or [],
            startup_script=startup_script,
            volumes=volume_attachments or [],
        )

    @staticmethod
    def format_volume_attachment(
        volume_id: str, mount_path: str, mode: str = "rw"
    ) -> dict[str, Any]:
        """Format a volume attachment specification.

        Args:
            volume_id: ID of the volume to attach
            mount_path: Path to mount the volume
            mode: Access mode (rw or ro)

        Returns:
            Volume attachment dict
        """
        return {
            "volume_id": volume_id,
            "mount_path": mount_path,
            "mode": mode,
        }
