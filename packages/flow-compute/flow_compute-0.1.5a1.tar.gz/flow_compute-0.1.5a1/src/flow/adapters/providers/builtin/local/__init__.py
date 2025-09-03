"""Local testing provider for Flow SDK.

Enables rapid development and testing without cloud infrastructure.
"""

from flow.adapters.providers.builtin.local.config import LocalInstanceMapping, LocalTestConfig
from flow.adapters.providers.builtin.local.executor import (
    ContainerTaskExecutor,
    ProcessTaskExecutor,
)
from flow.adapters.providers.builtin.local.manifest import LOCAL_MANIFEST
from flow.adapters.providers.builtin.local.provider import LocalProvider
from flow.adapters.providers.builtin.local.storage import LocalStorage

# Register with provider registry
from flow.adapters.providers.registry import ProviderRegistry

ProviderRegistry.register("local", LocalProvider)

__all__ = [
    "LocalProvider",
    "LocalTestConfig",
    "LocalInstanceMapping",
    "ContainerTaskExecutor",
    "ProcessTaskExecutor",
    "LocalStorage",
    "LOCAL_MANIFEST",
]
