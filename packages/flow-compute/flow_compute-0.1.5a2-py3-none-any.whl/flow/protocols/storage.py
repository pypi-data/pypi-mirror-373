from __future__ import annotations

from pathlib import Path
from typing import Protocol

# Avoid importing SDK types in ports to keep ports isolated.
Volume = object


class StorageProtocol(Protocol):
    """Abstraction for persistent storage and file transfer operations.

    This port allows the application layer to manage volumes and perform
    task-scoped file transfers without depending on concrete providers.
    """

    # ---- Volumes ----
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Volume: ...

    def delete_volume(self, volume_id: str) -> bool: ...

    def list_volumes(self, limit: int = 100) -> list[Volume]: ...

    def is_volume_id(self, identifier: str) -> bool: ...

    def mount_volume(
        self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume"
    ) -> bool: ...

    # ---- File Transfer (task-scoped) ----
    def upload_file(self, task_id: str, local_path: Path, remote_path: str = "~") -> bool: ...

    def download_file(self, task_id: str, remote_path: str, local_path: Path) -> bool: ...

    def upload_directory(
        self,
        task_id: str,
        local_dir: Path,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> bool: ...

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Path,
        exclude_patterns: list[str] | None = None,
    ) -> bool: ...
