from __future__ import annotations

from typing import Protocol

# Use a loose alias to avoid cross-layer imports in the ports package.
TaskConfig = object


class StartupProtocol(Protocol):
    """Startup script builder abstraction."""

    def build_startup_script(self, config: TaskConfig, **options: object) -> str: ...
