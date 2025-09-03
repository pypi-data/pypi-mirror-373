"""Domain models for instance types and specifications.

This module provides provider-agnostic models for representing
compute instance types and their specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GPUGeneration(Enum):
    """GPU generation categories."""

    CONSUMER = "consumer"  # Gaming GPUs (RTX 3090, etc.)
    DATACENTER = "datacenter"  # Data center GPUs (A100, H100, etc.)
    WORKSTATION = "workstation"  # Professional GPUs (A6000, etc.)
    LEGACY = "legacy"  # Older generation GPUs


@dataclass
class GPUSpec:
    """Specification for a GPU type."""

    name: str  # e.g., "A100", "H100"
    memory_gb: int  # GPU memory in GB
    generation: GPUGeneration  # GPU generation/category
    compute_capability: float  # CUDA compute capability

    def __str__(self) -> str:
        return f"{self.name}-{self.memory_gb}GB"


@dataclass
class InstanceSpec:
    """Complete specification for a compute instance."""

    # Core specs
    gpu_type: str | None  # e.g., "a100", "h100"
    gpu_count: int  # Number of GPUs
    cpu_cores: int | None  # Number of CPU cores
    memory_gb: int | None  # System RAM in GB
    storage_gb: int | None  # Local storage in GB

    # Optional specs
    gpu_spec: GPUSpec | None = None
    network_bandwidth_gbps: float | None = None
    ephemeral: bool = True  # Whether storage is ephemeral

    def to_string(self) -> str:
        """Convert to human-readable string."""
        if self.gpu_count > 1:
            return f"{self.gpu_count}x{self.gpu_type}"
        return self.gpu_type or "cpu"

    @classmethod
    def from_string(cls, spec: str) -> InstanceSpec:
        """Parse instance spec from string like '4xa100'."""
        from flow.domain.parsers.instance_parser import parse_instance_type

        components = parse_instance_type(spec)
        return cls(
            gpu_type=components.gpu_type,
            gpu_count=components.gpu_count or 1,
            cpu_cores=None,
            memory_gb=None,
            storage_gb=None,
        )


@dataclass
class InstanceTypeMapping:
    """Maps user-friendly names to provider-specific IDs."""

    user_name: str  # e.g., "a100", "4xa100"
    provider_id: str  # e.g., "it_abc123"
    spec: InstanceSpec  # Full specification
    available_regions: list[str] | None = None

    def matches(self, query: str) -> bool:
        """Check if this mapping matches a query string."""
        query_lower = query.lower().strip()

        # Exact match
        if query_lower == self.user_name.lower():
            return True

        # Match provider ID
        if query_lower == self.provider_id.lower():
            return True

        # Match spec string representation
        if query_lower == self.spec.to_string().lower():
            return True

        return False


class InstanceTypeRegistry:
    """Registry for managing instance type mappings.

    This is a domain service that manages the mapping between
    user-friendly instance names and provider-specific IDs.
    """

    def __init__(self):
        self._mappings: dict[str, InstanceTypeMapping] = {}
        self._provider_ids: dict[str, InstanceTypeMapping] = {}

    def register(self, mapping: InstanceTypeMapping) -> None:
        """Register an instance type mapping."""
        self._mappings[mapping.user_name.lower()] = mapping
        self._provider_ids[mapping.provider_id] = mapping

    def resolve(self, spec: str) -> str | None:
        """Resolve user spec to provider ID.

        Args:
            spec: User-provided spec (e.g., "a100", "4xa100", "it_abc123")

        Returns:
            Provider-specific ID or None if not found
        """
        spec_lower = spec.lower().strip()

        # Direct provider ID
        if spec_lower.startswith("it_"):
            return spec if spec in self._provider_ids else None

        # Look up in mappings
        if spec_lower in self._mappings:
            return self._mappings[spec_lower].provider_id

        # Try to parse and match
        try:
            parsed = InstanceSpec.from_string(spec)
            parsed_str = parsed.to_string().lower()
            if parsed_str in self._mappings:
                return self._mappings[parsed_str].provider_id
        except Exception:
            pass

        return None

    def get_spec(self, identifier: str) -> InstanceSpec | None:
        """Get instance specification by user name or provider ID."""
        identifier_lower = identifier.lower().strip()

        # Try user name first
        if identifier_lower in self._mappings:
            return self._mappings[identifier_lower].spec

        # Try provider ID
        if identifier in self._provider_ids:
            return self._provider_ids[identifier].spec

        return None

    def list_available(self, region: str | None = None) -> list[InstanceTypeMapping]:
        """List available instance types, optionally filtered by region."""
        mappings = list(self._mappings.values())

        if region:
            mappings = [
                m for m in mappings if m.available_regions is None or region in m.available_regions
            ]

        return mappings


# Common GPU specifications (used by providers)
COMMON_GPU_SPECS = {
    "a100": GPUSpec("A100", 80, GPUGeneration.DATACENTER, 8.0),
    "a100-40gb": GPUSpec("A100", 40, GPUGeneration.DATACENTER, 8.0),
    "h100": GPUSpec("H100", 80, GPUGeneration.DATACENTER, 9.0),
    "a6000": GPUSpec("A6000", 48, GPUGeneration.WORKSTATION, 8.6),
    "a40": GPUSpec("A40", 48, GPUGeneration.DATACENTER, 8.6),
    "l40": GPUSpec("L40", 48, GPUGeneration.DATACENTER, 8.9),
    "l40s": GPUSpec("L40S", 48, GPUGeneration.DATACENTER, 8.9),
    "rtx3090": GPUSpec("RTX3090", 24, GPUGeneration.CONSUMER, 8.6),
    "rtx4090": GPUSpec("RTX4090", 24, GPUGeneration.CONSUMER, 8.9),
}


def normalize_gpu_type(gpu_type: str) -> str:
    """Normalize GPU type string to canonical form.

    Examples:
        "A100" -> "a100"
        "a100-80gb" -> "a100"
        "H100-SXM" -> "h100"
    """
    if not gpu_type:
        return ""

    # Convert to lowercase and remove common suffixes
    normalized = gpu_type.lower().strip()

    # Remove memory suffixes
    for suffix in ["-80gb", "-40gb", "-48gb", "-24gb", "-16gb", "-8gb"]:
        normalized = normalized.replace(suffix, "")

    # Remove form factor suffixes
    for suffix in ["-sxm", "-pcie", "-nvlink"]:
        normalized = normalized.replace(suffix, "")

    return normalized
