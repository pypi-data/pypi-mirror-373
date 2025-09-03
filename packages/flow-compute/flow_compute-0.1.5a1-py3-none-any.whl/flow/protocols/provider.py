from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # import only for typing to avoid circular imports at runtime
    from flow.domain.ir.spec import TaskSpec


@dataclass(frozen=True, slots=True)
class Plan:
    """Execution plan generated from a TaskSpec."""

    id: str
    provider: str
    region: str
    estimated_cost: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class TaskHandle:
    """Handle to a running task."""

    id: str
    provider: str
    status: str | None = None


class Provider(Protocol):
    """Core provider interface for task execution.

    This is the simplified interface that all providers must implement.
    It works with the IR (TaskSpec) as input and provides basic task lifecycle.
    """

    def plan(self, spec: TaskSpec) -> Plan:
        """Generate an execution plan from a task specification.

        Args:
            spec: Task specification in IR format

        Returns:
            Execution plan with provider-specific details
        """
        ...

    def submit(self, plan: Plan) -> TaskHandle:
        """Submit a task based on an execution plan.

        Args:
            plan: Execution plan from plan() method

        Returns:
            Handle to the submitted task
        """
        ...

    def status(self, handle: TaskHandle) -> str:
        """Get current status of a task.

        Args:
            handle: Task handle from submit()

        Returns:
            Status string (e.g., "running", "completed", "failed")
        """
        ...

    def logs(self, handle: TaskHandle, tail: int | None = None) -> Iterable[str]:
        """Stream logs from a task.

        Args:
            handle: Task handle from submit()
            tail: Number of lines to return from end

        Returns:
            Iterator of log lines
        """
        ...

    def cancel(self, handle: TaskHandle) -> None:
        """Cancel a running task.

        Args:
            handle: Task handle from submit()
        """
        ...


class ProviderProtocol(Protocol):
    """Abstraction for compute providers used by the app layer.

    This mirrors the stable subset of operations the CLI and API require,
    while allowing providers to implement richer functionality internally.
    """

    # ---- Task lifecycle ----
    def submit_task(
        self,
        instance_type: str,
        config: Any,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Any: ...

    def get_task(self, task_id: str) -> Any: ...

    def get_task_status(self, task_id: str) -> Any: ...

    def list_tasks(
        self,
        status: str | None = None,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> list[Any]: ...

    def stop_task(self, task_id: str) -> bool: ...

    def cancel_task(self, task_id: str) -> None: ...

    # ---- Logs ----
    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str: ...

    def stream_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",
        follow: bool = True,
        tail: int = 10,
    ) -> Iterable[str]: ...

    # ---- Instances / discovery ----
    def find_instances(self, requirements: dict[str, Any], limit: int = 10) -> list[Any]: ...

    def parse_catalog_instance(self, instance: Any) -> dict[str, Any]: ...

    # ---- Volumes ----
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

    # ---- Reservations ----
    def create_reservation(
        self,
        instance_type: str,
        config: Any,
        volume_ids: list[str] | None = None,
    ) -> Any: ...

    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Any]: ...

    def get_reservation(self, reservation_id: str) -> Any: ...

    # ---- SSH Keys (optional, provider-dependent) ----
    def get_ssh_keys(self) -> list[dict[str, Any]]: ...

    def create_ssh_key(self, name: str, public_key: str) -> dict[str, Any]: ...

    def delete_ssh_key(self, key_id: str) -> bool: ...
