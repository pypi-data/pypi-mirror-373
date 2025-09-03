"""Streamlined allocation view - abbreviated version of `flow status`.

Focused GPU resource display for rapid allocation assessment.
"""

import sys
import termios
import time
import tty

import click
from rich.live import Live
from rich.panel import Panel

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.presentation.alloc_renderer import BeautifulTaskRenderer
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.errors import AuthenticationError
from flow.sdk.client import Flow
from flow.sdk.factory import create_client


class AllocCommand(BaseCommand):
    """GPU resource allocation and monitoring command.

    Provides multiple execution modes for resource visualization:
    - Standard: Single snapshot of current allocations
    - Watch: Continuous monitoring with periodic refresh
    - Interactive: Keyboard-driven navigation (future)
    """

    def __init__(self):
        super().__init__()
        self.renderer = BeautifulTaskRenderer(console)

    @property
    def name(self) -> str:
        return "alloc"

    @property
    def help(self) -> str:
        return "Streamlined GPU allocations (abbreviated `flow status`)"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        # @click.option("--interactive", "-i", is_flag=True, help="Interactive mode with keyboard navigation")  # Reserved for future implementation
        @click.option("--watch", "-w", is_flag=True, help="Continuous monitoring with auto-refresh")
        @click.option("--gpus", type=int, help="Request specific GPU count (future)")
        @click.option("--type", "gpu_type", help="Specify GPU model (e.g., h100, a100)")
        @click.option(
            "--refresh-rate",
            default=2.0,
            type=float,
            help="Update interval in seconds (default: 2.0)",
        )
        def alloc(watch: bool, gpus: int | None, gpu_type: str | None, refresh_rate: float):
            """Streamlined GPU allocation view - abbreviated version of `flow status`.

            Focused display optimized for rapid resource assessment.
            Use `flow status` for comprehensive task details and metrics.

            \b
            Examples:
                flow alloc              # Quick allocation snapshot
                flow alloc --watch      # Live GPU monitoring
                flow alloc --refresh-rate 5  # Custom refresh interval
            """
            self._execute(False, watch, gpus, gpu_type, refresh_rate)  # Interactive mode reserved

        return alloc

    def _execute(
        self,
        interactive: bool,
        watch: bool,
        gpus: int | None,
        gpu_type: str | None,
        refresh_rate: float,
    ) -> None:
        """Execute allocation command in specified mode.

        Args:
            interactive: Enable keyboard navigation mode.
            watch: Enable continuous monitoring.
            gpus: Requested GPU count (future feature).
            gpu_type: Requested GPU model (future feature).
            refresh_rate: Update interval for watch mode.
        """

        # Allocation features pending implementation
        if gpus or gpu_type:
            console.print("[dim]Allocation request noted. Displaying current resources...[/dim]\n")
            time.sleep(1)

        try:
            flow_client = create_client(auto_init=True)

            if interactive:
                self._run_interactive_mode(flow_client)
            elif watch:
                self._run_watch_mode(flow_client, refresh_rate)
            else:
                # Standard mode: single snapshot with progress indicator
                progress = AnimatedEllipsisProgress(
                    console,
                    "Fetching GPU allocations",
                    start_immediately=True,
                )

                with progress:
                    from flow.cli.services.alloc_service import AllocService
                    from flow.cli.ui.presentation.alloc_view import render_alloc_snapshot

                    tasks = AllocService(flow_client).list_tasks_for_allocation(limit=30)
                    render_alloc_snapshot(console, tasks)

                # Context-aware next steps
                try:
                    has_active = any(
                        getattr(t, "status", None)
                        and getattr(t.status, "value", str(t.status)) in ("running", "starting")
                        for t in tasks
                    )
                    actions: list[str] = []
                    if has_active:
                        actions = [
                            "Inspect tasks: [accent]flow status[/accent]",
                            "SSH into a task: [accent]flow ssh 1[/accent]",
                            "Stream logs: [accent]flow logs 1 -f[/accent]",
                        ]
                    else:
                        actions = [
                            "Submit a job: [accent]flow run <config.yaml>[/accent]",
                            "Start a dev VM: [accent]flow dev[/accent]",
                        ]
                    self.show_next_actions(actions)
                except Exception:
                    pass

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))

    def _run_interactive_mode(self, flow_client: Flow) -> None:
        """Execute interactive mode with keyboard-driven navigation.

        Provides vim-style navigation (j/k) and arrow key support for
        task selection and detail viewing.

        Args:
            flow_client: Authenticated Flow API client.
        """

        if not sys.stdin.isatty():
            console.print("[error]Error:[/error] Interactive mode requires a terminal")
            return

        from flow.cli.services.alloc_service import AllocService

        service = AllocService(flow_client)

        # Get initial tasks
        tasks = service.list_tasks_for_allocation(limit=30)

        def get_display():
            """Generate current display state.

            Returns:
                RenderableType: Current task view with selection.
            """
            nonlocal tasks
            return self.renderer.render_interactive_view(tasks)

        def get_key():
            """Read single keystroke from terminal.

            Handles multi-byte sequences for arrow keys.

            Returns:
                str: Key identifier or character.
            """
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)

                # Parse ANSI escape sequences for arrow keys
                if ch == "\x1b":
                    ch2 = sys.stdin.read(1)
                    if ch2 == "[":
                        ch3 = sys.stdin.read(1)
                        if ch3 == "A":
                            return "up"
                        elif ch3 == "B":
                            return "down"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        try:
            with Live(
                get_display(),
                console=console,
                refresh_per_second=10,  # Smooth for keyboard nav
                screen=True,
                transient=True,
            ) as live:
                while True:
                    key = get_key()

                    if key in ["q", "\x03"]:  # Quit on 'q' or Ctrl+C
                        break
                    elif key in ["up", "k"]:
                        self.renderer.move_selection(-1)
                        live.update(get_display())
                    elif key in ["down", "j"]:
                        self.renderer.move_selection(1)
                        live.update(get_display())
                    elif key in ["\r", "\n"]:  # Toggle details on Enter
                        self.renderer.toggle_details()
                        live.update(get_display())
                    elif key == "r":  # Manual refresh
                        tasks = service.list_tasks_for_allocation(limit=30)
                        self.renderer.tasks = tasks
                        live.update(get_display())

            console.clear()
            console.print("[dim]Interactive mode ended[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted[/dim]")
        except Exception as e:
            from rich.markup import escape

            console.print(f"[error]Error:[/error] {escape(str(e))}")

    def _run_watch_mode(self, flow_client: Flow, refresh_rate: float) -> None:
        """Execute continuous monitoring mode with periodic updates.

        Refreshes task display at specified intervals with animated
        status indicators for active tasks.

        Args:
            flow_client: Authenticated Flow API client.
            refresh_rate: Seconds between display updates.
        """

        if not sys.stdin.isatty():
            console.print("[error]Error:[/error] Watch mode requires an interactive terminal")
            return

        from flow.cli.utils.task_fetcher import TaskFetcher

        fetcher = TaskFetcher(flow_client)

        def get_display():
            """Generate display with incremented animation frame.

            Returns:
                Panel: Current task allocation view or error panel.
            """
            try:
                tasks = service.list_tasks_for_allocation(limit=30)
                return render_alloc_live_frame(console, tasks, self.renderer)
            except Exception as e:
                from rich.markup import escape

                from flow.cli.utils.theme_manager import theme_manager as _tm

                return Panel(
                    f"[{_tm.get_color('error')}]Error: {escape(str(e))}[/{_tm.get_color('error')}]",
                    border_style=_tm.get_color("error"),
                )

        try:
            # Initial data fetch with progress indicator
            with AnimatedEllipsisProgress(
                console,
                "Starting allocation monitor",
                start_immediately=True,
            ) as progress:
                initial_display = get_display()

            with Live(
                initial_display,
                console=console,
                refresh_per_second=2,  # Animation frame rate
                screen=True,
                transient=True,
            ) as live:
                while True:
                    try:
                        live.update(get_display())
                        time.sleep(refresh_rate)
                    except KeyboardInterrupt:
                        break

            console.clear()
            console.print("[dim]Allocation monitor stopped[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]Stopped[/dim]")


# Module-level command instance for CLI registration
command = AllocCommand()
