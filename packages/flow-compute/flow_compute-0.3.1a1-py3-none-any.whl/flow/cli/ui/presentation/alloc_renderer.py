"""Presentation: allocation renderer for concise GPU task views.

Contains `BeautifulTaskRenderer`, moved from `cli/commands/alloc.py`.
This module only handles Rich renderables and lightweight UI state.
"""

from __future__ import annotations

from datetime import datetime, timezone

from rich import box
from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.models import Task


class BeautifulTaskRenderer:
    """Render GPU task allocations with hierarchical organization.

    Implements a state-based rendering system that groups tasks by execution
    status and provides progressive detail levels. Optimized for terminal
    display with ANSI color support and box-drawing characters.
    """

    STATUS_SYMBOLS = {
        "running": "●",
        "starting": "◐",
        "pending": "○",
        "completed": "✓",
        "failed": "✗",
        "paused": "⏸",
        "cancelled": "⊘",
    }

    STATUS_COLORS = {
        "running": "green",
        "starting": "bright_blue",
        "pending": "dim white",
        "completed": "dim green",
        "failed": "red",
        "paused": "dim yellow",
        "cancelled": "dim red",
    }

    def __init__(self, console: Console):
        self.console = console
        self._animation_frame = 0
        self.selected_index = 0
        self.show_details = False
        self.selected_task: Task | None = None
        self.tasks: list[Task] | None = None

    def render_interactive_view(self, tasks: list[Task]) -> RenderableType:
        self.tasks = tasks
        main_panel = self._render_task_list_interactive(tasks)
        if self.show_details and self.selected_task:
            from rich.columns import Columns

            detail_panel = self._render_task_detail_panel(self.selected_task)
            return Columns([main_panel, detail_panel], padding=1, expand=True)
        return main_panel

    def render_allocation_view(self, tasks: list[Task]) -> Panel:
        self.tasks = tasks

        active_tasks: list[Task] = []
        pending_tasks: list[Task] = []
        completed_tasks: list[Task] = []

        for task in tasks[:20]:
            status = self._get_display_status(task)
            if status in ["running", "starting"]:
                active_tasks.append(task)
            elif status == "pending":
                pending_tasks.append(task)
            else:
                completed_tasks.append(task)

        groups: list[RenderableType] = []

        try:
            hint = self._format_next_reservation_hint(tasks)
            if hint:
                groups.append(hint)
                groups.append(Text(""))
        except Exception:
            pass

        if active_tasks:
            groups.append(self._render_task_group(active_tasks, "Active", show_details=True))
            groups.append(Text(""))

        if pending_tasks:
            groups.append(self._render_task_group(pending_tasks, "Waiting", show_details=False))
            groups.append(Text(""))

        if completed_tasks:
            recent_completed = completed_tasks[:5]
            groups.append(
                self._render_task_group(recent_completed, "Recent", show_details=False, dim=True)
            )

        if not tasks:
            groups.append(self._render_empty_state())

        content = Group(*groups) if groups else Text("Initializing...", style="dim")

        return Panel(
            Align.center(content, vertical="middle"),
            title="[bold]GPU Resources[/bold]",
            title_align="center",
            border_style="bright_black",
            box=box.ROUNDED,
            padding=(1, 3),
            expand=False,
        )

    def _format_next_reservation_hint(self, tasks: list[Task]) -> Text | None:
        upcoming: list[tuple[datetime, Task]] = []
        for t in tasks:
            try:
                meta = getattr(t, "provider_metadata", {}) or {}
                res = meta.get("reservation")
                if not res:
                    continue
                start = res.get("start_time") or res.get("start_time_utc")
                if not start:
                    continue
                s = str(start).replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
                if dt > datetime.now(timezone.utc):
                    upcoming.append((dt, t))
            except Exception:
                continue
        if not upcoming:
            return None
        dt, t = sorted(upcoming, key=lambda x: x[0])[0]
        remaining = int((dt - datetime.now(timezone.utc)).total_seconds())
        minutes = max(0, remaining // 60)
        name = t.name or t.task_id
        txt = Text(justify="center")
        txt.append("Reserved window: ")
        txt.append(name, style="bold")
        txt.append(f" starts in {minutes} min", style="dim")
        return txt

    def _render_task_list_interactive(self, tasks: list[Task]) -> Panel:
        table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2), expand=True)
        table.add_column("selector", width=3)
        table.add_column("status", width=3)
        table.add_column("name", min_width=20)
        table.add_column("gpu", width=12)
        table.add_column("time", width=8)

        for idx, task in enumerate(tasks[:15]):
            status = self._get_display_status(task)
            symbol = self.STATUS_SYMBOLS.get(status, "?")
            color = self.STATUS_COLORS.get(status, "white")

            if idx == self.selected_index:
                selector = "▶"
                row_style = "bold accent"
            else:
                selector = " "
                row_style = None

            name = task.name or task.task_id[:8]
            if len(name) > 20:
                name = name[:17] + "..."

            gpu_info = self._format_gpu_elegant(
                task.instance_type, getattr(task, "num_instances", 1)
            )
            time_info = self._format_time_elegant(task)

            table.add_row(
                selector, f"[{color}]{symbol}[/{color}]", name, gpu_info, time_info, style=row_style
            )

        help_text = Text(
            "\n↑↓/jk: navigate  Enter: details  q: quit  r: refresh", style="dim", justify="center"
        )
        content = Group(table, help_text)

        from flow.cli.utils.theme_manager import theme_manager as _tm

        border = _tm.get_color("accent") if self.selected_index >= 0 else "bright_black"
        return Panel(
            content,
            title="[bold]GPU Resources[/bold] - Interactive Mode",
            title_align="center",
            border_style=border,
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _render_task_detail_panel(self, task: Task) -> Panel:
        lines: list[str] = []

        status = self._get_display_status(task)
        symbol = self.STATUS_SYMBOLS.get(status, "?")
        color = self.STATUS_COLORS.get(status, "white")

        lines.append(f"[bold]{task.name or task.task_id}[/bold]")
        lines.append(f"[{color}]{symbol} {status.upper()}[/{color}]\n")

        if task.instance_type:
            from flow.cli.ui.presentation.gpu_formatter import GPUFormatter

            gpu_display = GPUFormatter.format_ultra_compact(
                task.instance_type, getattr(task, "num_instances", 1)
            )
            lines.append(f"[bold]GPU:[/bold] {gpu_display}")
        if task.num_instances and task.num_instances > 1:
            lines.append(f"[bold]Nodes:[/bold] {task.num_instances}")
        if getattr(task, "region", None):
            lines.append(f"[bold]Region:[/bold] {task.region}")

        lines.append("")

        if getattr(task, "ssh_host", None):
            lines.append("[bold accent]Connection:[/bold accent]")
            lines.append(f"  IP: {task.ssh_host}")
            if getattr(task, "ssh_port", None):
                lines.append(f"  Port: {task.ssh_port}")
            if getattr(task, "name", None):
                lines.append(f"\n  [dim]flow ssh {task.name}[/dim]")

        lines.append("")
        if task.created_at:
            lines.append(f"[bold]Created:[/bold] {self._format_time_detailed(task.created_at)}")

        duration = self._format_duration_detailed(task)
        if duration:
            lines.append(f"[bold]Duration:[/bold] {duration}")

        if hasattr(task, "estimated_cost"):
            lines.append(
                f"\n[bold]Est. Cost:[/bold] ${getattr(task, 'estimated_cost', 0.0):.2f}/hr"
            )

        content = "\n".join(lines)
        return Panel(
            content,
            title="[bold]Task Details[/bold]",
            title_align="left",
            border_style=theme_manager.get_color("accent"),
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _render_task_group(
        self,
        tasks: list[Task],
        title: str,
        show_details: bool = True,
        dim: bool = False,
    ) -> Table:
        table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2), expand=False)
        table.add_column("status", width=3)
        table.add_column("name", min_width=20)
        if show_details:
            table.add_column("gpu", width=12)
            table.add_column("time", width=8)

        title_style = "dim white" if dim else "bold white"
        table.add_row(
            "",
            f"[{title_style}]── {title} ──[/{title_style}]",
            *([""] * (2 if show_details else 0)),
        )

        for task in tasks:
            status = self._get_display_status(task)
            symbol = self.STATUS_SYMBOLS.get(status, "?")
            color = self.STATUS_COLORS.get(status, "white")
            if status == "running" and not dim:
                if self._animation_frame % 4 < 2:
                    color = f"bright_{color}"

            name = task.name or task.task_id[:8]
            if len(name) > 20:
                name = name[:17] + "..."
            row: list[str] = [
                f"[{color}]{symbol}[/{color}]",
                f"[{('dim ' if dim else '')}white]{name}[/{('dim ' if dim else '')}white]",
            ]
            if show_details:
                gpu_info = self._format_gpu_elegant(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                row.append(f"[dim accent]{gpu_info}[/dim accent]")
                time_info = self._format_time_elegant(task)
                row.append(f"[dim white]{time_info}[/dim white]")
            table.add_row(*row)

        return table

    def _render_empty_state(self) -> Panel:
        gradient_chars = [".", "·", "•", "●", "•", "·", "."]
        frame = self._animation_frame % len(gradient_chars)
        lines = [
            "",
            "[dim]No active allocations[/dim]",
            "",
            f"[dim accent]{gradient_chars[frame]}  {gradient_chars[frame]}  {gradient_chars[frame]}[/dim accent]",
            "",
            "[white]flow run <config.yaml>[/white]",
            "[dim]or[/dim]",
            "[white]flow dev[/white]",
            "",
        ]
        content = "\n".join(lines)
        return Panel(content, border_style="dim", box=box.ROUNDED, padding=(2, 4))

    def _get_display_status(self, task: Task) -> str:
        # Reuse the shared display-status logic for consistency with `flow status`
        from flow.cli.ui.presentation.task_formatter import TaskFormatter

        return TaskFormatter.get_display_status(task)

    def _format_gpu_elegant(self, instance_type: str | None, num_instances: int = 1) -> str:
        from flow.cli.ui.presentation.gpu_formatter import GPUFormatter

        return GPUFormatter.format_ultra_compact(instance_type, num_instances)

    def _format_time_elegant(self, task: Task) -> str:
        if not getattr(task, "created_at", None):
            return "-"
        now = datetime.now(timezone.utc)
        created = (
            task.created_at.replace(tzinfo=timezone.utc)
            if getattr(task.created_at, "tzinfo", None) is None
            else task.created_at
        )
        delta = now - created
        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m"
        elif hours < 24:
            return f"{int(hours)}h"
        else:
            days = int(hours / 24)
            return f"{days}d"

    def _format_time_detailed(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def _format_duration_detailed(self, task: Task) -> str | None:
        if not getattr(task, "created_at", None):
            return None
        now = datetime.now(timezone.utc)
        created = (
            task.created_at.replace(tzinfo=timezone.utc)
            if getattr(task.created_at, "tzinfo", None) is None
            else task.created_at
        )
        if getattr(task, "completed_at", None):
            end = (
                task.completed_at.replace(tzinfo=timezone.utc)
                if getattr(task.completed_at, "tzinfo", None) is None
                else task.completed_at
            )
        else:
            end = now
        delta = end - created
        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            seconds = int(delta.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        elif hours < 24:
            h = int(hours)
            m = int((hours * 60) % 60)
            return f"{h}h {m}m"
        else:
            days = int(hours / 24)
            h = int(hours % 24)
            return f"{days}d {h}h"

    def advance_animation(self):
        self._animation_frame += 1

    def move_selection(self, direction: int):
        if not self.tasks:
            return
        self.selected_index = max(0, min(len(self.tasks) - 1, self.selected_index + direction))
        if 0 <= self.selected_index < len(self.tasks):
            self.selected_task = self.tasks[self.selected_index]

    def toggle_details(self):
        if self.tasks and 0 <= self.selected_index < len(self.tasks):
            self.show_details = not self.show_details
            self.selected_task = self.tasks[self.selected_index] if self.show_details else None
