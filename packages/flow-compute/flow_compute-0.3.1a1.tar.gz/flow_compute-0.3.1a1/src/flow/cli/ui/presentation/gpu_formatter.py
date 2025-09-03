"""GPU and instance type formatting utilities for CLI output (canonical).

Provides canonical, compact representations using the multiplication sign (×)
and memory dot (·). Width-aware formatting degrades gracefully.
"""

from __future__ import annotations

import re

from flow.cli.ui.formatters.shared_gpu import GPUFormatter as _SharedGPU


class GPUFormatter:
    @staticmethod
    def format_gpu_type(instance_type: str | None) -> str:
        return _SharedGPU.format_gpu_type(instance_type)

    @staticmethod
    def parse_gpu_count(instance_type: str | None) -> int:
        # Use the same robust parsing as compact formatter to avoid
        # confusing memory (e.g., "-80gb") for GPU count.
        _, _, gpn, nvl = GPUFormatter._parse(instance_type)
        return int(gpn or (nvl or 0))

    @staticmethod
    def _parse(instance_type: str | None) -> tuple[str, str | None, int, int | None]:
        """Return (model, memory, gpus_per_node, nvl_count)."""
        if not instance_type:
            return "", None, 1, None
        raw = str(instance_type).strip()
        lower = raw.lower()

        # Opaque instance types
        if lower.startswith("it_"):
            return raw[:8].upper(), None, 1, None

        model: str = ""
        memory: str | None = None
        gpn: int = 1
        nvl: int | None = None

        # Detect NVL topology anywhere (e.g., gb200nvl72)
        m = re.search(r"nvl(\d{1,3})", lower)
        if m:
            try:
                nvl = int(m.group(1))
            except Exception:
                nvl = None

        # 1) Hyphen memory forms like "a100-80gb" or "gb200-128gb"
        hyphen_mem = re.search(
            r"\b(gb\d{2,3}|[ahvb]\d{2,3}|rtx\d{4}|t4)[- ]?(\d{2,3})\s*g(b)?\b",
            lower,
        )
        if hyphen_mem:
            model = hyphen_mem.group(1).upper()
            memory = hyphen_mem.group(2).lstrip("0") + "G"
        else:
            # 2) Hyphen count forms like "a100-4" (4 GPUs per node)
            hyphen_count = re.search(
                r"\b(gb\d{2,3}|[ahvb]\d{2,3}|rtx\d{4}|t4)[- ](\d{1,2})(?!\s*g)\b",
                lower,
            )
            if hyphen_count:
                model = hyphen_count.group(1).upper()
                try:
                    gpn = int(hyphen_count.group(2))
                except Exception:
                    gpn = 1
            else:
                # 3) Count-prefix forms like "8xa100" or "2xgb200"
                normalized = lower.replace(" ", "").replace("-", "")
                count_model = re.match(r"(\d+)x(gb\d{3}|[ahvb]\d{3}|rtx\d{4}|t4)", normalized)
                if count_model:
                    try:
                        gpn = int(count_model.group(1))
                    except Exception:
                        gpn = 1
                    model = count_model.group(2).upper()
                    rest = normalized[count_model.end() :]
                    mem = re.search(r"(\d{2,3})gb?", rest)
                    if mem:
                        memory = mem.group(1).lstrip("0") + "G"
                else:
                    # 4) Reverse multiplier like "a100x8"
                    rev = re.match(r"(gb\d{3}|[ahvb]\d{3}|rtx\d{4}|t4)x(\d+)", normalized)
                    if rev:
                        model = rev.group(1).upper()
                        try:
                            gpn = int(rev.group(2))
                        except Exception:
                            gpn = 1
                        rest = normalized[rev.end() :]
                        mem = re.search(r"(\d{2,3})gb?", rest)
                        if mem:
                            memory = mem.group(1).lstrip("0") + "G"
                    else:
                        # 5) Model only; memory may appear after model
                        mm = re.search(r"\b(gb\d{3}|[ahvb]\d{2,3}|rtx\d{4}|t4)\b", normalized)
                        if mm:
                            model = mm.group(1).upper()
                            search_start = mm.end()
                            mem = re.search(r"(\d{2,3})gb?", normalized[search_start:])
                            if mem:
                                memory = mem.group(1).lstrip("0") + "G"

        if not model:
            m2 = re.match(r"\s*([ahvb])\s*(\d{2,3})\b", lower)
            if m2:
                model = f"{m2.group(1).upper()}{m2.group(2)}"
            else:
                model = raw.upper()[:6]

        # Treat NVL topology as GPU count when not otherwise provided
        if nvl and gpn == 1:
            gpn = nvl

        # Apply model-based fallback when count is ambiguous (e.g., H100 → 8)
        gpn = _SharedGPU._fallback_gpus_per_node(model, gpn)

        return model, memory, gpn, nvl

    @staticmethod
    def format_gpu_details(instance_type: str | None, num_instances: int = 1) -> str:
        gpn = GPUFormatter.parse_gpu_count(instance_type)
        total = gpn * (num_instances or 1)
        if total == 0:
            return "No GPUs"
        gpu_type = GPUFormatter.format_gpu_type(instance_type)

        if (num_instances or 1) == 1:
            return gpu_type
        # Extract model for compact breakdown
        mm = re.search(
            r"[AHV]\d{2,3}|RTX\s*\d{4}|T4|[PK]\d{2,3}|M\d{2}|GB\d{2,3}", gpu_type, re.IGNORECASE
        )
        model = (
            mm.group(0).upper()
            if mm
            else re.sub(r"^\d+", "", gpu_type.replace("×", "").replace("X", ""))
        )
        return f"{total}×{model} ({num_instances}×{gpn})"

    @staticmethod
    def format_ultra_compact(instance_type: str | None, num_instances: int = 1) -> str:
        if not instance_type:
            return "-"
        model, memory, gpn, nvl = GPUFormatter._parse(instance_type)

        # Opaque ID case returns short code as model
        if model.startswith("IT_") or model.startswith("IT-"):
            return f"{model}×{num_instances}" if (num_instances and num_instances > 1) else model

        total = gpn * max(1, int(num_instances or 1))

        if (num_instances or 1) == 1:
            parts: list[str] = []
            parts.append(f"{gpn}×{model}" if gpn > 1 else model)
            if memory:
                parts.append(f"·{memory}")
            if nvl:
                parts.append(f"·NVL{nvl}")
            return "".join(parts)
        else:
            base = f"{total}×{model}"
            if memory:
                base += f"·{memory}"
            if nvl:
                base += f"·NVL{nvl}"
            return base

    @staticmethod
    def format_ultra_compact_width_aware(
        instance_type: str | None, num_instances: int = 1, max_width: int | None = None
    ) -> str:
        # If no width constraint, show compact canonical
        full = GPUFormatter.format_ultra_compact(instance_type, num_instances)
        if max_width is None or len(full) <= max_width:
            return full

        model, memory, gpn, _ = GPUFormatter._parse(instance_type)
        total = gpn * max(1, int(num_instances or 1))

        # Multi-node: try to show breakdown when space allows
        if (num_instances or 1) > 1:
            parts_full = f"{total}×{model}"
            if memory:
                parts_full += f"·{memory}"
            parts_full += f" ({num_instances}×{gpn})"
            if len(parts_full) <= (max_width or 0):
                return parts_full

            parts_med = f"{total}×{model} ({num_instances}×{gpn})"
            if len(parts_med) <= (max_width or 0):
                return parts_med

            parts_base = f"{total}×{model}"
            if len(parts_base) <= (max_width or 0):
                return parts_base

            # Truncate as last resort
            return parts_base[: max(0, (max_width or 0))]

        # Single node: drop memory first, then collapse to model
        single_full = full  # e.g., "A100·80G" or "8×A100·80G"
        if len(single_full) <= (max_width or 0):
            return single_full

        no_mem = single_full.split("·")[0]
        if len(no_mem) <= (max_width or 0):
            return no_mem

        # Fallback to bare model
        bare = model if gpn == 1 else f"{gpn}×{model}"
        if len(bare) <= (max_width or 0):
            return bare

        return bare[: max(0, (max_width or 0))]


__all__ = ["GPUFormatter"]
