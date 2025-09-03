"""Provider registry used for dynamic discovery and registration.

Providers self-register at import time rather than being hardcoded in the core.
This allows downstream integrations to plug in additional providers without
modifying the SDK.
"""

import logging
from importlib.metadata import entry_points

from flow.application.config.config import Config
from flow.errors import FlowError
from flow.protocols.facets import ProviderFacets
from flow.protocols.provider import ProviderProtocol as IProvider

logger = logging.getLogger(__name__)


class ProviderNotFoundError(FlowError):
    """Raised when requested provider is not registered."""

    pass


class ProviderRegistry:
    """Central registry for compute providers.

    Providers self-register when imported, allowing dynamic discovery
    and preventing circular dependencies between core and providers.

    Example:
        >>> # In provider module __init__.py:
        >>> from flow.adapters.providers.registry import ProviderRegistry
        >>> from .provider import MyProvider
        >>>
        >>> ProviderRegistry.register("my_provider", MyProvider)

        >>> # Later, in application code:
        >>> provider = ProviderRegistry.create("my_provider", config)
    """

    _providers: dict[str, type[IProvider]] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, name: str, provider_class: type[IProvider]) -> None:
        """Register a provider implementation.

        Args:
            name: Provider identifier (e.g., "mithril", "aws", "gcp")
            provider_class: Provider class implementing IProvider

        Raises:
            ValueError: If provider name already registered
        """
        if name in cls._providers:
            # Allow re-registration for hot reloading and entry-point + import overlap
            existing = cls._providers.get(name)
            if existing is provider_class:
                # Same class; no-op and keep logs quiet in normal operation
                logger.debug(f"Provider '{name}' already registered with same class; skipping")
                return
            # Different class; overwrite but keep noise to debug level
            logger.debug(
                f"Provider '{name}' already registered with {getattr(existing, '__name__', existing)}; "
                f"overwriting with {provider_class.__name__}"
            )

        cls._providers[name] = provider_class
        logger.debug(f"Registered provider: {name} -> {provider_class.__name__}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove a provider from the registry.

        Args:
            name: Provider identifier to remove
        """
        if name in cls._providers:
            del cls._providers[name]
            logger.debug(f"Unregistered provider: {name}")

    @classmethod
    def get(cls, name: str) -> type[IProvider]:
        """Get a registered provider class.

        Args:
            name: Provider identifier

        Returns:
            Provider class

        Raises:
            ProviderNotFoundError: If provider not registered
        """
        # Auto-discover providers on first access
        if not cls._initialized:
            cls._auto_discover()

        if name not in cls._providers:
            available = list(cls._providers.keys())
            raise ProviderNotFoundError(
                f"Provider '{name}' not found. Available providers: {sorted(available)}"
            )

        return cls._providers[name]

    @classmethod
    def create(cls, name: str, config: Config) -> IProvider:
        """Create a provider instance.

        Args:
            name: Provider identifier
            config: Configuration object

        Returns:
            Initialized provider instance

        Raises:
            ProviderNotFoundError: If provider not registered
        """
        provider_class = cls.get(name)

        # Use from_config factory method if available
        if hasattr(provider_class, "from_config"):
            return provider_class.from_config(config)

        # Fall back to direct instantiation
        return provider_class(config)

    @classmethod
    def list_providers(cls) -> dict[str, type[IProvider]]:
        """Get all registered providers.

        Returns:
            Dictionary mapping provider names to classes
        """
        if not cls._initialized:
            cls._auto_discover()

        return cls._providers.copy()

    @classmethod
    def get_facets(cls, name: str, config: Config) -> ProviderFacets:
        """Return provider facets (capabilities) for the given provider.

        This instantiates the provider via the normal factory and then returns
        a `ProviderFacets` aggregate where each facet is set when implemented
        by the provider instance. This is non-breaking and can be adopted
        incrementally by callers.
        """
        provider = cls.create(name, config)
        return cls._facets_from_instance(provider)

    @staticmethod
    def _facets_from_instance(provider: IProvider) -> ProviderFacets:
        # Structural typing: assign the provider as the facet implementation
        # when it exposes the corresponding methods.
        compute = provider if hasattr(provider, "submit_task") else None
        logs = provider if hasattr(provider, "get_task_logs") else None
        storage = provider if hasattr(provider, "create_volume") else None
        reservations = provider if hasattr(provider, "create_reservation") else None
        ssh = provider if hasattr(provider, "get_remote_operations") else None
        return ProviderFacets(
            compute=compute, logs=logs, storage=storage, reservations=reservations, ssh=ssh
        )

    @classmethod
    def facets_for_instance(cls, provider: IProvider) -> ProviderFacets:
        """Public wrapper to build facets from an existing provider instance."""
        return cls._facets_from_instance(provider)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers. Useful for testing."""
        cls._providers.clear()
        cls._initialized = False
        logger.debug("Cleared provider registry")

    @classmethod
    def _auto_discover(cls) -> None:
        """Auto-discover providers via entry points, plugin registry, and direct imports (fallback)."""
        cls._initialized = True

        # 1) Entry points (preferred)
        try:
            eps = entry_points()
            candidates = getattr(eps, "select", lambda **kw: [])(group="flow.providers")
            for ep in candidates:
                try:
                    provider_cls = ep.load()
                    # Use entry point name as key if class lacks explicit name
                    name = getattr(provider_cls, "NAME", ep.name)
                    cls.register(name, provider_cls)
                    logger.debug(f"EP-registered provider: {name} -> {provider_cls}")
                except Exception as ep_err:
                    logger.debug(f"Entry point '{ep.name}' load failed: {ep_err}")
        except Exception as e:
            logger.debug(f"Entry points not available: {e}")

        # 2) Plugin registry (new extensibility)
        try:
            from flow.plugins import registry as plugin_registry  # type: ignore

            for name, provider_cls in getattr(
                plugin_registry, "list_providers", lambda: {}
            )().items():
                try:
                    cls.register(name, provider_cls)
                    logger.debug(f"Plugin-registered provider: {name} -> {provider_cls}")
                except Exception as e:
                    logger.debug(f"Plugin provider '{name}' registration failed: {e}")
        except Exception as e:
            logger.debug(f"Plugin registry not available: {e}")

        # 3) Known package imports (built-ins; canonical path)
        for provider_name in ["mithril", "local", "mock"]:
            if provider_name in cls._providers:
                continue
            try:
                __import__(f"flow.adapters.providers.builtin.{provider_name}")
                logger.debug(f"Imported builtin provider package: {provider_name}")
            except ImportError as e:
                logger.debug(f"Builtin provider '{provider_name}' not importable: {e}")
