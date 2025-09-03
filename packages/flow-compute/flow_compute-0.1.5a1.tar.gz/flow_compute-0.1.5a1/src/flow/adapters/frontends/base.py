from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)


class BaseFrontendAdapter(ABC):
    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initialized {name} frontend adapter")

    @abstractmethod
    async def parse_and_convert(self, input_data: Any, **options: Any) -> TaskConfig: ...

    def to_flow_task_config(self, task_config: TaskConfig) -> TaskConfig:
        return task_config

    @abstractmethod
    def format_job_id(self, flow_job_id: str) -> str: ...

    @abstractmethod
    def format_status(self, flow_status: str) -> str: ...
