"""Factory for creating API clients implementing CLI-facing contracts.

This module provides a single entry point for the CLI layer to obtain an
`IClient` without importing concrete client implementations directly.
"""

from __future__ import annotations

from flow.application.config.config import Config
from flow.sdk.client import Flow
from flow.sdk.contracts import IClient


def create_client(*, auto_init: bool = False, config: Config | None = None) -> IClient:
    """Return a concrete client that implements `IClient`.

    Args:
        auto_init: If True, allow interactive initialization for CLI contexts.
        config: Optional explicit configuration object.

    Returns:
        IClient: A client implementing the union of task/logs/volume services.
    """
    return Flow(config=config, auto_init=auto_init)
