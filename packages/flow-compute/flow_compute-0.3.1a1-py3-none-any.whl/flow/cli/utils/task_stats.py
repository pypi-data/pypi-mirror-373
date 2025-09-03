"""Task statistics helpers shared across CLI presenters and commands."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone


def compute_total_gpu_hours(tasks: Iterable) -> float:
    """Compute aggregate GPU-hours across tasks.

    Rules:
    - Include running/completed/failed tasks
    - Duration from created_at to completed_at or now (UTC)
    - Multiply by GPU count parsed from instance_type prefix like "8xh100"
    """
    total = 0.0
    now = datetime.now(timezone.utc)

    for task in tasks:
        status = getattr(task, "status", None)
        status_value = getattr(status, "value", str(status)).lower()
        if status_value not in {"running", "completed", "failed"}:
            continue

        created_at = getattr(task, "created_at", None)
        # Require a real datetime for arithmetic; skip otherwise (tests may use Mocks)
        if not isinstance(created_at, datetime):
            continue
        if getattr(created_at, "tzinfo", None) is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        completed_at = getattr(task, "completed_at", None)
        if not isinstance(completed_at, datetime):
            completed_at = None
        elif getattr(completed_at, "tzinfo", None) is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)

        end = completed_at or now
        duration_hours = (end - created_at).total_seconds() / 3600.0

        # Parse GPU count from instance_type prefix
        gpu_count = 1
        instance_type = getattr(task, "instance_type", None) or ""
        if instance_type:
            try:
                import re

                match = re.match(r"(\d+)x", instance_type)
                if match:
                    gpu_count = int(match.group(1))
            except Exception:
                pass

        total += max(0.0, duration_hours) * gpu_count

    return total
