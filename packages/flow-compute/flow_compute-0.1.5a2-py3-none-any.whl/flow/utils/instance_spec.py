from __future__ import annotations

"""Parsing utilities for GPU instance specifications.

Supports common forms used across providers:
- "a100" (implicitly 1x)
- "4xa100"
- "h100-80gb.sxm.8x"
- "a100-40gb.sxm.2x"

Returns a minimal, provider-agnostic structure. Keep intentionally small to
avoid coupling: gpu_type, gpu_count, memory_gb, interconnect.
"""

from dataclasses import dataclass


@dataclass
class InstanceSpec:
    gpu_type: str | None
    gpu_count: int | None
    memory_gb: int | None
    interconnect: str | None


def parse(spec: str | None) -> InstanceSpec:
    s = (spec or "").strip().lower()
    gpu_type: str | None = None
    gpu_count: int | None = None
    memory_gb: int | None = None
    interconnect: str | None = None

    if not s:
        return InstanceSpec(gpu_type, gpu_count, memory_gb, interconnect)

    # Simple e.g., 4xa100
    if "x" in s and not any(ch in s for ch in ("/", ",", " ", ".")):
        try:
            left, right = s.split("x", 1)
            gpu_count = int(left)
            gpu_type = right
            return InstanceSpec(gpu_type, gpu_count, memory_gb, interconnect)
        except Exception:
            pass

    # Dotted canonical like h100-80gb.sxm.8x
    tokens = s.split(".")
    head = tokens[0]
    if "-" in head and head.endswith("gb"):
        try:
            base, mem = head.rsplit("-", 1)
            gpu_type = base
            memory_gb = int(mem.replace("gb", ""))
        except Exception:
            gpu_type = head
    else:
        gpu_type = head

    for tok in tokens[1:]:
        if tok.startswith("sxm") or tok == "sxm":
            interconnect = "sxm"
        elif tok.startswith("pcie") or tok == "pcie":
            interconnect = "pcie"
        elif tok.endswith("x"):
            try:
                gpu_count = int(tok[:-1])
            except Exception:
                pass

    if gpu_count is None and "x" not in s:
        gpu_count = 1

    return InstanceSpec(gpu_type, gpu_count, memory_gb, interconnect)


__all__ = ["InstanceSpec", "parse"]
