"""SDK facade for code transfer (rsync/SSH-based)."""

from __future__ import annotations

import importlib
from typing import Any


class CodeTransferConfig:
    """Facade for adapter CodeTransferConfig."""

    def __init__(self, *args, **kwargs):
        mod = importlib.import_module("flow.adapters.transport.code_transfer")
        _Cfg = mod.CodeTransferConfig
        # Store impl for delegation; also copy repr-friendly attrs when present
        self._impl = _Cfg(*args, **kwargs)

    def __getattr__(self, item: str) -> Any:  # delegate attributes
        return getattr(self._impl, item)


class CodeTransferManager:
    """Facade for adapter CodeTransferManager."""

    def __init__(self, *args, **kwargs):
        mod = importlib.import_module("flow.adapters.transport.code_transfer")
        _Mgr = mod.CodeTransferManager
        self._impl = _Mgr(*args, **kwargs)

    def transfer_code_to_task(self, *args, **kwargs):
        return self._impl.transfer_code_to_task(*args, **kwargs)
