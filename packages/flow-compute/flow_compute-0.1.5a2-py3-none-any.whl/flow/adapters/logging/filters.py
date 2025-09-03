from __future__ import annotations

import logging

from flow.utils.masking import mask_text


class RedactionFilter(logging.Filter):
    """Logging filter that redacts sensitive values in messages and args."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        try:
            if record.msg:
                record.msg = mask_text(str(record.msg))
            if record.args:
                record.args = tuple(mask_text(str(a)) for a in record.args)
        except Exception:
            pass
        return True
