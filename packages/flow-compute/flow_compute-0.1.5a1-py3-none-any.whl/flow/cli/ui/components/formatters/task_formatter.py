"""Task-specific formatting for interactive selection (delegates to shared)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flow.cli.ui.formatters.shared_task import (
    TaskFormatter as _BaseTaskFormatter,
)
from flow.cli.ui.formatters.shared_task import (
    format_task_duration as format_task_duration,
)

if TYPE_CHECKING:
    from flow.cli.ui.components.models import SelectionItem
    from flow.sdk.models import Task


class TaskFormatter(_BaseTaskFormatter):
    """Formats tasks for display in the interactive selector.

    Inherits shared formatting logic and adds selection helpers.
    """

    @staticmethod
    def to_selection_item(task: Task) -> SelectionItem:
        """Convert a Task to a SelectionItem for interactive lists."""
        from flow.cli.ui.components.models import SelectionItem

        subtitle_parts: list[str] = []

        # Add duration/age
        duration = format_task_duration(task)
        if duration != "unknown":
            subtitle_parts.append(duration)

        # Add machine type if available
        if getattr(task, "machine_type", None):
            subtitle_parts.append(str(task.machine_type))

        # Add region if available
        if getattr(task, "region", None):
            subtitle_parts.append(str(task.region))

        subtitle = " • ".join(subtitle_parts) if subtitle_parts else None

        return SelectionItem(
            value=task,
            id=task.task_id,
            title=(getattr(task, "name", None) or task.task_id),
            subtitle=subtitle,
            status=getattr(task, "status", None),
            extra={"task": task},
        )

    @staticmethod
    def format_preview(item: SelectionItem[Task]) -> str:
        """Format a task preview for the detail pane."""
        task = item.value
        lines: list[str] = []

        lines.append(f"Task: {getattr(task, 'name', None) or task.task_id}")
        if hasattr(task, "status"):
            lines.append(f"Status: {task.status}")

        if getattr(task, "started_at", None):
            lines.append(f"Started: {task.started_at}")
        if getattr(task, "completed_at", None):
            lines.append(f"Completed: {task.completed_at}")

        duration = format_task_duration(task)
        if duration != "unknown":
            lines.append(f"Duration: {duration}")

        if getattr(task, "machine_type", None):
            lines.append(f"Machine: {task.machine_type}")

        if getattr(task, "region", None):
            lines.append(f"Region: {task.region}")

        if getattr(task, "description", None):
            lines.append("")
            lines.append("Description:")
            lines.append(str(task.description))

        return "\n".join(lines)


__all__ = ["TaskFormatter", "format_task_duration"]
