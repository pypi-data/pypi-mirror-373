from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)


class UserScriptSection(ScriptSection):
    @property
    def name(self) -> str:
        return "user_script"

    @property
    def priority(self) -> int:
        return 90

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.user_script and context.user_script.strip())

    def generate(self, context: ScriptContext) -> str:
        if not context.user_script or not context.user_script.strip():
            return ""
        script_content = context.user_script.strip()
        if not script_content.startswith("#!"):
            script_content = "#!/bin/bash\n" + script_content
        # Prefer template for user script wrapper; fallback to inline
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/user_script_wrapper.sh.j2"), {"script_content": script_content}
                ).strip()
            except Exception:
                import logging as _log

                _log.debug(
                    "UserScriptSection: template render failed; using inline wrapper", exc_info=True
                )
        return textwrap.dedent(
            f"""
            echo "Executing user startup script"
            cat > /tmp/user_startup.sh <<'USER_SCRIPT_EOF'
{script_content}
            USER_SCRIPT_EOF
            chmod +x /tmp/user_startup.sh
            /tmp/user_startup.sh
        """
        ).strip()


__all__ = ["UserScriptSection"]
