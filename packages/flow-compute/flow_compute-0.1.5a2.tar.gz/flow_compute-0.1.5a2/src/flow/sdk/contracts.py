"""API contracts for Flow SDK services.

These lightweight Protocols define the interfaces used by the CLI service layer.
They intentionally avoid concrete dependencies on provider implementations.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable

from flow.sdk.models import Task, TaskConfig, TaskStatus, Volume


@runtime_checkable
class ITaskService(Protocol):
    def run(
        self, task: TaskConfig | str, wait: bool = False, mounts: str | dict[str, str] | None = None
    ) -> Task: ...
    def submit(
        self,
        command: str,
        *,
        gpu: str | None = None,
        mounts: str | dict[str, str] | None = None,
        instance_type: str | None = None,
        wait: bool = False,
    ) -> Task: ...
    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | None = None,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> list[Task]: ...
    def get_task(self, task_id: str) -> Task: ...


@runtime_checkable
class ILogsService(Protocol):
    def logs(
        self,
        task_id: str,
        follow: bool = False,
        tail: int = 100,
        stderr: bool = False,
        *,
        source: str | None = None,
        stream: str | None = None,
    ) -> str | Iterator[str]: ...


@runtime_checkable
class IVolumeService(Protocol):
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        *,
        region: str | None = None,
    ) -> Volume: ...
    def delete_volume(self, volume_id: str) -> None: ...
    def list_volumes(self, limit: int = 100) -> list[Volume]: ...
    def mount_volume(
        self, volume_id: str, task_id: str, mount_point: str | None = None
    ) -> None: ...


@runtime_checkable
class IReservationsService(Protocol):
    # Placeholder for future reservation operations needed by CLI
    # e.g., list_reservations, get_reservation, create_reservation, etc.
    def __call__(self) -> Any: ...


@runtime_checkable
class IClient(ITaskService, ILogsService, IVolumeService, Protocol):
    @property
    def provider(self) -> Any: ...
