from __future__ import annotations

from typing import Protocol


class LoggingProtocol(Protocol):
    def debug(
        self, msg: str, *args: object, **kwargs: object
    ) -> None:  # pragma: no cover - protocol
        ...

    def info(
        self, msg: str, *args: object, **kwargs: object
    ) -> None:  # pragma: no cover - protocol
        ...

    def warning(
        self, msg: str, *args: object, **kwargs: object
    ) -> None:  # pragma: no cover - protocol
        ...

    def error(
        self, msg: str, *args: object, **kwargs: object
    ) -> None:  # pragma: no cover - protocol
        ...

    def exception(
        self, msg: str, *args: object, **kwargs: object
    ) -> None:  # pragma: no cover - protocol
        ...


class LoggerProtocol(Protocol):
    """Structured logging interface for emitting JSON-friendly events."""

    def emit(self, event: str, **fields: object) -> None: ...
