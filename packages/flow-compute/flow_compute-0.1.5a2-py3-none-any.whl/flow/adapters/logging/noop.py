from __future__ import annotations

from typing import Any

from flow.protocols.logging import LoggingProtocol


class NoopLogger(LoggingProtocol):
    """No-op logger implementing `LoggingProtocol`.

    Discards all log messages. Useful as a safe default in contexts where
    logging configuration is external or intentionally suppressed.
    """

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        return None

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        return None

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        return None

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        return None

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        return None
