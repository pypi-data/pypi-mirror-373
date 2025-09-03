"""Cancel task use case.

Orchestrates task cancellation through the provider port.
"""

from dataclasses import dataclass

from flow.protocols.provider import Provider


@dataclass(frozen=True, slots=True)
class CancelTaskRequest:
    """Request to cancel a task."""

    task_id: str
    force: bool = False


@dataclass(frozen=True, slots=True)
class CancelTaskResponse:
    """Response from cancelling a task."""

    success: bool
    message: str | None = None


class CancelTaskUseCase:
    """Use case for cancelling tasks."""

    def __init__(self, provider: Provider):
        """Initialize with provider port.

        Args:
            provider: Provider port implementation
        """
        self._provider = provider

    def execute(self, request: CancelTaskRequest) -> CancelTaskResponse:
        """Cancel a task.

        Args:
            request: Cancel request with task ID

        Returns:
            Response indicating success/failure
        """
        try:
            self._provider.cancel_task(request.task_id, force=request.force)
            return CancelTaskResponse(
                success=True, message=f"Task {request.task_id} cancelled successfully"
            )
        except Exception as e:
            return CancelTaskResponse(success=False, message=str(e))
