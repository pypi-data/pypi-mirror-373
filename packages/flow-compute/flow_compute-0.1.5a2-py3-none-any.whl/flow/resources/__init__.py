"""Unified non-code resources for Flow SDK.

Subpackages:
- `flow.resources.data`: JSON/YAML data files (pricing, regions, logging)
- `flow.resources.templates`: Canonical Jinja2 templates
- `flow.resources.cli`: CLI visual/animation assets

Public API:
- Data access helpers re-exported from ``flow.resources.loader`` for convenience.
"""

from .loader import (
    DataLoader,
    clear_cache,
    get_default_region,
    get_gpu_patterns,
    get_gpu_pricing,
    get_instance_mapping,
    get_instance_names,
    get_valid_regions,
)

__all__ = [
    "DataLoader",
    "get_gpu_pricing",
    "get_valid_regions",
    "get_default_region",
    "get_instance_mapping",
    "get_instance_names",
    "get_gpu_patterns",
    "clear_cache",
]
