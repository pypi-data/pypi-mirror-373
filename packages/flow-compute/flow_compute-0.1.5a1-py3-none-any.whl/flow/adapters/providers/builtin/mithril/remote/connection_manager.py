from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from flow.adapters.providers.builtin.mithril.core.constants import (
    EXPECTED_PROVISION_MINUTES,
    SSH_QUICK_RETRY_ATTEMPTS,
    SSH_QUICK_RETRY_MAX_SECONDS,
)
from flow.adapters.providers.builtin.mithril.remote.errors import SshConnectionError, make_error
from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.sdk.ssh_utils import SSHNotReadyError, wait_for_task_ssh_info

logger = logging.getLogger(__name__)


@dataclass
class ConnectionDetails:
    """Holds resolved and validated SSH connection details."""

    user: str
    host: str
    port: int
    key_path: Path
    cache_key: tuple | None = None
    task: object | None = None


class SshConnectionManager:
    """Centralizes SSH setup, validation, retries, and caching."""

    def __init__(self, provider):
        self.provider = provider
        self._ssh_last_success: dict[tuple, float] = {}

    # Cache helpers --------------------------------------------------------
    def _build_cache_key(self, task_id: str, task, node: int | None) -> tuple | None:
        try:
            try:
                project_id = self.provider.project_id
            except Exception:
                project_id = "default"
            return (
                project_id,
                task_id,
                int(node or -1),
                task.ssh_host,
                int(getattr(task, "ssh_port", 22)),
            )
        except Exception:
            return None

    # Public wrapper used by callers to avoid using a private method
    def build_cache_key(self, task_id: str, task, node: int | None) -> tuple | None:
        return self._build_cache_key(task_id, task, node)

    def check_recent_success(self, cache_key: tuple | None, ttl_seconds: float = 60.0) -> bool:
        if cache_key is None:
            return False
        try:
            ts = self._ssh_last_success.get(cache_key)
            return ts is not None and (time.time() - ts) < ttl_seconds
        except Exception:
            return False

    def mark_success(self, cache_key: tuple | None) -> None:
        if cache_key is None:
            return
        try:
            self._ssh_last_success[cache_key] = time.time()
        except Exception:
            pass

    def bust_cache(self, cache_key: tuple | None) -> None:
        if cache_key is None:
            return
        try:
            self._ssh_last_success.pop(cache_key, None)
        except Exception:
            pass

    # Core establishment ---------------------------------------------------
    def establish_connection(
        self,
        task_id: str,
        request_id: str,
        timeout_seconds: int,
        node: int | None = None,
        quick_ready: bool = False,
    ) -> ConnectionDetails:
        """Resolve SSH details and ensure the remote host is ready."""
        # Resolve endpoint first (host/port)
        task = self._resolve_endpoint(task_id, node, request_id)

        # Compute an effective timeout that respects caller intent
        # If quick_ready: cap the wait to a small window, NEVER exceed caller timeout
        base_timeout = timeout_seconds if timeout_seconds is not None else SSH_READY_WAIT_SECONDS
        quick_cap = SSH_QUICK_RETRY_MAX_SECONDS * 2
        effective_timeout = min(base_timeout, quick_cap) if quick_ready else base_timeout

        # Build cache key and fast-path if we recently connected successfully
        cache_key = self._build_cache_key(task_id, task, node)

        # Ensure SSH key path (cheap/local)
        key_path = self._resolve_ssh_key(task_id, request_id)

        if self.check_recent_success(cache_key):
            return ConnectionDetails(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=int(getattr(task, "ssh_port", 22)),
                key_path=Path(key_path),
                cache_key=cache_key,
                task=task,
            )

        # Ensure SSH info exists (and refresh if needed)
        try:
            task = wait_for_task_ssh_info(
                task=task,
                provider=self.provider,
                timeout=effective_timeout,
                show_progress=False,
            )
        except SSHNotReadyError as e:
            raise make_error(
                f"No SSH access for task {task_id}: {e!s}",
                request_id,
                suggestions=e.suggestions,
                cls=SshConnectionError,
            ) from e

        # Wait for SSH service readiness using shared transport waiter
        try:
            from flow.adapters.transport.ssh import ExponentialBackoffSSHWaiter

            waiter = ExponentialBackoffSSHWaiter(self.provider)
            # Attach resolved ssh_port
            task.ssh_port = int(getattr(task, "ssh_port", 22))
            waiter.wait_for_ssh(task=task, timeout=effective_timeout, progress_callback=None)
        except Exception:
            # Fallback to local readiness probe on failure to import or waiter error
            self._ensure_ssh_ready(task, key_path, request_id)

        # Mark recent success for subsequent quick operations
        self.mark_success(cache_key)

        return ConnectionDetails(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=int(getattr(task, "ssh_port", 22)),
            key_path=Path(key_path),
            cache_key=cache_key,
            task=task,
        )

    # Internal helpers -----------------------------------------------------
    def _resolve_endpoint(self, task_id: str, node: int | None, request_id: str):
        task = self.provider.get_task(task_id)

        # Fresh resolve endpoint; handle multi-node selection
        try:
            host, port = self.provider.resolve_ssh_endpoint(task_id, node=node)
            task.ssh_host = host
            try:
                task.ssh_port = int(port or 22)
            except Exception:
                task.ssh_port = 22
        except Exception as e:
            if not getattr(task, "ssh_host", None):
                raise make_error(str(e), request_id)

        if node is not None and getattr(task, "instances", None):
            try:
                instances = self.provider.get_task_instances(task_id)
                if node < 0 or node >= len(instances):
                    raise make_error(
                        f"Invalid node index {node}; task has {len(instances)} nodes",
                        request_id,
                        cls=SshConnectionError,
                    )
                selected = instances[node]
                if getattr(selected, "ssh_host", None):
                    task.ssh_host = selected.ssh_host
            except Exception as e:
                raise make_error(str(e), request_id, cls=SshConnectionError)

        return task

    def _resolve_ssh_key(self, task_id: str, request_id: str) -> Path:
        # Ensure SSH key manager has project scoping
        try:
            if (
                getattr(self.provider, "ssh_key_manager", None) is not None
                and getattr(self.provider.ssh_key_manager, "project_id", None) is None
            ):
                self.provider.ssh_key_manager.project_id = self.provider.project_id
        except Exception:
            pass

        ssh_key_path, error_msg = self.provider.get_task_ssh_connection_info(task_id)
        if not ssh_key_path:
            raise make_error(
                f"SSH key resolution failed: {error_msg}", request_id, cls=SshConnectionError
            )
        return Path(ssh_key_path)

    def _ensure_ssh_ready(self, task, key_path: Path, request_id: str) -> None:
        if SshStack.is_ssh_ready(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=Path(key_path),
        ):
            return

        start_time = time.time()
        for attempt in range(SSH_QUICK_RETRY_ATTEMPTS):
            elapsed = time.time() - start_time
            if elapsed > SSH_QUICK_RETRY_MAX_SECONDS:
                break

            time.sleep(2 * (attempt + 1))
            if SshStack.is_ssh_ready(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                key_path=Path(key_path),
            ):
                return

        # Before surfacing a generic readiness error, run one last probe to capture
        # a specific authentication failure (e.g., Permission denied (publickey)).
        try:
            probe_cmd = SshStack.build_ssh_command(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                key_path=Path(key_path),
                prefix_args=[
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=4",
                    "-o",
                    "ConnectionAttempts=1",
                ],
                remote_command="echo SSH_OK",
            )
            result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=6)
            if result.returncode != 0:
                stderr = (result.stderr or "").lower()
                if "permission denied" in stderr or "publickey" in stderr:
                    from flow.adapters.providers.builtin.mithril.remote.errors import (
                        SshConnectionError,
                        make_error,
                    )

                    suggestions = [
                        "Verify the task was launched with your SSH key",
                        "Run: flow ssh-keys list (confirm your key on the project)",
                        "Optionally override: MITHRIL_SSH_KEY=/path/to/private/key flow <cmd>",
                    ]
                    raise make_error(
                        (
                            "SSH authentication failed (Permission denied).\n"
                            f"Key used: {Path(key_path).expanduser()!s}"
                        ),
                        request_id,
                        suggestions=suggestions,
                        cls=SshConnectionError,
                    )
        except Exception:
            # Best-effort diagnostics; fall back to generic flow below
            pass

        # Build nuanced error messaging based on instance status/age
        try:
            instance_age_seconds = float(getattr(task, "instance_age_seconds", 0) or 0)
        except Exception:
            instance_age_seconds = 0.0
        capped_seconds = max(0.0, min(instance_age_seconds, 7 * 24 * 3600))
        instance_age_minutes = int(capped_seconds // 60)

        instance_status = getattr(task, "instance_status", None)

        if instance_status == "STATUS_STARTING":
            raise make_error(
                "Instance is starting up. SSH will be available once startup completes. "
                "Please try again in a moment or check 'flow status' for current state.",
                request_id,
                cls=SshConnectionError,
            )
        elif instance_age_minutes < EXPECTED_PROVISION_MINUTES:
            raise make_error(
                f"Instance is still starting up ({instance_age_minutes} minutes elapsed). "
                f"SSH startup can take up to {EXPECTED_PROVISION_MINUTES} minutes. "
                f"Please try again in a moment.",
                request_id,
                cls=SshConnectionError,
            )
        else:
            raise make_error(
                f"SSH service on {getattr(task, 'ssh_host', 'host')} is not responding. "
                f"The instance may still be starting up (can take up to {EXPECTED_PROVISION_MINUTES} minutes). "
                f"Please try again in a moment.",
                request_id,
                cls=SshConnectionError,
            )
