"""Flow API models package (backwards-compatible facade).

This package provides a stable import surface compatible with
``from flow.sdk.models import ...``. During the PR-1.1 refactor, models
are being split into submodules. We re-export lightweight symbols
and lazily load the remaining symbols from a legacy module to keep
cold imports fast.

Additionally, this module re-exports IR (Intermediate Representation) models
as the canonical platform contract.
"""

from __future__ import annotations

from typing import Any  # noqa: F401 - kept for public API context

from flow.domain.ir import (
    MountSpec as IRMountSpec,
)
from flow.domain.ir import (
    ResourceSpec as IRResourceSpec,
)
from flow.domain.ir import (
    RunParams as IRRunParams,
)

# Re-export IR models as the canonical platform contract
from flow.domain.ir import (
    TaskSpec as IRTaskSpec,
)

# Avoid importing heavy pydantic symbols here to keep import light
from flow.sdk.models.config import (
    FlowConfig as FlowConfig,
)
from flow.sdk.models.config import (
    Project as Project,
)
from flow.sdk.models.config import (
    ValidationResult as ValidationResult,
)
from flow.sdk.models.enums import (
    InstanceStatus as InstanceStatus,
)
from flow.sdk.models.enums import (
    ReservationStatus as ReservationStatus,
)
from flow.sdk.models.enums import (
    StorageInterface as StorageInterface,
)
from flow.sdk.models.enums import (
    TaskStatus as TaskStatus,
)
from flow.sdk.models.hardware import (
    CPUSpec as CPUSpec,
)
from flow.sdk.models.hardware import (
    GPUSpec as GPUSpec,
)
from flow.sdk.models.hardware import (
    InstanceMatch as InstanceMatch,
)
from flow.sdk.models.hardware import (
    InstanceType as InstanceType,
)
from flow.sdk.models.hardware import (
    MemorySpec as MemorySpec,
)
from flow.sdk.models.hardware import (
    NetworkSpec as NetworkSpec,
)
from flow.sdk.models.hardware import (
    StorageSpec as StorageSpec,
)
from flow.sdk.models.instance import (
    AvailableInstance as AvailableInstance,
)
from flow.sdk.models.instance import (
    Instance as Instance,
)
from flow.sdk.models.requests import (
    ListTasksRequest as ListTasksRequest,
)
from flow.sdk.models.requests import (
    ListTasksResponse as ListTasksResponse,
)
from flow.sdk.models.requests import (
    SubmitTaskRequest as SubmitTaskRequest,
)
from flow.sdk.models.requests import (
    SubmitTaskResponse as SubmitTaskResponse,
)
from flow.sdk.models.reservations import Reservation as Reservation
from flow.sdk.models.reservations import ReservationSpec as ReservationSpec
from flow.sdk.models.retry import Retries as Retries
from flow.sdk.models.task import Task as Task
from flow.sdk.models.task_config import TaskConfig as TaskConfig
from flow.sdk.models.users import User as User
from flow.sdk.models.volume import MountSpec as MountSpec
from flow.sdk.models.volume import Volume as VolumeModel
from flow.sdk.models.volume import VolumeSpec as VolumeSpec

# All public symbols are re-exported above; no legacy fallback remains.
__all__ = (
    # IR models (canonical platform contract)
    "IRTaskSpec",
    "IRResourceSpec",
    "IRMountSpec",
    "IRRunParams",
    # Backwards-compat synonyms
    "TaskSpec",
    "Resources",
    "RunParams",
    # SDK models
    "TaskStatus",
    "InstanceStatus",
    "ReservationStatus",
    "StorageInterface",
    "Retries",
    "Task",
    "TaskConfig",
    "VolumeSpec",
    "MountSpec",
    "GPUSpec",
    "CPUSpec",
    "MemorySpec",
    "StorageSpec",
    "NetworkSpec",
    "InstanceType",
    "InstanceMatch",
    "Instance",
    "AvailableInstance",
    "Reservation",
    "ReservationSpec",
    "FlowConfig",
    "Project",
    "ValidationResult",
    "SubmitTaskRequest",
    "SubmitTaskResponse",
    "ListTasksRequest",
    "ListTasksResponse",
    "User",
    "Volume",  # backward-compat alias for volume entities if needed by callers
)


class Volume(VolumeModel):
    """Backwards-compatible alias to the canonical Volume model.

    Kept for import stability of the legacy Volume class while delegating to
    the real implementation in the volume module, which supports
    both persistent volumes and bind mounts (local/remote/read_only).
    """

    pass


# Backwards-compatible type aliases to IR models
TaskSpec = IRTaskSpec
Resources = IRResourceSpec
RunParams = IRRunParams


# __all__ is defined above to enumerate public symbols
