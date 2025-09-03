"""Script size handling for Mithril startup scripts.

Strategies for handling Mithril's 10KB startup script size limit through
compression, splitting, and external storage.
"""

from flow.adapters.providers.builtin.mithril.runtime.script_size.exceptions import (
    ScriptSizeError,
    ScriptTooLargeError,
)
from flow.adapters.providers.builtin.mithril.runtime.script_size.handler import ScriptSizeHandler
from flow.adapters.providers.builtin.mithril.runtime.script_size.models import PreparedScript
from flow.adapters.providers.builtin.mithril.runtime.script_size.strategies import (
    CompressionStrategy,
    InlineStrategy,
    ITransferStrategy,
    SplitStrategy,
)

__all__ = [
    "ScriptSizeHandler",
    "PreparedScript",
    "ITransferStrategy",
    "InlineStrategy",
    "CompressionStrategy",
    "SplitStrategy",
    "ScriptSizeError",
    "ScriptTooLargeError",
]
