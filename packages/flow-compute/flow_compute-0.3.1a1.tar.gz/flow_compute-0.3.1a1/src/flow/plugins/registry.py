"""Plugin registry using entry points.

This module provides dynamic discovery and loading of providers and frontends
via setuptools entry points, enabling extensibility without core changes.

Additionally, it exposes a minimal ``PluginRegistry`` class with a
``get_adapter(name)`` method to satisfy legacy imports like::

    from flow.plugins.registry import PluginRegistry as FrontendRegistry

The class defers to entry points first and falls back to the legacy
``flow.adapters.frontends.registry`` when no plugin is available.
"""

import logging
from importlib.metadata import entry_points

logger = logging.getLogger(__name__)

# Cache for loaded plugins
_provider_cache: dict[str, type] = {}
_frontend_cache: dict[str, type] = {}


def discover_providers() -> dict[str, type]:
    """Discover all available provider plugins.

    Returns:
        Dictionary mapping provider names to their classes
    """
    global _provider_cache

    if _provider_cache:
        return _provider_cache

    try:
        eps = entry_points(group="flow.providers")
        for ep in eps:
            try:
                _provider_cache[ep.name] = ep.load()
                logger.debug(f"Loaded provider: {ep.name}")
            except Exception as e:
                logger.warning(f"Failed to load provider {ep.name}: {e}")
    except Exception as e:
        logger.error(f"Failed to discover providers: {e}")

    return _provider_cache


def discover_frontends() -> dict[str, type]:
    """Discover all available frontend plugins.

    Returns:
        Dictionary mapping frontend names to their classes
    """
    global _frontend_cache

    if _frontend_cache:
        return _frontend_cache

    try:
        eps = entry_points(group="flow.frontends")
        for ep in eps:
            try:
                _frontend_cache[ep.name] = ep.load()
                logger.debug(f"Loaded frontend: {ep.name}")
            except Exception as e:
                logger.warning(f"Failed to load frontend {ep.name}: {e}")
    except Exception as e:
        logger.error(f"Failed to discover frontends: {e}")

    return _frontend_cache


def get_provider(name: str) -> type | None:
    """Get a specific provider by name.

    Args:
        name: Provider name

    Returns:
        Provider class or None if not found
    """
    providers = discover_providers()
    return providers.get(name)


def get_frontend(name: str) -> type | None:
    """Get a specific frontend by name.

    Args:
        name: Frontend name

    Returns:
        Frontend class or None if not found
    """
    frontends = discover_frontends()
    return frontends.get(name)


def list_providers() -> list[str]:
    """List all available provider names.

    Returns:
        List of provider names
    """
    return list(discover_providers().keys())


def list_frontends() -> list[str]:
    """List all available frontend names.

    Returns:
        List of frontend names
    """
    return list(discover_frontends().keys())


def clear_cache():
    """Clear the plugin cache.

    Useful for testing or when plugins are updated.
    """
    global _provider_cache, _frontend_cache
    _provider_cache.clear()
    _frontend_cache.clear()


class PluginRegistry:
    """Legacy-compatible registry facade for frontends.

    Provides ``get_adapter(name)`` returning an adapter instance. It prefers
    plugin entry points but falls back to the legacy adapters registry to keep
    existing code paths working during migration.
    """

    @staticmethod
    def get_adapter(name: str):
        try:
            cls = get_frontend(name)
            if cls is not None:
                return cls()  # Instantiate plugin-provided adapter
        except Exception:
            pass
        # Fallback to legacy adapters registry
        try:
            from flow.adapters.frontends.registry import FrontendRegistry as _Legacy

            return _Legacy.get_adapter(name)
        except Exception as e:  # pragma: no cover - defensive fallback
            raise ValueError(f"Unknown frontend: {name}") from e


# Lazy loading helpers
def lazy_import_provider(name: str) -> type:
    """Lazily import a provider only when needed.

    Args:
        name: Provider name

    Returns:
        Provider class

    Raises:
        ValueError: If provider not found
    """
    provider = get_provider(name)
    if provider is None:
        raise ValueError(f"Provider '{name}' not found. Available: {list_providers()}")
    return provider


def lazy_import_frontend(name: str) -> type:
    """Lazily import a frontend only when needed.

    Args:
        name: Frontend name

    Returns:
        Frontend class

    Raises:
        ValueError: If frontend not found
    """
    frontend = get_frontend(name)
    if frontend is None:
        raise ValueError(f"Frontend '{name}' not found. Available: {list_frontends()}")
    return frontend
