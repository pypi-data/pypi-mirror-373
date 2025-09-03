"""Configuration writer for Flow SDK.

Persists configuration to disk in a single canonical location:
- `~/.flow/config.yaml` for all configuration, including the API key.

Historical note: Older versions wrote provider credentials to
`~/.flow/credentials.{provider}`. This writer deliberately avoids that
split to remove ambiguity and simplify precedence.
"""

from __future__ import annotations

import configparser
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from flow.sdk.models import ValidationResult


class ConfigWriter:
    """Writes Flow configuration securely.

    Features:
    - Single source of truth in `~/.flow/config.yaml`
    - Atomic file writes with rollback
    - Proper file permissions (0600)
    - Simple, explicit behavior
    """

    def __init__(self, config_path: Path | None = None):
        """Initialize writer.

        Args:
            config_path: Path to config file (defaults to ~/.flow/config.yaml)
        """
        self.config_path = config_path or Path.home() / ".flow" / "config.yaml"
        self.flow_dir = self.config_path.parent

    def write(self, config: dict[str, Any], validation: ValidationResult) -> None:
        """Write configuration to disk.

        Args:
            config: Configuration dictionary
            validation: Validation result (for future use)

        Raises:
            OSError: If unable to write configuration
        """
        # Work on a copy to avoid mutating the caller's config
        cfg: dict[str, Any] = deepcopy(config)

        # Load the existing file to merge conservatively, so partial saves
        # (e.g., appending a generated SSH key) never wipe unrelated fields
        # like api_key or project.
        existing: dict[str, Any] = {}
        try:
            if self.config_path.exists():
                import yaml as _yaml

                with open(self.config_path) as _f:
                    loaded = _yaml.safe_load(_f) or {}
                    if isinstance(loaded, dict):
                        existing = deepcopy(loaded)
        except Exception:
            existing = {}

        # Keep API key inline in the YAML for explicit, single-source config
        api_key = cfg.get("api_key")

        # Transform to new config format if provider is specified
        provider = cfg.get("provider")
        if provider:
            # New provider-based format with explicit, non-clobbering merge semantics
            # Start from existing config to preserve previously saved values
            file_config: dict[str, Any] = {"provider": provider}
            if isinstance(existing.get("provider"), str) and not file_config.get("provider"):
                file_config["provider"] = existing.get("provider")

            # Start from any existing provider section and merge in normalized fields
            if provider == "mithril":
                # Begin with any existing mithril subsection (if present)
                # Merge existing mithril block first, then layer new normalized values
                existing_mithril: dict[str, Any] = {}
                if isinstance(existing.get("mithril"), dict):
                    existing_mithril = deepcopy(existing.get("mithril", {}))
                # If caller passed a mithril block, overlay it on top of existing
                if isinstance(cfg.get("mithril"), dict):
                    for mk, mv in dict(cfg.get("mithril", {})).items():
                        existing_mithril[mk] = mv

                # Collect normalized mithril fields from top-level
                normalized_mithril: dict[str, Any] = dict(existing_mithril)

                # Migrate top-level fields into provider section when present
                if cfg.get("project"):
                    normalized_mithril["project"] = cfg.pop("project")
                if cfg.get("region"):
                    normalized_mithril["region"] = cfg.pop("region")
                if cfg.get("api_url"):
                    normalized_mithril["api_url"] = cfg.pop("api_url")

                # Normalize SSH keys from "default_ssh_key" (string) into list under mithril.ssh_keys
                if "default_ssh_key" in cfg:
                    ssh_val = cfg.pop("default_ssh_key")
                    keys_list: list[str]
                    if ssh_val == "_auto_":
                        keys_list = ["_auto_"]
                    elif isinstance(ssh_val, str) and "," in ssh_val:
                        # Allow comma-separated values for advanced users
                        keys_list = [k.strip() for k in ssh_val.split(",") if k.strip()]
                    elif isinstance(ssh_val, str):
                        keys_list = [ssh_val]
                    elif isinstance(ssh_val, list):
                        keys_list = [str(k).strip() for k in ssh_val if str(k).strip()]
                    else:
                        keys_list = []
                    if keys_list:
                        normalized_mithril["ssh_keys"] = keys_list

                if normalized_mithril:
                    file_config["mithril"] = normalized_mithril

            # Ensure api_key remains explicitly persisted at the top level
            if api_key:
                file_config["api_key"] = api_key
            else:
                # Preserve existing api_key when not explicitly updating it
                if isinstance(existing.get("api_key"), str) and existing.get("api_key"):
                    file_config["api_key"] = existing["api_key"]

            # Remove internal keys from cfg that we've already handled to avoid clobbering
            for k in ("provider", "mithril", "api_key"):
                if k in cfg:
                    cfg.pop(k)

            # Any remaining unrelated fields go at top level (extensibility)
            for k, v in cfg.items():
                # Do not let a stray nested provider section clobber normalized one
                if k == "mithril" and isinstance(v, dict):
                    # Merge any keys not already set
                    mithril_target = file_config.setdefault("mithril", {})
                    for mk, mv in v.items():
                        if mk not in mithril_target:
                            mithril_target[mk] = mv
                else:
                    file_config[k] = v

            # Finally, merge through any keys in existing config that the new
            # payload did not touch, to avoid accidental loss (e.g., project/region)
            for k, v in existing.items():
                if k == "mithril" and isinstance(v, dict):
                    tgt = file_config.setdefault("mithril", {})
                    for mk, mv in v.items():
                        if mk not in tgt:
                            tgt[mk] = mv
                else:
                    if k not in file_config:
                        file_config[k] = v
        else:
            # Legacy format - write as-is (copy) to avoid side effects
            file_config = cfg

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config file atomically
        self._write_config_file(file_config)

        # Credentials files are deprecated; do not write them

    def read_api_key(self, provider: str = "mithril") -> str | None:
        """Read API key from provider-specific credentials file.

        Args:
            provider: Provider name (defaults to mithril)

        Returns:
            API key if found, None otherwise
        """
        credentials_path = self.flow_dir / f"credentials.{provider}"
        if not credentials_path.exists():
            return None

        try:
            config = configparser.ConfigParser()
            config.read(credentials_path)
            return config.get("default", "api_key", fallback=None)
        except Exception:
            return None

    def _write_provider_credentials(self, provider: str, api_key: str) -> None:
        """Write provider-specific credentials file.

        Args:
            provider: Provider name (e.g., 'mithril', 'local')
            api_key: API key to store

        Raises:
            OSError: If unable to write file
        """
        credentials_path = self.flow_dir / f"credentials.{provider}"

        # Simple INI format
        config = configparser.ConfigParser()
        config.add_section("default")
        config.set("default", "api_key", api_key)

        # Write atomically
        with tempfile.NamedTemporaryFile(mode="w", dir=self.flow_dir, delete=False) as tmp:
            config.write(tmp)
            tmp_path = Path(tmp.name)

        # Set proper permissions
        try:
            tmp_path.chmod(0o600)
        except Exception:
            pass

        # Atomic rename
        try:
            tmp_path.replace(credentials_path)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

    def _write_config_file(self, config: dict[str, Any]) -> None:
        """Write config file atomically with proper permissions.

        Handles both legacy flat format and new provider-based format.

        Args:
            config: Configuration dictionary (without api_key)

        Raises:
            OSError: If unable to write file
        """
        # Write to temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", dir=self.config_path.parent, delete=False
        ) as tmp:
            yaml.dump(config, tmp, default_flow_style=False, sort_keys=False)
            tmp_path = Path(tmp.name)

        # Set proper permissions (0600 - read/write for owner only)
        try:
            tmp_path.chmod(0o600)
        except Exception:
            # Windows may not support chmod, continue anyway
            pass

        # Atomic rename
        try:
            tmp_path.replace(self.config_path)
        except Exception:
            # Clean up temp file on failure
            tmp_path.unlink(missing_ok=True)
            raise
