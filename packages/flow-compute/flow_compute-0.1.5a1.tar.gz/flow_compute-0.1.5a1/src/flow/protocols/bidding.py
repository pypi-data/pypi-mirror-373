from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class BidRequest(Protocol):
    instance_type_id: str
    limit_price: float | None
    count: int
    region: str | None
    metadata: dict[str, Any] | None


class BiddingServiceProtocol(Protocol):
    """Protocol for building provider-agnostic bid requests for spot/reservations."""

    def build_bid(
        self,
        *,
        instance_type: str,
        count: int = 1,
        max_price_per_hour: float | None = None,
        region: str | None = None,
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...


__all__ = ["BiddingServiceProtocol", "BidRequest"]


@dataclass
class AuctionCriteria:
    gpu_type: str | None = None
    num_gpus: int | None = None
    min_gpu_count: int | None = None
    region: str | None = None
    max_price_per_hour: float | None = None
    instance_type: str | None = None
    internode_interconnect: str | None = None
    intranode_interconnect: str | None = None

    def __post_init__(self) -> None:
        if self.min_gpu_count is None and self.num_gpus is not None:
            self.min_gpu_count = self.num_gpus


__all__.append("AuctionCriteria")
