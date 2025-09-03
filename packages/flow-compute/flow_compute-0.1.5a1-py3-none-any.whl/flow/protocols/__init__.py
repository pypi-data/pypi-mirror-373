"""Contracts (ports) used by the application layer.

Typed ``Protocol`` interfaces define the seams between orchestration and
integration. Adapters implement these contracts; the application orchestrates
against them without knowing concrete details.

Included protocols:
  - ProviderProtocol: provision/submit/status/cancel/reservations
  - StorageProtocol: volume and mount operations
  - LoggerProtocol / MetricsProtocol: observability hooks
  - HTTP/SSH/Startup primitives live alongside as typed helpers
"""

from __future__ import annotations

from flow.protocols.logging import LoggerProtocol
from flow.protocols.metrics import MetricsProtocol
from flow.protocols.provider import ProviderProtocol
from flow.protocols.storage import StorageProtocol

__all__ = [
    "ProviderProtocol",
    "LoggerProtocol",
    "MetricsProtocol",
    "StorageProtocol",
]
