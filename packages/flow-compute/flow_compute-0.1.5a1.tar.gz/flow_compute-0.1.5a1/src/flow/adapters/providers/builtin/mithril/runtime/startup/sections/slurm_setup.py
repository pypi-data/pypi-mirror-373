from __future__ import annotations

from dataclasses import dataclass

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    IScriptSection,
    ScriptContext,
)


@dataclass
class SlurmSetupSection(IScriptSection):
    """Provision a Slurm controller+workers within a reservation.

    - Triggered only when `_FLOW_WITH_SLURM=1` is present in the environment
    - Assumes provider injects `_FLOW_MITHRIL_API_URL`, `_FLOW_MITHRIL_API_KEY`,
      `_FLOW_MITHRIL_PROJECT`, and `_FLOW_RESERVATION_ID` for rendezvous/peer discovery
    - Uses FLOW_NODE_RANK/FLOW_MAIN_IP from the rendezvous section if available;
      treats single-node reservations as leader-only
    """

    name: str = "slurm_setup"
    priority: int = 460  # After rendezvous (default ~450), before docker/user_script

    def should_include(self, context: ScriptContext) -> bool:
        env = context.environment or {}
        return env.get("_FLOW_WITH_SLURM") == "1"

    def validate(self, context: ScriptContext) -> list[str]:
        errors: list[str] = []
        # Hard requirements for provisioning
        env = context.environment or {}
        for key in ("_FLOW_MITHRIL_API_URL", "_FLOW_MITHRIL_API_KEY", "_FLOW_MITHRIL_PROJECT"):
            if not env.get(key):
                errors.append(f"Missing {key} in environment for Slurm provisioning")
        # Reservation ID is highly recommended for multi-node discovery
        # but we can proceed on single-node
        return errors

    def generate(self, context: ScriptContext) -> str:
        # Render shell via Jinja2 template
        return self.template_engine.render(
            "sections/slurm_setup.sh.j2",
            {
                "env": context.environment or {},
            },
        )
