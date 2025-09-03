from __future__ import annotations

"""Reservations facet: capacity reservation lifecycle."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ReservationsProtocol(Protocol):
    """Reservation creation and inspection."""

    def create_reservation(
        self,
        instance_type: str,
        config: Any,
        volume_ids: list[str] | None = None,
    ) -> Any: ...

    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Any]: ...

    def get_reservation(self, reservation_id: str) -> Any: ...
