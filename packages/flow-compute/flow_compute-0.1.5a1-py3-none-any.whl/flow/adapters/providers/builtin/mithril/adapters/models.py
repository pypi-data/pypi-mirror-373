"""Adapter between Mithril and domain models.

This module handles all the impedance mismatch between Mithril's API
and our domain models, keeping both layers clean.
"""

import logging
from datetime import datetime

from flow.adapters.providers.builtin.mithril.adapters.storage import MithrilStorageMapper
from flow.adapters.providers.builtin.mithril.domain.models import (
    MithrilBid,
    MithrilInstance,
    MithrilVolume,
)
from flow.sdk.models import Instance, InstanceStatus, Task, TaskStatus, Volume

logger = logging.getLogger(__name__)


class MithrilAdapter:
    """Convert between Mithril models and domain models.

    This adapter handles all the messy conversions so that:
    1. The provider can work with Mithril-native models internally
    2. The public API can provide stable domain models
    3. Changes to either side don't affect the other
    """

    # Status mapping from Mithril to domain
    STATUS_MAP = {
        # Queueing/starting
        "pending": TaskStatus.PENDING,
        "open": TaskStatus.PENDING,
        "provisioning": TaskStatus.PENDING,
        # Active
        "allocated": TaskStatus.RUNNING,
        "running": TaskStatus.RUNNING,
        # Transitional
        "preempting": TaskStatus.PREEMPTING,
        "paused": TaskStatus.PAUSED,
        # Terminal
        "completed": TaskStatus.COMPLETED,
        "failed": TaskStatus.FAILED,
        # Mithril terminal statuses; tests expect COMPLETED at list-time for 'terminated'
        "terminated": TaskStatus.COMPLETED,
        "cancelled": TaskStatus.CANCELLED,
        "deactivated": TaskStatus.CANCELLED,
        "terminating": TaskStatus.CANCELLED,
        "replaced": TaskStatus.CANCELLED,
    }

    @classmethod
    def bid_to_task(
        cls,
        bid: MithrilBid,
        instances: list[MithrilInstance] | None = None,
        instance_type_name: str | None = None,
    ) -> Task:
        """Convert Mithril bid to domain Task model.

        Args:
            bid: Mithril bid model
            instances: Optional instance details for richer info
            instance_type_name: Human-readable instance type (e.g., "H100 80GB 8x")

        Returns:
            Domain Task model

        Note:
            This method handles all the impedance mismatch:
            - Mithril uses "bid" terminology, we use "task"
            - Mithril has "Allocated" status, we use "RUNNING"
            - Mithril uses dollar strings, we use floats
        """
        # Determine started time
        started_at = None
        if bid.status.lower() in ["allocated", "running"] and instances:
            # Use earliest instance creation time
            try:
                started_at = min(i.created_at for i in instances if i.created_at)
            except (ValueError, TypeError):
                # No valid creation times
                pass
        elif bid.status.lower() in ["allocated", "running"]:
            # Approximate with bid creation time
            started_at = bid.created_at

        # Determine completed time
        completed_at = None
        if bid.deactivated_at and bid.status.lower() in ["terminated", "cancelled", "deactivated"]:
            completed_at = bid.deactivated_at

        # Build status message
        message = cls._build_status_message(bid, instances)

        # Calculate costs
        price_per_hour = cls._parse_price(bid.limit_price)
        total_hours = cls._calculate_runtime_hours(bid.created_at, completed_at or datetime.now())

        # Map status
        task_status = cls.STATUS_MAP.get(bid.status.lower(), TaskStatus.PENDING)

        return Task(
            task_id=bid.fid,
            name=bid.name,
            status=task_status,
            created_at=bid.created_at,
            started_at=started_at,
            completed_at=completed_at,
            created_by=bid.created_by,
            # Use human-readable instance type if available, otherwise the ID
            instance_type=instance_type_name or bid.instance_type,
            num_instances=bid.instance_quantity,
            region=bid.region,
            # Extract instance IDs
            instances=[i.fid for i in instances] if instances else bid.instances,
            message=message,
            # Format cost per hour
            cost_per_hour=f"${price_per_hour:.2f}",
            # Calculate total cost if task has been running
            total_cost=(
                f"${price_per_hour * total_hours * bid.instance_quantity:.2f}"
                if completed_at or task_status == TaskStatus.RUNNING
                else None
            ),
        )

    # Instance status mapping from Mithril to domain
    INSTANCE_STATUS_MAP = {
        "provisioning": InstanceStatus.PENDING,
        "starting": InstanceStatus.PENDING,
        "running": InstanceStatus.RUNNING,
        "stopping": InstanceStatus.STOPPED,
        "stopped": InstanceStatus.STOPPED,
        "terminating": InstanceStatus.TERMINATED,
        "terminated": InstanceStatus.TERMINATED,
    }

    @classmethod
    def mithril_instance_to_instance(
        cls, mithril_instance: MithrilInstance, bid: MithrilBid
    ) -> Instance:
        """Convert Mithril instance to domain Instance model.

        Args:
            mithril_instance: Mithril instance model
            bid: Parent bid for context (SSH keys, etc.)

        Returns:
            Domain Instance model with connection details
        """
        # Extract SSH key from bid's launch specification
        ssh_keys = bid.launch_specification.get("ssh_keys", [])
        ssh_key_id = ssh_keys[0] if ssh_keys else None

        # Determine SSH host
        ssh_host = mithril_instance.ssh_host or mithril_instance.public_ip

        # Map instance status
        instance_status = cls.INSTANCE_STATUS_MAP.get(
            mithril_instance.status.lower(), InstanceStatus.PENDING
        )

        return Instance(
            instance_id=mithril_instance.fid,
            task_id=bid.fid,
            status=instance_status,
            ssh_host=ssh_host,
            private_ip=mithril_instance.private_ip,
            created_at=mithril_instance.created_at,
            terminated_at=mithril_instance.terminated_at,
        )

    @classmethod
    def mithril_volume_to_volume(cls, mithril_volume: MithrilVolume) -> Volume:
        """Convert Mithril volume to domain Volume model.

        Args:
            mithril_volume: Mithril volume model

        Returns:
            Domain Volume model
        """
        # Determine storage interface from Mithril data
        interface = MithrilStorageMapper.determine_interface(
            mount_path=mithril_volume.mount_path,
            # Prefer explicit disk interface from API if available
            device_type=None,
            volume_type=None,
            mithril_metadata={"disk_interface": getattr(mithril_volume, "disk_interface", None)},
        )

        # Volume model allows extra fields; include bid/reservation relationships when present
        return Volume(
            volume_id=mithril_volume.fid,
            name=mithril_volume.name,
            size_gb=mithril_volume.size_gb,
            region=mithril_volume.region,
            interface=interface,
            created_at=mithril_volume.created_at,
            attached_to=mithril_volume.attached_to,
            bids=getattr(mithril_volume, "bids", []),
            reservations=getattr(mithril_volume, "reservations", []),
            attachments_supported=getattr(mithril_volume, "attachments_supported", None),
        )

    @classmethod
    def _build_status_message(cls, bid: MithrilBid, instances: list[MithrilInstance] | None) -> str:
        """Build human-readable status message.

        Examples:
            - "Waiting for instance allocation"
            - "2/4 instances running"
            - "All instances terminated"
        """
        status_lower = bid.status.lower()

        if status_lower == "pending":
            return "Waiting for instance allocation"
        elif status_lower == "provisioning":
            return "Provisioning instances"
        elif status_lower == "paused":
            return "Instance paused - billing stopped, boot disk preserved"
        elif status_lower == "allocated" and instances:
            running = sum(1 for i in instances if i.status.lower() == "running")
            total = len(instances)
            if running == total:
                return f"All {total} instance{'s' if total > 1 else ''} running"
            else:
                return f"{running}/{total} instances running"
        elif status_lower == "failed":
            return "Failed to allocate instances"
        elif status_lower == "terminated":
            return "All instances terminated"
        elif status_lower == "cancelled":
            return "Bid cancelled by user"
        elif status_lower == "replaced":
            return "Bid replaced by newer bid"

        # Default message
        return f"Status: {bid.status}"

    @classmethod
    def _parse_price(cls, price_str: str) -> float:
        """Parse Mithril price string to float.

        Examples:
            "$12.00" -> 12.0
            "$0.50" -> 0.5
            "25.00" -> 25.0 (handle missing $)
            "$1,000.50" -> 1000.5 (handle comma separators)
        """
        if not price_str:
            return 0.0

        # Remove $ sign, commas, and any whitespace
        clean_price = price_str.strip().lstrip("$").replace(",", "").strip()

        try:
            return float(clean_price)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse price: {price_str}")
            return 0.0

    @classmethod
    def _calculate_runtime_hours(cls, start: datetime, end: datetime) -> float:
        """Calculate runtime in hours.

        Args:
            start: Start time
            end: End time

        Returns:
            Hours between start and end (minimum 0.0)
        """
        if not start or not end:
            return 0.0

        # Handle timezone-aware and naive datetimes
        if start.tzinfo is not None and end.tzinfo is None:
            # Make end timezone-aware using start's timezone
            from datetime import timezone

            end = end.replace(tzinfo=start.tzinfo or timezone.utc)
        elif start.tzinfo is None and end.tzinfo is not None:
            # Make start timezone-aware using end's timezone
            from datetime import timezone

            start = start.replace(tzinfo=end.tzinfo or timezone.utc)

        try:
            delta = end - start
            hours = delta.total_seconds() / 3600
            return max(0.0, hours)  # Never negative
        except Exception as e:
            logger.warning(f"Failed to calculate runtime hours: {e}")
            return 0.0
