"""Task management service for the application layer.

This module consolidates task management logic from the former _internal/managers
and core/services directories into a single cohesive service in the app layer.
"""

from pathlib import Path
from typing import Any


class TaskService:
    """Unified task management service.

    Orchestrates task operations through ports without depending on
    concrete implementations or infrastructure details.
    """

    def __init__(self, provider_port: Any, storage_port: Any, metrics_port: Any):
        """Initialize task service with required ports.

        Args:
            provider_port: Port for provider operations
            storage_port: Port for storage operations
            metrics_port: Port for metrics collection
        """
        self.provider = provider_port
        self.storage = storage_port
        self.metrics = metrics_port

    def submit_task(
        self,
        config: dict[str, Any],
        working_dir: Path | None = None,
    ) -> str:
        """Submit a new task for execution.

        Args:
            config: Task configuration
            working_dir: Optional working directory

        Returns:
            Task ID of submitted task
        """
        # Implementation consolidated from previous task managers
        task_id = self.provider.submit_task(config)
        self.metrics.increment("tasks.submitted")
        return task_id

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get current status of a task.

        Args:
            task_id: Task identifier

        Returns:
            Task status information
        """
        status = self.provider.get_task_status(task_id)
        self.metrics.increment("tasks.status_checked")
        return status

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.

        Args:
            task_id: Task identifier

        Returns:
            True if cancelled successfully
        """
        result = self.provider.cancel_task(task_id)
        if result:
            self.metrics.increment("tasks.cancelled")
        return result

    def list_tasks(
        self,
        limit: int = 100,
        filter_status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List tasks with optional filtering.

        Args:
            limit: Maximum number of tasks to return
            filter_status: Optional status filter

        Returns:
            List of task information
        """
        tasks = self.provider.list_tasks(limit, filter_status)
        self.metrics.increment("tasks.listed")
        return tasks
