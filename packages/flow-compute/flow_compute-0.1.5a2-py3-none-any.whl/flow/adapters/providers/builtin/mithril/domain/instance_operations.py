from __future__ import annotations

"""Instance operations for Mithril adapter.

Provides small, focused helpers for converting provider-specific instance
objects into the catalog dictionary shape expected by the SDK.
"""

from typing import Any


class InstanceOperations:
    """Pure utility for instance-related mappings.

    Keeps provider-facing logic tidy by isolating transformation details.
    """

    def __init__(self, instances_service: Any, instance_types: Any) -> None:
        self._instances = instances_service
        self._instance_types = instance_types

    def parse_catalog_instance(self, instance: Any) -> dict[str, Any]:
        """Convert a provider instance into the SDK catalog dictionary.

        Returns a minimal, stable dict with keys used by selection services:
        - instance_type: str
        - price_per_hour: float
        - available: bool
        - gpu: { memory_gb: int, model: str }
        """
        # Name/type
        name = (
            getattr(instance, "instance_type", None) or getattr(instance, "name", None) or "unknown"
        )

        # Price
        try:
            price = float(getattr(instance, "price_per_hour", 0.0) or 0.0)
        except Exception:
            price = 0.0

        # Availability
        qty = getattr(instance, "available_quantity", None)
        status = str(getattr(instance, "status", "")).lower()
        available = bool((qty or 0) > 0 or status == "available")

        # GPU details
        model = getattr(instance, "gpu_type", None) or ""
        mem_gb = 0
        try:
            import re as _re

            m = _re.search(r"(\d+)\s*gb", str(name).lower())
            if m:
                mem_gb = int(m.group(1))
        except Exception:
            mem_gb = 0

        return {
            "instance_type": str(name),
            "price_per_hour": price,
            "available": available,
            "gpu": {"memory_gb": mem_gb, "model": model},
        }
