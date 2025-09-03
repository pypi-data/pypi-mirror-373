"""Presentation helpers for verbose status help sections."""

from __future__ import annotations

from rich.panel import Panel

from flow.cli.utils.theme_manager import theme_manager


def render_verbose_help(console) -> None:
    """Render the verbose help content for `flow status --verbose`.

    Keeps status command lean by centralizing formatted explanatory text.
    """
    accent = theme_manager.get_color("accent")
    border = theme_manager.get_color("table.border")

    sections: list[str] = []
    sections.append("[bold]Filtering options:[/bold]")
    sections.extend(
        [
            "  flow status                       # Show active tasks (running/pending)",
            "  flow status --all                 # Show all tasks (not just active)",
            "  flow status --state running       # Filter by specific status",
            "  flow status --state pending       # Tasks waiting for resources",
            "  flow status --limit 50            # Show more results",
            "",
        ]
    )

    sections.append("[bold]Task details:[/bold]")
    sections.extend(
        [
            "  flow status task-abc123           # View specific task",
            "  flow status my-training           # Find by name",
            "  flow status training-v2           # Partial name match",
            "",
        ]
    )

    sections.append("[bold]Status values:[/bold]")
    sections.extend(
        [
            "  • pending     - Waiting for resources",
            "  • running     - Actively executing",
            "  • paused      - Temporarily stopped (no billing)",
            "  • preempting  - Will be terminated soon",
            "  • completed   - Finished successfully",
            "  • failed      - Terminated with error",
            "  • cancelled   - Cancelled by user",
            "",
        ]
    )

    sections.append("[bold]Monitoring workflows:[/bold]")
    sections.extend(
        [
            "  # Live updating status display",
            "  flow status --watch",
            "  flow status -w --refresh-rate 1    # Update every second",
            "",
            "  # Using system watch command",
            "  watch -n 5 'flow status --state running'",
            "",
            "  # Export for analysis",
            "  flow status --all --json > tasks.json",
            "",
            "  # Check failed tasks",
            "  flow status --state failed --limit 10",
            "",
        ]
    )

    sections.append("[bold]Next actions:[/bold]")
    sections.extend(
        [
            "  • View logs: flow logs [task.name]<task-name>[/task.name]",
            "  • Connect: flow ssh [task.name]<task-name>[/task.name]",
            "  • Cancel: flow cancel [task.name]<task-name>[/task.name]",
            "  • Check health: flow health --task [task.name]<task-name>[/task.name]",
        ]
    )

    content = "\n".join(sections)
    panel = Panel(
        content,
        title=f"[bold {accent}]Task Status and Monitoring[/bold {accent}]",
        border_style=border,
        padding=(1, 2),
    )
    console.print(panel)
