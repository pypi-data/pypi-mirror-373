"""Tabular layout helper for CLI selectors.

Provides adaptive column width calculation, effective width, and centering
padding computations in a provider-agnostic, reusable way.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TabularLayout:
    """Computed column widths for a tabular selector layout.

    Columns:
      - status: textual state (e.g., Pending, Running)
      - name: primary title
      - gpu: GPU/instance info (short)
      - time: relative age string (e.g., "just now", "3m ago")
    """

    status: int
    name: int
    gpu: int
    time: int

    def as_dict(self) -> dict:
        return {"status": self.status, "name": self.name, "gpu": self.gpu, "time": self.time}

    def effective_width(self) -> int:
        """Total occupied width including selection/arrow area and spacing."""
        # Selection marker + arrow area (approx 4) + two spaces between columns
        return 4 + self.status + 2 + self.name + 2 + self.gpu + 2 + self.time

    def left_padding(self, terminal_width: int) -> int:
        """Left padding to visually center the table within terminal width."""
        return max(2, (terminal_width - self.effective_width()) // 2)


def _extract_gpu_part(subtitle: str | None) -> str:
    if not subtitle:
        return ""
    if " • " in subtitle:
        return subtitle.split(" • ")[0]
    return ""


def _extract_time_part(subtitle: str | None) -> str:
    if not subtitle:
        return ""
    if " • " in subtitle:
        return subtitle.split(" • ")[-1]
    return subtitle


def compute_layout(
    terminal_width: int, items: Iterable[Any], sample_count: int = 20
) -> TabularLayout:
    """Compute adaptive column widths from terminal size and sample content.

    The algorithm mirrors the previous inline logic but is reusable and unit-testable.

    Args:
        terminal_width: Current terminal width in columns
        items: Iterable of objects having optional 'subtitle' attribute
        sample_count: Number of items to sample for GPU/time width derivation
    """
    # Reserve space for margins, arrow, and spacing between columns
    available_width = max(20, terminal_width - 12)

    # Fixed/status width optimized for readability (fits "● Preempting")
    status_width = 13

    # Derive GPU width from visible items, with a reasonable cap
    gpu_width = 11
    sampled = []
    try:
        for idx, it in enumerate(items):
            if idx >= sample_count:
                break
            sampled.append(it)
    except Exception:
        sampled = []

    try:
        for it in sampled:
            subtitle = getattr(it, "subtitle", None)
            gpu_part = _extract_gpu_part(subtitle)
            gpu_width = max(gpu_width, len(gpu_part))
        gpu_width = min(16, gpu_width)
    except Exception:
        gpu_width = min(16, gpu_width)

    # Time column width adaptive based on visible items
    try:
        max_time_len = 0
        for it in sampled:
            subtitle = getattr(it, "subtitle", None)
            time_part = _extract_time_part(subtitle)
            max_time_len = max(max_time_len, len(time_part))
        time_width = max(16, min(20, max_time_len or 20))
    except Exception:
        time_width = 20

    # Give remaining space to name column, but cap it
    name_width = available_width - status_width - gpu_width - time_width - 8  # spacing
    name_width = max(20, min(name_width, 36))

    return TabularLayout(status=status_width, name=name_width, gpu=gpu_width, time=time_width)
