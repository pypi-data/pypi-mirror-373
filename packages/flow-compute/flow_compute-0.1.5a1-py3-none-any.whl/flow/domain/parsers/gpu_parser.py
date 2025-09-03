"""Parse GPU specifications from strings (domain-level parser).

This parser is the canonical source for interpreting user GPU shorthand such as
"a100" or "a100:4" into normalized components.
"""

from __future__ import annotations

import re
from typing import Any

from flow.errors import ValidationError


class GPUParser:
    """Parses GPU strings like 'a100', 'a100:4', 'cheapest'."""

    GPU_ALIASES = {
        "a100": "a100-80gb",
        "h100": "h100-80gb",
        "a10": "a10-24gb",
        "t4": "t4-16gb",
        "v100": "v100-32gb",
        "l4": "l4-24gb",
    }

    def parse(self, gpu_string: str) -> dict[str, Any]:
        if not gpu_string:
            return {}
        match = re.match(r"^([a-z0-9]+)(?::(\d+))?$", gpu_string.lower())
        if not match:
            raise ValidationError(
                f"Invalid GPU string: {gpu_string}",
                suggestions=[
                    "Use format: 'a100' or 'a100:4'",
                    f"Supported GPUs: {', '.join(self.GPU_ALIASES.keys())}",
                ],
            )
        gpu_type = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1
        if gpu_type not in self.GPU_ALIASES:
            raise ValidationError(
                f"Unknown GPU type: {gpu_type}",
                suggestions=[
                    f"Supported GPUs: {', '.join(self.GPU_ALIASES.keys())}",
                    "Use 't4' for the most affordable GPU",
                ],
            )
        if count < 1 or count > 8:
            raise ValidationError(
                f"Invalid GPU count: {count}", suggestions=["GPU count must be between 1 and 8"]
            )
        return {"gpu_type": self.GPU_ALIASES[gpu_type], "count": count}
