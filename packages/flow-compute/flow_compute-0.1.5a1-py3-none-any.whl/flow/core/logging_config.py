"""Centralized logging initialization from YAML configuration.

This module loads a default logging configuration from `flow/resources/data/logging.yaml`
and applies it via `logging.config.dictConfig`. It is idempotent and safe to
call multiple times. Environment variables offer light customization:

- FLOW_LOGGING_CONFIG: Path to an alternative YAML config file
- FLOW_LOG_LEVEL: Override the `flow` logger level (e.g., DEBUG, INFO)
- FLOW_LOG_TO_FILE: If "1", enable rotating file handler (uses FLOW_LOG_FILE if set)
- FLOW_LOG_FILE: Path to the log file (default: ~/.flow/logs/flow.log)
- FLOW_LOG_JSON: If "1", switch console formatter to JSON

If YAML loading fails for any reason, we fall back to the legacy
`flow.utils.logging.configure_logging` behavior so the CLI remains usable.
"""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - yaml is a core dependency but guard anyway
    yaml = None  # type: ignore

try:
    from importlib.resources import files as _res_files
except Exception:  # Python <3.9 fallback is not needed here; we require 3.10+
    _res_files = None  # type: ignore


_INITIALIZED = False


def _ensure_log_dir(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _load_yaml_from_path(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is not available to load logging config")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_default_yaml_resource() -> dict[str, Any] | None:
    if _res_files is None:
        return None
    try:
        resource = _res_files("flow.resources.data") / "logging.yaml"
        if not resource.is_file():
            return None
        with resource.open("r", encoding="utf-8") as fh:
            if yaml is None:
                return None
            return yaml.safe_load(fh) or {}
    except Exception:
        return None


def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
    # Level override for `flow` logger
    level = os.environ.get("FLOW_LOG_LEVEL")
    if level:
        loggers = config.setdefault("loggers", {})
        flow_logger = loggers.setdefault("flow", {})
        flow_logger["level"] = level.upper()

    # Console formatter JSON toggle
    if os.environ.get("FLOW_LOG_JSON", "0") == "1":
        formatters = config.setdefault("formatters", {})
        if "json" in formatters:
            # Switch console handler to use json formatter when available
            handlers = config.setdefault("handlers", {})
            console = handlers.get("console")
            if isinstance(console, dict):
                console["formatter"] = "json"

    # Optional file logging
    enable_file = os.environ.get("FLOW_LOG_TO_FILE", "0") == "1" or bool(
        os.environ.get("FLOW_LOG_FILE")
    )
    if enable_file:
        handlers = config.setdefault("handlers", {})
        formatters = config.setdefault("formatters", {})
        if "plain" not in formatters and "json" in formatters:
            # Ensure there is at least one formatter
            formatters["plain"] = {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
            }
        log_file = Path(
            os.environ.get("FLOW_LOG_FILE", str(Path.home() / ".flow" / "logs" / "flow.log"))
        )
        _ensure_log_dir(log_file)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": os.environ.get("FLOW_LOG_LEVEL", "INFO").upper(),
            "formatter": handlers.get("console", {}).get("formatter", "plain"),
            "filename": str(log_file),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
        }
        # Attach file handler to `flow` logger if not already present
        loggers = config.setdefault("loggers", {})
        flow_logger = loggers.setdefault("flow", {})
        handler_list = flow_logger.setdefault("handlers", ["console"])  # type: ignore[assignment]
        if "file" not in handler_list:
            handler_list.append("file")

    return config


def initialize_logging(config_path: str | None = None, *, force: bool = False) -> None:
    """Initialize logging from YAML, with safe fallback.

    Args:
        config_path: Optional explicit path to YAML config.
        force: Re-apply configuration even if already initialized.
    """
    global _INITIALIZED
    if _INITIALIZED and not force:
        return

    # Resolve configuration source
    final_path: Path | None = None
    if not config_path:
        env_path = os.environ.get("FLOW_LOGGING_CONFIG")
        if env_path:
            final_path = Path(env_path).expanduser()
    else:
        final_path = Path(config_path).expanduser()

    config: dict[str, Any] | None = None

    try:
        if final_path and final_path.exists():
            config = _load_yaml_from_path(final_path)
        else:
            config = _load_default_yaml_resource()
    except Exception:
        config = None

    if not config:
        # Fallback to legacy env-driven initializer
        try:
            from flow.adapters.logging.json_formatter import configure_logging

            configure_logging(force=force)
            _INITIALIZED = True
            return
        except Exception:
            # As a last resort, leave default logging configuration in place
            _INITIALIZED = True
            return

    # Apply environment overrides and any dynamic adjustments
    config = _apply_env_overrides(config)

    # Ensure default root does not spam output; we primarily use `flow.*`
    config.setdefault("version", 1)
    config.setdefault("disable_existing_loggers", False)
    config.setdefault("root", {"level": "WARNING", "handlers": []})

    try:
        logging.config.dictConfig(config)  # type: ignore[arg-type]
        _INITIALIZED = True
    except Exception:
        # Never fail due to logging; fallback to legacy
        try:
            from flow.adapters.logging.json_formatter import configure_logging

            configure_logging(force=True)
        except Exception:
            pass
        _INITIALIZED = True
