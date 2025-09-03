"""Mithril provider setup module."""

# Only import the adapter to avoid circular imports
from flow.adapters.providers.builtin.mithril.setup.adapter import MithrilSetupAdapter

__all__ = ["MithrilSetupAdapter"]
