"""Provider manifest for the mock provider (minimal for CLI integration)."""

from flow.adapters.providers.base import ProviderCapabilities, ProviderInfo

capabilities = ProviderCapabilities(
    supports_spot_instances=False,
    supports_on_demand=True,
    supports_multi_node=False,
    supports_attached_storage=True,
    supports_shared_storage=False,
    pricing_model="fixed",  # type: ignore[arg-type]
    supported_regions=["demo-region-1"],
)

info = ProviderInfo(
    name="mock",
    display_name="Mock (Demo)",
    description="In-memory mock provider for demos and tutorials",
    website=None,
    documentation=None,
    capabilities=capabilities,
)
