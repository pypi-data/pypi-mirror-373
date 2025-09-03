from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from flow.sdk.models.enums import ReservationStatus


class ReservationSpec(BaseModel):
    """Provider-agnostic spec for creating a reservation."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        description="Optional reservation name for display",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$",
    )
    project_id: str | None = Field(default=None, description="Provider project/workspace ID")
    instance_type: str = Field(..., description="Explicit instance type (e.g., 'a100', '8xh100')")
    region: str = Field(..., description="Target region/zone for the reservation")
    quantity: int = Field(1, ge=1, le=100, description="Number of instances to reserve")
    start_time_utc: datetime = Field(..., description="Reservation start time (UTC)")
    duration_hours: int = Field(
        ..., ge=3, le=336, description="Reservation duration in hours (3-336)"
    )
    ssh_keys: list[str] = Field(default_factory=list, description="Authorized SSH key IDs")
    volumes: list[str] = Field(
        default_factory=list, description="Volume IDs to attach (provider-specific)"
    )
    startup_script: str | None = Field(
        default=None, description="Optional startup script executed when instances boot"
    )


class Reservation(BaseModel):
    """Reservation details returned by providers."""

    model_config = ConfigDict(extra="allow")

    reservation_id: str = Field(..., description="Reservation identifier")
    name: str | None = Field(default=None, description="Display name")
    status: ReservationStatus = Field(..., description="Lifecycle state")
    instance_type: str = Field(..., description="Instance type identifier")
    region: str = Field(..., description="Region/zone")
    quantity: int = Field(..., ge=1, description="Number of instances")
    start_time_utc: datetime = Field(..., description="Scheduled start time (UTC)")
    end_time_utc: datetime | None = Field(default=None, description="Scheduled end time (UTC)")
    price_total_usd: float | None = Field(
        default=None, ge=0, description="Quoted/actual total price"
    )
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
