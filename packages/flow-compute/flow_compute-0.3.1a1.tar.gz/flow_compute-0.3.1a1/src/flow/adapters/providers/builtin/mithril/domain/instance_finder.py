"""Instance finding and auction optimization service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from flow.adapters.providers.builtin.mithril.domain.models import Auction
from flow.sdk.models import Instance

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient

logger = logging.getLogger(__name__)


class InstanceFinderService:
    """Service for finding instances and optimal auctions."""

    def __init__(self, api: MithrilApiClient) -> None:
        """Initialize instance finder service.

        Args:
            api: Mithril API client for instance operations
        """
        self._api = api

    def find_instances(
        self,
        requirements: dict[str, Any],
        limit: int = 100,
    ) -> list[Instance]:
        """Find instances matching requirements.

        Args:
            requirements: Dict with search criteria like:
                - instance_type: Type of instance
                - min_gpu: Minimum GPU count
                - min_memory: Minimum memory in GB
                - region: Preferred region
                - max_price: Maximum price per hour
            limit: Maximum number of results

        Returns:
            List of matching instances
        """
        # Build search parameters
        params = {"limit": limit}

        # Map common requirement keys to API parameters
        mapping = {
            "instance_type": "instance_type",
            "min_gpu": "min_gpu_count",
            "min_memory": "min_memory_gb",
            "region": "region",
            "max_price": "max_price_per_hour",
            "gpu_type": "gpu_type",
        }

        for key, api_key in mapping.items():
            if key in requirements and requirements[key] is not None:
                params[api_key] = requirements[key]

        # Add any unmapped parameters directly
        for key, value in requirements.items():
            if key not in mapping and value is not None:
                params[key] = value

        # Query API
        response = self._api.list_instances(params)

        # Parse response
        if isinstance(response, dict):
            data = response.get("data", response.get("instances", []))
        else:
            data = response

        if not isinstance(data, list):
            data = [data] if data else []

        # Convert to Instance objects
        instances = []
        for item in data:
            try:
                instances.append(Instance.from_dict(item))
            except Exception as e:
                logger.debug(f"Failed to parse instance: {e}")
                continue

        return instances[:limit]

    def find_optimal_auction(
        self,
        instance_type: str,
        region: str | None = None,
        max_price: float | None = None,
        min_gpu: int | None = None,
    ) -> Auction | None:
        """Find the optimal auction for given requirements.

        This method searches for the best available auction based on:
        1. Instance type compatibility
        2. Region preference
        3. Price constraints
        4. GPU requirements

        Args:
            instance_type: Required instance type
            region: Preferred region (optional)
            max_price: Maximum acceptable price per hour (optional)
            min_gpu: Minimum GPU count required (optional)

        Returns:
            Best matching auction or None if no suitable auction found
        """
        # Build auction search parameters
        params = {
            "instance_type": instance_type,
            "status": "open",  # Only look for open auctions
            "limit": 50,  # Get enough to find optimal
        }

        if region:
            params["region"] = region
        if max_price is not None:
            params["max_price"] = max_price

        # Query auctions
        response = self._api.list_auctions(params)

        # Parse response
        if isinstance(response, dict):
            auctions_data = response.get("data", response.get("auctions", []))
        else:
            auctions_data = response

        if not isinstance(auctions_data, list):
            auctions_data = [auctions_data] if auctions_data else []

        # Convert to Auction objects and filter
        valid_auctions = []
        for auction_data in auctions_data:
            try:
                auction = Auction.from_dict(auction_data)

                # Apply additional filters
                if min_gpu is not None:
                    gpu_count = auction_data.get("gpu_count", 0)
                    if gpu_count < min_gpu:
                        continue

                if max_price is not None:
                    price = self._parse_price(auction_data.get("current_price", 0))
                    if price > max_price:
                        continue

                valid_auctions.append(auction)
            except Exception as e:
                logger.debug(f"Failed to parse auction: {e}")
                continue

        if not valid_auctions:
            return None

        # Sort by price (ascending) and return best
        valid_auctions.sort(key=lambda a: self._parse_price(a.current_price))
        return valid_auctions[0]

    def _parse_price(self, price: Any) -> float:
        """Parse price from various formats.

        Args:
            price: Price in string or numeric format

        Returns:
            Price as float
        """
        if isinstance(price, (int, float)):
            return float(price)

        if isinstance(price, str):
            # Remove currency symbols and parse
            price_str = price.strip().replace("$", "").replace(",", "")
            try:
                return float(price_str)
            except ValueError:
                return 0.0

        return 0.0
