from __future__ import annotations

"""Storage facet: persistent volumes and file transfer."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class StorageProtocol(Protocol):
    """Volume lifecycle and file transfer operations."""

    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Any: ...

    def delete_volume(self, volume_id: str) -> bool: ...

    def list_volumes(self, limit: int = 100) -> list[Any]: ...

    def is_volume_id(self, identifier: str) -> bool: ...

    def mount_volume(
        self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume"
    ) -> bool: ...

    def upload_file(self, task_id: str, local_path: Any, remote_path: str = "~") -> bool: ...

    def upload_directory(
        self,
        task_id: str,
        local_dir: Any,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> bool: ...

    def download_file(self, task_id: str, remote_path: str, local_path: Any) -> bool: ...

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Any,
        exclude_patterns: list[str] | None = None,
    ) -> bool: ...
