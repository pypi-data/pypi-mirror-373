"""Task filtering utilities for CLI commands."""

from datetime import datetime, timedelta, timezone

from flow.sdk.models import Task, TaskStatus


class TaskFilter:
    """Provides task filtering capabilities for CLI commands.

    This class encapsulates all task filtering logic, making it easy to
    apply consistent filtering across different commands.
    """

    @staticmethod
    def filter_by_time_window(
        tasks: list[Task], hours: int = 24, include_active: bool = True
    ) -> list[Task]:
        """Filter tasks by time window.

        Args:
            tasks: List of tasks to filter
            hours: Number of hours in the time window
            include_active: Whether to always include running/pending tasks

        Returns:
            Filtered list of tasks
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=hours)

        filtered = []
        for task in tasks:
            # Always include active tasks if requested
            if include_active and task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
                filtered.append(task)
                continue

            # Check if task was created within time window
            if task.created_at:
                created_at = task.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)

                if created_at > cutoff:
                    filtered.append(task)

        return filtered

    @staticmethod
    def filter_by_status(tasks: list[Task], status: TaskStatus | None) -> list[Task]:
        """Filter tasks by status.

        Args:
            tasks: List of tasks to filter
            status: Status to filter by (None means no filtering)

        Returns:
            Filtered list of tasks
        """
        if not status:
            return tasks

        return [task for task in tasks if task.status == status]

    @staticmethod
    def filter_by_name_pattern(
        tasks: list[Task], pattern: str, case_sensitive: bool = False
    ) -> list[Task]:
        """Filter tasks by name pattern.

        Args:
            tasks: List of tasks to filter
            pattern: Pattern to match in task names
            case_sensitive: Whether to use case-sensitive matching

        Returns:
            Filtered list of tasks
        """
        if not pattern:
            return tasks

        if not case_sensitive:
            pattern = pattern.lower()

        filtered = []
        for task in tasks:
            if not task.name:
                continue

            name = task.name if case_sensitive else task.name.lower()
            if pattern in name:
                filtered.append(task)

        return filtered

    @staticmethod
    def apply_filters(
        tasks: list[Task],
        status: TaskStatus | None = None,
        time_window_hours: int | None = None,
        include_active: bool = True,
        name_pattern: str | None = None,
        limit: int | None = None,
    ) -> list[Task]:
        """Apply multiple filters to a task list.

        Args:
            tasks: List of tasks to filter
            status: Optional status filter
            time_window_hours: Optional time window in hours
            include_active: Whether to always include active tasks
            name_pattern: Optional name pattern filter
            limit: Maximum number of tasks to return

        Returns:
            Filtered and limited list of tasks
        """
        # Apply filters in order of likely reduction
        if status:
            tasks = TaskFilter.filter_by_status(tasks, status)

        if time_window_hours:
            tasks = TaskFilter.filter_by_time_window(
                tasks, hours=time_window_hours, include_active=include_active
            )

        if name_pattern:
            tasks = TaskFilter.filter_by_name_pattern(tasks, name_pattern)

        # Apply limit if specified
        if limit and len(tasks) > limit:
            tasks = tasks[:limit]

        return tasks
