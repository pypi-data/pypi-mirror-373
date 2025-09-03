"""Cancel command - terminate running GPU tasks.

Allows terminating running or pending tasks with optional confirmation.

Examples:
    # Cancel a specific task
    $ flow cancel my-training-job

    # Cancel last task from status (using index)
    $ flow cancel 1

    # Cancel all dev tasks without confirmation (wildcard)
    $ flow cancel --name-pattern "dev-*" --yes

Command Usage:
    flow cancel TASK_ID_OR_NAME [OPTIONS]

The command will:
- Verify the task exists and is cancellable
- Prompt for confirmation (unless --yes is used)
- Send cancellation request to the provider
- Display cancellation status

Note:
    Only tasks in 'pending' or 'running' state can be cancelled.
    Completed or failed tasks cannot be cancelled.
"""

from __future__ import annotations

import fnmatch
import os
import re

import click

# Removed test-only re-export of resolver; import from canonical module in tests as needed
from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.utils import maybe_show_auto_status
from flow.cli.ui.formatters import GPUFormatter, TaskFormatter
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.errors import AuthenticationError

# Back-compat: expose Flow for tests that patch flow.cli.commands.cancel.Flow
from flow.sdk.client import Flow as Flow
from flow.sdk.factory import create_client
from flow.sdk.models import Task, TaskStatus


def _invalidate_task_prefetch_cache():
    try:
        from flow.cli.utils.prefetch import _CACHE  # type: ignore

        for k in ("tasks_running", "tasks_pending", "tasks_all"):
            if hasattr(_CACHE, "_data"):
                _CACHE._data.pop(k, None)
    except Exception:
        pass


from flow.cli.utils.task_index_cache import TaskIndexCache


