"""Unified task presentation utilities.

Consolidates task display logic including filtering, rendering,
and formatting for consistent presentation across CLI commands.
"""

import os
from dataclasses import dataclass
from typing import Any

try:
    from rich.console import Console
except Exception:  # pragma: no cover
    # Minimal stub type to avoid Rich in pure presenters path
    class Console:  # type: ignore
        pass


# Prefer Flow symbol from the status module to keep tests that patch it consistent
try:
    from flow.cli.commands.status import Flow  # type: ignore
except Exception:  # pragma: no cover - fallback path
    from flow.sdk.client import Flow  # type: ignore
from flow.cli.ui.presentation.task_renderer import TaskDetailRenderer, TaskTableRenderer
from flow.cli.utils.task_fetcher import TaskFetcher
from flow.cli.utils.task_filter import TaskFilter
from flow.cli.utils.task_index_cache import TaskIndexCache
from flow.cli.utils.task_resolver import resolve_task_identifier
from flow.sdk.factory import create_client


@dataclass
class DisplayOptions:
    """Options for task display."""

    show_all: bool = False
    status_filter: str | None = None
    limit: int = 20
    show_details: bool = True
    json_output: bool = False


@dataclass
class TaskSummary:
    """Summary information about displayed tasks."""

    total_shown: int
    total_available: int
    filtered_by_status: bool
    filtered_by_time: bool
    active_tasks: int
    total_gpu_hours: float = 0.0
    pending_tasks: int = 0
    running_tasks: int = 0
    paused_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    def has_more_tasks(self) -> bool:
        """Check if there are more tasks than shown."""
        return self.total_shown < self.total_available


