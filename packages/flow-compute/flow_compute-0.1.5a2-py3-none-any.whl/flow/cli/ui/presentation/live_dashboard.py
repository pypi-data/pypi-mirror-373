"""Live dashboard for real-time task monitoring.

Provides an interactive dashboard with auto-refresh, metrics display,
and keyboard controls for monitoring Flow tasks.
"""

import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from flow.cli.ui.presentation.task_presenter import DisplayOptions, TaskPresenter
from flow.cli.ui.presentation.task_renderer import TaskTableRenderer
from flow.cli.utils.animations import animation_engine
from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.client import Flow
from flow.sdk.models import Task, TaskStatus


@dataclass
class TaskMetrics:
    """Aggregated task metrics."""

    total_tasks: int = 0
    active_tasks: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    gpu_hours: float = 0.0
    success_rate: float = 0.0
    avg_wait_time: timedelta = timedelta()
    avg_runtime: timedelta = timedelta()


@dataclass
class DashboardState:
    """Current dashboard state."""

    tasks: list[Task]
    metrics: TaskMetrics
    last_update: datetime
    filter_status: str | None = None
    sort_by: str = "created"
    paused: bool = False
    selected_task_idx: int = 0


class MetricsCollector:
    """Collects and calculates task metrics."""

    def __init__(self, flow_client: Flow):
        """Initialize metrics collector.

        Args:
            flow_client: Flow client instance
        """
        self.flow_client = flow_client

    def calculate_metrics(self, tasks: list[Task]) -> TaskMetrics:
        """Calculate metrics from task list.

        Args:
            tasks: List of tasks

        Returns:
            Calculated metrics
        """
        metrics = TaskMetrics()

        if not tasks:
            return metrics

        metrics.total_tasks = len(tasks)

        # Count by status
        status_counts = defaultdict(int)
        for task in tasks:
            status_counts[task.status] += 1

        metrics.active_tasks = status_counts[TaskStatus.RUNNING]
        metrics.pending_tasks = status_counts[TaskStatus.PENDING]
        metrics.completed_tasks = status_counts[TaskStatus.COMPLETED]
        metrics.failed_tasks = status_counts[TaskStatus.FAILED]

        # Calculate success rate
        finished_tasks = metrics.completed_tasks + metrics.failed_tasks
        if finished_tasks > 0:
            metrics.success_rate = metrics.completed_tasks / finished_tasks * 100

        # Calculate GPU hours and times
        total_wait_time = timedelta()
        total_runtime = timedelta()
        wait_count = 0
        run_count = 0

        for task in tasks:
            # GPU hours (approximate based on runtime)
            if task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]:
                if task.created_at:
                    runtime = datetime.now() - task.created_at
                    gpu_multiplier = self._get_gpu_multiplier(task.instance_type)
                    metrics.gpu_hours += runtime.total_seconds() / 3600 * gpu_multiplier

            # Wait times (for pending tasks that became running)
            if task.status != TaskStatus.PENDING and task.created_at:
                # Approximate wait time as 10% of total age for completed tasks
                wait_time = (datetime.now() - task.created_at) * 0.1
                total_wait_time += wait_time
                wait_count += 1

            # Runtime (for running/completed tasks)
            if task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED] and task.created_at:
                runtime = datetime.now() - task.created_at
                total_runtime += runtime
                run_count += 1

        # Calculate averages
        if wait_count > 0:
            metrics.avg_wait_time = total_wait_time / wait_count
        if run_count > 0:
            metrics.avg_runtime = total_runtime / run_count

        return metrics

    def _get_gpu_multiplier(self, instance_type: str | None) -> float:
        """Get GPU count multiplier from instance type.

        Args:
            instance_type: Instance type string

        Returns:
            Number of GPUs (approximate)
        """
        if not instance_type:
            return 1.0

        # Simple heuristic based on instance type
        if "8x" in instance_type.lower():
            return 8.0
        elif "4x" in instance_type.lower():
            return 4.0
        elif "2x" in instance_type.lower():
            return 2.0
        else:
            return 1.0


