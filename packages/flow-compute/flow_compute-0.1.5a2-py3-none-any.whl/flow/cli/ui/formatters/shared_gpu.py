"""Shared GPU formatting utilities for CLI UI."""

from __future__ import annotations

import re


class GPUFormatter:
    """Handles GPU and instance type formatting (shared)."""

    _DEFAULT_GPUS_PER_NODE_BY_MODEL: dict[str, int] = {"H100": 8}

    @staticmethod
    def _fallback_gpus_per_node(model: str | None, current: int) -> int:
        try:
            if (not model) or current != 1:
                return current
            default = GPUFormatter._DEFAULT_GPUS_PER_NODE_BY_MODEL.get(model.upper())
            return int(default) if default else current
        except Exception:
            return current

    @staticmethod
    def format_gpu_type(instance_type: str | None) -> str:
        if not instance_type:
            return "N/A"
        if instance_type.startswith("it_"):
            return instance_type[:12].upper() + "..."
        return instance_type.upper()

    @staticmethod
    def format_ultra_compact(instance_type: str | None, num_instances: int = 1) -> str:
        if not instance_type:
            return "-"
        base = str(instance_type).strip().upper()
        return f"{base}×{num_instances}" if num_instances and num_instances > 1 else base

    @staticmethod
    def format_ultra_compact_width_aware(
        instance_type: str | None, num_instances: int = 1, max_width: int | None = None
    ) -> str:
        s = GPUFormatter.format_ultra_compact(instance_type, num_instances)
        if max_width is None or len(s) <= max_width:
            return s
        return s[: max_width - 3] + "..." if max_width and max_width > 3 else s[: max_width or 0]

    @staticmethod
    def parse_gpu_count(instance_type: str | None) -> int:
        if not instance_type:
            return 0
        lower = instance_type.lower().strip()
        m = re.search(r"(\d+)x[a-z]+\d+", lower)
        if m:
            return int(m.group(1))
        rev = re.search(r"[a-z]+\d+x(\d+)", lower)
        if rev:
            return int(rev.group(1))
        hyphen = re.search(r"\b([ahvb]\d{2,3}|gb\d{2,3}|rtx\d{4}|t4)[- ](\d{1,2})\b", lower)
        if hyphen:
            return int(hyphen.group(2))
        model = re.search(r"\b(gb\d{3}|[ahvb]\d{2,3}|rtx\d{4}|t4)\b", lower)
        if model:
            return GPUFormatter._fallback_gpus_per_node(model.group(1).upper(), 1)
        return 0
