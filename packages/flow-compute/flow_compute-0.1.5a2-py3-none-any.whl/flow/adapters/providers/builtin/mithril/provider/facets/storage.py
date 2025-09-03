"""Storage facet - handles volume and file transfer operations."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.adapters.providers.builtin.mithril.core.constants import DEFAULT_REGION, VOLUME_ID_PREFIX
from flow.errors import ValidationError
from flow.sdk.models import TaskConfig, Volume

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class StorageFacet:
    """Handles storage operations - volumes and file transfers."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize storage facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx

    # ========== Volume Operations ==========

    @handle_mithril_errors("Create volume")
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Volume:
        """Create a new volume.

        Args:
            size_gb: Size of volume in GB
            name: Optional volume name
            interface: Volume interface type ("block" or "file")
            region: Region to create volume in

        Returns:
            Created volume
        """
        return self.ctx.volumes.create_volume(
            project_id=self.ctx.get_project_id(),
            size_gb=size_gb,
            name=name,
            interface=interface,
            region=region or self.ctx.mithril_config.region or DEFAULT_REGION,
        )

    def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume.

        Args:
            volume_id: Volume ID to delete

        Returns:
            True if deletion successful
        """
        try:
            return self.ctx.volumes.delete_volume(volume_id)
        except Exception as e:
            logger.error(f"Failed to delete volume {volume_id}: {e}")
            return False

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List volumes in the project.

        Args:
            limit: Maximum number of volumes to return

        Returns:
            List of volumes
        """
        return self.ctx.volumes.list_volumes(
            project_id=self.ctx.get_project_id(), region=None, limit=limit
        )

    def mount_volume(self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume") -> bool:
        """Mount a volume to a running task.

        Args:
            task_id: Task to mount volume to
            volume_id: Volume to mount
            mount_path: Path to mount volume at

        Returns:
            True if mount successful
        """
        try:
            # VolumeAttachService API uses (volume_identifier, task_id, mount_point)
            self.ctx.volume_attach.mount_volume(
                volume_identifier=volume_id, task_id=task_id, mount_point=mount_path
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mount volume {volume_id} to task {task_id}: {e}")
            return False

    def is_volume_id(self, identifier: str) -> bool:
        """Check if a string is a volume ID.

        Args:
            identifier: String to check

        Returns:
            True if identifier is a volume ID
        """
        return identifier.startswith(VOLUME_ID_PREFIX)

    def prepare_volume_attachments(
        self, volume_ids: list[str] | None, config: TaskConfig
    ) -> list[dict[str, Any]]:
        """Prepare volume attachment specifications.

        Args:
            volume_ids: List of volume IDs to attach
            config: Task configuration with volume details

        Returns:
            List of volume attachment specifications
        """
        if not volume_ids:
            return []

        # Resolve volume names to IDs
        resolved: list[str] = []
        all_vols = self.list_volumes()

        for ident in volume_ids:
            # Direct ID
            if self.is_volume_id(ident):
                resolved.append(ident)
                continue

            # Try exact name match
            matches = [v for v in all_vols if v.name == ident]
            if len(matches) == 1:
                resolved.append(matches[0].id)
            elif len(matches) > 1:
                raise ValidationError(f"Multiple volumes named '{ident}'. Use the volume ID.")
            else:
                # Try partial match
                partial = [v for v in all_vols if v.name and ident.lower() in v.name.lower()]
                if len(partial) == 1:
                    resolved.append(partial[0].id)
                else:
                    raise ValidationError(f"No volume found matching '{ident}'.")

        # Build attachment specifications
        from flow.adapters.providers.builtin.mithril.bidding.builder import BidBuilder

        attachments = []

        for i, vid in enumerate(resolved):
            # Determine mount path
            if i < len(config.volumes) and hasattr(config.volumes[i], "mount_path"):
                mount_path = config.volumes[i].mount_path
            else:
                from flow.utils.paths import default_volume_mount_path

                name = getattr(config.volumes[i], "name", None) if i < len(config.volumes) else None
                mount_path = default_volume_mount_path(name=name, volume_id=vid)

            attachments.append(
                BidBuilder.format_volume_attachment(volume_id=vid, mount_path=mount_path, mode="rw")
            )

        return attachments

    # ========== File Transfer Operations ==========

    def upload_file(self, task_id: str, local_path: Path, remote_path: str = "~") -> bool:
        """Upload a file to a task.

        Args:
            task_id: Task to upload to
            local_path: Local file path
            remote_path: Remote destination path

        Returns:
            True if upload successful
        """
        try:
            import os as _os

            from flow.adapters.transport.code_transfer import (
                CodeTransferConfig,
                CodeTransferManager,
            )

            task = self.ctx.task_service.get_task(task_id)
            # Determine target directory from remote path
            target_dir = remote_path
            try:
                if remote_path and not remote_path.endswith("/"):
                    target_dir = _os.path.dirname(remote_path) or "~"
            except Exception:
                target_dir = "~"

            cfg = CodeTransferConfig(source_dir=local_path.parent, target_dir=target_dir)
            CodeTransferManager(provider=self.ctx).transfer_code_to_task(task, cfg)
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to task {task_id}: {e}")
            return False

    def download_file(self, task_id: str, remote_path: str, local_path: Path) -> bool:
        """Download a file from a task.

        Args:
            task_id: Task to download from
            remote_path: Remote file path
            local_path: Local destination path

        Returns:
            True if download successful
        """
        try:
            # Not yet implemented via shared transport layer
            logger.error("Download of single files is not supported by the current transport")
            return False
        except Exception as e:
            logger.error(f"Failed to download file from task {task_id}: {e}")
            return False

    def upload_directory(
        self,
        task_id: str,
        local_dir: Path,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Upload a directory to a task.

        Args:
            task_id: Task to upload to
            local_dir: Local directory path
            remote_dir: Remote destination directory
            exclude_patterns: Patterns to exclude from upload

        Returns:
            True if upload successful
        """
        try:
            from flow.adapters.transport.code_transfer import (
                CodeTransferConfig,
                CodeTransferManager,
            )

            task = self.ctx.task_service.get_task(task_id)
            cfg = CodeTransferConfig(source_dir=local_dir, target_dir=remote_dir)
            CodeTransferManager(provider=self.ctx).transfer_code_to_task(task, cfg)
            return True
        except Exception as e:
            logger.error(f"Failed to upload directory to task {task_id}: {e}")
            return False

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Path,
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Download a directory from a task.

        Args:
            task_id: Task to download from
            remote_dir: Remote directory path
            local_dir: Local destination directory
            exclude_patterns: Patterns to exclude from download

        Returns:
            True if download successful
        """
        try:
            # Not yet implemented via shared transport layer
            logger.error("Download of directories is not supported by the current transport")
            return False
        except Exception as e:
            logger.error(f"Failed to download directory from task {task_id}: {e}")
            return False
