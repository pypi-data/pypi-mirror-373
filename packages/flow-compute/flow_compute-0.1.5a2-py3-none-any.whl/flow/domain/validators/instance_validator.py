"""Instance type validation for Flow SDK with strong typing."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Provider-agnostic models used for validation (kept minimal and local to domain)
class GPUModel(BaseModel):
    name: str
    vram_gb: int = Field(..., ge=1)
    count: int = Field(..., ge=1)


class InstanceTypeModel(BaseModel):
    name: str
    fid: str
    cpu_cores: int
    ram_gb: int
    gpus: list[GPUModel]


class AuctionModel(BaseModel):
    # Accept any fields from availability APIs; domain doesn't depend on specifics here
    model_config = ConfigDict(extra="allow")


InstanceTypesResponse = list[InstanceTypeModel]
SpotAvailabilityResponse = list[AuctionModel]
from flow.domain.parsers.instance_parser import canonicalize_instance_type
from flow.errors import ValidationError

logger = logging.getLogger(__name__)


class InstanceValidator:
    """Validates instance types against available offerings."""

    def __init__(self, cache_dir: Path | None = None):
        """Initialize validator with optional cache directory.

        Args:
            cache_dir: Directory to cache API responses (defaults to ~/.flow/cache)
        """
        self.cache_dir = cache_dir or (Path.home() / ".flow" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._instance_types: dict[str, InstanceTypeModel] | None = None
        self._availability: list[AuctionModel] | None = None
        self._cache_ttl = timedelta(hours=1)
        # Map from original API names to canonical names
        self._name_mapping: dict[str, str] = {}

    def load_cached_data(self) -> bool:
        """Load cached instance data if available and fresh.

        Returns:
            True if valid cached data was loaded
        """
        instance_cache = self.cache_dir / "instance_types.json"
        availability_cache = self.cache_dir / "spot_availability.json"

        if not (instance_cache.exists() and availability_cache.exists()):
            return False

        try:
            cache_age = datetime.now() - datetime.fromtimestamp(instance_cache.stat().st_mtime)
            if cache_age > self._cache_ttl:
                logger.debug("Cache expired, will refresh")
                return False

            with open(instance_cache) as f:
                raw_data = json.load(f)
                instance_types = [InstanceTypeModel(**item) for item in raw_data]
                self._instance_types = {}
                self._name_mapping = {}

                for inst in instance_types:
                    # Store by canonical name
                    canonical_name = canonicalize_instance_type(inst.name)
                    self._instance_types[canonical_name] = inst
                    self._name_mapping[inst.name] = canonical_name
                    logger.debug(f"Loaded instance type: {inst.name} -> {canonical_name}")

            with open(availability_cache) as f:
                raw_data = json.load(f)
                self._availability = [AuctionModel(**item) for item in raw_data]

            logger.debug(f"Loaded {len(self._instance_types)} instance types from cache")
            return True

        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return False

    def save_cache(
        self, instance_types: InstanceTypesResponse, availability: SpotAvailabilityResponse
    ) -> None:
        """Save instance data to cache.

        Args:
            instance_types: Instance type data from API
            availability: Spot availability data from API
        """
        try:
            with open(self.cache_dir / "instance_types.json", "w") as f:
                json.dump([item.dict() for item in instance_types], f)

            with open(self.cache_dir / "spot_availability.json", "w") as f:
                json.dump([item.dict() for item in availability], f)

            logger.debug("Saved instance data to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def fetch_from_api(self, http_client) -> None:
        """Fetch instance data from API.

        Args:
            http_client: HTTP client to use for API calls
        """
        try:
            raw_instance_types = http_client.request("GET", "/v2/instance-types")
            instance_types = [InstanceTypeModel(**item) for item in raw_instance_types]
            self._instance_types = {}
            self._name_mapping = {}

            for inst in instance_types:
                # Store by canonical name
                canonical_name = canonicalize_instance_type(inst.name)
                self._instance_types[canonical_name] = inst
                self._name_mapping[inst.name] = canonical_name
                logger.debug(f"Fetched instance type: {inst.name} -> {canonical_name}")

            raw_availability = http_client.request("GET", "/v2/spot/availability")
            self._availability = [AuctionModel(**item) for item in raw_availability]

            self.save_cache(instance_types, self._availability)

            logger.info(f"Fetched {len(self._instance_types)} instance types from API")

        except Exception as e:
            logger.error(f"Failed to fetch instance data from API: {e}")
            if not self._instance_types:
                self._load_fallback_instances()

    def _load_fallback_instances(self) -> None:
        """Load hardcoded fallback instance types."""
        fallback_configs = [
            ("a100", 80, "sxm4", [1, 2, 4, 8]),
            ("a100", 40, "sxm4", [1, 2, 4, 8]),
            ("h100", 80, "sxm5", [1, 2, 4, 8]),
            ("a40", 48, "pcie", [1, 2, 4, 8]),
            ("a5000", 24, "pcie", [1, 2, 4]),
        ]

        self._instance_types = {}
        for gpu, memory, interconnect, counts in fallback_configs:
            for count in counts:
                # Use canonical format as the key
                canonical_name = f"{gpu}.{memory}gb.{interconnect}.{count}x"
                self._instance_types[canonical_name] = InstanceTypeModel(
                    name=canonical_name,
                    fid=canonical_name,
                    cpu_cores=16 * count,
                    ram_gb=128 * count,
                    gpus=[GPUModel(name=f"NVIDIA {gpu.upper()}", vram_gb=memory, count=count)],
                )

        self._instance_types["h100x1"] = self._instance_types["h100.80gb.sxm5.1x"]
        self._instance_types["h100.80gb.sxm"] = self._instance_types["h100.80gb.sxm5.1x"]
        logger.warning(f"Using fallback instance types ({len(self._instance_types)} types)")

    def ensure_loaded(self, http_client=None) -> None:
        """Ensure instance data is loaded.

        Args:
            http_client: Optional HTTP client for API calls
        """
        if self._instance_types is not None:
            return

        if self.load_cached_data():
            return

        if http_client:
            self.fetch_from_api(http_client)
        else:
            self._load_fallback_instances()

    def validate_instance_type(
        self, instance_type: str, http_client=None
    ) -> tuple[str, InstanceTypeModel]:
        """Validate instance type and return normalized name with details.

        Args:
            instance_type: Instance type to validate
            http_client: Optional HTTP client for API calls

        Returns:
            Tuple of (normalized_name, instance_details)

        Raises:
            ValidationError: If instance type is invalid
        """
        self.ensure_loaded(http_client)

        if not self._instance_types:
            raise ValidationError("No instance type data available")

        # Use canonicalize_instance_type function directly
        canonical_name = canonicalize_instance_type(instance_type)
        logger.debug(f"Validating instance type: {instance_type} -> {canonical_name}")
        logger.debug(f"Available canonical types: {sorted(self._instance_types.keys())[:5]}...")

        if canonical_name not in self._instance_types:
            valid_types = sorted(self._instance_types.keys())
            raise ValidationError(
                f"Invalid instance type: {instance_type} (canonical: {canonical_name}). "
                f"Valid types: {', '.join(valid_types[:10])}..."
            )

        return canonical_name, self._instance_types[canonical_name]

    def get_available_instance_types(self, http_client=None) -> list[str]:
        """Get list of available instance types.

        Args:
            http_client: Optional HTTP client for API calls

        Returns:
            Sorted list of instance type names
        """
        self.ensure_loaded(http_client)
        return sorted(self._instance_types.keys()) if self._instance_types else []

    def get_instance_details(
        self, instance_type: str, http_client=None
    ) -> InstanceTypeModel | None:
        """Get details for a specific instance type.

        Args:
            instance_type: Instance type name
            http_client: Optional HTTP client for API calls

        Returns:
            Instance details or None if not found
        """
        self.ensure_loaded(http_client)
        if not self._instance_types:
            return None

        try:
            canonical_name, details = self.validate_instance_type(instance_type, http_client)
            return details
        except ValidationError:
            return None


# Module-level singleton
_validator_instance: InstanceValidator | None = None


def get_validator() -> InstanceValidator:
    """Get the singleton instance validator."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = InstanceValidator()
    return _validator_instance


def validate_instance_type(instance_type: str, region: str | None = None, http_client=None) -> None:
    """Validate an instance type.

    Args:
        instance_type: Instance type to validate
        region: Optional region to check (not used in current implementation)
        http_client: Optional HTTP client for API calls

    Raises:
        ValidationError: If validation fails
    """
    validator = get_validator()
    # Class method returns (canonical_name, instance_details), but we just validate
    _, _ = validator.validate_instance_type(instance_type, http_client)
