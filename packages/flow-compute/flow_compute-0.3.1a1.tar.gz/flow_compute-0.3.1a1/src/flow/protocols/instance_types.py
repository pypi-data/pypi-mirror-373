from __future__ import annotations

from typing import Protocol


class InstanceTypeResolverProtocol(Protocol):
    """Protocol for resolving user-facing instance specs to provider IDs.

    Adapters should implement this interface to map human-friendly specs
    (e.g., "a100", "4xa100", "8xh100") to provider-specific instance type IDs,
    offer candidate alternatives, and normalize GPU count/type requests.
    """

    def resolve(self, user_spec: str) -> str:
        """Resolve a user-friendly spec to a provider-specific instance type ID."""
        ...

    def resolve_simple(self, spec: str) -> str:
        """Resolve an exact spec without canonicalization; raise on unknown."""
        ...

    def candidate_ids(self, user_spec: str) -> list[str]:
        """Return candidate instance IDs for a spec, covering variants."""
        ...

    def normalize_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:
        """Normalize (gpu_count, gpu_type) to (instance_type, num_instances, warning)."""
        ...


__all__ = ["InstanceTypeResolverProtocol"]
