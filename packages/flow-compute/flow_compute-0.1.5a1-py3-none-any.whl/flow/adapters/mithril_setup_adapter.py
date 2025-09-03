"""Mithril provider setup adapter.

Extracts Mithril-specific logic from the wizard to keep the wizard provider-agnostic
while preserving the UI and functionality.
"""

import asyncio
import os
from pathlib import Path
from typing import Any

from rich.console import Console

from flow.adapters.http.client import HttpClient
from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.application.config.manager import ConfigManager
from flow.cli.commands._init_components.config_analyzer import ConfigAnalyzer
from flow.cli.utils.config_validator import ConfigValidator, ValidationStatus
from flow.core.setup_adapters import ConfigField, FieldType, ProviderSetupAdapter, ValidationResult


def _run_async(awaitable):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        try:
            import nest_asyncio  # type: ignore

            try:
                nest_asyncio.apply()
            except Exception:
                pass
        except Exception:
            pass
        return loop.run_until_complete(awaitable)
    else:
        return asyncio.run(awaitable)


class MithrilSetupAdapter(ProviderSetupAdapter):
    """Mithril provider setup adapter."""

    def __init__(self, console: Console | None = None):
        """Initialize Mithril setup adapter.

        Args:
            console: Rich console for output (creates one if not provided)
        """
        self.console = console or Console()
        self.validator = ConfigValidator()
        # Canonical provider API URL; FLOW_API_URL no longer supported here
        self.api_url = os.environ.get("MITHRIL_API_URL", "https://api.mithril.ai")
        self.config_path = Path.home() / ".flow" / "config.yaml"
        self.analyzer = ConfigAnalyzer(self.config_path)

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "mithril"

    def get_configuration_fields(self) -> list[ConfigField]:
        """Get Mithril configuration fields."""
        return [
            ConfigField(
                name="api_key",
                field_type=FieldType.PASSWORD,
                required=True,
                mask_display=True,
                help_url=__import__("flow.utils.links", fromlist=["WebLinks"]).WebLinks.api_keys(),
                help_text="Get your API key from Mithril",
                default=None,
            ),
            ConfigField(
                name="project",
                field_type=FieldType.CHOICE,
                required=True,
                dynamic_choices=True,
                help_text="Select your Mithril project",
            ),
            ConfigField(
                name="default_ssh_key",
                field_type=FieldType.CHOICE,
                required=False,
                dynamic_choices=True,
                help_url=__import__("flow.utils.links", fromlist=["WebLinks"]).WebLinks.ssh_keys(),
                help_text="SSH key for accessing running instances",
            ),
            ConfigField(
                name="region",
                field_type=FieldType.CHOICE,
                required=False,
                choices=[
                    "us-central2-a",
                    "us-central1-b",
                    "eu-central1-a",
                    "eu-central1-b",
                ],
                default="us-central1-b",
                help_text="Default region for instances",
            ),
        ]

    def validate_field(self, field_name: str, value: str) -> ValidationResult:
        """Validate a single field value."""
        if field_name == "api_key":
            return self._validate_api_key(value)
        elif field_name == "project":
            return self._validate_project(value)
        elif field_name == "default_ssh_key":
            return self._validate_ssh_key(value)
        elif field_name == "region":
            return self._validate_region(value)
        else:
            return ValidationResult(is_valid=False, message=f"Unknown field: {field_name}")

    def get_dynamic_choices(self, field_name: str, context: dict[str, Any]) -> list[str]:
        """Get dynamic choices for a field."""
        if field_name == "project":
            return self._get_project_choices(context.get("api_key"))
        elif field_name == "default_ssh_key":
            return self._get_ssh_key_choices(context.get("api_key"), context.get("project"))
        else:
            return []

    def detect_existing_config(self) -> dict[str, Any]:
        """Detect existing configuration from environment, files, etc."""
        manager = ConfigManager(self.config_path)
        return manager.detect_existing_config()

    def save_configuration(self, config: dict[str, Any]) -> bool:
        """Save the final configuration."""
        try:
            manager = ConfigManager(self.config_path)
            payload = dict(config)
            payload.setdefault("provider", "mithril")
            saved = manager.save(payload)
            # Write env script without embedding the API key by default
            manager.write_env_script(saved, include_api_key=False)
            return True
        except Exception:
            return False

    def verify_configuration(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """Verify that the configuration works end-to-end."""
        try:
            # Set environment from config
            if "api_key" in config:
                os.environ["MITHRIL_API_KEY"] = config["api_key"]
            if "project" in config:
                os.environ["MITHRIL_PROJECT"] = config["project"]

            # Test API operation
            from flow.sdk.client import Flow

            client = Flow()
            client.list_tasks(limit=1)

            return True, None

        except Exception as e:
            return False, str(e)

    def get_welcome_message(self) -> tuple[str, list[str]]:
        """Get Mithril-specific welcome message."""
        return (
            "Welcome to Mithril Flow Setup",
            [
                "Get and validate your API key",
                "Select your project",
                "Configure SSH access",
                "Verify everything works",
            ],
        )

    def get_completion_message(self) -> str:
        """Get Mithril-specific completion message."""
        return "🎉 Setup Complete! Your Mithril Flow is configured and ready to run GPU workloads."

    # Private helper methods

    def _validate_api_key(self, api_key: str) -> ValidationResult:
        """Validate API key format and with API."""
        # Format validation
        format_result = self.validator.validate_api_key_format(api_key)
        if format_result.status != ValidationStatus.VALID:
            return ValidationResult(is_valid=False, message=format_result.message)

        # API validation
        try:
            result = _run_async(self.validator.verify_api_key(api_key))
            if result.status == ValidationStatus.VALID:
                masked_key = (
                    f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 10 else "[CONFIGURED]"
                )
                return ValidationResult(is_valid=True, display_value=masked_key)
            else:
                return ValidationResult(is_valid=False, message=result.message)
        except Exception as e:
            return ValidationResult(is_valid=False, message=f"Validation failed: {e}")

    def _validate_project(self, project: str) -> ValidationResult:
        """Validate project name."""
        result = self.validator.validate_project_name(project)
        if result.status == ValidationStatus.VALID:
            return ValidationResult(is_valid=True, display_value=project)
        else:
            return ValidationResult(is_valid=False, message=result.message)

    def _validate_ssh_key(self, ssh_key: str) -> ValidationResult:
        """Validate SSH key ID."""
        result = self.validator.validate_ssh_key_id(ssh_key)
        if result.status == ValidationStatus.VALID:
            display_value = (
                f"Platform key ({ssh_key[:14]}...)"
                if ssh_key.startswith("sshkey_")
                else "Configured"
            )
            return ValidationResult(is_valid=True, display_value=display_value)
        else:
            return ValidationResult(is_valid=False, message=result.message)

    def _validate_region(self, region: str) -> ValidationResult:
        """Validate region."""
        result = self.validator.validate_region(region)
        if result.status == ValidationStatus.VALID:
            return ValidationResult(is_valid=True, display_value=region)
        else:
            return ValidationResult(is_valid=False, message=result.message)

    def _get_project_choices(self, api_key: str | None) -> list[str]:
        """Get available projects from API."""
        if not api_key:
            return []

        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            projects = MithrilApiClient(client).list_projects()
            return [proj["name"] for proj in projects if isinstance(projects, list)]
        except Exception:
            return []

    def _get_ssh_key_choices(self, api_key: str | None, project: str | None) -> list[str]:
        """Get available SSH keys from API."""
        if not api_key or not project:
            return []

        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )

            # Get project ID
            projects = MithrilApiClient(client).list_projects()
            project_id = None
            for proj in projects:
                if proj.get("name") == project:
                    project_id = proj.get("fid")
                    break

            if not project_id:
                return []

            # Get SSH keys
            ssh_keys = MithrilApiClient(client).list_ssh_keys({"project": project_id})
            return [
                f"{key['name']} ({key['fid']})" for key in ssh_keys if isinstance(ssh_keys, list)
            ]
        except Exception:
            return []

    def _save_credentials(self, api_key: str):
        """Save API key to credentials file."""
        import configparser

        credentials_dir = Path.home() / ".flow"
        credentials_dir.mkdir(exist_ok=True)
        credentials_path = credentials_dir / "credentials"

        config = configparser.ConfigParser()
        if credentials_path.exists():
            config.read(credentials_path)

        if "default" not in config:
            config.add_section("default")
        config["default"]["api_key"] = api_key

        with open(credentials_path, "w") as f:
            config.write(f)

        try:
            credentials_path.chmod(0o600)
        except Exception:
            pass  # Windows doesn't support chmod

    def _create_env_script(self, config: dict[str, Any]):
        """Create shell script with environment variables."""
        env_script = self.config_path.parent / "env.sh"

        with open(env_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Flow SDK environment variables\n")
            f.write("# Source this file: source ~/.flow/env.sh\n\n")

            if "api_key" in config:
                f.write(f'export MITHRIL_API_KEY="{config["api_key"]}"\n')
            if "project" in config:
                f.write(f'export FLOW_DEFAULT_PROJECT="{config["project"]}"\n')
            if "region" in config:
                f.write(f'export FLOW_DEFAULT_REGION="{config["region"]}"\n')
            if "default_ssh_key" in config:
                f.write(f'export FLOW_SSH_KEYS="{config["default_ssh_key"]}"\n')

        env_script.chmod(0o600)
