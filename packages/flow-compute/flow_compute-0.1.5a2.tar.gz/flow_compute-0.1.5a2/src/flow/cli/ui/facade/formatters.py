"""Formatter facade re-exports.

Prefer components-based formatters, fallback to presentation-only implementations.
"""

from __future__ import annotations

from flow.cli.utils.lazy_imports import import_attr

# Prefer presentation, then components; finally fall back to shared formatter.
TaskFormatter = import_attr(
    "flow.cli.ui.presentation.task_formatter",
    "TaskFormatter",
    import_attr("flow.cli.ui.components.formatters.task_formatter", "TaskFormatter"),
)
if TaskFormatter is None:
    # Robust fallback for environments where optional UI packages weren't included
    from flow.cli.ui.formatters.shared_task import (
        TaskFormatter as TaskFormatter,  # type: ignore[no-redef]
    )

format_task_duration = import_attr(
    "flow.cli.ui.presentation.task_formatter",
    "format_task_duration",
    import_attr("flow.cli.ui.components.formatters.task_formatter", "format_task_duration"),
)
if format_task_duration is None:
    # Robust fallback for environments where optional UI packages weren't included
    from flow.cli.ui.formatters.shared_task import (  # type: ignore
        format_task_duration as format_task_duration,
    )

GPUFormatter = import_attr(
    "flow.cli.ui.presentation.gpu_formatter",
    "GPUFormatter",
    import_attr("flow.cli.ui.components.formatters.gpu_formatter", "GPUFormatter"),
)

VolumeFormatter = import_attr(
    "flow.cli.ui.presentation.volume_formatter",
    "VolumeFormatter",
    import_attr("flow.cli.ui.components.formatters.volume_formatter", "VolumeFormatter"),
)

__all__ = [
    "TaskFormatter",
    "format_task_duration",
    "GPUFormatter",
    "VolumeFormatter",
]
