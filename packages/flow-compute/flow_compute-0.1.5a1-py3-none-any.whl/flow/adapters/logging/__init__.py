from __future__ import annotations

from typing import Any

from flow.adapters.logging.noop import NoopLogger
from flow.adapters.logging.stdlib_json import JsonLogger
from flow.protocols.logging import LoggingProtocol


class StdlibJSONLogger(LoggingProtocol):
    def __init__(self, logger_name: str = __name__) -> None:
        import logging as _logging

        self._logger = _logging.getLogger(logger_name)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.exception(msg, *args, **kwargs)


__all__ = ["JsonLogger", "StdlibJSONLogger", "NoopLogger"]
