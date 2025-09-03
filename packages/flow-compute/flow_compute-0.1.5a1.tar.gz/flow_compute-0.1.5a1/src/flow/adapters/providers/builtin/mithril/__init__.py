"""Mithril Provider implementation.

The Mithril  provider implements compute and storage
operations using the Mithril API. It supports market-based resource allocation
through auctions.
"""

from flow.adapters.providers.builtin.mithril.manifest import MITHRIL_MANIFEST
from flow.adapters.providers.builtin.mithril.provider.provider import MithrilProvider
from flow.adapters.providers.registry import ProviderRegistry

# Self-register with the provider registry via facade
ProviderRegistry.register("mithril", MithrilProvider)

__all__ = ["MithrilProvider", "MITHRIL_MANIFEST"]
