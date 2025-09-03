from __future__ import annotations

from pathlib import Path as _Path

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)


class RendezvousSection(ScriptSection):
    """Auto-rendezvous section for distributed jobs.

    Renders a lightweight discovery/bootstrap snippet that assigns ranks and
    leader IP when `FLOW_DISTRIBUTED_AUTO=1` is present. The rendered shell
    snippet is maintained as a Jinja template to avoid large inline heredocs
    in Python and to keep presentation separate from logic.
    """

    @property
    def name(self) -> str:
        return "rendezvous"

    @property
    def priority(self) -> int:
        # Must run before DockerSection (priority 40) so env is set prior to docker run
        return 39

    def should_include(self, context: ScriptContext) -> bool:
        # Only include when auto rendezvous is requested
        return context.environment.get("FLOW_DISTRIBUTED_AUTO", "0") == "1"

    def generate(self, context: ScriptContext) -> str:
        if getattr(self, "template_engine", None):
            try:
                return self.template_engine.render_file(
                    _Path("sections/rendezvous.sh.j2"), {}
                ).strip()
            except Exception:
                import logging as _log

                _log.debug(
                    "RendezvousSection: template render failed; skipping section", exc_info=True
                )
                return ""
        return ""

    def validate(self, context: ScriptContext) -> list[str]:
        return []


__all__ = ["RendezvousSection"]
