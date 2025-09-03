"""Configuration validation utilities.

Provides validation for API keys, projects, and other configuration values
used across CLI commands.
"""

import os
from dataclasses import dataclass
from enum import Enum

import httpx
from flow.errors import AuthenticationError, NetworkError
from flow.plugins import registry as plugin_registry


class ValidationStatus(Enum):
    """Status of configuration validation."""

    VALID = "valid"
    INVALID = "invalid"
    NETWORK_ERROR = "network_error"
    NOT_CHECKED = "not_checked"


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    status: ValidationStatus
    message: str | None = None
    details: dict | None = None


class ConfigValidator:
    """Validate Flow SDK configuration values using provider-specific rules."""

    def __init__(self, api_url: str | None = None, provider: str | None = None):
        """Initialize validator.

        Args:
            api_url: API endpoint URL (defaults to FLOW_API_URL env var)
            provider: Provider name for validation rules
        """
        self.api_url = api_url or os.environ.get(
            "MITHRIL_API_URL", os.environ.get("FLOW_API_URL", "https://api.mithril.ai")
        )
        self.provider = provider or os.environ.get("FLOW_PROVIDER")

    def validate_api_key_format(
        self, api_key: str, provider: str | None = None
    ) -> ValidationResult:
        """Validate API key format without making API calls.

        Args:
            api_key: API key to validate
            provider: Provider name (uses instance provider if not specified)

        Returns:
            ValidationResult with format validation status
        """
        if not api_key:
            return ValidationResult(
                status=ValidationStatus.INVALID, message="API key cannot be empty"
            )

        # Check for placeholder values
        if api_key.startswith("YOUR_") or api_key == "PLACEHOLDER":
            return ValidationResult(
                status=ValidationStatus.INVALID, message="API key appears to be a placeholder value"
            )

        # Check length
        if len(api_key) < 20:
            return ValidationResult(status=ValidationStatus.INVALID, message="API key is too short")

        # Use provider resolver for validation
        provider_name = provider or self.provider
        try:
            ProviderClass = plugin_registry.get_provider(provider_name)
            is_valid = False
            if ProviderClass and hasattr(ProviderClass, "validate_config_value"):
                is_valid = bool(ProviderClass.validate_config_value("api_key", api_key))
            else:
                is_valid = True  # no provider-specific rule -> accept
        except Exception:
            is_valid = True
        if is_valid:
            return ValidationResult(status=ValidationStatus.VALID)
        else:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                message=f"API key format is invalid for provider {provider_name}",
            )

    async def verify_api_key(self, api_key: str) -> ValidationResult:
        """Verify API key by making an API call.

        Args:
            api_key: API key to verify

        Returns:
            ValidationResult with verification status
        """
        # First check format
        format_result = self.validate_api_key_format(api_key)
        if format_result.status != ValidationStatus.VALID:
            return format_result

        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            with httpx.Client(base_url=self.api_url, timeout=httpx.Timeout(10.0)) as client:
                resp = client.get("/v2/projects", headers=headers)
                if resp.status_code in (401, 403):
                    raise AuthenticationError("Invalid API key")
                resp.raise_for_status()
                data = resp.json()
            details = {}
            if isinstance(data, list) and data:
                details["project_count"] = len(data)
                details["projects"] = [p.get("name", "Unknown") for p in data[:3]]
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="API key verified successfully",
                details=details,
            )
        except AuthenticationError:
            return ValidationResult(
                status=ValidationStatus.INVALID, message="API key is invalid or expired"
            )
        except httpx.TimeoutException as e:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR, message=f"Request timed out: {e}"
            )
        except httpx.HTTPError as e:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR, message=f"HTTP error: {e}"
            )
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR, message=f"Verification failed: {e}"
            )

    def validate_project_name(self, project: str, provider: str | None = None) -> ValidationResult:
        """Validate project name format using provider rules.

        Args:
            project: Project name to validate
            provider: Provider name (uses instance provider if not specified)

        Returns:
            ValidationResult with validation status
        """
        if not project:
            return ValidationResult(
                status=ValidationStatus.INVALID, message="Project name cannot be empty"
            )

        # Use provider resolver for validation
        provider_name = provider or self.provider
        try:
            ProviderClass = plugin_registry.get_provider(provider_name)
            is_valid = False
            if ProviderClass and hasattr(ProviderClass, "validate_config_value"):
                is_valid = bool(ProviderClass.validate_config_value("project", project))
            else:
                is_valid = True
        except Exception:
            is_valid = True
        if is_valid:
            return ValidationResult(status=ValidationStatus.VALID)
        else:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                message=f"Project name format is invalid for provider {provider_name}",
            )

    def validate_ssh_key_id(self, key_id: str) -> ValidationResult:
        """Validate SSH key ID format.

        Args:
            key_id: SSH key ID to validate

        Returns:
            ValidationResult with validation status
        """
        if not key_id:
            return ValidationResult(
                status=ValidationStatus.INVALID, message="SSH key ID cannot be empty"
            )

        # Check format
        if not key_id.startswith("sshkey_"):
            return ValidationResult(
                status=ValidationStatus.INVALID, message="SSH key ID should start with 'sshkey_'"
            )

        # Check length
        if len(key_id) < 10:
            return ValidationResult(
                status=ValidationStatus.INVALID, message="SSH key ID is too short"
            )

        return ValidationResult(status=ValidationStatus.VALID)

    def validate_region(self, region: str, provider: str | None = None) -> ValidationResult:
        """Validate region name format using provider rules.

        Args:
            region: Region name to validate
            provider: Provider name (uses instance provider if not specified)

        Returns:
            ValidationResult with validation status
        """
        if not region:
            return ValidationResult(
                status=ValidationStatus.INVALID, message="Region cannot be empty"
            )

        # Use provider resolver for validation
        provider_name = provider or self.provider
        try:
            ProviderClass = plugin_registry.get_provider(provider_name)
            is_valid = False
            if ProviderClass and hasattr(ProviderClass, "validate_config_value"):
                is_valid = bool(ProviderClass.validate_config_value("region", region))
            else:
                is_valid = True
        except Exception:
            is_valid = True
        if is_valid:
            return ValidationResult(status=ValidationStatus.VALID)
        else:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                message=f"Region format is invalid for provider {provider_name}",
            )

    def validate_all(self, config: dict) -> tuple[bool, list[str]]:
        """Validate all configuration values.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []
        provider = config.get("provider", self.provider)

        # Validate API key format
        if "api_key" in config:
            result = self.validate_api_key_format(config["api_key"], provider)
            if result.status != ValidationStatus.VALID:
                errors.append(f"API Key: {result.message}")

        # Validate project
        if "project" in config:
            result = self.validate_project_name(config["project"], provider)
            if result.status != ValidationStatus.VALID:
                errors.append(f"Project: {result.message}")

        # Validate SSH keys
        if "default_ssh_key" in config:
            result = self.validate_ssh_key_id(config["default_ssh_key"])
            if result.status != ValidationStatus.VALID:
                errors.append(f"SSH Key: {result.message}")

        # Validate region
        if "region" in config:
            result = self.validate_region(config["region"], provider)
            if result.status != ValidationStatus.VALID:
                errors.append(f"Region: {result.message}")

        return len(errors) == 0, errors