class TaskPresenter:
    """Unified task presentation handler."""

    def __init__(self, console: Console, flow_client: Flow | None = None):
        """Initialize task presenter.

        Args:
            console: Rich console for output
            flow_client: Optional Flow client (will create if not provided)
        """
        self.console = console
        self.flow_client = flow_client
        self.task_filter = TaskFilter()
        self.table_renderer = TaskTableRenderer(console)
        self.detail_renderer = TaskDetailRenderer(console)
        self.task_fetcher = None  # Created lazily when needed

    def present_single_task(self, task_identifier: str) -> bool:
        """Present details for a single task.

        Args:
            task_identifier: Task ID or name to look up

        Returns:
            True if task was found and displayed, False otherwise
        """
        if not self.flow_client:
            self.flow_client = create_client(auto_init=True)

        # Show a brief animated progress while resolving and fetching details
        try:
            from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
        except Exception:
            AnimatedEllipsisProgress = None  # type: ignore

        if AnimatedEllipsisProgress:
            with AnimatedEllipsisProgress(self.console, "Looking up task", start_immediately=True):
                task, error = resolve_task_identifier(self.flow_client, task_identifier)
        else:
            task, error = resolve_task_identifier(self.flow_client, task_identifier)

        if error:
            from rich.markup import escape

            self.console.print(f"[error]Error:[/error] {escape(str(error))}")
            return False

        self.detail_renderer.render_task_details(task)
        return True

    def present_task_list(
        self, options: DisplayOptions, tasks: list[Any] | None = None
    ) -> TaskSummary:
        """Present a list of tasks with filtering and formatting.

        Args:
            options: Display options for filtering and presentation
            tasks: Optional pre-fetched task list (will fetch if not provided)

        Returns:
            TaskSummary with information about displayed tasks
        """
        if not self.flow_client:
            self.flow_client = create_client(auto_init=True)

        # Fetch tasks if not provided
        if tasks is None:
            # Fast-path probe to minimize provider calls in empty states
            tasks_direct = None
            try:
                tasks_direct = self.flow_client.tasks.list(limit=options.limit)
            except Exception:
                tasks_direct = None

            if tasks_direct is not None:
                if not tasks_direct:
                    # No tasks at all — show empty state and return a minimal summary
                    self._show_no_tasks_message(options)
                    return TaskSummary(
                        total_shown=0,
                        total_available=0,
                        filtered_by_status=bool(options.status_filter),
                        filtered_by_time=(not options.show_all),
                        active_tasks=0,
                    )
                tasks = tasks_direct
            else:
                # Fall back to full fetcher logic
                tasks = self._fetch_tasks(options)
        else:
            # Explicit tasks provided by caller (including empty list) → do not call provider
            pass

        # Apply filters
        filtered_tasks, summary = self._filter_tasks(tasks, options)

        # Handle empty results
        if not filtered_tasks:
            self._show_no_tasks_message(options)
            return summary

        # Show pre-table summary
        self._show_pre_table_summary(summary)

        # Render the task list
        self.table_renderer.render_task_list(
            tasks=filtered_tasks, show_all=options.show_all, limit=options.limit
        )

        # Save task indices for quick reference
        # Only save when showing from command line (not programmatic usage)
        if filtered_tasks and not options.json_output:
            cache = TaskIndexCache()
            cache.save_indices(filtered_tasks)

        # Show summary information
        if options.show_details:
            self._show_summary_messages(summary, options)

        return summary

    def fetch_tasks(self, options: DisplayOptions) -> list[Any]:
        """Public API to fetch tasks for display.

        Delegates to the internal implementation while providing a stable
        interface for other components.
        """
        return self._fetch_tasks(options)

    def _fetch_tasks(self, options: DisplayOptions) -> list[Any]:
        """Fetch tasks from API based on options.

        Args:
            options: Display options including filters

        Returns:
            List of tasks from API
        """
        # Ensure we have a Flow client and task fetcher
        if not self.flow_client:
            self.flow_client = create_client(auto_init=True)
        if not self.task_fetcher:
            self.task_fetcher = TaskFetcher(self.flow_client)

        # Use centralized fetcher for consistent behavior
        return self.task_fetcher.fetch_for_display(
            show_all=options.show_all,
            status_filter=options.status_filter,
            limit=options.limit + 1,  # Fetch one extra to check if there are more
        )

    def _filter_tasks(
        self, tasks: list[Any], options: DisplayOptions
    ) -> tuple[list[Any], TaskSummary]:
        """Apply filters to task list.

        Args:
            tasks: Raw task list
            options: Display options

        Returns:
            Tuple of (filtered_tasks, summary)
        """
        total_available = len(tasks)
        filtered_tasks = tasks

        # Apply time filter if not showing all
        if not options.show_all:
            filtered_tasks = self.task_filter.filter_by_time_window(
                filtered_tasks, hours=24, include_active=True
            )

        # Calculate detailed statistics
        from flow.cli.utils.task_stats import compute_total_gpu_hours

        total_gpu_hours = 0.0
        pending_tasks = 0
        running_tasks = 0
        paused_tasks = 0
        completed_tasks = 0
        failed_tasks = 0
        active_tasks = 0

        for task in filtered_tasks:
            if hasattr(task, "status"):
                status_str = (
                    task.status.value if hasattr(task.status, "value") else str(task.status)
                )

                # Count by status
                if status_str == "pending":
                    pending_tasks += 1
                    active_tasks += 1
                elif status_str == "running":
                    running_tasks += 1
                    active_tasks += 1
                elif status_str == "paused":
                    # Paused tasks are not actively consuming resources but can be resumed
                    paused_tasks += 1
                    active_tasks += 1
                elif status_str == "completed":
                    completed_tasks += 1
                elif status_str == "failed":
                    failed_tasks += 1

                # GPU hours computed separately below
                pass

        # Apply limit
        shown_tasks = filtered_tasks[: options.limit]

        # Compute GPU hours once
        total_gpu_hours = compute_total_gpu_hours(filtered_tasks)

        summary = TaskSummary(
            total_shown=len(shown_tasks),
            total_available=total_available,
            filtered_by_status=bool(options.status_filter),
            filtered_by_time=not options.show_all,
            active_tasks=active_tasks,
            total_gpu_hours=total_gpu_hours,
            pending_tasks=pending_tasks,
            running_tasks=running_tasks,
            paused_tasks=paused_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
        )

        return shown_tasks, summary

    def _show_no_tasks_message(self, options: DisplayOptions) -> None:
        """Display message when no tasks found.

        Args:
            options: Display options that were applied
        """
        if options.status_filter:
            self.console.print(f"No tasks found with status '{options.status_filter}'")
        elif options.show_all:
            self.console.print("No tasks found in project")
        else:
            self.console.print("No recent or running tasks found")
            self.console.print("[dim]Use --all to see all tasks[/dim]")

    def _show_pre_table_summary(self, summary: TaskSummary) -> None:
        """Display summary line before the task table.

        Args:
            summary: Task summary information
        """
        parts = []

        # Active tasks (running + pending + paused)
        if summary.running_tasks > 0:
            parts.append(f"{summary.running_tasks} running")
        if summary.pending_tasks > 0:
            parts.append(f"{summary.pending_tasks} pending")
        if summary.paused_tasks > 0:
            parts.append(f"{summary.paused_tasks} paused")

        # Completed/failed
        if summary.completed_tasks > 0:
            parts.append(f"{summary.completed_tasks} completed")
        if summary.failed_tasks > 0:
            parts.append(f"{summary.failed_tasks} failed")

        # GPU hours
        if summary.total_gpu_hours > 0:
            if summary.total_gpu_hours >= 1:
                gpu_hrs_str = f"{summary.total_gpu_hours:.1f}"
            else:
                # Show more precision for small values
                gpu_hrs_str = f"{summary.total_gpu_hours:.2f}"
            parts.append(f"GPU-hrs: {gpu_hrs_str}")

        if parts:
            summary_line = " · ".join(parts)
            self.console.print(f"[dim]{summary_line}[/dim]\n")

    def _show_summary_messages(self, summary: TaskSummary, options: DisplayOptions) -> None:
        """Display summary messages after task list.

        Args:
            summary: Task summary information
            options: Display options used
        """
        # Determine if we're showing only active tasks or all recent tasks
        showing_active_only = (
            not options.show_all and not options.status_filter and summary.active_tasks > 0
        )

        # Show limit message if applicable
        if summary.total_shown == options.limit and summary.has_more_tasks():
            if options.show_all:
                self.console.print(
                    f"\n\n[dim]Showing first {options.limit} tasks. Use --limit to see more.[/dim]\n"
                )
            elif showing_active_only:
                self.console.print(
                    "\n\n[dim]Showing active tasks (running/pending). "
                    "Use --all to see all tasks.[/dim]\n"
                )
            else:
                self.console.print(f"\n\n[dim]Showing up to {options.limit} recent tasks.[/dim]")
                self.console.print(
                    "[dim]Use --all to see all tasks or --limit to see more.[/dim]\n"
                )
        elif not options.show_all and not options.status_filter:
            if showing_active_only:
                self.console.print(
                    "\n\n[dim]Showing active tasks only. Use --all to see all tasks.[/dim]\n"
                )
            else:
                # Fallback mode - no active tasks, showing recent
                self.console.print(
                    "\n\n[dim]No active tasks. Showing recent tasks. Use --all to see all tasks.[/dim]\n"
                )

        # Show debug info if enabled
        if os.environ.get("FLOW_DEBUG"):
            self._show_debug_info(summary)

    def _show_debug_info(self, summary: TaskSummary) -> None:
        """Show debug information about task display.

        Args:
            summary: Task summary information
        """
        self.console.print("\n[dim]Debug info:[/dim]")
        self.console.print(f"[dim]  Total available: {summary.total_available}[/dim]")
        self.console.print(f"[dim]  Shown: {summary.total_shown}[/dim]")
        self.console.print(f"[dim]  Active: {summary.active_tasks}[/dim]")
        self.console.print(f"[dim]  Filtered by status: {summary.filtered_by_status}[/dim]")
        self.console.print(f"[dim]  Filtered by time: {summary.filtered_by_time}[/dim]")

    def format_task_for_json(self, task: Any) -> dict:
        """Format task object for JSON output.

        Args:
            task: Task object to format

        Returns:
            Dictionary suitable for JSON serialization
        """
        # Extract relevant fields for JSON output
        return {
            "task_id": getattr(task, "task_id", "unknown"),
            "name": getattr(task, "name", None),
            "status": getattr(task, "status", "unknown"),
            "gpu_type": getattr(task, "gpu_type", None),
            "created_at": str(getattr(task, "created_at", "")),
            "started_at": str(getattr(task, "started_at", "")),
            "completed_at": str(getattr(task, "completed_at", "")),
            "error": getattr(task, "error", None),
        }
