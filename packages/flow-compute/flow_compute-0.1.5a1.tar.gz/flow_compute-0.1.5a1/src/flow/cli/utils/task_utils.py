"""Small shared task utilities for commands."""

from __future__ import annotations

from flow.sdk.models import Task


def validate_node_index(task: Task, node: int) -> None:
    """Validate that node index is in range for a (possibly multi-instance) task.

    Raises SystemExit(1) with a user-friendly message if invalid.
    """
    from flow.cli.utils.theme_manager import theme_manager

    console = theme_manager.create_console()

    is_multi_instance = hasattr(task, "num_instances") and (task.num_instances or 1) > 1
    if node is None:
        return
    if is_multi_instance:
        total = int(getattr(task, "num_instances", 1) or 1)
        if node < 0 or node >= total:
            console.print(
                f"[error]Error: Node index {node} out of bounds (task has {total} nodes)[/error]"
            )
            console.print(f"Valid nodes: 0-{total - 1}")
            raise SystemExit(1)
    else:
        if node != 0:
            ref = task.name or task.task_id
            console.print(f"[error]Error: Task '{ref}' is single-instance[/error]")
            console.print("Remove --node flag for single-instance tasks")
            raise SystemExit(1)
