"""Lazy JSON/asset data loader for Flow SDK.

Consolidated location for packaged data files. Prefers the unified
`flow.resources` package layout:

- `flow.resources.data`: JSON/YAML data files (pricing, regions, logging)
- `flow.resources.cli`: CLI visual/animation assets

Data is loaded on first access and cached for the process lifetime.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

# Cache for loaded data
_data_cache: dict[str, Any] = {}


class DataLoader:
    """Lazy loader for JSON configuration and CLI asset data."""

    def __init__(self):
        # Canonical resource packages
        self._pkg_data = "flow.resources.data"
        self._pkg_cli = "flow.resources.cli"

    def _load_json(self, filename: str) -> dict[str, Any]:
        """Load a JSON file from `flow.resources.data` and cache it.

        Args:
            filename: Name of the JSON file to load

        Returns:
            Parsed JSON data
        """
        if filename in _data_cache:
            return _data_cache[filename]

        with resources.files(self._pkg_data).joinpath(filename).open("rb") as f:
            data = json.load(f)
            _data_cache[filename] = data
            return data

    # ------------------------- CLI visuals -------------------------
    def _load_cli_json(self, filename: str) -> dict[str, Any]:
        """Load JSON from the `flow.resources.cli` package.

        Args:
            filename: Base filename under CLI resources
        """
        key = f"cli/{filename}"
        if key in _data_cache:
            return _data_cache[key]

        with resources.files(self._pkg_cli).joinpath(filename).open("rb") as f:
            data = json.load(f)
            _data_cache[key] = data
            return data

    # ------------------------- Data accessors -------------------------
    @property
    def pricing(self) -> dict[str, Any]:
        return self._load_json("pricing.json")

    @property
    def regions(self) -> dict[str, Any]:
        return self._load_json("regions.json")

    @property
    def instance_types(self) -> dict[str, Any]:
        return self._load_json("instance_types.json")

    def get_gpu_pricing(self) -> dict[str, dict[str, float]]:
        return self.pricing.get("gpu_pricing", {})

    def get_valid_regions(self, provider: str = "mithril") -> list[str]:
        provider_data = self.regions.get(provider, {})
        return provider_data.get("valid_regions", [])

    def get_default_region(self, provider: str = "mithril") -> str:
        provider_data = self.regions.get(provider, {})
        return provider_data.get("default_region", "us-central1-b")

    def get_instance_mapping(self, provider: str = "mithril") -> dict[str, str]:
        provider_data = self.instance_types.get(provider, {})
        return provider_data.get("instance_mappings", {})

    def get_instance_names(self, provider: str = "mithril") -> dict[str, str]:
        provider_data = self.instance_types.get(provider, {})
        return provider_data.get("instance_names", {})

    def get_gpu_patterns(self, provider: str = "mithril") -> list[str]:
        provider_data = self.instance_types.get(provider, {})
        return provider_data.get("gpu_patterns", [])

    # ------------------------- CLI visuals API -------------------------
    @property
    def cli_animation(self) -> dict[str, Any]:
        return self._load_cli_json("animation.json")

    @property
    def cli_visual(self) -> dict[str, Any]:
        return self._load_cli_json("visual.json")

    def clear_cache(self):
        global _data_cache
        _data_cache.clear()


# Global loader instance
_loader = DataLoader()


# Convenience functions for direct access
def get_gpu_pricing() -> dict[str, dict[str, float]]:
    return _loader.get_gpu_pricing()


def get_valid_regions(provider: str = "mithril") -> list[str]:
    return _loader.get_valid_regions(provider)


def get_default_region(provider: str = "mithril") -> str:
    return _loader.get_default_region(provider)


def get_instance_mapping(provider: str = "mithril") -> dict[str, str]:
    return _loader.get_instance_mapping(provider)


def get_instance_names(provider: str = "mithril") -> dict[str, str]:
    return _loader.get_instance_names(provider)


def get_gpu_patterns(provider: str = "mithril") -> list[str]:
    return _loader.get_gpu_patterns(provider)


def clear_cache():
    _loader.clear_cache()
