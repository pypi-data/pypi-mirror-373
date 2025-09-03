"""Registry for provider setup implementations.

Manages the mapping between provider names and their setup adapters.
"""

import os

from flow.core.provider_setup import ProviderSetup
from flow.core.setup_adapters import ProviderSetupAdapter


class SetupRegistry:
    """Registry for provider setup implementations."""

    _registry: dict[str, type[ProviderSetup]] = {}
    _adapter_registry: dict[str, type[ProviderSetupAdapter]] = {}

    @classmethod
    def register(cls, provider_name: str, setup_class: type[ProviderSetup]):
        """Register a provider setup implementation.

        Args:
            provider_name: Name of the provider
            setup_class: Setup implementation class
        """
        cls._registry[provider_name.lower()] = setup_class

    @classmethod
    def register_adapter(cls, provider_name: str, adapter_class: type[ProviderSetupAdapter]):
        """Register a provider setup adapter.

        Args:
            provider_name: Name of the provider
            adapter_class: Setup adapter implementation class
        """
        cls._adapter_registry[provider_name.lower()] = adapter_class

    @classmethod
    def get_setup(cls, provider_name: str) -> ProviderSetup | None:
        """Get setup implementation for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Setup instance or None if not found
        """
        setup_class = cls._registry.get(provider_name.lower())
        if setup_class:
            return setup_class()
        return None

    @classmethod
    def get_adapter(cls, provider_name: str) -> ProviderSetupAdapter | None:
        """Get setup adapter for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Setup adapter instance or None if not found
        """
        adapter_class = cls._adapter_registry.get(provider_name.lower())
        if adapter_class:
            return adapter_class()
        return None

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered providers.

        Returns:
            List of provider names
        """
        return list(cls._registry.keys())

    @classmethod
    def list_adapters(cls) -> list[str]:
        """List all providers that have registered setup adapters.

        Returns:
            List of provider names with adapters
        """
        return list(cls._adapter_registry.keys())


# Register providers
def register_providers():
    """Register all available provider setups."""
    # Import Mithril adapter dynamically to avoid static core→providers dependency
    import importlib

    try:
        _mod = importlib.import_module("flow.adapters.providers.builtin.mithril.setup.adapter")
        MithrilSetupAdapter = _mod.MithrilSetupAdapter
    except Exception:  # pragma: no cover - optional provider availability
        MithrilSetupAdapter = None  # type: ignore[assignment]

    # Mock provider adapter is disabled by default. Enable only via explicit env.
    try:
        enable_demo = str(os.environ.get("FLOW_ENABLE_DEMO_ADAPTER", "")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if enable_demo:
            from flow.core.setup_adapters import (
                ConfigField,
                FieldType,
                ProviderSetupAdapter,
                ValidationResult,
            )

            class _MockSetupAdapter(ProviderSetupAdapter):  # type: ignore
                """Demo/mock provider setup with full wizard experience.

                Presents realistic fields so users can practice configuring
                projects, regions, SSH keys, and a demo API key without
                touching real infrastructure.
                """

                _DEMO_PROJECTS = [
                    "post-training-team",
                    "reasoning-research",
                    "inference-optimization",
                    "pretraining",
                ]
                _DEMO_REGIONS = [
                    "us-demo-1",
                    "eu-demo-1",
                    "apac-demo-1",
                ]

                def get_provider_name(self) -> str:
                    return "mock"

                def get_configuration_fields(self):
                    return [
                        ConfigField(
                            name="demo_api_key",
                            field_type=FieldType.PASSWORD,
                            required=True,
                            mask_display=True,
                            display_name="Demo API Key",
                            help_text=(
                                "Enter any value to simulate authentication. This is NOT used against real services. "
                                "Tip: use DEMO-XXXX for tutorials."
                            ),
                        ),
                        ConfigField(
                            name="project",
                            field_type=FieldType.CHOICE,
                            required=True,
                            display_name="Demo Project",
                            help_text="Select a sample project for pre-populated examples.",
                            dynamic_choices=True,
                        ),
                        ConfigField(
                            name="region",
                            field_type=FieldType.CHOICE,
                            required=True,
                            display_name="Default Demo Region",
                            help_text="Pick a demo region for simulated capacity.",
                            choices=self._DEMO_REGIONS,
                            dynamic_choices=False,
                        ),
                        ConfigField(
                            name="default_ssh_key",
                            field_type=FieldType.CHOICE,
                            required=False,
                            display_name="Default SSH Key",
                            help_text=(
                                "Choose how SSH should behave in demos. Generate on Mithril (recommended) saves the private key locally; or pick a local public key."
                            ),
                            dynamic_choices=True,
                        ),
                    ]

                def detect_existing_config(self):
                    # Read existing ~/.flow/config.yaml to pre-populate wizard
                    try:
                        from flow.application.config.manager import ConfigManager

                        sources = ConfigManager().load_sources()
                        cfg = sources.config_file if isinstance(sources.config_file, dict) else {}
                        if (cfg.get("provider") or "").lower() == "mock":
                            demo = cfg.get("demo", {}) or {}
                            return {
                                "provider": "mock",
                                "project": cfg.get("project", self._DEMO_PROJECTS[0]),
                                "region": cfg.get("region", self._DEMO_REGIONS[0]),
                                "default_ssh_key": cfg.get("default_ssh_key", "_auto_"),
                                "demo_api_key": demo.get("api_key"),
                            }
                    except Exception:
                        pass
                    # Fallback defaults for first-time demo
                    return {
                        "provider": "mock",
                        "project": self._DEMO_PROJECTS[0],
                        "region": self._DEMO_REGIONS[0],
                        "default_ssh_key": "_auto_",
                    }

                def get_dynamic_choices(self, field_name: str, context):
                    if field_name == "project":
                        return list(self._DEMO_PROJECTS)
                    if field_name == "default_ssh_key":
                        # Include local ~/.ssh/*.pub keys as selectable options in demo
                        choices = [
                            "GENERATE_SERVER|Generate on Mithril (recommended; saves key locally)",
                            "none|No SSH access",
                        ]
                        try:
                            from pathlib import Path

                            ssh_dir = Path.home() / ".ssh"
                            if ssh_dir.exists():
                                for pub in sorted(ssh_dir.glob("*.pub")):
                                    # id format: local:/path/to/key.pub | display: Local: id_ed25519.pub
                                    choices.append(f"local:{pub}|Local: {pub.name}")
                        except Exception:
                            pass
                        return choices
                    return []

                def validate_field(
                    self, field_name: str, value: str, context=None
                ) -> ValidationResult:
                    if field_name == "project":
                        ok = value in self._DEMO_PROJECTS
                        return ValidationResult(
                            is_valid=ok,
                            display_value=value,
                            message=None if ok else "Unknown project",
                        )
                    if field_name == "region":
                        ok = value in self._DEMO_REGIONS
                        return ValidationResult(
                            is_valid=ok,
                            display_value=value,
                            message=None if ok else "Unknown region",
                        )
                    if field_name == "default_ssh_key":
                        # Accept 'none' or a local public key path prefixed with local:
                        if value == "none":
                            return ValidationResult(
                                is_valid=True, display_value="No SSH access", processed_value=value
                            )
                        if value.startswith("local:"):
                            key_path = value.split(":", 1)[1]
                            try:
                                from pathlib import Path

                                p = Path(key_path).expanduser()
                                if p.exists() and p.is_file():
                                    return ValidationResult(
                                        is_valid=True,
                                        display_value=f"Local key: {p.name}",
                                        processed_value=str(p),
                                    )
                                return ValidationResult(
                                    is_valid=False,
                                    display_value=None,
                                    message="Local key not found",
                                )
                            except Exception:
                                return ValidationResult(
                                    is_valid=False,
                                    display_value=None,
                                    message="Invalid local key path",
                                )
                        return ValidationResult(
                            is_valid=False, display_value=None, message="Unsupported key selection"
                        )
                    if field_name == "demo_api_key":
                        # Mirror Mithril-style validation: require non-empty, specific prefix optional
                        if not value or not str(value).strip():
                            return ValidationResult(
                                is_valid=False,
                                display_value=None,
                                message="Demo API key is required",
                            )
                        # Show masked last-4 for consistency with global masking utilities
                        try:
                            from flow.sdk.helpers.masking import mask_strict_last4  # type: ignore

                            display = mask_strict_last4(str(value))
                        except Exception:
                            display = "••••"
                        return ValidationResult(is_valid=True, display_value=display)
                    return ValidationResult(is_valid=True, display_value=value)

                def save_configuration(self, config):
                    # Persist a coherent demo configuration
                    from flow.application.config.manager import ConfigManager

                    payload = {
                        "provider": "mock",
                    }
                    if config.get("project"):
                        payload["project"] = config["project"]
                    if config.get("region"):
                        payload["region"] = config["region"]
                    if config.get("default_ssh_key"):
                        payload["default_ssh_key"] = config["default_ssh_key"]
                    if config.get("demo_api_key"):
                        payload["demo"] = {"api_key": config["demo_api_key"]}

                    manager = ConfigManager()
                    manager.save(payload)
                    return True

                def verify_configuration(self, config):
                    # Always successful in mock mode, but give helpful feedback
                    return True, None

            SetupRegistry.register_adapter("mock", _MockSetupAdapter)
    except Exception:
        pass

    # Only register the adapter for now (facade path)
    if MithrilSetupAdapter is not None:
        SetupRegistry.register_adapter("mithril", MithrilSetupAdapter)

    # Future providers would be registered here
    # from flow.adapters.providers.local.setup import LocalProviderSetup
    # SetupRegistry.register("local", LocalProviderSetup)
