"""Match GPU requirements to instance types."""

from typing import Any

from flow.errors import FlowError


class NoMatchingInstanceError(FlowError):
    """No instance matches requirements."""

    pass


class InstanceMatcher:
    """Matches GPU requirements to available instances.

    Single responsibility: matching only. Open for extension with new
    matching strategies. Testable in isolation.

    Performance: O(n) catalog scan, typically <10ms for 1000 instances.
    Algorithm: Finds cheapest exact match, then cheapest larger instance.

    Examples:
        >>> catalog = [{"gpu_type": "a100-80gb", "gpu_count": 4, ...}]
        >>> matcher = InstanceMatcher(catalog)
        >>> matcher.match({"gpu_type": "a100-80gb", "count": 4})
        'a100.80gb.sxm4.4x'
    """

    def __init__(self, catalog: list[dict[str, Any]]):
        """Initialize with instance catalog.

        Args:
            catalog: List of available instances with properties:
                - instance_type: str
                - gpu_type: str
                - gpu_count: int
                - price_per_hour: float
                - available: bool
        """
        self.catalog = catalog

        # Build indices for fast lookup
        self._by_gpu_type: dict[str, list[dict]] = {}
        for instance in catalog:
            gpu_type = instance.get("gpu_type", "").lower()
            if gpu_type not in self._by_gpu_type:
                self._by_gpu_type[gpu_type] = []
            self._by_gpu_type[gpu_type].append(instance)

    def match(self, requirements: dict[str, Any]) -> str:
        """Find best instance for requirements.

        Args:
            requirements: Parsed GPU requirements

        Returns:
            Instance type string

        Raises:
            NoMatchingInstanceError: If no match found
        """

        # Match by GPU type and count
        gpu_type = requirements.get("gpu_type")
        count = requirements.get("count", 1)

        if not gpu_type:
            raise NoMatchingInstanceError(
                "No GPU type specified",
                suggestions=["Specify a GPU type like gpu='a100' or gpu='h100'"],
            )

        candidates = self._find_candidates(gpu_type, count)
        if not candidates:
            self._raise_no_match_error(gpu_type, count)

        # Return cheapest matching instance
        best = min(candidates, key=lambda x: x["price_per_hour"])
        return best["instance_type"]

    def _find_candidates(self, gpu_type: str, count: int) -> list[dict[str, Any]]:
        """Find instances matching GPU requirements."""
        candidates = []

        # Exact match preferred. Accept multiple naming conventions for gpu_type.
        norm = gpu_type.lower()
        aliases = {norm}
        # Normalize common variants: a100 vs a100-80gb
        if "a100" in norm and "80" not in norm:
            aliases.add("a100-80gb")
        if "h100" in norm and "80" not in norm:
            aliases.add("h100-80gb")

        # Aggregate candidates across aliases
        alias_bucket: list[dict[str, Any]] = []
        for key in aliases:
            alias_bucket.extend(self._by_gpu_type.get(key, []))

        # Remove duplicates (by instance_type) while preserving order
        seen_it: set[str] = set()
        unique_alias_bucket: list[dict[str, Any]] = []
        for inst in alias_bucket:
            it = inst.get("instance_type")
            if it and it not in seen_it:
                seen_it.add(it)
                unique_alias_bucket.append(inst)

        for instance in unique_alias_bucket:
            if instance.get("gpu_count") == count and instance.get("available", False):
                candidates.append(instance)

        # If no exact match, find larger instances
        if not candidates:
            for instance in unique_alias_bucket:
                if instance.get("gpu_count") >= count and instance.get("available", False):
                    candidates.append(instance)

        return candidates

    def _raise_no_match_error(self, gpu_type: str, count: int):
        """Raise error with helpful suggestions."""
        # Just tell them what's actually available
        available = []
        norm = gpu_type.lower()
        keys = {norm}
        if "a100" in norm and "80" not in norm:
            keys.add("a100-80gb")
        if "h100" in norm and "80" not in norm:
            keys.add("h100-80gb")
        dedup: dict[str, dict[str, Any]] = {}
        for key in keys:
            for instance in self._by_gpu_type.get(key, []):
                it = instance.get("instance_type")
                if instance.get("available", False) and it and it not in dedup:
                    dedup[it] = instance
        for inst in dedup.values():
            available.append(f"{inst['instance_type']} ({inst['gpu_count']} GPUs)")

        suggestions = []
        if available:
            suggestions.append(f"Available {gpu_type}: {', '.join(available)}")
        else:
            suggestions.append(f"No {gpu_type} instances currently available")

        raise NoMatchingInstanceError(
            f"No instances found with {count}x {gpu_type}", suggestions=suggestions
        )
