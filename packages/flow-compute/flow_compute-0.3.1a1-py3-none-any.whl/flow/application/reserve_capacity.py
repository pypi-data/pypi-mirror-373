"""Reserve capacity use case.

Orchestrates capacity reservation through the provider port.
"""

from dataclasses import dataclass
from datetime import datetime

from flow.domain.ir.spec import ResourceSpec as Resources
from flow.protocols.provider import Provider


@dataclass(frozen=True, slots=True)
class ReserveCapacityRequest:
    """Request to reserve compute capacity."""

    resources: Resources
    duration_hours: int
    start_time: datetime | None = None
    auto_renew: bool = False


@dataclass(frozen=True, slots=True)
class ReservationInfo:
    """Reservation information."""

    reservation_id: str
    instance_type: str
    price_per_hour: float
    total_cost: float
    start_time: datetime
    end_time: datetime
    status: str


@dataclass(frozen=True, slots=True)
class ReserveCapacityResponse:
    """Response from capacity reservation."""

    success: bool
    reservation: ReservationInfo | None = None
    error_message: str | None = None


class ReserveCapacityUseCase:
    """Use case for reserving compute capacity."""

    def __init__(self, provider: Provider):
        """Initialize with provider port.

        Args:
            provider: Provider port implementation
        """
        self._provider = provider

    def execute(self, request: ReserveCapacityRequest) -> ReserveCapacityResponse:
        """Reserve compute capacity.

        Args:
            request: Reservation request with resource requirements

        Returns:
            Response with reservation details or error
        """
        try:
            reservation = self._provider.reserve_capacity(
                resources=request.resources,
                duration_hours=request.duration_hours,
                start_time=request.start_time,
                auto_renew=request.auto_renew,
            )

            return ReserveCapacityResponse(
                success=True,
                reservation=ReservationInfo(
                    reservation_id=reservation.id,
                    instance_type=reservation.instance_type,
                    price_per_hour=reservation.price_per_hour,
                    total_cost=reservation.total_cost,
                    start_time=reservation.start_time,
                    end_time=reservation.end_time,
                    status=reservation.status,
                ),
            )
        except Exception as e:
            return ReserveCapacityResponse(success=False, error_message=str(e))
