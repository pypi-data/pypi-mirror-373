from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class InstanceCatalogEntry(Protocol):
    name: str
    gpu_type: str
    gpu_count: int
    price_per_hour: float | None
    available: bool | None


class SelectionServiceProtocol(Protocol):
    """Protocol for instance selection/capability discovery.

    Implementations provide a provider-agnostic way to query instance offerings
    and select candidates by basic capabilities.
    """

    def list_instances(self, *, region: str | None = None) -> list[dict[str, Any]]: ...

    def find_by_min_memory(
        self, min_memory_gb: int, *, max_price: float | None = None
    ) -> list[dict[str, Any]]: ...


__all__ = ["SelectionServiceProtocol", "InstanceCatalogEntry"]


# Normalized selection outcome used by providers and application code
@dataclass
class SelectionOutcome:
    region: str | None
    auction: Any | None
    instance_type_id: str | None
    candidate_regions: list[str]
    source: str

    def is_successful(self) -> bool:
        return self.region is not None

    def has_auction(self) -> bool:
        return self.auction is not None


__all__.append("SelectionOutcome")
