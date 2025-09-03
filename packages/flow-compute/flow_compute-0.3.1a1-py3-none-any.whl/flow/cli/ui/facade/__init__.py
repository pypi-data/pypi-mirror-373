"""UI import facades.

Use these re-exports to avoid scattered try/except optional imports.
They prefer the rich `components` implementations and fall back to
`presentation` modules when components are unavailable.
"""

from .formatters import GPUFormatter, TaskFormatter, VolumeFormatter, format_task_duration
from .views import TaskDetailRenderer, TaskPresenter, TerminalAdapter

__all__ = [
    "TaskFormatter",
    "GPUFormatter",
    "VolumeFormatter",
    "format_task_duration",
    "TaskPresenter",
    "TerminalAdapter",
    "TaskDetailRenderer",
]
