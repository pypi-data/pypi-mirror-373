"""Provider factory using the registry pattern.

This replaces the old provider_factory in core, removing the circular
dependency where core imported from providers.
"""

from flow.adapters.logging import StdlibJSONLogger
from flow.adapters.metrics import NoopMetrics
from flow.adapters.metrics import from_health_config as _metrics_from_cfg
from flow.adapters.providers.registry import ProviderRegistry
from flow.application.config.config import Config
from flow.protocols.facets import ProviderFacets
from flow.protocols.logging import LoggingProtocol
from flow.protocols.metrics import MetricsProtocol
from flow.protocols.provider import ProviderProtocol as IProvider


def create_provider(
    config: Config,
    *,
    logger: LoggingProtocol | None = None,
    metrics: MetricsProtocol | None = None,
) -> IProvider:
    """Create a provider instance from configuration.

    This is the main entry point for provider creation, used by
    the Flow class and other high-level APIs.

    Args:
        config: SDK configuration with provider settings

    Returns:
        Initialized provider instance

    Raises:
        ProviderNotFoundError: If the requested provider is not available

    Example:
        >>> from flow.application.config.config import Config
        >>> from flow.adapters.providers.factory import create_provider
        >>>
        >>> config = Config(provider="mithril", ...)
        >>> provider = create_provider(config)
    """
    provider = ProviderRegistry.create(config.provider, config)
    # Inject logging/metrics when supported (duck-typed)
    try:
        if hasattr(provider, "set_logger"):
            provider.set_logger(logger or StdlibJSONLogger(f"flow.providers.{config.provider}"))
    except Exception:
        pass
    try:
        if hasattr(provider, "set_metrics"):
            # Prefer provided metrics; otherwise build from health config, falling back to noop
            if metrics is not None:
                provider.set_metrics(metrics)
            else:
                try:
                    provider.set_metrics(_metrics_from_cfg(config.health_config))
                except Exception:
                    provider.set_metrics(NoopMetrics())
    except Exception:
        pass
    return provider


def get_provider_facets(config: Config) -> ProviderFacets:
    """Return provider facets (capabilities aggregate) for the configured provider.

    This is a non-breaking companion to `create_provider`, allowing callers to
    depend on smaller, role-based protocols when appropriate.
    """
    return ProviderRegistry.get_facets(config.provider, config)
