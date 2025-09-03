"""
Monarch-Flow integration.

Provides a production-oriented adapter that allocates GPU resources via Flow
and wires them into Monarch's process lifecycle.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from flow.errors import FlowError
from flow.sdk.client import Flow
from flow.sdk.models import Task, TaskConfig


@dataclass
class ComputeRequirements:
    gpu_count: int
    gpu_memory_gb: int | None = None
    gpu_type: str | None = None
    cpu_count: int | None = None
    memory_gb: int | None = None
    region: str | None = None


@dataclass
class ProcessHandle:
    id: str
    address: str
    metadata: dict[str, Any]


class ProcessLifecycleEvents(Protocol):
    async def on_created(self, handle: ProcessHandle) -> None: ...
    async def on_running(self, handle: ProcessHandle) -> None: ...
    async def on_stopped(self, handle: ProcessHandle, reason: str) -> None: ...
    async def on_failed(self, handle: ProcessHandle, error: str) -> None: ...


class ComputeAllocator(Protocol):
    async def allocate(
        self, requirements: ComputeRequirements, lifecycle: ProcessLifecycleEvents
    ) -> ProcessHandle: ...
    async def deallocate(self, handle: ProcessHandle) -> None: ...
    async def health_check(self, handle: ProcessHandle) -> bool: ...


@dataclass
class MonarchFlowConfig:
    default_region: str = field(
        default_factory=lambda: os.getenv("MITHRIL_REGION", "us-central1-b")
    )
    project: str | None = field(default_factory=lambda: os.getenv("MITHRIL_PROJECT"))
    api_url: str = field(
        default_factory=lambda: os.getenv("MITHRIL_API_URL", "https://api.mithril.ai")
    )


class FlowComputeAllocator:
    def __init__(self, config: MonarchFlowConfig | None = None):
        self._config = config or MonarchFlowConfig()
        self._flow = Flow()
        self._log = logging.getLogger(__name__)

    async def allocate(
        self, requirements: ComputeRequirements, lifecycle: ProcessLifecycleEvents
    ) -> ProcessHandle:
        try:
            # Prepare TaskConfig and submit
            cfg = TaskConfig(
                name="monarch-job",
                instance_type=requirements.gpu_type or "a100",
                num_instances=requirements.gpu_count or 1,
                region=requirements.region or self._config.default_region,
                command=["bash", "-lc", "sleep 1h"],
            )
            task: Task = await asyncio.to_thread(self._flow.run, cfg, wait=True)
            handle = ProcessHandle(id=task.task_id, address=task.ssh_host or "", metadata={})
            await lifecycle.on_created(handle)
            await lifecycle.on_running(handle)
            return handle
        except Exception as e:
            self._log.error(f"Allocation failed: {e}")
            raise FlowError(str(e))

    async def deallocate(self, handle: ProcessHandle) -> None:
        try:
            await asyncio.to_thread(self._flow.cancel, handle.id)
        except Exception as e:
            self._log.warning(f"Deallocate failed: {e}")

    async def health_check(self, handle: ProcessHandle) -> bool:
        try:
            status = await asyncio.to_thread(self._flow.status, handle.id)
            return bool(status)
        except Exception:
            return False
