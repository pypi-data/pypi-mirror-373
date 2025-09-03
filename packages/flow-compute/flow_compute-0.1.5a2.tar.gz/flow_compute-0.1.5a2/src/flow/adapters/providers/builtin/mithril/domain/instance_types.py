"""Mithril-specific instance type adapter.

Adapts the domain instance type models to work with Mithril's
specific instance type IDs and mappings.
"""

from __future__ import annotations

from flow.adapters.providers.builtin.mithril.core.constants import (
    INSTANCE_TYPE_MAPPINGS,
    INSTANCE_TYPE_NAMES,
)
from flow.errors import FlowError
from flow.protocols.instance_types import InstanceTypeResolverProtocol


class InstanceTypeResolver(InstanceTypeResolverProtocol):
    """Mithril-specific instance type resolver.

    Adapts domain InstanceTypeRegistry to work with Mithril's
    specific mappings and IDs.
    """

    def __init__(self):
        """Initialize with Mithril's instance type mappings (no domain deps)."""
        self._map = dict(INSTANCE_TYPE_MAPPINGS)
        self._reverse = {v: k for k, v in self._map.items()}
        # Precompute family → known IDs from reverse names for broader candidate coverage
        try:
            self._family_ids: dict[str, list[str]] = {}
            for it_id, name in (INSTANCE_TYPE_NAMES or {}).items():
                key = str(name or "").lower()
                for fam in ("h100", "a100"):
                    if fam in key:
                        self._family_ids.setdefault(fam, []).append(it_id)
        except Exception:
            self._family_ids = {}

    def resolve(self, user_spec: str) -> str:
        """Resolve user-friendly spec (e.g., "a100", "4xa100") to a Mithril ID.

        Raises FlowError with helpful suggestions when resolution fails.
        """
        if not user_spec:
            raise FlowError("Instance type specification is required")

        # Enforce lowercase simple names to reduce ambiguous inputs
        if user_spec != user_spec.strip() or any(ch.isupper() for ch in user_spec):
            available_types = list(INSTANCE_TYPE_MAPPINGS.keys())
            raise FlowError(
                f"Unknown instance type: {user_spec}",
                suggestions=[
                    f"Available: {', '.join(available_types[:5])}...",
                    "Use 'flow instances' to see all available instance types",
                    "Examples: 'a100', '4xa100', '8xh100'",
                ],
            )

        normalized_spec = user_spec.lower().strip()

        # Direct ID passthrough
        if normalized_spec.startswith("it_"):
            return user_spec

        # Direct map
        if normalized_spec in self._map:
            return self._map[normalized_spec]

        # Try parser-based canonicalization
        # Minimal parser: "4xa100" -> "4xa100"; normalize whitespace/case
        try:
            key = self._parse_key(user_spec)
            if key in self._map:
                return self._map[key]
        except Exception:
            pass

        available_types = list(self._map.keys())
        raise FlowError(
            f"Unknown instance type: {user_spec}",
            suggestions=[
                f"Available: {', '.join(available_types[:5])}...",
                "Use 'flow instances' to see all available instance types",
                "Examples: 'a100', '4xa100', '8xh100'",
            ],
        )

    def resolve_simple(self, spec: str) -> str:
        """Simple exact resolution using the static mapping (no canonicalization)."""
        normalized = spec.strip()
        if normalized.startswith("it_"):
            return normalized
        if normalized in self._map:
            return self._map[normalized]
        available = sorted(self._map.keys())
        raise ValueError(f"Unknown instance type: {spec}. Available: {', '.join(available)}")

    def candidate_ids(self, user_spec: str) -> list[str]:
        """Return candidate instance type IDs for a spec, covering variants.

        For H100, consider both SXM and PCIe 8x variants to allow region-specific
        availability differences.
        """
        candidates: list[str] = []
        try:
            primary = self.resolve(user_spec)
            if primary:
                candidates.append(primary)
        except Exception:
            # Continue to try canonical forms below
            pass

        spec_lower = (user_spec or "").lower()
        try:
            if any(token in spec_lower for token in ("h100", "xh100")):
                # Include any known H100 IDs from constants (handles multiple backends)
                for alt_id in self._family_ids.get("h100", []) or []:
                    if alt_id not in candidates:
                        candidates.append(alt_id)
            # Broaden A100 generic requests across common node sizes (1/2/4/8x)
            # to improve availability selection when a specific size is scarce.
            # Only broaden when the request is generic single‑GPU A100
            if spec_lower in {"a100", "1xa100"}:
                for alt in (
                    "a100-80gb.sxm.1x",
                    "a100-80gb.sxm.2x",
                    "a100-80gb.sxm.4x",
                    "a100-80gb.sxm.8x",
                ):
                    try:
                        alt_id = self.resolve(alt)
                        if alt_id not in candidates:
                            candidates.append(alt_id)
                    except Exception:
                        continue
        except Exception:
            pass

        # Fallback to just returning any that resolved
        return candidates

    def normalize_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:
        """Normalize a (count, type) request into (instance_type, num_instances, warning).

        Enforces provider-specific constraints (e.g., H100 only in 8x nodes).
        """
        if not gpu_type:
            gpu_type = "h100"
        gpu_type = gpu_type.lower().strip()

        # H100: only 8x nodes; round up to nearest multiple of 8
        if gpu_type == "h100":
            num_nodes = (gpu_count + 7) // 8
            actual_gpus = num_nodes * 8
            warning: str | None = None
            if actual_gpus != gpu_count:
                warning = (
                    "H100s only available in 8-GPU nodes. Allocating "
                    f"{actual_gpus} GPUs ({num_nodes} node{'s' if num_nodes > 1 else ''})."
                )
            return "8xh100", num_nodes, warning

        # Prefer 8x, then 4x, then 2x, else 1x
        if gpu_count >= 8 and gpu_count % 8 == 0:
            return f"8x{gpu_type}", gpu_count // 8, None
        if gpu_count >= 4 and gpu_count % 4 == 0:
            return f"4x{gpu_type}", gpu_count // 4, None
        if gpu_count >= 2 and gpu_count % 2 == 0:
            return f"2x{gpu_type}", gpu_count // 2, None
        return gpu_type, gpu_count, None

    @staticmethod
    def _parse_key(user_spec: str) -> str:
        """Parse user spec into a normalized key present in mapping.

        Accepts inputs like "a100", "4xa100", "8xh100", or canonical long forms
        like "h100-80gb.sxm.8x" and returns the same when appropriate.
        """
        s = (user_spec or "").strip().lower()
        if not s:
            return s
        # If already in dotted long form, return as-is
        if "." in s and any(tok in s for tok in ("sxm", "pcie")):
            return s
        # If it looks like N x gpu
        if "x" in s:
            left, right = s.split("x", 1)
            try:
                _ = int(left)
                return f"{left}x{right}"
            except Exception:
                return s
        return s
