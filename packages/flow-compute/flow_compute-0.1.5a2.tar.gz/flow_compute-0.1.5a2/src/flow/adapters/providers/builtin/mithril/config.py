"""Production configuration for Mithril provider."""

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class MithrilScriptSizeConfig:
    """Configuration for script size handling in Mithril provider."""

    # Size limits
    max_script_size: int = 10_000
    safety_margin: int = 1_000

    # Feature flags
    enable_compression: bool = True
    enable_split_storage: bool = True
    enable_metrics: bool = True
    enable_health_checks: bool = True

    # Storage backend
    storage_backend: str = "local"  # "local" or "s3"
    storage_config: dict[str, Any] | None = None

    # Operational settings
    compression_level: int = 9
    max_retries: int = 3
    request_timeout_seconds: int = 30

    # Monitoring
    enable_detailed_logging: bool = False
    metrics_endpoint: str | None = None

    @classmethod
    def from_env(cls) -> "MithrilScriptSizeConfig":
        """Create configuration from environment variables and YAML (env > YAML)."""
        # Read YAML defaults via ConfigLoader; fall back silently on errors
        yaml_ss: dict[str, Any] = {}
        try:
            from flow.application.config.loader import ConfigLoader as _CL  # local import

            y = _CL().get_mithril_config()
            yaml_ss = y.get("script_size", {}) if isinstance(y, dict) else {}
        except Exception:
            yaml_ss = {}

        def _int(key: str, default_yaml: int, env_key: str | None = None) -> int:
            ek = env_key or key
            v = os.getenv(f"MITHRIL_{ek.upper()}")
            if v is not None and str(v).strip() != "":
                try:
                    return int(str(v).strip())
                except Exception:
                    pass
            try:
                return int(yaml_ss.get(key, default_yaml))
            except Exception:
                return default_yaml

        def _bool(key: str, default_yaml: bool, env_key: str | None = None) -> bool:
            ek = env_key or key
            v = os.getenv(f"MITHRIL_{ek.upper()}")
            if v is not None:
                return str(v).strip().lower() in {"1", "true", "yes", "on"}
            try:
                yv = yaml_ss.get(key)
                if isinstance(yv, bool):
                    return yv
                if isinstance(yv, str):
                    return yv.strip().lower() in {"1", "true", "yes", "on"}
            except Exception:
                pass
            return default_yaml

        return cls(
            # Size limits
            max_script_size=_int("max_script_size", 10000, "MAX_SCRIPT_SIZE"),
            safety_margin=_int("safety_margin", 1000, "SCRIPT_SAFETY_MARGIN"),
            # Feature flags
            enable_compression=_bool("enable_compression", True, "ENABLE_COMPRESSION"),
            enable_split_storage=_bool("enable_split_storage", True, "ENABLE_SPLIT_STORAGE"),
            enable_metrics=_bool("enable_metrics", True, "ENABLE_METRICS"),
            enable_health_checks=_bool("enable_health_checks", True, "ENABLE_HEALTH_CHECKS"),
            # Storage backend
            storage_backend=(
                os.getenv("MITHRIL_STORAGE_BACKEND")
                or str(yaml_ss.get("storage_backend") or "local")
            ),
            # Operational settings
            compression_level=_int("compression_level", 9, "COMPRESSION_LEVEL"),
            max_retries=_int("max_retries", 3, "MAX_RETRIES"),
            request_timeout_seconds=_int("request_timeout_seconds", 30, "REQUEST_TIMEOUT"),
            # Monitoring
            enable_detailed_logging=_bool("enable_detailed_logging", False, "DETAILED_LOGGING"),
            metrics_endpoint=(
                os.getenv("MITHRIL_METRICS_ENDPOINT") or yaml_ss.get("metrics_endpoint")
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for passing to handlers."""
        return {
            "max_script_size": self.max_script_size,
            "safety_margin": self.safety_margin,
            "enable_compression": self.enable_compression,
            "enable_split": self.enable_split_storage,
            "compression_level": self.compression_level,
            "max_compression_attempts": 1,
            "enable_metrics": self.enable_metrics,
            "enable_detailed_logging": self.enable_detailed_logging,
        }


@dataclass
class MithrilProviderConfig:
    """Complete configuration for Mithril provider."""

    # Core settings
    api_url: str = "https://api.mithril.ai"
    project: str | None = None
    region: str | None = None

    # Script size handling
    script_size: MithrilScriptSizeConfig = None

    # Operational settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    connection_pool_size: int = 50

    # Development settings
    debug_mode: bool = False
    dry_run: bool = False

    def __post_init__(self):
        if self.script_size is None:
            self.script_size = MithrilScriptSizeConfig.from_env()

    @classmethod
    def from_env(cls) -> "MithrilProviderConfig":
        """Create complete configuration from environment."""
        # Prefer centralized loader (env > YAML) for core provider fields
        api_url = os.getenv("MITHRIL_API_URL")
        project = os.getenv("MITHRIL_PROJECT")
        region = os.getenv("MITHRIL_REGION")
        if not (api_url and project and region):
            try:
                from flow.application.config.loader import ConfigLoader as _CL  # local import

                _cfg = _CL().get_mithril_config()
                api_url = api_url or _cfg.get("api_url") or "https://api.mithril.ai"
                project = project or _cfg.get("project")
                region = region or _cfg.get("region")
            except Exception:
                api_url = api_url or "https://api.mithril.ai"

        # Use loader for provider-level flags when env is absent
        yaml_flags: dict[str, Any] = {}
        try:
            from flow.application.config.loader import ConfigLoader as _CL  # local import

            yaml_flags = _CL().get_mithril_config()
        except Exception:
            yaml_flags = {}

        def _bool(key_env: str, key_yaml: str, default_yaml: bool | None = None) -> bool:
            v = os.getenv(key_env)
            if v is not None:
                return str(v).strip().lower() in {"1", "true", "yes", "on"}
            yv = yaml_flags.get(key_yaml)
            return bool(yv) if yv is not None else bool(default_yaml)

        def _int(key_env: str, key_yaml: str, default_yaml: int | None = None) -> int:
            v = os.getenv(key_env)
            if v is not None and str(v).strip() != "":
                try:
                    return int(str(v).strip())
                except Exception:
                    pass
            yv = yaml_flags.get(key_yaml)
            try:
                return (
                    int(yv)
                    if yv is not None
                    else int(default_yaml) if default_yaml is not None else 0
                )
            except Exception:
                return int(default_yaml) if default_yaml is not None else 0

        return cls(
            api_url=api_url or "https://api.mithril.ai",
            project=project,
            region=region,
            script_size=MithrilScriptSizeConfig.from_env(),
            enable_caching=_bool("MITHRIL_ENABLE_CACHING", "enable_caching", True),
            cache_ttl_seconds=_int("MITHRIL_CACHE_TTL", "cache_ttl_seconds", 300),
            connection_pool_size=_int("MITHRIL_CONNECTION_POOL_SIZE", "connection_pool_size", 50),
            debug_mode=_bool("MITHRIL_DEBUG", "debug_mode", False),
            dry_run=_bool("MITHRIL_DRY_RUN", "dry_run", False),
        )

    def validate(self):
        """Validate configuration."""
        if self.script_size.max_script_size <= 0:
            raise ValueError("max_script_size must be positive")

        if self.script_size.compression_level not in range(1, 10):
            raise ValueError("compression_level must be between 1 and 9")

        if self.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")

        if self.connection_pool_size <= 0:
            raise ValueError("connection_pool_size must be positive")


def get_mithril_config() -> MithrilProviderConfig:
    """Get validated Mithril configuration from environment."""
    config = MithrilProviderConfig.from_env()
    config.validate()
    return config
