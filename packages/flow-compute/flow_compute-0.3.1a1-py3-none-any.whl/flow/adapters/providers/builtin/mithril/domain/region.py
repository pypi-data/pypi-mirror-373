"""Region availability and selection policy for the Mithril provider.

Provides utilities to query cross-region availability for a resolved
instance type and to select the best region given capacity and price.
"""

from __future__ import annotations

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.domain.models import Auction
from flow.adapters.providers.builtin.mithril.domain.pricing import PricingService


class RegionSelector:
    """Query availability and choose regions for spot instances.

    Args:
        http: HTTP client bound to the Mithril API base URL.
        pricing: Pricing service used to parse price strings.
    """

    def __init__(self, api: MithrilApiClient, pricing: PricingService) -> None:
        self._api = api
        self._pricing = pricing

    def check_availability(self, instance_fid: str) -> dict[str, Auction]:
        """Return cheapest auction per region for the given instance type.

        Tries the primary availability endpoint first. Falls back to legacy
        "auctions" shapes often used in tests/mocks.

        Args:
            instance_fid: Mithril instance type ID (e.g., "it_...")

        Returns:
            Dict mapping region -> Auction describing cheapest option in that region.
        """

        def _normalize_response(resp):
            # Accept list directly
            if isinstance(resp, list):
                return resp
            # Accept dict with "auctions" list
            if isinstance(resp, dict) and isinstance(resp.get("auctions"), list):
                return resp["auctions"]
            return []

        auctions: list[dict] = []
        try:
            primary = self._api.list_spot_availability({"instance_type": instance_fid})
            auctions = _normalize_response(primary)
        except Exception:
            auctions = []

        # Fallback to legacy endpoint if primary didn't yield usable data
        if not auctions:
            try:
                legacy = self._api.list_legacy_auctions({"instance_type": instance_fid})
                auctions = _normalize_response(legacy)
            except Exception:
                auctions = []

        availability_by_region: dict[str, Auction] = {}
        if not auctions:
            return availability_by_region

        for a in auctions:
            # Accept when instance identifier is missing (legacy mocks) or when the
            # response uses a human-readable name instead of an ID. Only filter out
            # entries when the response explicitly provides an instance ID that
            # clearly does not match the requested one.
            resp_instance = a.get("instance_type") or a.get("instanceType") or a.get("type")
            try:
                # If the field looks like a Mithril ID ("it_...") and differs from
                # the requested ID, skip it. Otherwise keep it — the upstream API
                # already scoped results by the requested instance_type.
                if isinstance(resp_instance, str) and resp_instance.startswith("it_"):
                    if resp_instance != instance_fid:
                        continue
            except Exception:
                # Be permissive on unexpected shapes
                pass

            # Fall back to Mithril's primary region when missing
            region = a.get("region") or a.get("location") or "us-central1-b"
            if not region:
                continue

            auction = Auction(
                fid=a.get("fid") or a.get("id") or a.get("auction_id") or "auction-unknown",
                instance_type=resp_instance or instance_fid,
                region=region,
                capacity=a.get("capacity", a.get("available_gpus", 1) or 1),
                last_instance_price=a.get("last_instance_price") or a.get("price") or "$0",
            )
            price = self._pricing.parse_price(auction.last_instance_price)
            if region not in availability_by_region:
                availability_by_region[region] = auction
            else:
                existing = availability_by_region[region]
                existing_price = self._pricing.parse_price(existing.last_instance_price)
                if price < existing_price:
                    availability_by_region[region] = auction
        return availability_by_region

    def select_best_region(
        self, availability: dict[str, Auction], preferred_region: str | None = None
    ) -> str | None:
        """Choose a region given availability and an optional preferred region.

        Policy:
          1. Honor preferred region if available.
          2. Otherwise pick highest capacity, then lowest price.
        """
        if not availability:
            return None
        if preferred_region and preferred_region in availability:
            return preferred_region

        best_region: str | None = None
        best_capacity_price = (-1, float("inf"))
        for region, auction in availability.items():
            capacity = auction.capacity or 0
            price = self._pricing.parse_price(auction.last_instance_price)
            score = (capacity, price)
            if score[0] > best_capacity_price[0] or (
                score[0] == best_capacity_price[0] and score[1] < best_capacity_price[1]
            ):
                best_capacity_price = score
                best_region = region
        return best_region
