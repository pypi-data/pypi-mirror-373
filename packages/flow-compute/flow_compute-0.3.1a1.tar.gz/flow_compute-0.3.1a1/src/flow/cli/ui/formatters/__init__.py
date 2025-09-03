"""Shared UI formatters import surface.

Expose canonical imports for core formatters without cross‑package coupling.
This avoids circular imports with the facade layer.
"""

from __future__ import annotations

from .shared_gpu import GPUFormatter as GPUFormatter

# Re‑export shared/core implementations. Higher‑level facades that choose
# between presentation/components can be imported from
# ``flow.cli.ui.facade`` when needed by callers.
from .shared_task import TaskFormatter as TaskFormatter
from .shared_task import format_task_duration as format_task_duration

__all__ = [
    "TaskFormatter",
    "GPUFormatter",
    "format_task_duration",
]
