from __future__ import annotations

from flow.adapters.providers.builtin.mithril.core.constants import (
    FLOW_LOG_DIR,
    MITHRIL_LOG_DIR,
    MITHRIL_STARTUP_LOG,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.origin import get_flow_origin_header
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import (
    ensure_install_pkgs_function,
)


class HeaderSection(ScriptSection):
    @property
    def name(self) -> str:
        return "header"

    @property
    def priority(self) -> int:
        return 10

    def should_include(self, context: ScriptContext) -> bool:
        return True

    def generate(self, context: ScriptContext) -> str:
        # Prefer template for header; inline fallback kept minimal
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/header.sh.j2"),
                    {
                        "flow_origin_header": get_flow_origin_header(),
                        "task_name": context.task_name if hasattr(context, "task_name") else "",
                        "flow_log_dir": FLOW_LOG_DIR,
                        "mithril_log_dir": MITHRIL_LOG_DIR,
                        "mithril_startup_log": MITHRIL_STARTUP_LOG,
                        # Keep header lean: include only install_pkgs function and a hint line
                        "ensure_basic_tools": ensure_install_pkgs_function()
                        + "\n# Ensure basic tools are available\n",
                    },
                ).strip()
            except Exception:
                import logging as _log

                _log.debug(
                    "HeaderSection: template render failed; using inline header", exc_info=True
                )
        return f"#!/bin/bash\n{get_flow_origin_header()}\nset -euxo pipefail"


__all__ = ["HeaderSection"]
