"""Script preparation service.

Wraps startup script building and size/orchestration decisions into a simple
service used by the provider facade.
"""

from __future__ import annotations

from flow.adapters.providers.builtin.mithril.adapters.runtime import (
    MithrilStartupScriptBuilder,
    ScriptSizeHandler,
)
from flow.sdk.models import TaskConfig


class ScriptPreparationResult:
    def __init__(self, content: str, requires_network: bool) -> None:
        self.content = content
        self.requires_network = requires_network


class ScriptPreparationService:
    """Builds and prepares startup scripts for Mithril tasks."""

    def __init__(
        self,
        builder: MithrilStartupScriptBuilder,
        size_handler: ScriptSizeHandler,
    ) -> None:
        self._builder = builder
        self._size = size_handler

    def build_and_prepare(self, config: TaskConfig) -> ScriptPreparationResult:
        script_obj = self._builder.build(config)
        raw = script_obj.content
        prepared = self._size.prepare_script(raw)
        return ScriptPreparationResult(
            content=prepared.content, requires_network=prepared.requires_network
        )
