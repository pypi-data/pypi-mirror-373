"""Mount operation planner (core).

Plans provider-agnostic mount operations from parsed/validated specs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PlannedMount:
    source: str
    target: str
    mount_type: str  # bind | s3fs | volume
    options: dict[str, Any]


class MountPlanner:
    def plan(self, target_to_source: dict[str, str]) -> list[PlannedMount]:
        plans: list[PlannedMount] = []
        for target, source in target_to_source.items():
            if source.startswith("s3://"):
                plans.append(PlannedMount(source, target, "s3fs", {"readonly": True}))
            elif source.startswith("volume://"):
                # Volume id/name resolved later by data resolver
                plans.append(PlannedMount(source, target, "volume", {}))
            else:
                plans.append(PlannedMount(source, target, "bind", {"readonly": True}))
        return plans
