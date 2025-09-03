"""Provider initialization interface.

This module defines the interface for provider initialization and configuration,
separate from the main provider runtime interface.
"""

from typing import Protocol

from flow.adapters.providers.base import ConfigField


class ProviderInitProtocol(Protocol):
    """Provider initialization and configuration interface.

    Defines provider-specific initialization capabilities and enables the CLI
    to gather configuration without hard-coding provider logic. This abstraction
    allows new providers to be added without modifying the CLI commands.
    """

    def get_config_fields(self) -> dict[str, ConfigField]:
        """Return configuration field definitions for this provider.

        Returns:
            Dictionary mapping field names to ConfigField objects that describe
            the required and optional configuration for this provider.
        """
        ...

    def validate_config(self, config: dict[str, str]) -> tuple[bool, str]:
        """Validate provider configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        ...

    def get_setup_instructions(self) -> list[str]:
        """Get human-readable setup instructions for this provider.

        Returns:
            List of setup instruction strings for display to users.
        """
        ...

    def test_connection(self, config: dict[str, str]) -> tuple[bool, str]:
        """Test connection to provider with given configuration.

        Args:
            config: Configuration dictionary to test

        Returns:
            Tuple of (is_connected, status_message).
        """
        ...


# Backward compatibility alias
IProviderInit = ProviderInitProtocol
