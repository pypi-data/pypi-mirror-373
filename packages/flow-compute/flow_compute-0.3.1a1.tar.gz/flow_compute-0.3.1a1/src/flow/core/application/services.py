"""Application facade - single entry point for all use cases.

This module provides the ApplicationFacade that orchestrates all use cases
through ports, following hexagonal architecture principles.
"""

from dataclasses import dataclass

from flow.application.cancel_task import (
    CancelTaskRequest as CancelRequest,
)
from flow.application.cancel_task import (
    CancelTaskResponse as CancelResponse,
)
from flow.application.cancel_task import (
    CancelTaskUseCase as CancelService,
)
from flow.application.query_status import (
    QueryStatusRequest as StatusRequest,
)
from flow.application.query_status import (
    QueryStatusResponse as StatusResponse,
)
from flow.application.query_status import (
    QueryStatusUseCase as StatusService,
)
from flow.application.reserve_capacity import (
    ReserveCapacityRequest as ReserveRequest,
)
from flow.application.reserve_capacity import (
    ReserveCapacityResponse as ReserveResponse,
)
from flow.application.reserve_capacity import (
    ReserveCapacityUseCase as ReserveService,
)
from flow.application.run_task import RunRequest, RunResponse, RunService
from flow.protocols.logging import LoggingProtocol
from flow.protocols.metrics import MetricsProtocol
from flow.protocols.provider import Provider
from flow.protocols.storage import StorageProtocol


@dataclass
class ApplicationFacade:
    """Central facade for all application use cases.

    This facade provides a single, cohesive interface for all application
    operations. It orchestrates use cases through injected ports, maintaining
    clean separation between business logic and infrastructure.

    The facade pattern ensures:
    - Single entry point for all entrypoints (CLI, SDK, API)
    - Consistent error handling and metrics across all operations
    - Clean dependency injection of ports
    - No direct coupling to adapters or infrastructure
    """

    provider: Provider
    metrics: MetricsProtocol
    logger: LoggingProtocol
    storage: StorageProtocol | None = None

    def __post_init__(self):
        """Initialize use case services with injected ports."""
        self._run_service = RunService(self.provider)
        self._cancel_service = CancelService(self.provider)
        self._status_service = StatusService(self.provider)
        self._reserve_service = ReserveService(self.provider)

    def run_task(self, request: RunRequest) -> RunResponse:
        """Execute a task through the provider.

        Args:
            request: Run request containing task specification

        Returns:
            Response containing task handle and optional trace info
        """
        self.logger.debug("Running task", extra={"spec": request.spec})
        self.metrics.increment("application.run_task.calls")

        try:
            response = self._run_service.run(request)
            self.metrics.increment("application.run_task.success")
            self.logger.info("Task submitted successfully", extra={"task_id": response.handle.id})
            return response
        except Exception as e:
            self.metrics.increment("application.run_task.errors")
            self.logger.error("Task submission failed", extra={"error": str(e)})
            raise

    def cancel_task(self, request: CancelRequest) -> CancelResponse:
        """Cancel a running task.

        Args:
            request: Cancel request containing task ID

        Returns:
            Response indicating cancellation status
        """
        self.logger.debug("Cancelling task", extra={"task_id": request.task_id})
        self.metrics.increment("application.cancel_task.calls")

        try:
            response = self._cancel_service.execute(request)
            self.metrics.increment("application.cancel_task.success")
            self.logger.info("Task cancelled successfully", extra={"task_id": request.task_id})
            return response
        except Exception as e:
            self.metrics.increment("application.cancel_task.errors")
            self.logger.error(
                "Task cancellation failed", extra={"task_id": request.task_id, "error": str(e)}
            )
            raise

    def query_status(self, request: StatusRequest) -> StatusResponse:
        """Query the status of a task.

        Args:
            request: Status request containing task ID or filter criteria

        Returns:
            Response containing task status information
        """
        self.logger.debug("Querying task status", extra={"request": request})
        self.metrics.increment("application.query_status.calls")

        try:
            response = self._status_service.execute(request)
            self.metrics.increment("application.query_status.success")
            return response
        except Exception as e:
            self.metrics.increment("application.query_status.errors")
            self.logger.error("Status query failed", extra={"error": str(e)})
            raise

    def reserve_capacity(self, request: ReserveRequest) -> ReserveResponse:
        """Reserve compute capacity.

        Args:
            request: Reserve request containing capacity requirements

        Returns:
            Response containing reservation details
        """
        self.logger.debug("Reserving capacity", extra={"request": request})
        self.metrics.increment("application.reserve_capacity.calls")

        try:
            response = self._reserve_service.execute(request)
            self.metrics.increment("application.reserve_capacity.success")
            self.logger.info(
                "Capacity reserved successfully", extra={"reservation_id": response.reservation_id}
            )
            return response
        except Exception as e:
            self.metrics.increment("application.reserve_capacity.errors")
            self.logger.error("Capacity reservation failed", extra={"error": str(e)})
            raise


def create_application(
    provider: Provider,
    metrics: MetricsProtocol | None = None,
    logger: LoggingProtocol | None = None,
    storage: StorageProtocol | None = None,
) -> ApplicationFacade:
    """Factory function to create an ApplicationFacade with sensible defaults.

    Args:
        provider: Provider implementation (required)
        metrics: Metrics port (optional, defaults to NoopMetrics)
        logger: Logging port (optional, defaults to NoopLogger)
        storage: Storage port (optional)

    Returns:
        Configured ApplicationFacade instance
    """
    # Default ports: use explicit noop adapters to respect boundaries
    from flow.adapters.logging.noop import NoopLogger
    from flow.adapters.metrics.noop import NoopMetrics

    return ApplicationFacade(
        provider=provider,
        metrics=metrics or NoopMetrics(),
        logger=logger or NoopLogger(),
        storage=storage,
    )
