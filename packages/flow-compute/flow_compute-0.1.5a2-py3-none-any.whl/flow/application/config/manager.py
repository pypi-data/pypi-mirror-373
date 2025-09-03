"""Centralized configuration manager for Flow SDK.

Provides a single abstraction for:
- Reading configuration from env and YAML via ConfigLoader
- Normalizing transient wizard inputs into canonical YAML structure
- Persisting configuration atomically via ConfigWriter
- Writing provider-specific environment scripts consistently

Design goals:
- One obvious way to read/write configuration
- Clear provider-specific namespace under `mithril`
- Canonical env variables for runtime: MITHRIL_*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from flow.application.config.loader import ConfigLoader
from flow.application.config.writer import ConfigWriter
from flow.sdk.models import ValidationResult as ApiValidationResult


@dataclass
class MithrilConfig:
    project: str | None = None
    region: str | None = None
    api_url: str | None = None
    ssh_keys: list[str] = field(default_factory=list)


@dataclass
class FlowConfig:
    provider: str = "mithril"
    api_key: str | None = None
    mithril: MithrilConfig = field(default_factory=MithrilConfig)


class ConfigManager:
    """Central manager for reading, normalizing, and persisting configuration."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or (Path.home() / ".flow" / "config.yaml")
        self.loader = ConfigLoader(self.config_path)
        self.writer = ConfigWriter(self.config_path)

    # ----- Read paths -----
    def load_sources(self):
        """Return ConfigSources (env + file)."""
        return self.loader.load_all_sources()

    def detect_existing_config(self) -> dict[str, Any]:
        """Detect existing configuration for wizard status.

        Returns a flat dict suitable for the wizard with keys:
        - api_key, project, default_ssh_key, region
        """
        sources = self.load_sources()
        detected: dict[str, Any] = {}

        # API key: env > file
        api_key = sources.api_key
        if api_key and not str(api_key).startswith("YOUR_"):
            detected["api_key"] = api_key

        mithril_cfg = sources.get_mithril_config()
        project = mithril_cfg.get("project")
        if project and not str(project).startswith("YOUR_"):
            detected["project"] = project

        # Normalize ssh_keys to default_ssh_key for display
        ssh_keys = mithril_cfg.get("ssh_keys")
        if ssh_keys:
            if isinstance(ssh_keys, list):
                if ssh_keys == ["_auto_"]:
                    detected["default_ssh_key"] = "_auto_"
                else:
                    detected["default_ssh_key"] = ",".join(ssh_keys)
            else:
                detected["default_ssh_key"] = str(ssh_keys)

        region = mithril_cfg.get("region")
        if region:
            detected["region"] = region

        return detected

    # ----- Write paths -----
    def normalize_payload(self, config: dict[str, Any]) -> dict[str, Any]:
        """Normalize a wizard/CLI config dict into canonical YAML structure.

        - provider at top-level
        - api_key at top-level
        - all provider settings under `mithril`
        - `default_ssh_key` converted to `mithril.ssh_keys`
        """
        # Take a shallow copy to avoid caller mutation
        normalized: dict[str, Any] = dict(config)
        normalized.setdefault("provider", "mithril")

        # Build mithril block
        mithril: dict[str, Any] = {}

        # Migrate top-level fields when present
        for key in ("project", "region", "api_url"):
            if normalized.get(key):
                mithril[key] = normalized.pop(key)

        # Convert default_ssh_key to list under mithril.ssh_keys
        if "default_ssh_key" in normalized:
            val = normalized.pop("default_ssh_key")
            keys: list[str] = []
            if val == "_auto_":
                keys = ["_auto_"]
            elif isinstance(val, str) and "," in val:
                keys = [k.strip() for k in val.split(",") if k.strip()]
            elif isinstance(val, str):
                keys = [val]
            elif isinstance(val, list):
                keys = [str(k).strip() for k in val if str(k).strip()]
            if keys:
                mithril["ssh_keys"] = keys

        # Merge any existing mithril block without clobbering new fields
        if isinstance(normalized.get("mithril"), dict):
            existing_mithril = normalized.pop("mithril")
            merged = {**existing_mithril, **mithril}
            mithril = merged

        if mithril:
            normalized["mithril"] = mithril

        return normalized

    def save(self, config: dict[str, Any]) -> dict[str, Any]:
        """Normalize and persist configuration. Returns the persisted dict."""
        normalized = self.normalize_payload(config)
        # Ensure api_key stays at top-level, provider set
        validation = ApiValidationResult(is_valid=True, projects=[])
        self.writer.write(dict(normalized), validation)
        return normalized

    def write_env_script(self, config: dict[str, Any], *, include_api_key: bool = False) -> Path:
        """Write provider-specific environment script.

        Writes canonical `MITHRIL_*` variables that are safe to persist in shell
        profiles. By default this excludes the API key to avoid storing secrets
        in plaintext files. Set `include_api_key=True` only for ephemeral,
        non-committed environments (e.g., CI) where this is acceptable.

        Args:
            config: Persisted configuration dictionary
            include_api_key: When True, also write `MITHRIL_API_KEY` to the script

        Returns:
            Path to the generated script
        """
        env_script = self.config_path.parent / "env.sh"
        env_script.parent.mkdir(parents=True, exist_ok=True)

        mithril = config.get("mithril", {}) if isinstance(config, dict) else {}
        with open(env_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Flow SDK Mithril provider environment variables\n")
            f.write("# Source this file: source ~/.flow/env.sh\n\n")

            if include_api_key and config.get("api_key"):
                f.write(f'export MITHRIL_API_KEY="{config["api_key"]}"\n')
            if mithril.get("project"):
                f.write(f'export MITHRIL_PROJECT="{mithril["project"]}"\n')
            if mithril.get("region"):
                f.write(f'export MITHRIL_REGION="{mithril["region"]}"\n')
            if mithril.get("ssh_keys"):
                # Store as comma-separated for shell convenience
                keys = mithril["ssh_keys"]
                if isinstance(keys, list):
                    keys_str = ",".join(keys)
                else:
                    keys_str = str(keys)
                f.write(f'export MITHRIL_SSH_KEYS="{keys_str}"\n')

        try:
            env_script.chmod(0o600)
        except Exception:
            # Windows and some FS may not support chmod
            pass
        return env_script
