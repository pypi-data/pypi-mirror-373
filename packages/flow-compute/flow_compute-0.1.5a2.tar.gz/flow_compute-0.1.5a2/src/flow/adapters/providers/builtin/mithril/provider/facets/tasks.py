"""Tasks facet - handles task retrieval, status, and control operations."""

from __future__ import annotations

import logging
from contextlib import suppress
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.errors import TaskNotFoundError
from flow.errors.messages import TASK_NOT_FOUND, format_error
from flow.sdk.models import Instance, Task, TaskStatus

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class TasksFacet:
    """Handles task operations - get, list, status, stop, etc."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize tasks facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx
        # Prefer injected logger via context when available
        self._logger = getattr(ctx, "logger", logger)

    @handle_mithril_errors("Get task")
    def get_task(self, task_id: str) -> Task:
        """Get task details.

        Args:
            task_id: Task ID

        Returns:
            Task object

        Raises:
            TaskNotFoundError: If task not found
        """
        task = self.ctx.task_query.get_task(task_id)
        if not task:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        # Try to enrich with instance details
        with suppress(Exception):
            if isinstance(task.instances, list) and task.instances:
                enriched = self.ctx.task_query.get_task(task_id)
                if enriched:
                    return enriched

        return task

    @handle_mithril_errors("Get task status")
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get task status.

        Args:
            task_id: Task ID

        Returns:
            Task status

        Raises:
            TaskNotFoundError: If task not found
        """
        status = self.ctx.task_query.get_task_status(task_id)
        if status is None:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))
        return status

    def list_tasks(
        self, status: str | None = None, limit: int = 100, force_refresh: bool = False
    ) -> list[Task]:
        """List tasks with optional filtering.

        Args:
            status: Optional status filter
            limit: Maximum number of tasks to return
            force_refresh: Whether to bypass cache

        Returns:
            List of tasks
        """
        tasks = self.ctx.task_query.list_tasks(
            status=status, limit=limit, force_refresh=force_refresh
        )
        # Attach context as provider reference so Task.get_user() and similar helpers work
        # even when tasks are constructed from bid dictionaries without a provider facade.
        try:
            for t in tasks:
                try:
                    t._provider = self.ctx  # type: ignore[attr-defined]
                except Exception:
                    pass
        except Exception:
            pass
        return tasks

    def list_active_tasks(self, limit: int = 100) -> list[Task]:
        """List active tasks.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of active tasks
        """
        return self.ctx.task_query.list_active_tasks(limit=limit)

    def stop_task(self, task_id: str) -> bool:
        """Stop a running task.

        Args:
            task_id: Task ID

        Returns:
            True if task was stopped successfully
        """
        try:
            # Try to cancel the bid
            self.ctx.api.cancel_bid(task_id)
            self._logger.info(f"Successfully stopped task {task_id}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to stop task {task_id}: {e}")
            return False

    @handle_mithril_errors("Cancel task")
    def cancel_task(self, task_id: str) -> None:
        """Cancel a task.

        Args:
            task_id: Task ID

        Raises:
            MithrilAPIError: If cancellation fails
        """
        self.ctx.api.cancel_bid(task_id)

    def get_task_instances(self, task_id: str) -> list[Instance]:
        """Get instances for a task.

        Args:
            task_id: Task ID

        Returns:
            List of instances
        """
        # Get bid data
        bid = self.get_bid_dict(task_id)
        instances_data = bid.get("instances", [])

        # Convert to Instance objects
        instances = []
        for inst_data in instances_data:
            try:
                if isinstance(inst_data, Instance):
                    instances.append(inst_data)
                else:
                    instances.append(Instance.from_dict(inst_data))
            except Exception:
                # Keep raw data if conversion fails
                instances.append(inst_data)  # type: ignore[arg-type]

        return instances

    def get_bid_dict(self, task_id: str) -> dict:
        """Get bid dictionary for a task.

        Args:
            task_id: Task ID

        Returns:
            Bid data dictionary

        Raises:
            TaskNotFoundError: If task/bid not found
        """
        try:
            bid = self.ctx.api.get_bid(task_id)
        except Exception as e:
            if "404" in str(e):
                raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))
            raise

        if not bid:
            raise TaskNotFoundError(format_error(TASK_NOT_FOUND, task_id=task_id))

        return bid

    def build_task_from_bid(
        self, bid_data: dict, config: TaskConfig | None = None, fetch_instance_details: bool = False
    ) -> Task:
        """Build a Task object from bid data.

        Args:
            bid_data: Bid data from API
            config: Optional task configuration
            fetch_instance_details: Whether to fetch additional instance details

        Returns:
            Task object
        """
        return self.ctx.task_service.build_task(
            bid_data, config=config, fetch_instance_details=fetch_instance_details
        )

    def build_task_from_reservation(self, reservation: Any, config: TaskConfig) -> Task:
        """Build a Task object from a reservation.

        Args:
            reservation: Reservation object
            config: Task configuration

        Returns:
            Task object
        """
        return self.ctx.task_service.build_task_from_reservation(reservation, config)

    def convert_auction_to_available_instance(self, auction_data: dict) -> Any:
        """Convert auction data to AvailableInstance format.

        Args:
            auction_data: Raw auction data from API

        Returns:
            AvailableInstance object or None
        """
        try:
            from flow.adapters.providers.builtin.mithril.domain.auctions import (
                convert_auction_to_available_instance,
            )

            return convert_auction_to_available_instance(auction_data, self.ctx.pricing)
        except ImportError:
            # Fallback implementation
            from flow.sdk.models import AvailableInstance

            return AvailableInstance(
                allocation_id=auction_data.get("id", ""),
                provider="mithril",
                instance_type=auction_data.get("instance_type", ""),
                region=auction_data.get("region", ""),
                price_per_hour=float(auction_data.get("price", 0)),
                availability="spot",
                gpu_count=auction_data.get("gpu_count", 0),
                cpu_count=auction_data.get("cpu_count", 0),
                memory_gb=auction_data.get("memory_gb", 0),
            )
