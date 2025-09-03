"""GPU selection helpers centralizing instance type matching and queries (domain)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# InstanceMatcher remains in core for now; re-use it until migrated.
from flow.core.resources.matcher import InstanceMatcher  # type: ignore
from flow.domain.parsers.gpu_parser import GPUParser

if TYPE_CHECKING:  # pragma: no cover
    from flow.protocols.provider import ProviderProtocol as IProvider
else:
    IProvider = object  # type: ignore


class GPUSelectionService:
    """Service to select instance types based on GPU requirements."""

    def __init__(self, provider: IProvider):
        self.provider = provider

    def select_instance_type(self, gpu_spec: str) -> str:
        parsed_gpu: dict[str, Any] = GPUParser().parse(gpu_spec)
        catalog = self._build_catalog_for_gpu_type(parsed_gpu.get("gpu_type"))
        matcher = InstanceMatcher(catalog)
        return matcher.match(parsed_gpu)

    def find_instances_by_min_memory(
        self, min_memory_gb: int, max_price: float | None = None
    ) -> list[dict[str, Any]]:
        catalog = self._load_full_catalog()
        suitable: list[dict[str, Any]] = []
        for entry in catalog:
            gpu_info = entry.get("gpu", {})
            if not gpu_info:
                continue
            memory_gb = gpu_info.get("memory_gb", 0)
            if memory_gb < min_memory_gb:
                continue
            price = entry.get("price_per_hour")
            if price is None:
                continue
            if max_price is not None and price > max_price:
                continue
            suitable.append(
                {
                    "name": entry.get("name") or entry.get("instance_type"),
                    "gpu_memory_gb": memory_gb,
                    "price_per_hour": price,
                    "gpu_model": gpu_info.get("model", "unknown"),
                }
            )
        suitable.sort(key=lambda x: x["price_per_hour"])  # cheapest first
        return suitable

    # ------------------------- Internal helpers -------------------------
    def _build_catalog_for_gpu_type(self, gpu_type: str | None) -> list[dict[str, Any]]:
        catalog: list[dict[str, Any]] = []
        if gpu_type:
            try:
                available = self.provider.find_instances({"gpu_type": gpu_type}, limit=50)
                catalog = [self.provider.parse_catalog_instance(inst) for inst in available]
            except Exception:
                catalog = []
        if not catalog:
            catalog = self._load_full_catalog()
        return catalog

    def _load_full_catalog(self) -> list[dict[str, Any]]:
        instances = self.provider.find_instances({}, limit=1000)
        return [self.provider.parse_catalog_instance(inst) for inst in instances]
