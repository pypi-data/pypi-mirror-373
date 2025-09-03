from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import ensure_docker_available


class DevVMDockerSection(ScriptSection):
    @property
    def name(self) -> str:
        return "dev_vm_docker"

    @property
    def priority(self) -> int:
        return 38

    def should_include(self, context: ScriptContext) -> bool:
        env = getattr(context, "environment", None)
        if not isinstance(env, dict):
            env = (
                getattr(context, "env_vars", {})
                if isinstance(getattr(context, "env_vars", None), dict)
                else {}
            )
        # Accept either explicit environment switch or a test-only is_dev_vm flag
        is_dev_vm_flag = bool(getattr(context, "is_dev_vm", False))
        has_image = bool(getattr(context, "docker_image", None))
        return has_image and (env.get("FLOW_DEV_VM") == "true" or is_dev_vm_flag)

    def generate(self, context: ScriptContext) -> str:
        return textwrap.dedent(
            f"""
            echo "Ensuring Docker is available on host for dev VM"
            {ensure_docker_available()}
            mkdir -p /home/persistent
            chmod 755 /home/persistent
            echo "Docker and persistent storage ready for dev VM"
        """
        ).strip()


__all__ = ["DevVMDockerSection"]
