"""Local storage management for testing provider."""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalStorage:
    """Manages local storage for test tasks and volumes."""

    def __init__(self, base_dir: Path):
        """Initialize local storage.

        Args:
            base_dir: Base directory for all storage
        """
        self.base_dir = Path(base_dir)
        self.volumes_dir = self.base_dir / "volumes"
        self.tasks_dir = self.base_dir / "tasks"
        self.metadata_dir = self.base_dir / "metadata"

    def initialize(self):
        """Initialize storage directories."""
        for directory in [self.volumes_dir, self.tasks_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def create_volume(self, volume_id: str, size_gb: int) -> Path:
        """Create a local volume.

        Args:
            volume_id: Volume identifier
            size_gb: Volume size in GB

        Returns:
            Path to volume directory
        """
        volume_path = self.volumes_dir / volume_id
        volume_path.mkdir(exist_ok=True)

        # Store metadata
        metadata = {
            "volume_id": volume_id,
            "size_gb": size_gb,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "path": str(volume_path),
        }

        metadata_path = self.metadata_dir / f"volume-{volume_id}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        logger.info(f"Created volume {volume_id} at {volume_path}")
        return volume_path

    def delete_volume(self, volume_id: str):
        """Delete a volume.

        Args:
            volume_id: Volume to delete
        """
        volume_path = self.volumes_dir / volume_id
        metadata_path = self.metadata_dir / f"volume-{volume_id}.json"

        if volume_path.exists():
            shutil.rmtree(volume_path)

        if metadata_path.exists():
            metadata_path.unlink()

        logger.info(f"Deleted volume {volume_id}")

    def get_volume_info(self, volume_id: str) -> dict | None:
        """Get volume information.

        Args:
            volume_id: Volume identifier

        Returns:
            Volume metadata or None if not found
        """
        metadata_path = self.metadata_dir / f"volume-{volume_id}.json"

        if metadata_path.exists():
            return json.loads(metadata_path.read_text())

        return None

    def list_volumes(self) -> list[str]:
        """List all volume IDs.

        Returns:
            List of volume identifiers
        """
        volumes = []

        for metadata_file in self.metadata_dir.glob("volume-*.json"):
            try:
                metadata = json.loads(metadata_file.read_text())
                volumes.append(metadata["volume_id"])
            except Exception as e:
                logger.warning(f"Error reading volume metadata {metadata_file}: {e}")

        return volumes

    def get_task_dir(self, task_id: str) -> Path:
        """Get task working directory.

        Args:
            task_id: Task identifier

        Returns:
            Path to task directory
        """
        task_dir = self.tasks_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir

    def cleanup(self):
        """Clean up all storage."""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
            logger.info(f"Cleaned up storage at {self.base_dir}")

    def get_storage_usage(self) -> dict[str, int]:
        """Get storage usage statistics.

        Returns:
            Dictionary with usage statistics in bytes
        """
        usage = {
            "total": 0,
            "volumes": 0,
            "tasks": 0,
            "metadata": 0,
        }

        for category, directory in [
            ("volumes", self.volumes_dir),
            ("tasks", self.tasks_dir),
            ("metadata", self.metadata_dir),
        ]:
            if directory.exists():
                size = sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())
                usage[category] = size
                usage["total"] += size

        return usage
