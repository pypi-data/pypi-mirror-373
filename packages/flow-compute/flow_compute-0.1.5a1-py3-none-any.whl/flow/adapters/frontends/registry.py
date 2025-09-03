from __future__ import annotations

import warnings
from typing import ClassVar

from flow.adapters.frontends.base import BaseFrontendAdapter


class FrontendRegistry:
    _adapters: ClassVar[dict[str, type[BaseFrontendAdapter]]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(adapter_class: type[BaseFrontendAdapter]) -> type[BaseFrontendAdapter]:
            cls._adapters[name] = adapter_class
            return adapter_class

        return decorator

    @classmethod
    def get_adapter(cls, name: str) -> BaseFrontendAdapter:
        if name not in cls._adapters:
            raise ValueError(
                f"Unknown frontend: {name}. Available frontends: {list(cls._adapters.keys())}"
            )
        adapter_class = cls._adapters[name]
        warnings.warn(
            "flow.adapters.frontends is deprecated; frontends are moving under flow.plugins.*",
            DeprecationWarning,
            stacklevel=2,
        )
        return adapter_class(name=name)

    @classmethod
    def list_frontends(cls) -> list[str]:
        return list(cls._adapters.keys())

    @classmethod
    def clear(cls) -> None:
        cls._adapters.clear()