class CancelCommand(BaseCommand, TaskOperationCommand):
    """Cancel a running task."""

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "cancel"

    @property
    def help(self) -> str:
        return """Cancel GPU tasks - pattern matching uses wildcards by default
        
        Example: flow cancel -n 'dev-*'"""

    # Progress/selection behavior: fetch under spinner; stop spinner before confirmation
    @property
    def prefer_fetch_before_selection(self) -> bool:  # type: ignore[override]
        return True

    @property
    def stop_spinner_before_confirmation(self) -> bool:  # type: ignore[override]
        return True

    # Spinner label for the fetch phase
    @property
    def _fetch_spinner_label(self) -> str:  # type: ignore[override]
        return "Looking up tasks to cancel"

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
        @click.option("--all", is_flag=True, help="Cancel all running tasks")
        @click.option(
            "--name-pattern",
            "-n",
            help="Cancel tasks matching wildcard pattern (e.g., 'dev-*', '*-gpu-8x*', 'train-v?'). Use --regex for regex.",
        )
        @click.option("--regex", is_flag=True, help="Treat pattern as regex instead of wildcard")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and patterns")
        @click.option(
            "--interactive/--no-interactive",
            default=None,
            help="Force interactive selector on/off regardless of terminal autodetect",
        )
        # @demo_aware_command()
        @cli_error_guard(self)
        def cancel(
            task_identifier: str,  # Optional at runtime, Click passes ''/None if omitted
            yes: bool,
            all: bool,
            name_pattern: str,  # Optional at runtime
            regex: bool,
            verbose: bool,
            interactive: bool | None,
        ):
            """Cancel a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow cancel                       # Interactive task selector
                flow cancel my-training           # Cancel by name
                flow cancel task-abc123           # Cancel by ID
                flow cancel -n 'dev-*' --yes      # Cancel tasks starting with 'dev-'
                flow cancel --all --yes           # Cancel all running tasks

            Pattern matching uses wildcards by default:
                flow cancel -n 'dev-*'           # Matches: dev-1, dev-test, dev-experiment
                flow cancel -n '*-gpu-8x*'       # Matches tasks mentioning 8x GPU
                flow cancel -n 'train-v?'        # Single character wildcard
            Use --regex for advanced regex patterns:
                flow cancel -n '^gpu-test-' --regex     # Start anchor
                flow cancel -n '.*-v[0-9]+' --regex     # Version pattern

            Use 'flow cancel --verbose' for advanced pattern matching examples.
            """
            if verbose:
                console.print("\n[bold]Pattern Matching Examples[/bold]\n")

                console.print("[bold]Wildcard patterns (default):[/bold]")
                console.print(
                    "  flow cancel -n 'dev-*'                # Cancel all starting with dev-"
                )
                console.print("  flow cancel -n '*-gpu-8x*'            # Match GPU type")
                console.print(
                    "  flow cancel -n 'train-v?'             # Single character wildcard\n"
                )

                console.print("[bold]Regex patterns (with --regex flag):[/bold]")
                console.print(
                    "  flow cancel -n '^dev-' --regex        # Matches tasks starting with 'dev-'"
                )
                console.print(
                    "  flow cancel -n 'dev-$' --regex        # Matches tasks ending with 'dev-'"
                )
                console.print(
                    "  flow cancel -n '.*-v[0-9]+' --regex  # Version pattern (e.g., app-v1, test-v23)"
                )
                console.print("  flow cancel -n '^test-.*-2024' --regex   # Complex matching")
                console.print(
                    "  flow cancel -n 'gpu-(test|prod)' --regex # Match gpu-test OR gpu-prod\n"
                )

                console.print(
                    "[warning]Note: When using wildcards (default), quote them to prevent shell expansion:[/warning]"
                )
                console.print("  [success]✓ CORRECT:[/success]  flow cancel -n 'gpu-test-*'")
                console.print(
                    "  [error]✗ WRONG:[/error]    flow cancel -n gpu-test-*   # Shell expands *\n"
                )

                console.print("[bold]Batch operations:[/bold]")
                console.print(
                    "  flow cancel --all                       # Cancel all (with confirmation)"
                )
                console.print("  flow cancel --all --yes                 # Force cancel all\n")

                console.print("[bold]Common workflows:[/bold]")
                console.print("  • Cancel all dev tasks: flow cancel -n 'dev-*' --yes")
                console.print("  • Clean up test tasks: flow cancel -n '*test*' --yes")
                console.print("  • Cancel specific prefix: flow cancel -n 'training-v2-*' --yes")
                console.print("  • Cancel by suffix: flow cancel -n '*-temp' --yes\n")
                return

            # Interactive toggle via flag overrides autodetect
            if interactive is True:
                os.environ["FLOW_FORCE_INTERACTIVE"] = "true"
            elif interactive is False:
                os.environ["FLOW_NONINTERACTIVE"] = "1"

            # Ensure a client variable exists for subsequent logic. It may be
            # initialized below or passed into _execute where a client will be
            # created as needed.
            client = None

            # Selection grammar: allow batch cancel via indices (works after 'flow status')
            if task_identifier:
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err

                    error_color = _tm_err.get_color("error")
                    console.print(f"[{error_color}]{err}[/{error_color}]")
                    return
                if ids is not None:
                    # Echo expansion
                    cache = TaskIndexCache()
                    display_names: list[str] = []
                    for tid in ids:
                        cached = cache.get_cached_task(tid)
                        name = (cached or {}).get("name") if cached else None
                        display_names.append(name or (tid[:12] + "…"))
                    console.print(
                        f"[dim]Selection {task_identifier} → {', '.join(display_names)}[/dim]"
                    )
                    # Confirm unless --yes
                    if not yes:
                        if not click.confirm(f"Cancel {len(ids)} task(s)?"):
                            console.print("[dim]Cancellation aborted[/dim]")
                            return
                    # Execute cancellations one by one
                    # Reuse one Flow client instance (patchable in tests)
                    _client = create_client(auto_init=True)
                    for tid in ids:
                        try:
                            self.execute_on_task(
                                task=_client.get_task(tid),
                                client=_client,
                                yes=True,
                                suppress_next_steps=True,
                            )
                        except Exception as e:
                            from rich.markup import escape

                            from flow.cli.utils.theme_manager import theme_manager as _tm_fail

                            error_color = _tm_fail.get_color("error")
                            console.print(
                                f"[{error_color}]✗[/{error_color}] Failed to cancel {tid[:12]}…: {escape(str(e))}"
                            )
                    # After batch, invalidate caches/snapshots and kick background refresh
                    try:
                        from flow.cli.utils.prefetch import (
                            invalidate_cache_for_current_context as _inv_ctx,
                        )
                        from flow.cli.utils.prefetch import (
                            invalidate_snapshots as _inv_snap,
                        )
                        from flow.cli.utils.prefetch import (
                            refresh_active_task_caches as _rf_active,
                        )
                        from flow.cli.utils.prefetch import (
                            refresh_all_tasks_cache as _rf_all,
                        )

                        # Preserve index cache to keep :N shortcuts stable for a short window
                        # (Consistency with single-task cancellation path)

                        _inv_ctx(["tasks_running", "tasks_pending", "tasks_all"])
                        _inv_snap(["tasks_running", "tasks_pending", "tasks_all"])
                        import threading as _th

                        _th.Thread(target=_rf_active, daemon=True).start()
                        _th.Thread(target=_rf_all, daemon=True).start()
                    except Exception:
                        pass
                    # Show next steps once after batch
                    self.show_next_actions(
                        [
                            "View all tasks: [accent]flow status[/accent]",
                            "Submit a new task: [accent]flow run <config.yaml>[/accent]",
                        ]
                    )
                    return
            # For non-batch flows, create and reuse a single client
            if client is None:
                try:
                    client = create_client(auto_init=True)
                except AuthenticationError:
                    self.handle_auth_error()
                    return

            self._execute(task_identifier, yes, all, name_pattern, regex, flow_client=client)

        return cancel

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show cancellable tasks."""
        return TaskFilter.cancellable

    def get_selection_title(self) -> str:
        return "Select a task to cancel"

    def get_no_tasks_message(self) -> str:
        return "No running tasks to cancel"

    # Command execution
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute cancellation on the selected task."""
        yes = kwargs.get("yes", False)
        suppress_next_steps = kwargs.get("suppress_next_steps", False)

        # Double-check task is still cancellable
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            status_str = str(task.status).replace("TaskStatus.", "").lower()
            console.print(
                f"[warning]Task '{task.name or task.task_id}' is already {status_str}[/warning]"
            )
            return

        # Show confirmation with task details
        if not yes:
            self._show_cancel_confirmation(task)

            # Simple, focused confirmation prompt
            if not click.confirm("\nProceed with cancellation?", default=False):
                console.print("[dim]Cancellation aborted[/dim]")
                return

        # StepTimeline progress
        from flow.cli.utils.step_progress import StepTimeline

        timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
        timeline.start()
        step_idx = timeline.add_step(f"Cancelling {task.name or task.task_id}", show_bar=False)
        timeline.start_step(step_idx)
        try:
            client.cancel(task.task_id)
            # Reflect cancellation in the local task object for immediate UX/tests
            try:
                task.status = TaskStatus.CANCELLED
            except Exception:
                pass
            timeline.complete_step()
        except Exception as e:
            timeline.fail_step(str(e))
            timeline.finish()
            raise
        finally:
            try:
                timeline.finish()
            except Exception:
                pass

        # Success message
        from flow.cli.utils.theme_manager import theme_manager as _tm

        success_color = _tm.get_color("success")
        console.print(
            f"\n[{success_color}]✓[/{success_color}] Cancelled [bold]{task.name or task.task_id}[/bold]"
        )

        # Show next actions (suppress in batch mode)
        if not suppress_next_steps:
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow run <config.yaml>[/accent]",
                ]
            )

        # Invalidate stale task lists and trigger a refresh after cancellation
        try:
            from flow.cli.utils.prefetch import (
                invalidate_cache_for_current_context,
                invalidate_snapshots,
                refresh_active_task_caches,
                refresh_all_tasks_cache,
            )

            # NOTE: We do NOT clear the index cache here anymore. The index cache
            # should only be updated by list-style commands (flow status, flow list).
            # This preserves the user's ability to use index shortcuts for the
            # promised 5-minute duration.

            invalidate_cache_for_current_context(["tasks_running", "tasks_pending", "tasks_all"])
            # Also drop on-disk snapshots so a fresh CLI process won't rehydrate stale lists
            invalidate_snapshots(["tasks_running", "tasks_pending", "tasks_all"])
            import threading

            def _refresh():
                try:
                    refresh_active_task_caches()
                    refresh_all_tasks_cache()
                except Exception:
                    pass

            threading.Thread(target=_refresh, daemon=True).start()
        except Exception:
            pass

        # Show a compact status snapshot after state change
        try:
            maybe_show_auto_status(
                focus=(task.name or task.task_id), reason="After cancellation", show_all=False
            )
        except Exception:
            pass

    def _show_cancel_confirmation(self, task: Task) -> None:
        """Show a confirmation panel with task details."""
        from datetime import datetime, timezone

        from rich.panel import Panel
        from rich.table import Table

        from flow.cli.ui.presentation.time_formatter import TimeFormatter

        time_fmt = TimeFormatter()

        # Create a clean table for task details
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        # Task name
        table.add_row("Task", task.name or "Unnamed task")

        # GPU type - show total GPUs if multiple instances
        gpu_display = GPUFormatter.format_ultra_compact(
            task.instance_type, getattr(task, "num_instances", 1)
        )
        table.add_row("GPU", gpu_display)

        # Status
        try:
            from flow.cli.ui.formatters import TaskFormatter as _TF

            status_display = _TF.format_status_with_color(task.status.value)
        except Exception:
            status_display = str(getattr(task.status, "value", task.status))
        table.add_row("Status", status_display)

        # Duration and cost
        duration = time_fmt.calculate_duration(task)
        table.add_row("Duration", duration)

        # Calculate approximate cost if available
        if (
            hasattr(task, "price_per_hour")
            and task.price_per_hour
            and task.status == TaskStatus.RUNNING
        ):
            if task.started_at:
                start = task.started_at
                if hasattr(start, "tzinfo") and start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                hours_run = (now - start).total_seconds() / 3600
                cost_so_far = hours_run * task.price_per_hour

                table.add_row("Cost so far", f"${cost_so_far:.2f}")
                table.add_row("Hourly rate", f"${task.price_per_hour:.2f}/hr")

        # Create panel with calmer themed colors
        from flow.cli.utils.theme_manager import theme_manager as _tm

        warning_color = _tm.get_color("warning")
        border_color = _tm.get_color("table.border")
        panel = Panel(
            table,
            title=f"[bold {warning_color}]⚠  Cancel Task[/bold {warning_color}]",
            title_align="center",
            border_style=border_color,
            padding=(1, 2),
        )

        console.print()
        console.print(panel)

    def _execute(
        self,
        task_identifier: str,
        yes: bool,
        all: bool,
        name_pattern: str,
        regex: bool,
        flow_client=None,
    ) -> None:
        """Execute the cancel command."""
        if all:
            self._execute_cancel_all(yes, flow_client=flow_client)
        elif name_pattern:
            self._execute_cancel_pattern(name_pattern, yes, regex, flow_client=flow_client)
        else:
            # Prefer direct path to allow tests to patch Flow and resolver cleanly
            if task_identifier:
                try:
                    client = flow_client or create_client(auto_init=True)
                    task = self.resolve_task(task_identifier, client)
                    self.execute_on_task(task, client, yes=yes)
                except AuthenticationError:
                    self.handle_auth_error()
                except Exception as e:
                    self.handle_error(str(e))
            else:
                # Fallback to interactive selection via mixin
                self.execute_with_selection(
                    task_identifier,
                    yes=yes,
                    flow_factory=lambda: (flow_client or create_client(auto_init=True)),
                )

    # Override resolve_task to import resolver from its canonical module so tests can patch it there
    def resolve_task(self, task_identifier: str | None, client: Flow, allow_multiple: bool = False):  # type: ignore[override]
        if task_identifier:
            from flow.cli.utils.task_resolver import (
                resolve_task_identifier as resolver,  # type: ignore
            )

            task, error = resolver(client, task_identifier)
            if error:
                from flow.cli.commands.base import console as _console

                _console.print(f"[error]✗ Error:[/error] {error}")
                raise SystemExit(1)
            return task
        # Fallback to base mixin behavior for interactive selection
        return super().resolve_task(task_identifier, client, allow_multiple)

    def _execute_cancel_all(self, yes: bool, *, flow_client=None) -> None:
        """Handle --all flag separately as it's a special case."""
        from flow.cli.utils.step_progress import StepTimeline

        try:
            timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
            timeline.start()

            # Step 1: Discover cancellable tasks
            find_idx = timeline.add_step("Finding all cancellable tasks", show_bar=False)
            timeline.start_step(find_idx)
            client = flow_client or create_client(auto_init=True)

            # Get cancellable tasks using TaskFetcher for consistent behavior
            from flow.cli.utils.task_fetcher import TaskFetcher

            fetcher = TaskFetcher(client)
            all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
            cancellable = TaskFilter.cancellable(all_tasks)
            timeline.complete_step()

            if not cancellable:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn

                warn = _tm_warn.get_color("warning")
                timeline.finish()
                console.print(f"[{warn}]No running tasks to cancel[/{warn}]")
                return

            # Confirm
            if not yes:
                if not click.confirm(f"Cancel {len(cancellable)} running tasks?"):
                    timeline.finish()
                    console.print("Cancelled")
                    return

            # Step 2: Cancel tasks iteratively with a progress bar
            cancelled_count = 0
            failed_count = 0
            total = len(cancellable)
            cancel_idx = timeline.add_step(
                f"Cancelling {total} task(s)", show_bar=True, estimated_seconds=None
            )
            timeline.start_step(cancel_idx)
            for i, task in enumerate(cancellable):
                task_name = task.name or task.task_id
                try:
                    client.cancel(task.task_id)
                    cancelled_count += 1
                except Exception as e:
                    from rich.markup import escape

                    from flow.cli.utils.theme_manager import theme_manager as _tm_fail2

                    err = _tm_fail2.get_color("error")
                    console.print(
                        f"[{err}]✗[/{err}] Failed to cancel {task_name}: {escape(str(e))}"
                    )
                    failed_count += 1
                finally:
                    # Update bar by item count
                    pct = (i + 1) / float(total)
                    timeline.update_active(percent=pct, message=f"{i + 1}/{total} – {task_name}")

            timeline.complete_step(note=f"{cancelled_count} succeeded, {failed_count} failed")
            timeline.finish()

            # Summary
            console.print()
            if cancelled_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm2

                success_color = _tm2.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Cancelled {cancelled_count} task(s)"
                )
            if failed_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm_fail3

                err = _tm_fail3.get_color("error")
                console.print(f"[{err}]✗[/{err}] Failed to cancel {failed_count} task(s)")

            # Next actions
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow run <config.yaml>[/accent]",
                ]
            )

        except click.Abort:
            # Ensure live UI is cleaned up and exit gracefully on Ctrl+C
            try:
                timeline.finish()
            except Exception:
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except KeyboardInterrupt:
            try:
                timeline.finish()
            except Exception:
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))

    def _execute_cancel_pattern(
        self, pattern: str, yes: bool, use_regex: bool, *, flow_client=None
    ) -> None:
        """Cancel tasks matching a name pattern."""
        from flow.cli.utils.step_progress import StepTimeline

        try:
            timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
            timeline.start()

            # Step 1: Discover candidates
            find_idx = timeline.add_step(f"Finding tasks matching: {pattern}", show_bar=False)
            timeline.start_step(find_idx)
            client = flow_client or create_client(auto_init=True)

            # Get cancellable tasks
            from flow.cli.utils.task_fetcher import TaskFetcher

            fetcher = TaskFetcher(client)
            all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
            cancellable = TaskFilter.cancellable(all_tasks)
            timeline.complete_step()

            if not cancellable:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn2

                warn = _tm_warn2.get_color("warning")
                timeline.finish()
                console.print(f"[{warn}]No running tasks to cancel[/{warn}]")
                return

            # Filter by pattern
            matching_tasks = []
            for task in cancellable:
                if task.name:
                    if use_regex:
                        # Use regex matching when requested
                        try:
                            if re.search(pattern, task.name):
                                matching_tasks.append(task)
                        except re.error as e:
                            from rich.markup import escape

                            from flow.cli.utils.theme_manager import theme_manager as _tm_err2

                            err = _tm_err2.get_color("error")
                            console.print(f"[{err}]Invalid regex pattern: {escape(str(e))}[/{err}]")
                            return
                    else:
                        # Default to wildcard matching
                        if fnmatch.fnmatch(task.name, pattern):
                            matching_tasks.append(task)

            if not matching_tasks:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn3

                warn = _tm_warn3.get_color("warning")
                console.print(f"[{warn}]No running tasks match pattern '{pattern}'[/{warn}]")

                # Help users debug common issues
                if "*" in pattern or "?" in pattern:
                    try:
                        from flow.cli.ui.presentation.next_steps import (
                            render_next_steps_panel as _ns,
                        )

                        _ns(
                            console,
                            [
                                "Quote your pattern: [accent]flow cancel -n 'pattern*'[/accent]",
                                "List tasks: [accent]flow status --all[/accent]",
                            ],
                            title="Tips",
                        )
                    except Exception:
                        console.print(
                            "\n[dim]Tip: Quote your pattern: flow cancel -n 'pattern*'[/dim]"
                        )

                # Show what tasks ARE available
                sample_names = [t.name for t in cancellable[:5] if t.name]
                if sample_names:
                    console.print(
                        f"\n[dim]Available task names: {', '.join(sample_names)}"
                        f"{' ...' if len(cancellable) > 5 else ''}[/dim]"
                    )
                return

            # Show matching tasks
            console.print(
                f"\n[bold]Found {len(matching_tasks)} task(s) matching pattern '[accent]{pattern}[/accent]':[/bold]\n"
            )
            from rich.table import Table

            table = Table(show_header=True, box=None)
            from flow.cli.utils.theme_manager import theme_manager as _tm

            table.add_column("Task Name", style=_tm.get_color("accent"))
            table.add_column("Task ID", style="dim")
            table.add_column("Status")
            table.add_column("GPU Type")

            for task in matching_tasks:
                from flow.cli.ui.formatters import GPUFormatter as _GPUF
                from flow.cli.ui.formatters import TaskFormatter as _TF

                try:
                    status_display = _TF.format_status_with_color(task.status.value)
                except Exception:
                    status_display = str(getattr(task.status, "value", task.status))
                gpu_display = _GPUF.format_ultra_compact(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                table.add_row(
                    task.name or "Unnamed",
                    task.task_id[:12] + "...",
                    status_display,
                    gpu_display,
                )

            console.print(table)
            console.print()

            # Confirm
            if not yes:
                if not click.confirm(f"Cancel {len(matching_tasks)} matching task(s)?"):
                    timeline.finish()
                    console.print("[dim]Cancellation aborted[/dim]")
                    return

            # Cancel each task with a progress bar
            cancelled_count = 0
            failed_count = 0
            total = len(matching_tasks)
            cancel_idx = timeline.add_step(
                f"Cancelling {total} matching task(s)", show_bar=True, estimated_seconds=None
            )
            timeline.start_step(cancel_idx)
            for i, task in enumerate(matching_tasks):
                task_name = task.name or task.task_id
                try:
                    client.cancel(task.task_id)
                    cancelled_count += 1
                except Exception as e:
                    from rich.markup import escape

                    from flow.cli.utils.theme_manager import theme_manager as _tm_err3

                    err = _tm_err3.get_color("error")
                    console.print(
                        f"[{err}]✗[/{err}] Failed to cancel {task_name}: {escape(str(e))}"
                    )
                    failed_count += 1
                finally:
                    pct = (i + 1) / float(total)
                    timeline.update_active(percent=pct, message=f"{i + 1}/{total} – {task_name}")
            timeline.complete_step(note=f"{cancelled_count} succeeded, {failed_count} failed")
            timeline.finish()

            # Summary
            console.print()
            if cancelled_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm3

                success_color = _tm3.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Cancelled {cancelled_count} task(s)"
                )
            if failed_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm_err4

                err = _tm_err4.get_color("error")
                console.print(f"[{err}]✗[/{err}] Failed to cancel {failed_count} task(s)")

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow run <config.yaml>[/accent]",
                ]
            )

            # Reuse a single client unless we take the fast batch index path
            client = None
        except click.Abort:
            try:
                timeline.finish()
            except Exception:
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except KeyboardInterrupt:
            try:
                timeline.finish()
            except Exception:
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))


# Export command instance
command = CancelCommand()
