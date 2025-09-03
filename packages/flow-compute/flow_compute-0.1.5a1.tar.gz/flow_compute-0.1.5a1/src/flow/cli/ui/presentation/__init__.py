"""Presentation layer for CLI commands.

Contains renderers and UI composition helpers that build Rich renderables.
"""

from .reservations_view import (
    choose_availability_slot,
    handle_availability_flow,
    handle_list_flow,
    render_availability,
    render_reservation_details,
    render_reservation_live,
    render_reservations_csv,
    render_reservations_table,
    render_reservations_yaml,
)

__all__ = [
    "render_reservation_details",
    "render_reservations_table",
    "render_reservations_csv",
    "render_reservations_yaml",
    "render_availability",
    "render_reservation_live",
    "choose_availability_slot",
    "handle_availability_flow",
    "handle_list_flow",
]
