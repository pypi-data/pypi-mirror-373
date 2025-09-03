from __future__ import annotations

from pathlib import Path
from typing import Any

from flow.sdk.models import TaskConfig

from .parser import parse_sbatch_script
from .converter import SlurmToFlowConverter, SlurmConfig


class SlurmFrontendAdapter:
    """SLURM frontend adapter (plugins namespace).

    Provides a narrow API used by config loaders:
    - parse_and_convert(path, **overrides) -> TaskConfig
    - parse_array_job(path, **overrides) -> list[TaskConfig]
    """

    def __init__(self, name: str = "slurm") -> None:
        self.name = name
        self._converter = SlurmToFlowConverter()

    async def parse_and_convert(self, path: str | Path, **overrides: Any) -> TaskConfig:
        cfg = parse_sbatch_script(str(path))
        cfg = self._apply_overrides(cfg, overrides)
        # Convert to a minimal TaskConfig
        converted = self._converter.convert(cfg)
        return TaskConfig(
            name=getattr(converted, "name", None) or "slurm-job",
            command=["bash", "-lc", getattr(converted, "command", "")],
            instance_type=getattr(converted, "instance_type", ""),
            num_instances=int(getattr(converted, "num_instances", 1) or 1),
        )

    async def parse_array_job(self, path: str | Path, **overrides: Any) -> list[TaskConfig]:
        cfg = parse_sbatch_script(str(path))
        cfg = self._apply_overrides(cfg, overrides)
        # Determine array spec from script; if absent, return single config
        array_spec = getattr(cfg, "array", None)
        if not array_spec:
            single = await self.parse_and_convert(path, **overrides)
            return [single]
        indices = self._parse_array_spec(str(array_spec))
        base = await self.parse_and_convert(path, **overrides)
        # Return N copies with same base config; higher layers can add index envs
        return [base for _ in indices]

    @staticmethod
    def _parse_array_spec(spec: str) -> list[int]:
        indices: list[int] = []
        parts = (spec or "").split(",")
        for p in parts:
            p = p.strip()
            if not p:
                continue
            if "-" in p:
                rng, *step_bits = p.split(":", 1)
                start_str, end_str = rng.split("-", 1)
                try:
                    start = int(start_str)
                    end = int(end_str)
                    step = int(step_bits[0]) if step_bits else 1
                    for i in range(start, end + 1, max(1, step)):
                        indices.append(i)
                except Exception:
                    continue
            else:
                try:
                    indices.append(int(p))
                except Exception:
                    continue
        return indices

    def _apply_overrides(self, cfg: SlurmConfig, overrides: dict[str, Any]) -> SlurmConfig:
        # Apply simple overrides for GPU spec and nodes
        g = overrides.get("gpus")
        if isinstance(g, str):
            # Formats: "a100" or "a100:4"
            if ":" in g:
                gpu_type, count = g.split(":", 1)
                try:
                    cfg.instance_type = gpu_type
                    cfg.gpus_per_node = int(count)
                except Exception:
                    pass
            else:
                cfg.instance_type = g
        n = overrides.get("nodes")
        if isinstance(n, int) and n > 0:
            cfg.nodes = n
        return cfg
