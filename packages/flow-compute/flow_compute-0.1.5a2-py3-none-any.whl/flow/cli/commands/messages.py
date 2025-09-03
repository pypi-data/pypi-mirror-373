"""Common CLI message helpers to keep output consistent across commands.

Minimal helpers only; aim to reduce duplication without introducing heavy abstractions.
"""

from __future__ import annotations

from collections.abc import Iterable

from rich.console import Console

from flow.cli.commands.feedback import feedback
from flow.cli.ui.presentation.next_steps import render_next_steps_panel


def print_next_actions(console: Console, actions: Iterable[str]) -> None:
    """Render a compact, themed Next steps panel."""
    actions = [str(a) for a in (actions or []) if str(a).strip()]
    if not actions:
        return
    render_next_steps_panel(console, actions)


def print_yaml_usage_hint(example_name: str) -> None:
    """Show a compact info panel on how to save and submit YAML configs."""
    message = (
        "Save this to a file and submit:\n"
        f"  flow example {example_name} --show > job.yaml\n"
        "  flow run job.yaml"
    )
    feedback.info(message, title="How to use this config")


def print_submission_success(
    console: Console,
    task_ref: str,
    instance_type: str | None,
    commands: Iterable[str],
    warnings: Iterable[str] | None = None,
    subtitle: str | None = "You can safely exit and run the commands later",
) -> None:
    """Render a compact success panel after submission with commands and warnings."""
    lines = [
        f"[bold]{task_ref}[/bold]"
        + (f" on [accent]{instance_type}[/accent]" if instance_type else ""),
        "",
        "Commands:",
        "\n".join(list(commands)),
    ]
    warnings = list(warnings or [])
    if warnings:
        lines.extend(["", "[warning]Warnings:[/warning]"] + [f"  {w}" for w in warnings])
    feedback.success("\n".join(lines), title="Task submitted", subtitle=subtitle)
