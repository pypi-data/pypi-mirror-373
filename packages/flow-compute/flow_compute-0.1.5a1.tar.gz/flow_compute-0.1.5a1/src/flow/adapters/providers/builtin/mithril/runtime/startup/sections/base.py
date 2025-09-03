from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from flow.adapters.providers.builtin.mithril.core.constants import GPU_INSTANCE_PATTERNS
from flow.adapters.providers.builtin.mithril.runtime.startup.templates import ITemplateEngine

logger = logging.getLogger(__name__)


@dataclass
class ScriptContext:
    ports: list[int] | None = None
    volumes: list[dict[str, Any]] | None = None
    docker_image: str | None = None
    docker_command: list[str] | None = None
    user_script: str | None = None
    environment: dict[str, str] | None = None
    upload_code: bool = False
    code_archive: str | None = None
    instance_type: str | None = None
    enable_workload_resume: bool = True
    task_id: str | None = None
    task_name: str | None = None
    max_run_time_hours: float | None = None
    min_run_time_hours: float | None = None
    deadline_hours: float | None = None
    # Centralized health configuration (optional)
    health_enabled: bool = False
    health: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        self.ports = self.ports or []
        self.volumes = self.volumes or []
        self.environment = self.environment or {}

    @property
    def has_gpu(self) -> bool:
        if not self.instance_type:
            return False
        instance_lower = self.instance_type.lower()
        return any(pattern in instance_lower for pattern in GPU_INSTANCE_PATTERNS)


class IScriptSection(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def priority(self) -> int: ...

    def should_include(self, context: ScriptContext) -> bool: ...

    def generate(self, context: ScriptContext) -> str: ...

    def validate(self, context: ScriptContext) -> list[str]: ...


class ScriptSection(ABC):
    def __init__(self, template_engine: ITemplateEngine | None = None):
        self.template_engine = template_engine

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def priority(self) -> int:
        return 50

    def should_include(self, context: ScriptContext) -> bool:
        return bool(self.generate(context).strip())

    @abstractmethod
    def generate(self, context: ScriptContext) -> str: ...

    def validate(self, context: ScriptContext) -> list[str]:
        return []


__all__ = ["ScriptContext", "IScriptSection", "ScriptSection"]
