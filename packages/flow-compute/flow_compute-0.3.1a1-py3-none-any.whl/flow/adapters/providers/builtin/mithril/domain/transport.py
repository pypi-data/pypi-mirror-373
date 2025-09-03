"""Transport service for SSH and code transfer operations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider import MithrilProvider
    from flow.sdk.models import Task


class TransportService:
    """Service for SSH and code transfer operations.

    This service provides high-level transport operations for tasks,
    including waiting for SSH availability and uploading code.
    """

    def __init__(self, provider: MithrilProvider) -> None:
        """Initialize transport service with provider reference.

        Args:
            provider: MithrilProvider instance for accessing transport utilities
        """
        self._provider = provider

    def wait_for_ssh(self, task: Task, timeout: int | None = None) -> bool:
        """Wait for SSH to become available on a task.

        Args:
            task: Task to wait for SSH on
            timeout: Maximum time to wait in seconds

        Returns:
            True if SSH became available, False if timeout
        """
        from flow.adapters.transport.ssh import ExponentialBackoffSSHWaiter

        waiter = ExponentialBackoffSSHWaiter(self._provider)
        return waiter.wait_for_ssh(task, timeout=timeout)

    def upload_code(self, task: Task, source_dir: Path, target_dir: str = "~") -> bool:
        """Upload code directory to a task.

        Args:
            task: Task to upload code to
            source_dir: Local directory to upload
            target_dir: Remote directory path (default: home directory)

        Returns:
            True if upload succeeded
        """
        from flow.adapters.transport.code_transfer import (
            CodeTransferConfig,
            CodeTransferManager,
        )

        manager = CodeTransferManager(provider=self._provider)
        cfg = CodeTransferConfig(source_dir=source_dir, target_dir=target_dir)
        return manager.transfer_code_to_task(task, cfg)
