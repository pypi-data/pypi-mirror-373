"""Exceptions for script size handling."""


class ScriptSizeError(Exception):
    """Base exception for script size handling errors."""

    pass


class ScriptTooLargeError(ScriptSizeError):
    """Raised when a script is too large for any available strategy."""

    def __init__(self, script_size: int, max_size: int, strategies_tried: list):
        self.script_size = script_size
        self.max_size = max_size
        self.strategies_tried = strategies_tried

        strategies_str = ", ".join(strategies_tried)
        super().__init__(
            f"Script size ({script_size:,} bytes) exceeds maximum supported size "
            f"({max_size:,} bytes) after trying strategies: {strategies_str}"
        )