class LiveDashboard:
    """Interactive live monitoring dashboard for Flow tasks."""

    def __init__(
        self, flow_client: Flow, refresh_rate: float = 2.0, console: Console | None = None
    ):
        """Initialize live dashboard.

        Args:
            flow_client: Flow client instance
            refresh_rate: Refresh interval in seconds
            console: Console instance (optional)
        """
        self.flow_client = flow_client
        self.refresh_rate = refresh_rate
        self.console = console or theme_manager.create_console()

        self.task_presenter = TaskPresenter(self.console)
        self.task_renderer = TaskTableRenderer(self.console)
        self.metrics_collector = MetricsCollector(flow_client)

        self.state = DashboardState(tasks=[], metrics=TaskMetrics(), last_update=datetime.now())

        self._stop_event = threading.Event()
        self._update_thread = None

    def _create_layout(self) -> Layout:
        """Create dashboard layout.

        Returns:
            Configured layout
        """
        layout = Layout()

        # Main layout structure
        layout.split_column(
            Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=4)
        )

        # Body split into tasks and metrics
        layout["body"].split_row(Layout(name="tasks", ratio=3), Layout(name="metrics", ratio=1))

        return layout

    def _render_header(self) -> Panel:
        """Render dashboard header.

        Returns:
            Header panel
        """
        title = Text("Flow Task Monitor", style="bold")

        # Add live indicator with animation
        if not self.state.paused:
            phase = animation_engine.get_phase(1.0)
            live_indicator = animation_engine.pulse_effect("● LIVE", phase, 0.8)
        else:
            live_indicator = Text("● PAUSED", style=theme_manager.get_color("warning"))

        # Status line
        status_parts = []
        if self.state.filter_status:
            status_parts.append(f"Filter: {self.state.filter_status}")
        status_parts.append(f"Sort: {self.state.sort_by}")
        status_parts.append(f"Updated: {self.state.last_update.strftime('%H:%M:%S')}")

        status_line = Text(" | ".join(status_parts), style=theme_manager.get_color("muted"))

        # Combine elements
        from rich.console import Group

        content = Group(Align.center(title), Align.center(live_indicator))

        return Panel(
            content, box=box.ROUNDED, border_style=theme_manager.get_color("accent"), padding=(0, 1)
        )

    def _render_tasks(self) -> Panel:
        """Render tasks table.

        Returns:
            Tasks panel
        """
        # Use existing task renderer with responsive layout
        layout = self.task_renderer.terminal.get_responsive_layout()
        density_config = self.task_renderer.terminal.get_density_config(layout["density"])

        # Create table
        table = self.task_renderer.create_table(
            None,
            layout,
            density_config,  # No title on table itself, will use panel title
        )

        # Add columns
        self.task_renderer.add_responsive_columns(table, layout)

        # Add rows with selection highlight
        for idx, task in enumerate(self.state.tasks[:20]):  # Limit to 20 for performance
            row_data = self.task_renderer.build_row_data(task, layout)

            # Highlight selected row
            if idx == self.state.selected_task_idx:
                row_data = [f"[reverse]{cell}[/reverse]" for cell in row_data]

            table.add_row(*row_data)

        return Panel(
            table,
            title="Active Tasks",
            box=box.ROUNDED,
            border_style=theme_manager.get_color("border"),
        )

    def _render_metrics(self) -> Panel:
        """Render metrics panel.

        Returns:
            Metrics panel
        """
        metrics = self.state.metrics

        # Create metrics table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style=theme_manager.get_color("muted"))
        table.add_column("Value", style="bold")

        # Task counts
        table.add_row("Active", f"{metrics.active_tasks}")
        table.add_row("Pending", f"{metrics.pending_tasks}")
        table.add_row("Completed", f"{metrics.completed_tasks}")
        table.add_row("Failed", f"{metrics.failed_tasks}")
        table.add_row("", "")  # Spacer

        # Performance metrics
        table.add_row("GPU Hours", f"{metrics.gpu_hours:.1f}")
        table.add_row("Success Rate", f"{metrics.success_rate:.1f}%")
        table.add_row("Avg Wait", self._format_duration(metrics.avg_wait_time))
        table.add_row("Avg Runtime", self._format_duration(metrics.avg_runtime))

        return Panel(
            table, title="Metrics", box=box.ROUNDED, border_style=theme_manager.get_color("border")
        )

    def _render_footer(self) -> Panel:
        """Render footer with controls.

        Returns:
            Footer panel
        """
        controls = [
            "[q]uit",
            "[p]ause" if not self.state.paused else "[r]esume",
            "[f]ilter",
            "[s]ort",
            "[↑↓] navigate",
            "[Enter] details",
            "[?] help",
        ]

        control_text = "  ".join(controls)

        return Panel(
            Align.center(control_text),
            box=box.ROUNDED,
            border_style=theme_manager.get_color("muted"),
            style=theme_manager.get_color("muted"),
        )

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display.

        Args:
            duration: Duration to format

        Returns:
            Formatted string
        """
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def _update_data(self):
        """Background thread to update data."""
        while not self._stop_event.is_set():
            if not self.state.paused:
                try:
                    # Fetch tasks
                    display_options = DisplayOptions(
                        show_all=False, status_filter=self.state.filter_status, limit=50
                    )

                    tasks = self.task_presenter.fetch_tasks(display_options)

                    # Update state
                    self.state.tasks = tasks
                    self.state.metrics = self.metrics_collector.calculate_metrics(tasks)
                    self.state.last_update = datetime.now()

                except Exception:
                    # Silently handle errors to keep dashboard running
                    pass

            self._stop_event.wait(self.refresh_rate)

    def generate_layout(self) -> Layout:
        """Generate current dashboard layout.

        Returns:
            Populated layout
        """
        layout = self._create_layout()

        # Populate sections
        layout["header"].update(self._render_header())
        layout["tasks"].update(self._render_tasks())
        layout["metrics"].update(self._render_metrics())
        layout["footer"].update(self._render_footer())

        return layout

    def run(self):
        """Run the live dashboard."""
        import select
        import sys
        import termios
        import tty

        # Start background update thread
        self._update_thread = threading.Thread(target=self._update_data, daemon=True)
        self._update_thread.start()

        # Wait a moment for initial data fetch
        time.sleep(0.5)

        # Check if running in a TTY
        if not sys.stdin.isatty():
            self.console.print("[error]Error:[/error] Live mode requires an interactive terminal")
            return

        # Save terminal settings
        try:
            old_settings = termios.tcgetattr(sys.stdin)
        except termios.error as e:
            from rich.markup import escape

            self.console.print(f"[error]Error:[/error] Cannot configure terminal: {escape(str(e))}")
            return

        try:
            # Set terminal to raw mode for key detection
            tty.setcbreak(sys.stdin.fileno())

            with Live(
                self.generate_layout(), console=self.console, refresh_per_second=4, screen=True
            ) as live:
                while True:
                    # Update display
                    live.update(self.generate_layout())

                    # Check for keyboard input with timeout
                    if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)

                        # Handle key presses
                        if key.lower() == "q":
                            break
                        elif key.lower() == "p":
                            self.state.paused = True
                        elif key.lower() == "r":
                            self.state.paused = False
                        elif key == "\x1b":  # ESC sequence
                            # Read the rest of the escape sequence
                            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                                seq = sys.stdin.read(2)
                                if seq == "[A":  # Up arrow
                                    self.state.selected_task_idx = max(
                                        0, self.state.selected_task_idx - 1
                                    )
                                elif seq == "[B":  # Down arrow
                                    self.state.selected_task_idx = min(
                                        len(self.state.tasks) - 1, self.state.selected_task_idx + 1
                                    )

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pass
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

            # Clean up
            self._stop_event.set()
            if self._update_thread:
                self._update_thread.join(timeout=5.0)
