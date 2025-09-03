from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from flow.sdk.models import TaskConfig


class YamlFrontendAdapter:
    """YAML frontend adapter (plugins namespace).

    Parses a YAML file into a ``TaskConfig``. Supports a minimal subset used by
    tests and CLI: name, command, instance_type, volumes, env, and other
    TaskConfig fields. Unknown keys are passed to the model where applicable.
    """

    def __init__(self, name: str = "yaml") -> None:
        self.name = name

    async def parse_and_convert(self, input_data: Any, **options: Any) -> TaskConfig:
        # input_data is expected to be a path to a YAML file
        path = Path(str(input_data))
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ValueError("YAML must be a mapping at the top level")

        # Apply any simple overrides (e.g., instance_type) passed by callers
        if options:
            data = {**data, **options}

        return TaskConfig(**data)

    def to_flow_task_config(self, task_config: TaskConfig) -> TaskConfig:
        return task_config
