"""Centralized logging configuration for Flow.

Idempotent initializer that configures a parent `flow` logger so that all
`flow.*` child loggers propagate to it. This avoids touching the root logger
and prevents duplicate handlers while enabling consistent formatting.

Environment variables:
- FLOW_LOG_LEVEL: global log level (DEBUG, INFO, WARNING, ERROR). Default: WARNING
- FLOW_LOG_CONSOLE_LEVEL: console handler level. Default: same as FLOW_LOG_LEVEL
- FLOW_LOG_JSON: if "1", use JSON formatting. Default: "0"
- FLOW_LOG_TO_FILE: if "1", enable file logging. Default: "0"
- FLOW_LOG_FILE: path to log file (implies file logging enabled if set)
"""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_CONFIGURED = False


class JsonLogFormatter(logging.Formatter):
    """Simple JSON log formatter without external dependencies."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Add useful extras if present
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        payload["file"] = record.filename
        payload["line"] = record.lineno
        return json.dumps(payload, ensure_ascii=False)


def _parse_level(value: str | None, default: int) -> int:
    if not value:
        return default
    v = value.strip()
    # Numeric level
    if v.isdigit():
        try:
            return int(v)
        except Exception:
            return default
    # Named level
    return getattr(logging, v.upper(), default)


def configure_logging(force: bool = False) -> None:
    """Configure the `flow` logger exactly once.

    - Attaches console handler by default
    - Optionally attaches rotating file handler when enabled
    - Uses JSON or plain formatter based on env
    - Avoids mutating root logger to prevent host app interference
    """
    global _CONFIGURED
    if _CONFIGURED and not force:
        return

    logger = logging.getLogger("flow")

    # If already configured with handlers, avoid duplicate configuration
    if logger.handlers and not force:
        _CONFIGURED = True
        return

    # Resolve config via centralized runtime settings
    try:
        from flow.application.config.runtime import settings as _settings  # local import

        log_cfg = _settings.logging or {}
    except Exception:
        log_cfg = {}

    log_level = _parse_level(
        str(log_cfg.get("level")) if log_cfg.get("level") is not None else None, logging.WARNING
    )
    console_level = _parse_level(
        str(log_cfg.get("console_level")) if log_cfg.get("console_level") is not None else None,
        log_level,
    )
    use_json = bool(log_cfg.get("json", False))

    logger.setLevel(log_level)
    logger.propagate = False  # Child loggers under flow.* will stop at this logger

    # Formatter
    if use_json:
        formatter: logging.Formatter = JsonLogFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

    # Console handler to stderr
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file logging
    log_file_env = str(log_cfg.get("file")) if log_cfg.get("file") is not None else None
    enable_file = bool(log_cfg.get("to_file", False) or log_file_env)
    if enable_file:
        try:
            if log_file_env:
                log_path = Path(log_file_env).expanduser()
            else:
                log_path = Path.home() / ".flow" / "logs" / "flow.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # Never fail due to logging configuration issues
            pass

    _CONFIGURED = True
