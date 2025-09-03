"""Configuration analysis utilities for the init command.

Detects and analyzes existing configuration from environment variables,
configuration files, and other sources.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Lazy import in constructor to avoid static CLI->core dependency


class ConfigStatus(Enum):
    """Configuration item status."""

    CONFIGURED = "configured"
    MISSING = "missing"
    INVALID = "invalid"
    OPTIONAL = "optional"


@dataclass
class ConfigItem:
    """Configuration item with status and metadata."""

    name: str
    status: ConfigStatus
    value: Any | None = None
    source: str | None = None  # 'env', 'file', 'default'
    display_value: str | None = None  # For display purposes


class ConfigAnalyzer:
    """Analyze existing Flow SDK configuration."""

    def __init__(self, config_path: Path):
        """Initialize analyzer.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        from flow.cli.utils.lazy_imports import import_attr as _import_attr

        ConfigLoader = _import_attr("flow.application.config.loader", "ConfigLoader", default=None)
        self.loader = ConfigLoader(config_path) if ConfigLoader else None  # type: ignore[assignment]

    def analyze_configuration(self) -> dict[str, ConfigItem]:
        """Detect and analyze existing configuration.

        Returns:
            Dictionary mapping component names to ConfigItem objects
        """
        # Load configuration from all sources (env + config file)
        if self.loader is None:
            # Best-effort fallback when core loader unavailable
            return {}
        sources = self.loader.load_all_sources()

        # Analyze each component
        config_status = {}

        # API Key
        config_status["api_key"] = self._analyze_api_key(sources)

        # Project
        config_status["project"] = self._analyze_project(sources)

        # SSH Keys
        config_status["ssh_keys"] = self._analyze_ssh_keys(sources)

        # Region
        config_status["region"] = self._analyze_region(sources)

        return config_status

    def _analyze_api_key(self, sources: Any) -> ConfigItem:
        """Analyze API key configuration.

        Args:
            sources: Configuration sources object

        Returns:
            ConfigItem for API key
        """
        api_key = sources.api_key

        if api_key and not api_key.startswith("YOUR_"):
            # Determine source
            if sources.env_vars.get("MITHRIL_API_KEY"):
                source = "env"
            else:
                source = "file"

            return ConfigItem(
                name="API Key",
                status=ConfigStatus.CONFIGURED,
                value=api_key,
                source=source,
                display_value=self._get_api_key_display(api_key),
            )
        else:
            return ConfigItem(name="API Key", status=ConfigStatus.MISSING)

    def _analyze_project(self, sources: Any) -> ConfigItem:
        """Analyze project configuration.

        Args:
            sources: Configuration sources object

        Returns:
            ConfigItem for project
        """
        mithril_config = sources.get_mithril_config()
        project = mithril_config.get("project") or sources.config_file.get("project")

        if project and not project.startswith("YOUR_"):
            source = "env" if sources.env_vars.get("MITHRIL_PROJECT") else "file"

            return ConfigItem(
                name="Project",
                status=ConfigStatus.CONFIGURED,
                value=project,
                source=source,
                display_value=project,
            )
        else:
            return ConfigItem(name="Project", status=ConfigStatus.MISSING)

    def _analyze_ssh_keys(self, sources: Any) -> ConfigItem:
        """Analyze SSH key configuration.

        Args:
            sources: Configuration sources object

        Returns:
            ConfigItem for SSH keys
        """
        mithril_config = sources.get_mithril_config()
        ssh_keys = mithril_config.get("ssh_keys") or sources.config_file.get("default_ssh_key")

        if ssh_keys:
            # Convert to string for display
            ssh_keys_str = ssh_keys if isinstance(ssh_keys, str) else ",".join(ssh_keys)
            source = "env" if sources.env_vars.get("MITHRIL_SSH_KEYS") else "file"

            return ConfigItem(
                name="SSH Keys",
                status=ConfigStatus.CONFIGURED,
                value=ssh_keys_str,
                source=source,
                display_value=self._get_ssh_key_display(ssh_keys_str),
            )
        else:
            return ConfigItem(
                name="SSH Keys",
                status=ConfigStatus.OPTIONAL,
                display_value="Not configured (optional)",
            )

    def _analyze_region(self, sources: Any) -> ConfigItem:
        """Analyze region configuration.

        Args:
            sources: Configuration sources object

        Returns:
            ConfigItem for region
        """
        mithril_config = sources.get_mithril_config()
        region = mithril_config.get("region") or sources.config_file.get("region")

        if region:
            source = "env" if sources.env_vars.get("MITHRIL_REGION") else "file"

            return ConfigItem(
                name="Region",
                status=ConfigStatus.CONFIGURED,
                value=region,
                source=source,
                display_value=region,
            )
        else:
            return ConfigItem(name="Region", status=ConfigStatus.OPTIONAL, display_value="Default")

    def _get_api_key_display(self, api_key: str) -> str:
        """Create safe display string for API key.

        Args:
            api_key: Full API key value

        Returns:
            Masked string (e.g., "fkey_1234...abcd")
        """
        if len(api_key) > 10:
            return f"{api_key[:8]}...{api_key[-4:]}"
        return "[CONFIGURED]"

    def _get_ssh_key_display(self, ssh_keys: str) -> str:
        """Create display string for SSH key configuration.

        Args:
            ssh_keys: SSH key ID(s), comma-separated for multiple

        Returns:
            Human-readable description
        """
        if "," in ssh_keys:
            count = len(ssh_keys.split(","))
            return f"{count} keys configured"
        elif ssh_keys.startswith("sshkey_"):
            return f"Platform key ({ssh_keys[:14]}...)"
        else:
            return "Configured"

    def get_existing_config(self) -> dict[str, Any]:
        """Get existing configuration from file.

        Returns:
            Dictionary of existing configuration values
        """
        sources = self.loader.load_all_sources()
        return sources.config_file.copy()

    def is_fully_configured(self, config_status: dict[str, ConfigItem]) -> bool:
        """Check if all required components are configured.

        Args:
            config_status: Dictionary of configuration items

        Returns:
            True if all required items are configured
        """
        required = ["api_key", "project"]
        return all(
            config_status.get(name, ConfigItem(name, ConfigStatus.MISSING)).status
            == ConfigStatus.CONFIGURED
            for name in required
        )
