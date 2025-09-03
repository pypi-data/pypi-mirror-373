"""Auction finding and matching functionality for Mithril provider.

Auction discovery functionality with:
- Multiple data sources (API and local catalog)
- Complex matching criteria
- Data enrichment from local catalogs
"""

import logging
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

import yaml

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.domain.models import Auction
from flow.errors import FlowError
from flow.protocols.bidding import AuctionCriteria

logger = logging.getLogger(__name__)


class AuctionCatalogError(FlowError):
    """Error loading or parsing auction catalog."""

    pass


# AuctionCriteria is now imported from domain services


class AuctionMatcher:
    """Matches auctions against specified criteria."""

    def __init__(self, criteria: AuctionCriteria):
        self.criteria = criteria

    def matches(self, auction: Auction) -> bool:
        """Check if auction matches all criteria."""
        checks = [
            self._check_gpu_type(auction),
            self._check_gpu_count(auction),
            self._check_region(auction),
            self._check_price(auction),
            self._check_instance_type(auction),
            self._check_interconnects(auction),
        ]

        # Log failures for debugging
        failures = [check for check in checks if check[0] is False]
        if failures:
            logger.debug(f"Auction {auction.auction_id} failed checks: {[f[1] for f in failures]}")

        return all(check[0] for check in checks)

    def _check_gpu_type(self, auction: Auction) -> tuple[bool, str]:
        """Check GPU type match."""
        if not self.criteria.gpu_type:
            return True, "No GPU type requirement"

        if not auction.gpu_type:
            return False, "Auction has no GPU type"

        # Normalize and compare
        expected = self.criteria.gpu_type.lower().replace("-", "").replace("_", "")
        actual = auction.gpu_type.lower().replace("-", "").replace("_", "")

        # Check for exact match or partial match (e.g., "A100" matches "NVIDIA A100-80GB")
        if expected in actual or actual in expected:
            return True, f"GPU type matches: {auction.gpu_type}"

        return False, f"GPU type mismatch: wanted {self.criteria.gpu_type}, got {auction.gpu_type}"

    def _check_gpu_count(self, auction: Auction) -> tuple[bool, str]:
        """Check GPU count requirements."""
        if self.criteria.min_gpu_count is None:
            return True, "No GPU count requirement"

        available = auction.available_gpus or 0
        if available >= self.criteria.min_gpu_count:
            return True, f"Sufficient GPUs: {available} >= {self.criteria.min_gpu_count}"

        return False, f"Insufficient GPUs: {available} < {self.criteria.min_gpu_count}"

    def _check_region(self, auction: Auction) -> tuple[bool, str]:
        """Check region match."""
        if not self.criteria.region:
            return True, "No region requirement"

        if auction.region == self.criteria.region:
            return True, f"Region matches: {auction.region}"

        return False, f"Region mismatch: wanted {self.criteria.region}, got {auction.region}"

    def _check_price(self, auction: Auction) -> tuple[bool, str]:
        """Check price constraints."""
        if self.criteria.max_price_per_hour is None:
            return True, "No price limit"

        if auction.price_per_hour and auction.price_per_hour <= self.criteria.max_price_per_hour:
            return (
                True,
                f"Price acceptable: ${auction.price_per_hour} <= ${self.criteria.max_price_per_hour}",
            )

        return (
            False,
            f"Price too high: ${auction.price_per_hour} > ${self.criteria.max_price_per_hour}",
        )

    def _check_instance_type(self, auction: Auction) -> tuple[bool, str]:
        """Check instance type match."""
        if not self.criteria.instance_type:
            return True, "No instance type requirement"

        if auction.instance_type_id == self.criteria.instance_type:
            return True, "Instance type matches"

        return False, "Instance type mismatch"

    def _check_interconnects(self, auction: Auction) -> tuple[bool, str]:
        """Check interconnect requirements."""
        if self.criteria.internode_interconnect:
            if auction.internode_interconnect != self.criteria.internode_interconnect:
                return False, "Internode interconnect mismatch"

        if self.criteria.intranode_interconnect:
            if auction.intranode_interconnect != self.criteria.intranode_interconnect:
                return False, "Intranode interconnect mismatch"

        return True, "Interconnects match"


