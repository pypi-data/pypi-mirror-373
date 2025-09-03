"""Allocation view presentation wrappers."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from flow.cli.ui.presentation.alloc_renderer import BeautifulTaskRenderer
from flow.sdk.models import Task


def render_alloc_snapshot(console: Console, tasks: list[Task]) -> None:
    renderer = BeautifulTaskRenderer(console)
    panel = renderer.render_allocation_view(tasks)
    console.print(panel)


def render_alloc_live_frame(
    console: Console, tasks: list[Task], renderer: BeautifulTaskRenderer
) -> Panel:
    renderer.advance_animation()
    return renderer.render_allocation_view(tasks)
