from __future__ import annotations

"""SSH client-side wait utilities and connection info structures.

This module contains portable, provider-agnostic SSH helpers used by the CLI
and adapters. Import `SSHConnectionInfo`, `ISSHWaiter`, or
`ExponentialBackoffSSHWaiter` from here for direct use, or from
`flow.adapters.transport.ssh` for the stable facade.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.sdk.models import Task
from flow.sdk.ssh_utils import SSHNotReadyError, wait_for_task_ssh_info

logger = logging.getLogger(__name__)


@dataclass
class SSHConnectionInfo:
    host: str
    port: int
    user: str
    key_path: Path
    task_id: str

    @property
    def destination(self) -> str:
        return f"{self.user}@{self.host}"


class ISSHWaiter(Protocol):
    def wait_for_ssh(
        self,
        task: Task,
        timeout: int | None = None,
        probe_interval: float = 10.0,
        progress_callback: Callable[[str], None] | None = None,
    ) -> SSHConnectionInfo: ...


class ExponentialBackoffSSHWaiter:
    """Waits for SSH reachability using exponential backoff probes."""

    def __init__(self, provider: object | None = None):
        self.provider = provider
        self.max_backoff = 60
        self.backoff_multiplier = 1.5

    def wait_for_ssh(
        self,
        task: Task,
        timeout: int | None = None,
        probe_interval: float = 10.0,
        progress_callback: Callable[[str], None] | None = None,
    ) -> SSHConnectionInfo:
        # Delegate to shared API to wait for ssh info first
        try:
            task = wait_for_task_ssh_info(
                task=task, provider=self.provider, timeout=timeout or 1200, show_progress=False
            )
        except SSHNotReadyError as e:
            raise TimeoutError(str(e)) from e

        connection = SSHConnectionInfo(
            host=task.ssh_host,
            port=int(getattr(task, "ssh_port", 22)),
            user=getattr(task, "ssh_user", "ubuntu"),
            key_path=self._get_ssh_key_path(task),
            task_id=task.task_id,
        )

        # Quick readiness loop
        import time as _t

        start = _t.time()
        interval = probe_interval
        while True:
            elapsed = _t.time() - start
            if timeout and elapsed >= timeout:
                raise TimeoutError(f"SSH connection timeout after {int(elapsed)}s")

            if progress_callback:
                mins, secs = divmod(int(elapsed), 60)
                progress_callback(f"Waiting for SSH ({mins}m {secs}s elapsed)")

            if SshStack.is_ssh_ready(
                user=connection.user,
                host=connection.host,
                port=connection.port,
                key_path=connection.key_path,
            ):
                return connection

            _t.sleep(min(interval, self.max_backoff))
            interval *= self.backoff_multiplier

    def _get_ssh_key_path(self, task: Task) -> Path:
        # Provider-backed resolution if available
        if getattr(self.provider, "get_task_ssh_connection_info", None):
            key_path, error = self.provider.get_task_ssh_connection_info(task.task_id)
            if not key_path:
                raise RuntimeError(f"Failed to resolve SSH key: {error}")
            return Path(key_path)

        # Fallbacks
        default = Path.home() / ".ssh" / "id_rsa"
        if default.exists():
            return default
        raise RuntimeError("No SSH key available; set provider or ensure default key exists")
