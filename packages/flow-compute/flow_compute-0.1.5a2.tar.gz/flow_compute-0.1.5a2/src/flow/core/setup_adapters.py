"""Setup adapter interfaces for Flow SDK.

Defines the adapter pattern that allows the GenericSetupWizard to work with any
provider while maintaining a consistent UI and functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class FieldType(Enum):
    """Types of configuration fields."""

    TEXT = "text"
    PASSWORD = "password"
    CHOICE = "choice"
    BOOLEAN = "boolean"


@dataclass
class ConfigField:
    """Configuration field specification."""

    name: str
    field_type: FieldType
    required: bool = True
    mask_display: bool = False  # For API keys, etc.
    help_url: str | None = None
    help_text: str | None = None
    default: str | None = None
    choices: list[str] | None = None  # For CHOICE type
    dynamic_choices: bool = False  # If choices come from API
    display_name: str | None = None  # Custom display name in UI
    # Optional dependencies that should be configured before this field
    # is actionable (used for clearer UX hints when choices are empty).
    depends_on: list[str] | None = None
    # Optional hint to show when dynamic choices are empty for this field
    # (e.g., "Requires API key to list projects").
    empty_choices_hint: str | None = None


@dataclass
class ValidationResult:
    """Result of field validation."""

    is_valid: bool
    message: str | None = None
    display_value: str | None = None  # For masked fields
    processed_value: str | None = None  # For transformations like SSH key generation


class ProviderSetupAdapter(ABC):
    """Adapter interface for provider-specific setup logic.

    This allows the GenericSetupWizard to work with any provider
    while maintaining its polished UI and functionality.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass

    @abstractmethod
    def get_configuration_fields(self) -> list[ConfigField]:
        """Get the configuration fields for this provider."""
        pass

    @abstractmethod
    def validate_field(
        self, field_name: str, value: str, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate a single field value.

        Args:
            field_name: Name of the field
            value: Field value to validate
            context: Optional context with previously configured values

        Returns:
            ValidationResult with validation status and display value
        """
        pass

    @abstractmethod
    def get_dynamic_choices(self, field_name: str, context: dict[str, Any]) -> list[str]:
        """Get dynamic choices for a field (e.g., projects from API).

        Args:
            field_name: Name of the field
            context: Previously configured values for context

        Returns:
            List of available choices
        """
        pass

    @abstractmethod
    def detect_existing_config(self) -> dict[str, Any]:
        """Detect existing configuration from environment, files, etc.

        Returns:
            Dictionary of detected configuration values
        """
        pass

    @abstractmethod
    def save_configuration(self, config: dict[str, Any]) -> bool:
        """Save the final configuration.

        Args:
            config: Configuration to save

        Returns:
            True if save was successful
        """
        pass

    @abstractmethod
    def verify_configuration(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """Verify that the configuration works end-to-end.

        Args:
            config: Configuration to verify

        Returns:
            Tuple of (success, error_message)
        """
        pass

    def get_welcome_message(self) -> tuple[str, list[str]]:
        """Get provider-specific welcome message.

        Returns:
            Tuple of (title, feature_list)
        """
        return (
            f"{self.get_provider_name().upper()} Provider Setup",
            ["Configure authentication", "Select project settings", "Set up optional features"],
        )

    def get_completion_message(self) -> str:
        """Get provider-specific completion message."""
        return f"Your {self.get_provider_name().upper()} configuration is ready!"
