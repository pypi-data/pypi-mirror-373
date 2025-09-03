from __future__ import annotations

"""Minimal compatibility implementation for file/directory transfer.

Implements a subset of the legacy FileTransferManager API and delegates
directory upload to the shared CodeTransferManager. File-level operations
are currently best-effort and may transfer the containing directory.
"""

from pathlib import Path
from typing import Any

from flow.adapters.transport.code_transfer import CodeTransferConfig, CodeTransferManager


class FileTransferManager:
    def __init__(self, provider: Any):
        self._provider = provider
        self._mgr = CodeTransferManager(provider=provider)

    def upload_file(self, task_id: str, local_path: Path, remote_path: str = "~") -> None:
        # Best-effort: upload containing directory
        task = getattr(self._provider, "get_task", None)
        if callable(task):
            t = task(task_id)
            cfg = CodeTransferConfig(source_dir=local_path.parent, target_dir=remote_path)
            self._mgr.transfer_code_to_task(t, cfg)

    def download_file(
        self, task_id: str, remote_path: str, local_path: Path
    ) -> None:  # pragma: no cover
        # Not implemented in shared transport; no-op
        raise NotImplementedError("download_file not implemented")

    def upload_directory(
        self,
        task_id: str,
        local_dir: Path,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> None:
        task = getattr(self._provider, "get_task", None)
        if callable(task):
            t = task(task_id)
            cfg = CodeTransferConfig(source_dir=local_dir, target_dir=remote_dir)
            self._mgr.transfer_code_to_task(t, cfg)

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Path,
        exclude_patterns: list[str] | None = None,
    ) -> None:  # pragma: no cover
        # Not implemented in shared transport; no-op
        raise NotImplementedError("download_directory not implemented")
