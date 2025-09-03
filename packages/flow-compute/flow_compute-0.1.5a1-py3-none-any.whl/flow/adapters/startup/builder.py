from __future__ import annotations

from flow.protocols.startup import StartupProtocol
from flow.sdk.models import TaskConfig


class AdapterStartupBuilder(StartupProtocol):
    """StartupProtocol implementation using existing Mithril builder.

    This provides a stable adapter location while generic sections are migrated
    under adapters/startup. For now it delegates to the Mithril builder which
    already supports generic scripts for non-containerized and containerized flows.
    """

    def __init__(self, builder: object | None = None, *, health_config: dict | None = None) -> None:
        if builder is None:
            # Lazy import to avoid heavy deps at import time
            from flow.adapters.providers.builtin.mithril.runtime.startup.builder import (
                StartupScriptBuilder as _SB,
            )

            builder = _SB()
        self._builder = builder
        # Pass centralized health config to the underlying builder when supported
        try:
            self._builder._health_config = health_config
        except Exception:
            pass

    def build(self, config: TaskConfig):
        """Build the structured startup script via the underlying builder.

        This adapter exposes a `.build()` method to maintain compatibility with
        callers that expect the Mithril `StartupScriptBuilder` interface.
        """
        # Delegate directly to the wrapped builder which returns a StartupScript
        return self._builder.build(config)

    def build_startup_script(self, config: TaskConfig, **options: object) -> str:
        # Keep StartupProtocol compatibility (string content), delegating to `.build()`
        script_obj = self.build(config)
        # Return raw content; compression decisions are handled inside builder
        return script_obj.content
