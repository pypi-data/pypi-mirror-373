"""Time formatting utilities for CLI output."""

from datetime import datetime, timezone

from flow.sdk.models import Task, TaskStatus


class TimeFormatter:
    """Handles all time-related formatting for tasks.

    This formatter provides consistent time formatting across all CLI commands,
    ensuring users see time information in a human-readable format.
    """

    @staticmethod
    def format_time_ago(timestamp: datetime | None) -> str:
        """Format timestamp as human-readable time ago.

        Args:
            timestamp: The datetime to format

        Returns:
            Human-readable string like "2 hours ago" or "just now"
        """
        if not timestamp:
            return "-"

        now = datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        delta = now - timestamp

        if delta.days > 0:
            if delta.days == 1:
                return "1 day ago"
            return f"{delta.days} days ago"

        hours = delta.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "1 hour ago"
            # Keep single line format to prevent wrapping issues
            return f"{hours} hours ago"

        minutes = delta.seconds // 60
        if minutes > 0:
            if minutes == 1:
                return "1 min ago"
            return f"{minutes} mins ago"

        return "just now"

    @staticmethod
    def calculate_duration(task: Task) -> str:
        """Calculate task duration based on actual runtime.

        Args:
            task: The task to calculate duration for

        Returns:
            Formatted duration string like "2h 30m" or "-" if not applicable
        """
        if task.status == TaskStatus.PENDING:
            return "-"

        # Use started_at if available, otherwise fall back to created_at
        start_time = task.started_at or task.created_at
        if not start_time:
            return "-"

        # Determine end time based on task state
        if task.status == TaskStatus.RUNNING:
            end_time = datetime.now(timezone.utc)
        elif task.completed_at:
            end_time = task.completed_at
        elif task.status in [TaskStatus.CANCELLED, TaskStatus.FAILED, TaskStatus.COMPLETED]:
            # Terminal state but no completed_at timestamp
            return "-"
        else:
            return "-"

        # Ensure timezone awareness
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        duration = end_time - start_time

        # Format duration
        if duration.days > 0:
            hours = duration.seconds // 3600
            return f"{duration.days}d {hours}h"

        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"

        return f"{minutes}m"

    @staticmethod
    def format_compact_time_ago(timestamp: datetime | None, include_suffix: bool = False) -> str:
        """Format a timestamp as a compact age string using duration syntax.

        Uses the same unit style as calculate_duration (e.g., "2d 3h", "4h 12m", "7m").

        Args:
            timestamp: The datetime to format
            include_suffix: If True, append " ago" to the result

        Returns:
            Compact age string or "-" if timestamp is None
        """
        if not timestamp:
            return "-"

        now = datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        duration = now - timestamp

        if duration.days > 0:
            hours = duration.seconds // 3600
            if hours > 0:
                text = f"{duration.days}d {hours}h"
            else:
                text = f"{duration.days}d"
        else:
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            if hours > 0:
                text = f"{hours}h {minutes}m"
            else:
                text = f"{minutes}m"

        if include_suffix:
            return f"{text} ago"
        return text

    @staticmethod
    def format_ultra_compact_age(timestamp: datetime | None) -> str:
        """Format age in an ultra-compact style for narrow tables.

        Rules:
        - < 1 hour: "Nm" (e.g., "5m")
        - 1 to < 24 hours: "Nh" (e.g., "11h")
        - >= 1 day: "Nd" (e.g., "2d")

        Args:
            timestamp: The datetime representing the start time

        Returns:
            Compact age string or "-" if timestamp is None
        """
        if not timestamp:
            return "-"
        try:
            now = datetime.now(timezone.utc)
            # Some tests may pass non-datetime or mocks; coerce or bail out
            if not hasattr(timestamp, "tzinfo"):
                return "-"
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            delta = now - timestamp
        except Exception:
            return "-"

        if delta.days >= 1:
            return f"{delta.days}d"

        total_seconds = delta.seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours >= 1:
            return f"{hours}h"

        return f"{minutes}m"

    @staticmethod
    def format_datetime(dt: datetime | None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime using specified format string.

        Args:
            dt: The datetime to format
            format_str: strftime format string

        Returns:
            Formatted datetime string or "-" if None
        """
        if not dt:
            return "-"
        try:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime(format_str)
        except Exception:
            return "-"
