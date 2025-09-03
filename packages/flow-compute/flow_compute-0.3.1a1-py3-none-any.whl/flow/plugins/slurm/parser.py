from __future__ import annotations

# Minimal parser shim used by tests
import re
from dataclasses import dataclass


@dataclass
class SlurmConfig:  # pragma: no cover - test-only shim
    nodes: int | None = None
    gpus_per_node: int | None = None
    instance_type: str | None = None
    constraint: str | None = None
    cpus_per_task: int | None = None
    output: str | None = None
    error: str | None = None
    command: str | None = None


def parse_sbatch_script(path: str) -> SlurmConfig:  # pragma: no cover
    text = open(path, encoding="utf-8").read()
    cfg = SlurmConfig()
    # nodes
    m = re.search(r"^#SBATCH\s+--nodes=(\d+)", text, re.MULTILINE)
    if m:
        cfg.nodes = int(m.group(1))
    # gpus-per-node format: model:count
    m = re.search(r"^#SBATCH\s+--gpus-per-node=([a-zA-Z0-9]+):(\d+)", text, re.MULTILINE)
    if m:
        cfg.instance_type = m.group(1)
        cfg.gpus_per_node = int(m.group(2))
    # cpus per task
    m = re.search(r"^#SBATCH\s+-c\s+(\d+)", text, re.MULTILINE)
    if m:
        cfg.cpus_per_task = int(m.group(1))
    # constraint stored as-is and also used as instance_type if not set
    m = re.search(r"^#SBATCH\s+-C\s+(\S+)", text, re.MULTILINE)
    if m:
        cfg.constraint = m.group(1)
        if not cfg.instance_type:
            cfg.instance_type = cfg.constraint
    # output/error placeholders
    m = re.search(r"^#SBATCH\s+--output=(\S+)", text, re.MULTILINE)
    if m:
        cfg.output = m.group(1)
    m = re.search(r"^#SBATCH\s+--error=(\S+)", text, re.MULTILINE)
    if m:
        cfg.error = m.group(1)
    # Command line (last non-comment)
    lines = [
        ln.rstrip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")
    ]
    cfg.command = lines[-1] if lines else ""
    return cfg


def parse_slurm_options(text: str) -> dict:  # pragma: no cover
    opts: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip().startswith("#SBATCH"):
            try:
                _, val = line.split(None, 1)
                if "=" in val:
                    k, v = val.split("=", 1)
                    opts[k.strip()] = v.strip()
            except Exception:
                continue
    return opts
