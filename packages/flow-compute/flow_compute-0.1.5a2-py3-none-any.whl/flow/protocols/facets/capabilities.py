from __future__ import annotations

"""Provider capabilities aggregate of facet protocols."""

from dataclasses import dataclass, field

from .compute import ComputeProtocol
from .logs import LogsProtocol
from .reservations import ReservationsProtocol
from .ssh import SSHProtocol
from .storage import StorageProtocol


@dataclass(frozen=True)
class ProviderFacets:
    """Aggregates facet implementations exposed by a provider.

    Empty (None) facets indicate the provider does not implement that
    capability. The `features` set can be used for fine-grained checks.
    """

    compute: ComputeProtocol | None = None
    logs: LogsProtocol | None = None
    storage: StorageProtocol | None = None
    reservations: ReservationsProtocol | None = None
    ssh: SSHProtocol | None = None
    features: set[str] = field(default_factory=set)
