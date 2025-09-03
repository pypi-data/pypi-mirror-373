"""Provider facets - domain-specific operation handlers."""

from flow.adapters.providers.builtin.mithril.provider.facets.compute import ComputeFacet
from flow.adapters.providers.builtin.mithril.provider.facets.logs import LogsFacet
from flow.adapters.providers.builtin.mithril.provider.facets.meta import MetaFacet
from flow.adapters.providers.builtin.mithril.provider.facets.reservations import ReservationsFacet
from flow.adapters.providers.builtin.mithril.provider.facets.selection import SelectionFacet
from flow.adapters.providers.builtin.mithril.provider.facets.ssh import SSHFacet
from flow.adapters.providers.builtin.mithril.provider.facets.storage import StorageFacet
from flow.adapters.providers.builtin.mithril.provider.facets.tasks import TasksFacet
from flow.protocols.selection import SelectionOutcome

__all__ = [
    "ComputeFacet",
    "LogsFacet",
    "MetaFacet",
    "ReservationsFacet",
    "SelectionFacet",
    "SelectionOutcome",
    "SSHFacet",
    "StorageFacet",
    "TasksFacet",
]
