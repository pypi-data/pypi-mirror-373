"""Query status use case.

Orchestrates status queries through the provider port.
"""

from dataclasses import dataclass

from flow.protocols.provider import Provider
from flow.sdk.models.enums import TaskStatus


@dataclass(frozen=True, slots=True)
class QueryStatusRequest:
    """Request to query task status."""

    task_id: str | None = None
    all_tasks: bool = False
    filter_status: TaskStatus | None = None


@dataclass(frozen=True, slots=True)
class TaskStatusInfo:
    """Task status information."""

    task_id: str
    status: TaskStatus
    instance_type: str | None
    instance_ip: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class QueryStatusResponse:
    """Response from status query."""

    tasks: list[TaskStatusInfo]
    total_count: int


class QueryStatusUseCase:
    """Use case for querying task status."""

    def __init__(self, provider: Provider):
        """Initialize with provider port.

        Args:
            provider: Provider port implementation
        """
        self._provider = provider

    def execute(self, request: QueryStatusRequest) -> QueryStatusResponse:
        """Query task status.

        Args:
            request: Status query request

        Returns:
            Response with task status information
        """
        if request.task_id:
            # Query single task
            task = self._provider.get_task(request.task_id)
            return QueryStatusResponse(
                tasks=[
                    TaskStatusInfo(
                        task_id=task.id,
                        status=task.status,
                        instance_type=task.instance_type,
                        instance_ip=task.instance_ip,
                        created_at=task.created_at,
                        updated_at=task.updated_at,
                    )
                ],
                total_count=1,
            )
        else:
            # Query all tasks
            tasks = self._provider.list_tasks(status_filter=request.filter_status)
            status_infos = [
                TaskStatusInfo(
                    task_id=task.id,
                    status=task.status,
                    instance_type=task.instance_type,
                    instance_ip=task.instance_ip,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in tasks
            ]
            return QueryStatusResponse(tasks=status_infos, total_count=len(status_infos))
