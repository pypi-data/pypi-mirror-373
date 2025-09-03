"""Reservation management service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flow.sdk.models import Reservation

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient


class ReservationsService:
    """Service for managing reservations."""

    def __init__(self, api: MithrilApiClient) -> None:
        """Initialize reservation service.

        Args:
            api: Mithril API client for reservation operations
        """
        self._api = api

    def create(
        self,
        instance_type: str,
        num_nodes: int,
        duration_hours: float,
        region: str | None = None,
        earliest_start_time: str | None = None,
        latest_start_time: str | None = None,
    ) -> Reservation:
        """Create a new reservation.

        Args:
            instance_type: Type of instance to reserve
            num_nodes: Number of nodes to reserve
            duration_hours: Duration of reservation in hours
            region: Preferred region (optional)
            earliest_start_time: Earliest start time in ISO format (optional)
            latest_start_time: Latest start time in ISO format (optional)

        Returns:
            Created reservation

        Raises:
            MithrilAPIError: If reservation creation fails
        """
        spec = {
            "instance_type": instance_type,
            "num_nodes": num_nodes,
            "duration": int(duration_hours * 3600),  # Convert to seconds
        }

        if region:
            spec["region"] = region
        if earliest_start_time:
            spec["earliest_start_time"] = earliest_start_time
        if latest_start_time:
            spec["latest_start_time"] = latest_start_time

        response = self._api.create_reservation(spec)
        return Reservation.from_dict(response)

    def list(self, params: dict[str, Any] | None = None) -> list[Reservation]:
        """List reservations.

        Args:
            params: Optional filter parameters

        Returns:
            List of reservations
        """
        params = params or {}
        response = self._api.list_reservations(params)

        # Handle various response formats
        if isinstance(response, dict):
            data = response.get("data", response.get("reservations", []))
        else:
            data = response

        if not isinstance(data, list):
            data = [data] if data else []

        return [Reservation.from_dict(r) for r in data]

    def get(self, reservation_id: str) -> Reservation:
        """Get a specific reservation.

        Args:
            reservation_id: ID of reservation to retrieve

        Returns:
            Reservation details

        Raises:
            MithrilAPIError: If reservation not found
        """
        response = self._api.get_reservation(reservation_id)
        return Reservation.from_dict(response)

    def get_availability(
        self,
        instance_type: str,
        num_nodes: int,
        duration_hours: float,
        earliest_start_time: str | None = None,
        latest_end_time: str | None = None,
    ) -> list[dict[str, Any]]:
        """Check availability for a reservation.

        Args:
            instance_type: Type of instance to check
            num_nodes: Number of nodes needed
            duration_hours: Duration needed in hours
            earliest_start_time: Earliest start time in ISO format (optional)
            latest_end_time: Latest end time in ISO format (optional)

        Returns:
            List of availability windows
        """
        params = {
            "instance_type": instance_type,
            "num_nodes": num_nodes,
            "duration": int(duration_hours * 3600),
        }

        if earliest_start_time:
            params["earliest_start_time"] = earliest_start_time
        if latest_end_time:
            params["latest_end_time"] = latest_end_time

        resp = self._api.get_reservation_availability(params)
        return resp.get("data", resp) if isinstance(resp, dict) else resp
