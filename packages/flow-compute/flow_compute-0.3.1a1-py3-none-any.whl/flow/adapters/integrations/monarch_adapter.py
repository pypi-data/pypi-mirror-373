"""Monarch adapter for Flow integration (moved from _internal)."""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from flow.adapters.integrations.monarch import (
    ComputeAllocator,
    ComputeRequirements,
    FlowComputeAllocator,
    MonarchFlowConfig,
    ProcessHandle,
    ProcessLifecycleEvents,
)

try:
    from monarch._src.actor.allocator import (
        AllocConstraints as MonarchAllocConstraints,
    )
    from monarch._src.actor.allocator import (
        AllocSpec as MonarchAllocSpec,
    )
    from monarch._src.actor.allocator import (
        RemoteAllocator,
        RemoteAllocInitializer,
    )
    from monarch._src.actor.proc_mesh import ProcMesh as MonarchProcMesh
except Exception:  # pragma: no cover - optional dep
    MonarchAllocSpec = None  # type: ignore
    MonarchAllocConstraints = None  # type: ignore
    RemoteAllocator = None  # type: ignore
    RemoteAllocInitializer = object  # type: ignore
    MonarchProcMesh = None  # type: ignore


@dataclass
class AllocSpec:
    shape: tuple[int, int]
    constraints: dict[str, Any] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


@dataclass
class MonarchAllocation:
    handles: list[ProcessHandle]
    shape: tuple[int, int]
    addresses: list[str]


class FlowRemoteAllocator(RemoteAllocator):  # type: ignore[misc]
    def __init__(self, config: MonarchFlowConfig | None = None):
        self._allocator: ComputeAllocator = FlowComputeAllocator(config=config)
        self._log = logging.getLogger(__name__)

    async def allocate(self, spec: AllocSpec) -> MonarchAllocation:  # type: ignore[override]
        handles: list[ProcessHandle] = []

        class _Lifecycle(ProcessLifecycleEvents):
            async def on_created(self, handle: ProcessHandle) -> None: ...
            async def on_running(self, handle: ProcessHandle) -> None: ...
            async def on_stopped(self, handle: ProcessHandle, reason: str) -> None: ...
            async def on_failed(self, handle: ProcessHandle, error: str) -> None: ...

        lifecycle = _Lifecycle()

        hosts, gpus_per_host = spec.shape
        for _ in range(hosts):
            req = ComputeRequirements(gpu_count=gpus_per_host)
            handle = await self._allocator.allocate(req, lifecycle)
            handles.append(handle)

        addresses = [h.address for h in handles]
        return MonarchAllocation(handles=handles, shape=spec.shape, addresses=addresses)

    async def deallocate(self, alloc: MonarchAllocation) -> None:  # type: ignore[override]
        await asyncio.gather(*(self._allocator.deallocate(h) for h in alloc.handles))


class FlowRemoteAllocInitializer(RemoteAllocInitializer):  # type: ignore[misc]
    def __init__(self, config: MonarchFlowConfig | None = None):
        self._config = config or MonarchFlowConfig()

    def create_allocator(self) -> FlowRemoteAllocator:  # type: ignore[override]
        return FlowRemoteAllocator(config=self._config)