class AuctionFinder:
    """Finds and filters auctions from multiple sources."""

    def __init__(
        self,
        api_client: MithrilApiClient,
        local_catalog_path: Path | None = None,
    ):
        """Initialize auction finder.

        Args:
            http_client: HTTP client for API calls
            local_catalog_path: Optional path to local auction catalog
        """
        # Centralized API client
        self._api: MithrilApiClient = api_client
        self.local_catalog_path = local_catalog_path or self._default_catalog_path()
        self._catalog_cache: dict[str, Any] | None = None

    def _default_catalog_path(self) -> Path:
        """Get default catalog path inside the provider package (zip-safe)."""
        res = files("flow.adapters.providers.builtin.mithril").joinpath(
            "mithril_auction_catalog.yaml"
        )
        return Path(as_file(res).__enter__())

    def fetch_auctions(
        self,
        from_api: bool = True,
        from_catalog: bool = True,
        criteria: AuctionCriteria | None = None,
    ) -> list[Auction]:
        """Fetch auctions from configured sources.

        Args:
            from_api: Whether to fetch from Mithril API
            from_catalog: Whether to include local catalog
            criteria: Optional pre-filtering criteria

        Returns:
            List of Auction objects
        """
        auctions = []

        # Fetch from API
        if from_api:
            api_auctions = self._fetch_from_api(criteria)
            auctions.extend(api_auctions)
            logger.info(f"Fetched {len(api_auctions)} auctions from API")

        # Fetch from local catalog
        if from_catalog and self.local_catalog_path.exists():
            catalog_auctions = self._fetch_from_catalog(criteria)
            auctions.extend(catalog_auctions)
            logger.info(f"Loaded {len(catalog_auctions)} auctions from catalog")

        # Deduplicate by auction_id
        seen = set()
        unique_auctions = []
        for auction in auctions:
            if auction.auction_id not in seen:
                seen.add(auction.auction_id)
                unique_auctions.append(auction)

        return unique_auctions

    def _fetch_from_api(self, criteria: AuctionCriteria | None) -> list[Auction]:
        """Fetch auctions from Mithril API."""
        params = {"limit": "100"}

        if criteria:
            if criteria.instance_type:
                params["instance_type"] = criteria.instance_type
            if criteria.region:
                params["region"] = criteria.region
            if criteria.min_gpu_count:
                params["min_gpu_count"] = str(criteria.min_gpu_count)
            if criteria.max_price_per_hour:
                params["max_price"] = str(criteria.max_price_per_hour)

        response = self._api.list_legacy_auctions(params)

        auctions = []
        for data in response.get("auctions", []):
            auction = Auction(
                auction_id=data.get("fid", ""),
                instance_type_id=data.get("instance_type_id"),
                gpu_type=data.get("gpu_type"),
                available_gpus=data.get("available_gpus", 0),
                price_per_hour=float(data.get("price", 0)) / 100,  # Convert cents to dollars
                region=data.get("region"),
                internode_interconnect=data.get("internode_interconnect"),
                intranode_interconnect=data.get("intranode_interconnect"),
            )
            auctions.append(auction)

        return auctions

    def _fetch_from_catalog(self, criteria: AuctionCriteria | None) -> list[Auction]:
        """Load auctions from local catalog."""
        if not self._catalog_cache:
            self._load_catalog()

        auctions = []

        # Catalog structure: {gpu_type: {region: [auction_data]}}
        for gpu_type, regions in self._catalog_cache.items():
            # Pre-filter by GPU type if specified
            if criteria and criteria.gpu_type:
                if not self._matches_gpu_type(gpu_type, criteria.gpu_type):
                    continue

            for region, auction_list in regions.items():
                # Pre-filter by region if specified
                if criteria and criteria.region and region != criteria.region:
                    continue

                for data in auction_list:
                    auction = self._parse_catalog_auction(data, gpu_type, region)
                    if auction:
                        auctions.append(auction)

        return auctions

    def _load_catalog(self):
        """Load catalog from YAML file."""
        try:
            if self.local_catalog_path:
                with open(self.local_catalog_path) as f:
                    self._catalog_cache = yaml.safe_load(f) or {}
            else:
                res = files("flow.adapters.providers.builtin.mithril").joinpath(
                    "mithril_auction_catalog.yaml"
                )
                with as_file(res) as p:
                    with open(p) as f:
                        self._catalog_cache = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load auction catalog: {e}")
            self._catalog_cache = {}

    def _matches_gpu_type(self, catalog_type: str, requested_type: str) -> bool:
        """Check if catalog GPU type matches requested type."""
        # Normalize for comparison
        cat_norm = catalog_type.lower().replace("-", "").replace("_", "")
        req_norm = requested_type.lower().replace("-", "").replace("_", "")
        return req_norm in cat_norm or cat_norm in req_norm

    def _parse_catalog_auction(
        self, data: dict[str, Any], gpu_type: str, region: str
    ) -> Auction | None:
        """Parse auction from catalog data."""
        try:
            base = data.get("base_auction", {})
            return Auction(
                auction_id=base.get("id", f"catalog-{gpu_type}-{region}"),
                instance_type_id=base.get("instance_type_id"),
                gpu_type=base.get("gpu_type", gpu_type),
                available_gpus=base.get("inventory_quantity", 0),
                price_per_hour=base.get("last_price", 0.0),
                region=base.get("region", region),
                internode_interconnect=base.get("internode_interconnect"),
                intranode_interconnect=base.get("intranode_interconnect"),
            )
        except Exception as e:
            logger.warning(f"Failed to parse catalog auction: {e}")
            return None

    def find_matching_auctions(
        self,
        auctions: list[Auction],
        criteria: AuctionCriteria,
    ) -> list[Auction]:
        """Filter auctions by criteria.

        Args:
            auctions: List of auctions to filter
            criteria: Matching criteria

        Returns:
            List of matching auctions
        """
        matcher = AuctionMatcher(criteria)
        matching = [a for a in auctions if matcher.matches(a)]

        logger.info(f"Found {len(matching)} matching auctions out of {len(auctions)} total")

        return matching

    def enrich_with_catalog(self, auctions: list[Auction]) -> list[Auction]:
        """Enrich API auctions with catalog data.

        Useful when API returns incomplete data that can be supplemented
        from the local catalog.

        Args:
            auctions: Auctions from API

        Returns:
            Enriched auctions
        """
        if not self._catalog_cache:
            self._load_catalog()

        # Build lookup by instance_type_id
        catalog_lookup = {}
        for gpu_type, regions in self._catalog_cache.items():
            for region, auction_list in regions.items():
                for data in auction_list:
                    base = data.get("base_auction", {})
                    if instance_id := base.get("instance_type_id"):
                        catalog_lookup[instance_id] = base

        # Enrich auctions
        enriched = []
        for auction in auctions:
            if auction.instance_type_id in catalog_lookup:
                catalog_data = catalog_lookup[auction.instance_type_id]
                # Fill in missing fields from catalog
                enriched_auction = Auction(
                    auction_id=auction.auction_id,
                    instance_type_id=auction.instance_type_id,
                    gpu_type=auction.gpu_type or catalog_data.get("gpu_type"),
                    available_gpus=auction.available_gpus
                    or catalog_data.get("inventory_quantity", 0),
                    price_per_hour=auction.price_per_hour or catalog_data.get("last_price", 0.0),
                    region=auction.region or catalog_data.get("region"),
                    internode_interconnect=auction.internode_interconnect
                    or catalog_data.get("internode_interconnect"),
                    intranode_interconnect=auction.intranode_interconnect
                    or catalog_data.get("intranode_interconnect"),
                )
                enriched.append(enriched_auction)
            else:
                enriched.append(auction)

        return enriched
