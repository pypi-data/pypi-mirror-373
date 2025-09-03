"""Task selector mixin for commands that operate on tasks.

Provides a small abstraction for commands that need to resolve or select tasks
interactively, and utilities for common task filters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

from flow.cli.ui.components import select_task
from flow.cli.utils.task_resolver import resolve_task_identifier
from flow.errors import AuthenticationError
from flow.sdk.factory import create_client
from flow.sdk.models import Task

T = TypeVar("T")


class TaskFilter:
    """Composable task filters following the Strategy pattern."""

    @staticmethod
    def running_only(tasks: list[Task]) -> list[Task]:
        """Filter for running tasks only."""
        from flow.sdk.models import TaskStatus

        return [t for t in tasks if t.status == TaskStatus.RUNNING]

    @staticmethod
    def cancellable(tasks: list[Task]) -> list[Task]:
        """Filter for tasks that can be cancelled."""
        from flow.sdk.models import TaskStatus

        return [t for t in tasks if t.status in [TaskStatus.PENDING, TaskStatus.RUNNING]]

    @staticmethod
    def with_logs(tasks: list[Task]) -> list[Task]:
        """Filter for tasks that have logs available."""
        from flow.sdk.models import TaskStatus

        # Only running and completed tasks have accessible logs
        # Cancelled tasks have terminated instances with no SSH access
        return [t for t in tasks if t.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]]

    @staticmethod
    def with_ssh(tasks: list[Task]) -> list[Task]:
        """Filter for tasks with SSH access."""
        try:
            from flow.sdk.models import TaskStatus

            return [
                t
                for t in tasks
                if getattr(t, "ssh_host", None) and getattr(t, "status", None) == TaskStatus.RUNNING
            ]
        except Exception:
            # Fallback: compare by value string
            return [
                t
                for t in tasks
                if getattr(t, "ssh_host", None)
                and getattr(
                    getattr(t, "status", None), "value", str(getattr(t, "status", "")).lower()
                )
                == "running"
            ]


class TaskSelectorMixin(ABC):
    """Mixin for commands that need to select tasks.

    This follows the Template Method pattern, providing a clean way
    for commands to get a task either from arguments or interactive selection.
    """

    @abstractmethod
    def get_task_filter(self) -> Callable[[list[Task]], list[Task]] | None:
        """Return the filter to apply to tasks, or None for all tasks."""
        pass

    @abstractmethod
    def get_selection_title(self) -> str:
        """Return the title for the interactive selector."""
        pass

    @abstractmethod
    def get_no_tasks_message(self) -> str:
        """Return message when no tasks match the filter."""
        pass

    def resolve_task(
        self, task_identifier: str | None, client, allow_multiple: bool = False
    ) -> Task | None | list[Task]:
        """Resolve a task from identifier or interactive selection.

        This method encapsulates the common pattern of:
        1. Using provided identifier if available
        2. Otherwise showing interactive selection
        3. Applying appropriate filters

        Args:
            task_identifier: Optional task ID/name from command args
            client: Flow API client
            allow_multiple: Whether to allow multiple selection

        Returns:
            Selected task(s) or None if cancelled

        Raises:
            SystemExit: If task not found or selection cancelled
        """
        from flow.cli.commands.base import console

        # If identifier provided, resolve it directly
        if task_identifier:
            task, error = resolve_task_identifier(client, task_identifier)
            if error:
                console.print(f"[error]✗ Error:[/error] {error}")
                raise SystemExit(1)
            return task

        # Interactive selection
        # Use TaskFetcher to ensure we find all active tasks
        from flow.cli.utils.task_fetcher import TaskFetcher

        fetcher = TaskFetcher(client)
        all_tasks = fetcher.fetch_for_resolution(limit=1000)

        # Apply filter if specified
        task_filter = self.get_task_filter()
        if task_filter:
            filtered_tasks = task_filter(all_tasks)
        else:
            filtered_tasks = all_tasks

        if not filtered_tasks:
            console.print(f"[warning]{self.get_no_tasks_message()}[/warning]")
            raise SystemExit(0)

        # Show selector
        selected = select_task(
            filtered_tasks, title=self.get_selection_title(), allow_multiple=allow_multiple
        )

        if not selected:
            console.print("No task selected")
            raise SystemExit(0)

        return selected


class TaskOperationCommand(TaskSelectorMixin):
    """Base class for commands that operate on tasks.

    Provides a clean abstraction that:
    - Handles authentication errors consistently
    - Manages task selection/resolution
    - Follows the Template Method pattern for execution
    """

    @abstractmethod
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute the command logic on the selected task."""
        pass

    # --- Optional progress/selection hooks (subclasses may override) ---
    @property
    def prefer_fetch_before_selection(self) -> bool:  # pragma: no cover - default off
        """When True, fetch lists under a spinner and stop before selectors/prompts."""
        return False

    @property
    def stop_spinner_before_confirmation(self) -> bool:  # pragma: no cover - default off
        """When True, ensure spinners stop before any confirmation prompts."""
        return False

    @property
    def _fetch_spinner_label(self) -> str:  # pragma: no cover - default label
        return "Fetching tasks"

    def progress_label_for_identifier(self, task_identifier: str) -> str:
        """Spinner label when resolving a specific identifier (override to customize)."""
        return f"Looking up task: {task_identifier}"

    def execute_with_selection(self, task_identifier: str | None, **kwargs) -> None:
        """Execute command with task selection.

        This is the main entry point that:
        1. Handles authentication
        2. Resolves/selects the task
        3. Executes the command logic
        """
        from flow.cli.commands.base import console
        from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

        try:
            # Honor JSON mode by skipping animations/spinners entirely
            json_mode = bool(kwargs.get("output_json", False))
            progress_enabled = not json_mode
            # Check if command manages its own progress
            if hasattr(self, "manages_own_progress") and self.manages_own_progress:
                # Commands that manage their own progress display
                if task_identifier:
                    # Show a lightweight loader to avoid initial perceived latency
                    try:
                        from flow.cli.ui.presentation.animated_progress import (
                            AnimatedEllipsisProgress as _Anim,
                        )

                        if progress_enabled:
                            with _Anim(
                                console,
                                "Preparing connection",
                                start_immediately=True,
                                transient=True,
                            ):
                                flow_factory = kwargs.pop("flow_factory", None) or (
                                    lambda: create_client(auto_init=True)
                                )
                                client = flow_factory()
                                task = self.resolve_task(task_identifier, client)
                        else:
                            flow_factory = kwargs.pop("flow_factory", None) or (
                                lambda: create_client(auto_init=True)
                            )
                            client = flow_factory()
                            task = self.resolve_task(task_identifier, client)
                    except Exception:
                        flow_factory = kwargs.pop("flow_factory", None) or (
                            lambda: create_client(auto_init=True)
                        )
                        client = flow_factory()
                        task = self.resolve_task(task_identifier, client)
                    self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - need animation while fetching tasks
                    if progress_enabled:
                        with AnimatedEllipsisProgress(
                            console, "Fetching tasks", transient=True, start_immediately=True
                        ) as progress:
                            flow_factory = kwargs.pop("flow_factory", None) or (
                                lambda: create_client(auto_init=True)
                            )
                            client = flow_factory()
                            # Fetch tasks within animation context to show progress
                            from flow.cli.utils.task_fetcher import TaskFetcher

                            fetcher = TaskFetcher(client)
                            all_tasks = fetcher.fetch_for_resolution(limit=1000)
                    else:
                        flow_factory = kwargs.pop("flow_factory", None) or (
                            lambda: create_client(auto_init=True)
                        )
                        client = flow_factory()
                        # Fetch tasks within animation context to show progress
                        from flow.cli.utils.task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[warning]{self.get_no_tasks_message()}[/warning]")
                        raise SystemExit(0)

                    # Show selector
                    from flow.cli.ui.components import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)
            elif getattr(self, "prefer_fetch_before_selection", False) or getattr(
                self, "stop_spinner_before_confirmation", False
            ):
                # Generic path for commands that want to fetch during AEP and stop before confirmations
                if task_identifier:
                    display_msg = f"Looking up task: {task_identifier}"
                    if progress_enabled:
                        with AnimatedEllipsisProgress(
                            console, display_msg, transient=True, start_immediately=True
                        ):
                            flow_factory = kwargs.pop("flow_factory", None) or (
                                lambda: create_client(auto_init=True)
                            )
                            client = flow_factory()
                            # Resolve task only under spinner
                            task = self.resolve_task(task_identifier, client)
                        # Execute after spinner closes (e.g., for confirmations)
                        self.execute_on_task(task, client, **kwargs)
                    else:
                        flow_factory = kwargs.pop("flow_factory", None) or (
                            lambda: create_client(auto_init=True)
                        )
                        client = flow_factory()
                        task = self.resolve_task(task_identifier, client)
                        self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - fetch list during spinner, then select and execute after
                    fetch_label = getattr(self, "_fetch_spinner_label", None) or "Fetching tasks"
                    if progress_enabled:
                        with AnimatedEllipsisProgress(
                            console, fetch_label, transient=True, start_immediately=True
                        ) as progress:
                            flow_factory = kwargs.pop("flow_factory", None) or (
                                lambda: create_client(auto_init=True)
                            )
                            client = flow_factory()
                            from flow.cli.utils.task_fetcher import TaskFetcher

                            fetcher = TaskFetcher(client)
                            all_tasks = fetcher.fetch_for_resolution(limit=1000)
                    else:
                        flow_factory = kwargs.pop("flow_factory", None) or (
                            lambda: create_client(auto_init=True)
                        )
                        client = flow_factory()
                        from flow.cli.utils.task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    task_filter = self.get_task_filter()
                    filtered_tasks = task_filter(all_tasks) if task_filter else all_tasks
                    if not filtered_tasks:
                        console.print(f"[warning]{self.get_no_tasks_message()}[/warning]")
                        raise SystemExit(0)
                    from flow.cli.ui.components import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )
                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)
                    self.execute_on_task(selected, client, **kwargs)
            else:
                # For other commands, use animated progress
                if task_identifier:
                    # If we have a specific identifier, run the animation through the whole process
                    if progress_enabled:
                        label = self.progress_label_for_identifier(task_identifier)
                        with AnimatedEllipsisProgress(
                            console, label, transient=True, start_immediately=True
                        ):
                            flow_factory = kwargs.pop("flow_factory", None) or (
                                lambda: create_client(auto_init=True)
                            )
                            client = flow_factory()
                            # Resolve task (from arg or interactive)
                            task = self.resolve_task(task_identifier, client)
                            # Execute command logic
                            self.execute_on_task(task, client, **kwargs)
                    else:
                        flow_factory = kwargs.pop("flow_factory", None) or (
                            lambda: create_client(auto_init=True)
                        )
                        client = flow_factory()
                        # Resolve task (from arg or interactive)
                        task = self.resolve_task(task_identifier, client)
                        # Execute command logic
                        self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - fetch tasks before showing the selector
                    if progress_enabled:
                        with AnimatedEllipsisProgress(
                            console, "Fetching tasks", transient=True, start_immediately=True
                        ) as progress:
                            flow_factory = kwargs.pop("flow_factory", None) or (
                                lambda: create_client(auto_init=True)
                            )
                            client = flow_factory()
                            # Fetch tasks within animation context to show progress
                            from flow.cli.utils.task_fetcher import TaskFetcher

                            fetcher = TaskFetcher(client)
                            all_tasks = fetcher.fetch_for_resolution(limit=1000)
                    else:
                        flow_factory = kwargs.pop("flow_factory", None) or (
                            lambda: create_client(auto_init=True)
                        )
                        client = flow_factory()
                        # Fetch tasks within animation context to show progress
                        from flow.cli.utils.task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[warning]{self.get_no_tasks_message()}[/warning]")
                        raise SystemExit(0)

                    # Show selector
                    from flow.cli.ui.components import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)

        except AuthenticationError:
            # Delegate to the current command's auth handler for consistent UX
            # This will raise click.exceptions.Exit; do not print fallback to avoid duplication.
            self.handle_auth_error()  # type: ignore[attr-defined]
            return
        except SystemExit:
            raise
        except Exception as e:
            # Route through command's centralized error handler when available
            try:
                # Detect common auth misconfig pattern that surfaces as ValueError
                msg = str(e)
                if (
                    isinstance(e, ValueError)
                    and (("Authentication not configured" in msg) or ("MITHRIL_API_KEY" in msg))
                ) or ("Authentication not configured" in msg):
                    if hasattr(self, "handle_auth_error"):
                        self.handle_auth_error()
                        raise SystemExit(1)
            except Exception:
                pass

            if hasattr(self, "handle_error"):
                # type: ignore[attr-defined]
                self.handle_error(e)
            else:
                console.print(f"[error]Error: {e!s}[/error]")
            raise SystemExit(1)
