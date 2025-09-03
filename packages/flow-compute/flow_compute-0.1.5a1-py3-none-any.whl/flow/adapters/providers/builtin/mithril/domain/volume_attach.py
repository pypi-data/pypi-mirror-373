"""Volume attach/mount orchestration for Mithril.

Extracts the provider's mount_volume flow into a reusable service that
handles validation, bid state transitions, bid volume updates, and
optional SSH mounting when the instance is ready.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from flow.adapters.providers.builtin.mithril.core.errors import MithrilAPIError
from flow.adapters.providers.builtin.mithril.domain.bids import BidsService
from flow.adapters.providers.builtin.mithril.domain.volumes import VolumeService
from flow.adapters.providers.builtin.mithril.volume_operations import VolumeOperations
from flow.errors import ResourceNotFoundError, TaskNotFoundError, ValidationError
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class VolumeAttachService:
    def __init__(
        self,
        api_client: Any,
        volumes: VolumeService,
        bids: BidsService,
        *,
        get_project_id: Callable[[], str],
        get_task_by_id: Callable[[str], Task],
        make_remote_ops: Callable[[], Any],
        is_instance_ssh_ready: Callable[[Task], bool],
    ) -> None:
        self._api = api_client
        self._volumes = volumes
        self._bids = bids
        self._get_project_id = get_project_id
        self._get_task = get_task_by_id
        self._make_remote_ops = make_remote_ops
        self._is_instance_ssh_ready = is_instance_ssh_ready

    def _resolve_volume_id(self, identifier: str) -> str:
        """Resolve a volume identifier (ID or name/partial name) to an ID."""
        if identifier.startswith("vol_"):
            return identifier
        volumes = self._volumes.list_volumes(
            project_id=self._get_project_id(), region=None, limit=1000
        )
        matches = [v for v in volumes if v.name == identifier]
        if len(matches) == 1:
            return matches[0].id
        if len(matches) > 1:
            raise ValidationError(
                f"Multiple volumes found with name '{identifier}'. Please use the volume ID instead."
            )
        # Try partial match
        partial = [v for v in volumes if v.name and identifier.lower() in v.name.lower()]
        if len(partial) == 1:
            return partial[0].id
        raise ResourceNotFoundError(f"Volume '{identifier}' not found")

    def mount_volume(
        self, volume_identifier: str, task_id: str, mount_point: str | None = None
    ) -> None:
        """Attach a volume to a bid and mount it if possible.

        Performs validations, updates the bid's volumes (pause/update/unpause),
        and attempts a best-effort SSH mount when the instance is ready.
        """
        # Resolve entities
        resolved_volume_id = self._resolve_volume_id(volume_identifier)
        # Fetch volume details via listing (provider has no get_volume)
        volumes_list = self._volumes.list_volumes(
            project_id=self._get_project_id(), region=None, limit=1000
        )
        volume = next(
            (
                v
                for v in volumes_list
                if getattr(v, "id", None) == resolved_volume_id
                or getattr(v, "volume_id", None) == resolved_volume_id
            ),
            None,
        )
        if volume is None:
            raise ResourceNotFoundError(f"Volume '{resolved_volume_id}' not found")
        task = self._get_task(task_id)

        # Validate region match
        if volume.region != task.region:
            raise ValidationError(
                "Cannot mount volume to task across regions.\n\n"
                f"  - Volume region: {volume.region}\n"
                f"  - Task region: {task.region}\n"
                "Volumes must be in the same region as tasks.\n\n"
                "Solutions:\n"
                f"  1. Create a new volume in {task.region}:\n"
                f"     flow create-volume --size {volume.size_gb} --name {volume.name}-{task.region} --region {task.region}\n"
                f"  2. Use a different volume in {task.region}:\n"
                f"     flow volumes get | grep {task.region}"
            )

        # Validate multi-node restrictions for block volumes
        if len(task.instances) > 1:
            if hasattr(volume, "interface") and str(volume.interface).lower() == "file":
                logger.info(
                    f"File share volume {volume.id} can be mounted to all {len(task.instances)} instances"
                )
            else:
                raise ValidationError(
                    "Cannot mount block volume to multi-instance task:\n"
                    f"  - Task '{task.name or task.task_id}' has {len(task.instances)} instances\n"
                    "  - Block volumes can only be attached to one instance at a time\n\n"
                    "Solutions:\n"
                    "  1. Use a file share volume instead (supports multi-instance access; region/quota dependent)\n"
                    "  2. Mount to a single-instance task\n"
                    "  3. For read-only datasets, prefer data_mounts (e.g., s3://...) shared across nodes\n"
                    "  4. Use Mithril's upcoming instance-specific mount feature (not yet available)"
                )

        # Fetch current bid (for current volumes)
        project_id = self._get_project_id()
        response = self._api.list_bids({"project": project_id})
        bids = response if isinstance(response, list) else response.get("data", [])
        bid = next((b for b in bids if b.get("fid") == task_id), None)
        if not bid:
            raise TaskNotFoundError(f"Task {task_id} not found")

        # Build new volumes list and mount path
        launch_spec = bid.get("launch_specification", {})
        current_volumes = launch_spec.get("volumes", [])

        # Compute target index and updated list with idempotency
        if resolved_volume_id in current_volumes:
            volume_index = current_volumes.index(resolved_volume_id)
            updated_volumes = current_volumes  # no-op update
        else:
            volume_index = len(current_volumes)
            updated_volumes = current_volumes + [resolved_volume_id]

        # Compute a readable default mount path (stable) for user guidance
        if mount_point:
            mount_path = mount_point
        else:
            try:
                from flow.utils.paths import default_volume_mount_path as _default_mount

                mount_path = _default_mount(name=getattr(volume, "name", None), volume_id=volume.id)
            except Exception:
                # Fallback if helper is unavailable
                try:
                    next_device_letter = VolumeOperations.get_device_letter_from_volumes(
                        current_volumes
                    )
                except ValueError as e:
                    raise ValidationError(
                        f"Exceeded maximum number of attachable block volumes for this instance: {e}"
                    )
                mount_path = f"/volumes/{volume.name or f'volume-{next_device_letter}'}"

        # Pause → update volumes → unpause with idempotency; fallback to live update when supported
        try:
            # Only patch the bid when we are actually adding a new volume
            if updated_volumes is not current_volumes:
                try:
                    self._bids.pause_bid(task_id)
                    # Use robust helper that tries nested and top-level shapes
                    self._bids.update_bid_volumes(task_id, updated_volumes)
                    self._bids.unpause_bid(task_id)
                except Exception as e:
                    # Attempt best-effort live update without pausing (API revision dependent)
                    try:
                        # Try updating without pause (some APIs support live updates)
                        self._bids.update_bid_volumes(task_id, updated_volumes)
                        logger.debug("Updated volumes without pausing (API supported live updates)")
                    except Exception:
                        self._bids.safe_unpause_bid(task_id)
                        if "already paused" in str(e).lower():
                            raise MithrilAPIError(
                                "Failed to update volumes: Bid state conflict. The bid may be in transition. Please try again in a few seconds."
                            ) from e
                        raise MithrilAPIError(f"Failed to update bid volumes: {e}") from e
        except Exception as e:
            self._bids.safe_unpause_bid(task_id)
            if "already paused" in str(e).lower():
                raise MithrilAPIError(
                    "Failed to update volumes: Bid state conflict. The bid may be in transition. Please try again in a few seconds."
                ) from e
            raise MithrilAPIError(f"Failed to update bid volumes: {e}") from e

        # Decide if we can attempt an immediate mount
        task_status = str(bid.get("status", "")).lower()
        if task_status not in ["allocated", "running"] or not self._is_instance_ssh_ready(task):
            logger.info(
                f"Volume {volume.name or volume.id} attached to task {task.name or task.task_id}. "
                f"Mount will complete when instance is ready."
            )
            return

        # Attempt SSH mount
        try:
            remote_ops = self._make_remote_ops()
            is_file_share = hasattr(volume, "interface") and str(volume.interface).lower() == "file"
            mount_script = VolumeOperations.generate_mount_script(
                volume_index=volume_index,
                mount_path=mount_path,
                volume_id=volume.id if is_file_share else None,
                format_if_needed=True,
                add_to_fstab=False,
                is_file_share=is_file_share,
            )
            mount_cmd = f"sudo bash -c '{mount_script}'"
            remote_ops.execute_command(task_id, mount_cmd, timeout=30)

            # Verify mount
            verify_cmd = f"mountpoint -q {mount_path} && echo MOUNTED || echo FAILED"
            result = remote_ops.execute_command(task_id, verify_cmd, timeout=10)
            if "FAILED" in result:
                logger.warning(
                    f"Mount command executed but volume not mounted at {mount_path}. "
                    f"Volume is attached and will be available on next reboot."
                )
            else:
                logger.debug(
                    f"Successfully mounted and verified volume {volume.name or volume.id} at {mount_path}"
                )
        except Exception as e:
            error_msg = str(e).lower()
            if any(k in error_msg for k in ("ssh", "not responding", "connection")):
                logger.info(
                    f"Volume attached successfully. SSH mount deferred: {e}. "
                    f"Volume will be available at {mount_path} when instance is ready."
                )
                return
            logger.warning(
                f"Volume attached but mount failed: {e}. "
                f"Manual mount may be required at {mount_path}"
            )
            return
