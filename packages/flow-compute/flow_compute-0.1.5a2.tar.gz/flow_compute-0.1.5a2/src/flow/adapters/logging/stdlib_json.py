from __future__ import annotations

import json
import logging
import time

from flow.protocols.logging import LoggerProtocol


class JsonLogger(LoggerProtocol):
    """Stdlib logging adapter that emits structured JSON lines."""

    def __init__(self, name: str = "flow") -> None:
        self._log = logging.getLogger(name)

    def emit(self, event: str, **fields: object) -> None:
        record = dict(fields)
        record.setdefault("evt", event)
        record.setdefault("ts", time.time())
        try:
            self._log.info(json.dumps(record))
        except Exception:
            # Fallback to plain string on serialization failure
            self._log.info("%s %s", event, record)
