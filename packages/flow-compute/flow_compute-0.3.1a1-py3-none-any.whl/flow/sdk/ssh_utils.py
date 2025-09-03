"""Provider-agnostic SSH utilities shared by SDK and CLI."""

import time
from typing import TYPE_CHECKING, ContextManager, Optional

from flow.sdk.models import Task

if TYPE_CHECKING:
    # Avoid importing provider internals at runtime; use Protocol only for typing.
    from typing import Protocol

    class IProvider(Protocol):  # pragma: no cover - typing only
        def get_task(self, task_id: str): ...


# Default provisioning timeout expectations
# Source from top-level constant if available to keep UX consistent across CLI
try:
    from flow import DEFAULT_PROVISION_MINUTES as _FLOW_DEFAULT_PROVISION_MINUTES  # type: ignore

    DEFAULT_PROVISION_MINUTES = int(_FLOW_DEFAULT_PROVISION_MINUTES)  # e.g., 20
except Exception:
    # Fallback for import cycles or partial imports
    DEFAULT_PROVISION_MINUTES = 20


class SSHNotReadyError(Exception):
    """Raised when SSH is not ready within the expected timeframe."""

    pass


def check_task_age_for_ssh(task: Task) -> str | None:
    """Return a readiness hint based on task age, or None if within norms."""
    if not task.started_at:
        return None

    from datetime import datetime, timezone

    # Ensure timezone-aware comparison
    started_at = task.started_at
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)

    age = datetime.now(timezone.utc) - started_at
    age_minutes = age.total_seconds() / 60

    if age_minutes > DEFAULT_PROVISION_MINUTES * 2:
        return f"Task has been running for {int(age_minutes)} minutes - SSH should be available by now (unexpected delay)"
    elif age_minutes > DEFAULT_PROVISION_MINUTES:
        return f"Task has been running for {int(age_minutes)} minutes - SSH is taking longer than usual"

    return None


def wait_for_task_ssh_info(
    task: Task,
    provider: Optional["IProvider"] = None,
    timeout: int = 600,
    show_progress: bool = True,
    *,
    progress_adapter: object | None = None,
) -> Task:
    """Wait until SSH info is available on the task or resolvable via provider.

    Behavior change: in addition to polling the Task view for `ssh_host`, we now
    attempt to resolve the SSH endpoint directly from the provider, which often
    becomes available before the Task record is updated. When resolution succeeds,
    we treat the endpoint as ready and return immediately, allowing callers (CLI)
    to proceed and optionally perform a brief handshake check.
    """
    start_time = time.time()
    # SDK does not own UI lifecycle. If a progress_adapter is provided by the caller
    # (e.g., CLI), the SDK may nudge it via update_eta(). Otherwise, show_progress
    # is a no-op here to avoid importing CLI UI components from the SDK.

    try:
        while time.time() - start_time < timeout:
            # If the task already has SSH info, we're done.
            if getattr(task, "ssh_host", None):
                return task

            # Try to refresh task information via provider (preferred path)
            if provider:
                # 1) Fresh task lookup may populate ssh_host
                try:
                    if hasattr(provider, "get_task"):
                        updated_task = provider.get_task(task.task_id)  # type: ignore[attr-defined]
                        if updated_task and getattr(updated_task, "ssh_host", None):
                            task = updated_task
                            return task
                except Exception:
                    # Fall back to legacy task_manager if present
                    try:
                        tm = getattr(provider, "task_manager", None)
                        if tm and hasattr(tm, "get_task"):
                            updated_task = tm.get_task(task.task_id)
                            if updated_task and getattr(updated_task, "ssh_host", None):
                                task = updated_task
                                return task
                    except Exception:
                        # Continue with endpoint resolution attempts
                        pass

                # 2) Endpoint fast-path: resolve host/port even if Task view isn't updated yet
                try:
                    if hasattr(provider, "resolve_ssh_endpoint"):
                        host_port = provider.resolve_ssh_endpoint(task.task_id)  # type: ignore[attr-defined]
                        # Accept tuple(host, port) or just host
                        host: str | None = None
                        port: int | None = None
                        if isinstance(host_port, tuple) and len(host_port) >= 1:
                            host = host_port[0]
                            try:
                                port = int(host_port[1]) if len(host_port) > 1 and host_port[1] else 22
                            except Exception:
                                port = 22
                        elif isinstance(host_port, str):
                            host = host_port
                            port = 22
                        if host:
                            # Populate transiently to signal readiness; callers may still perform
                            # a handshake probe (CLI does a short readiness check after this).
                            try:
                                task.ssh_host = host  # type: ignore[attr-defined]
                                task.ssh_port = int(port or 22)  # type: ignore[attr-defined]
                            except Exception:
                                pass
                            return task
                except Exception:
                    # Endpoint not resolvable yet; continue waiting
                    pass

            # Wait before next check and nudge any UI adapter
            if progress_adapter is not None:
                try:
                    if hasattr(progress_adapter, "update_eta"):
                        progress_adapter.update_eta()
                except Exception:
                    pass
                time.sleep(1)
            else:
                time.sleep(2)

        # Timeout reached
        elapsed = int(time.time() - start_time)
        raise SSHNotReadyError(f"SSH access not available after {elapsed} seconds")

    except KeyboardInterrupt:
        raise SSHNotReadyError("SSH wait interrupted by user")
    except Exception:
        raise


class SSHTunnelManager:
    """Simplified SSH tunnel manager interface (provider-specific)."""

    @staticmethod
    def tunnel_context(task: Task, remote_port: int, local_port: int = 0) -> ContextManager[None]:
        """Create an SSH tunnel context (must be implemented by the provider)."""
        # This is a simplified implementation
        # In practice, this would delegate to the provider's SSH tunnel
        raise NotImplementedError(
            "SSH tunnel support requires provider-specific implementation. "
            "Use flow_client.provider.get_ssh_tunnel_manager() instead."
        )
