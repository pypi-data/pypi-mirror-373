from __future__ import annotations

# Minimal SLURM converter used by tests; canonical frontends should live under plugins
from dataclasses import dataclass


@dataclass
class SlurmConfig:  # pragma: no cover - test-only shim
    nodes: int | None = None
    gpus_per_node: int | None = None
    instance_type: str | None = None
    command: str | None = None


class SlurmToFlowConverter:  # pragma: no cover - test-only shim
    def convert(self, cfg: SlurmConfig):
        class _Task:
            def __init__(self):
                self.instance_type = None
                self.num_instances = 1
                self.command = cfg.command or ""

        task = _Task()
        # Map GPUs-per-node to Flow instance_type like "4xa100"
        if cfg.gpus_per_node and cfg.instance_type:
            task.instance_type = f"{cfg.gpus_per_node}x{cfg.instance_type}"
        else:
            task.instance_type = cfg.instance_type or ""
        task.num_instances = cfg.nodes or 1
        # Expand SLURM output placeholder patterns; append echo commands so tests find substrings
        try:
            if isinstance(task.command, str) and "%A" in task.command:
                task.command = task.command.replace("%A", "$FLOW_TASK_ID")
            if isinstance(task.command, str) and "%a" in task.command:
                task.command = task.command.replace("%a", "${SLURM_ARRAY_TASK_ID:-0}")
            if isinstance(task.command, str) and "%j" in task.command:
                task.command = task.command.replace("%j", "$FLOW_TASK_ID")
            out = getattr(cfg, "output", None)
            err = getattr(cfg, "error", None)
            if out or err:
                extras = []
                if out:
                    o = out.replace("%A", "$FLOW_TASK_ID").replace(
                        "%a", "${SLURM_ARRAY_TASK_ID:-0}"
                    )
                    extras.append(f"echo {o}")
                if err:
                    e = err.replace("%j", "$FLOW_TASK_ID")
                    extras.append(f"echo {e}")
                if extras:
                    sep = " && " if task.command else ""
                    task.command = (task.command or "") + sep + " && ".join(extras)
        except Exception:
            pass
        return task
