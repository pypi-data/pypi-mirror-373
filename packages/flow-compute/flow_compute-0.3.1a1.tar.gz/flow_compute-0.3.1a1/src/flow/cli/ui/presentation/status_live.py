"""Presentation helpers for live status modes (table and compact)."""

from __future__ import annotations

import sys
import time

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.sdk.contracts import IClient
from flow.sdk.factory import create_client


def run_live_table(
    console,
    flow_client: IClient | None,
    *,
    show_all: bool,
    status_filter: str | None,
    limit: int,
    refresh_rate: float,
) -> None:
    if not sys.stdin.isatty():
        from flow.cli.utils.theme_manager import theme_manager as _tm

        console.print(
            f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] Live mode requires an interactive terminal"
        )
        return

    from rich.console import Group

    from flow.cli.ui.presentation.task_renderer import TaskTableRenderer
    from flow.cli.utils.task_fetcher import TaskFetcher

    flow_client = flow_client or create_client(auto_init=True)

    def get_display():
        try:
            fetcher = TaskFetcher(flow_client)
            tasks = fetcher.fetch_for_display(
                show_all=show_all, status_filter=status_filter, limit=limit
            )
        except Exception as e:
            from rich.markup import escape

            from flow.cli.utils.theme_manager import theme_manager as _tm

            return Text(f"Error fetching tasks: {escape(str(e))}", style=_tm.get_color("error"))

        if not tasks:
            return Text("No tasks found", style="dim")

        running = sum(
            1 for t in tasks if getattr(getattr(t, "status", None), "value", None) == "running"
        )
        pending = sum(
            1 for t in tasks if getattr(getattr(t, "status", None), "value", None) == "pending"
        )

        total_gpu_hours = 0.0
        for task in tasks:
            try:
                import re
                from datetime import datetime, timezone

                status_val = getattr(getattr(task, "status", None), "value", None)
                created_at = getattr(task, "created_at", None)
                if status_val in ["running", "completed", "failed"] and created_at is not None:
                    end_time = getattr(task, "completed_at", None) or datetime.now(timezone.utc)
                    created_at = (
                        created_at.replace(tzinfo=timezone.utc)
                        if getattr(created_at, "tzinfo", None) is None
                        else created_at
                    )
                    duration_hours = (end_time - created_at).total_seconds() / 3600.0
                    it = getattr(task, "instance_type", "") or ""
                    m = re.match(r"(\d+)x", str(it))
                    gpu_count = int(m.group(1)) if m else 1
                    total_gpu_hours += float(duration_hours) * float(gpu_count)
            except Exception:
                continue

        parts = []
        if running > 0:
            parts.append(f"{running} running")
        if pending > 0:
            parts.append(f"{pending} pending")
        if total_gpu_hours > 0:
            gpu_hrs_str = (
                f"{total_gpu_hours:.1f}" if total_gpu_hours >= 1 else f"{total_gpu_hours:.2f}"
            )
            parts.append(f"GPU-hrs: {gpu_hrs_str}")
        summary_line = " · ".join(parts) if parts else ""

        renderer = TaskTableRenderer(console)
        title = f"Tasks (showing up to {limit}"
        if not show_all:
            title += ", last 24 hours"
        title += ")"
        panel = renderer.render_task_list(
            tasks, title=title, show_all=show_all, limit=limit, return_renderable=True
        )
        if panel is None:
            from flow.cli.utils.theme_manager import theme_manager as _tm

            return Text("Error: Could not render tasks", style=_tm.get_color("error"))

        if summary_line:
            return Group(Text(summary_line, style="dim"), Text(""), panel)
        return panel

    with AnimatedEllipsisProgress(console, "Starting live status monitor", start_immediately=True):
        initial_display = get_display()

    if initial_display is None:
        from flow.cli.utils.theme_manager import theme_manager as _tm

        initial_display = Panel(
            "Initializing...",
            title="[bold accent]Status[/bold accent]",
            border_style=_tm.get_color("accent"),
        )

    with Live(
        initial_display,
        console=console,
        refresh_per_second=1 / max(0.05, refresh_rate),
        screen=True,
    ) as live:
        while True:
            try:
                display = get_display()
                if display:
                    live.update(display)
                time.sleep(refresh_rate)
            except KeyboardInterrupt:
                break

    from flow.cli.utils.theme_manager import theme_manager as _tm

    success_color = _tm.get_color("success")
    console.print(f"\n[{success_color}]Live monitor stopped.[/{success_color}]")


def safe_run_live_table(
    console,
    flow_client: IClient | None,
    *,
    show_all: bool,
    status_filter: str | None,
    limit: int,
    refresh_rate: float,
) -> None:
    try:
        run_live_table(
            console,
            flow_client,
            show_all=show_all,
            status_filter=status_filter,
            limit=limit,
            refresh_rate=refresh_rate,
        )
    except Exception as e:
        from rich.markup import escape

        console.print(f"[error]Error:[/error] {escape(str(e))}")


def run_live_compact(
    console,
    flow_client: IClient | None,
    *,
    show_all: bool,
    status_filter: str | None,
    limit: int,
    refresh_rate: float,
) -> None:
    if not sys.stdin.isatty():
        console.print("[error]Error:[/error] Live mode requires an interactive terminal")
        return

    from flow.cli.ui.presentation.alloc_renderer import BeautifulTaskRenderer
    from flow.cli.utils.task_fetcher import TaskFetcher

    renderer = BeautifulTaskRenderer(console)
    flow_client = flow_client or create_client(auto_init=True)
    fetcher = TaskFetcher(flow_client)

    def get_display():
        try:
            tasks = fetcher.fetch_for_display(
                show_all=show_all, status_filter=status_filter, limit=limit
            )
            renderer.advance_animation()
            return renderer.render_allocation_view(tasks)
        except Exception as e:
            from rich.markup import escape

            from flow.cli.utils.theme_manager import theme_manager as _tm

            return Panel(
                f"[{_tm.get_color('error')}]Error: {escape(str(e))}[/{_tm.get_color('error')}]",
                border_style=_tm.get_color("error"),
            )

    with AnimatedEllipsisProgress(console, "Starting compact monitor", start_immediately=True):
        initial_display = get_display()

    with Live(
        initial_display, console=console, refresh_per_second=2, screen=True, transient=True
    ) as live:
        while True:
            try:
                live.update(get_display())
                time.sleep(refresh_rate)
            except KeyboardInterrupt:
                break

    from flow.cli.utils.theme_manager import theme_manager as _tm2

    success_color = _tm2.get_color("success")
    console.print(f"\n[{success_color}]Live monitor stopped.[/{success_color}]")


def safe_run_live_compact(
    console,
    flow_client: IClient | None,
    *,
    show_all: bool,
    status_filter: str | None,
    limit: int,
    refresh_rate: float,
) -> None:
    try:
        run_live_compact(
            console,
            flow_client,
            show_all=show_all,
            status_filter=status_filter,
            limit=limit,
            refresh_rate=refresh_rate,
        )
    except Exception as e:
        from rich.markup import escape

        from flow.cli.utils.theme_manager import theme_manager as _tm

        console.print(
            f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] {escape(str(e))}"
        )
