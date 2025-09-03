"""Facet protocols for provider capabilities.

These small, role-based protocols adhere to ISP and allow providers to expose
only the capabilities they implement. Callers can depend on the smallest
interfaces needed for their use case.
"""

from __future__ import annotations

from .capabilities import ProviderFacets
from .compute import ComputeProtocol
from .logs import LogsProtocol
from .reservations import ReservationsProtocol
from .ssh import SSHProtocol
from .storage import StorageProtocol

__all__ = [
    "ComputeProtocol",
    "LogsProtocol",
    "ReservationsProtocol",
    "StorageProtocol",
    "SSHProtocol",
    "ProviderFacets",
]
