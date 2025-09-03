from __future__ import annotations

"""Compute facet: task submission and lifecycle operations."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ComputeProtocol(Protocol):
    """Compute operations for submitting and managing tasks."""

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
