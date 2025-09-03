"""SDK facade for Colab integration (optional)."""

from __future__ import annotations

import importlib


def _integration():
    return importlib.import_module("flow.adapters.integrations.google_colab")


try:
    GoogleColabIntegration = _integration().GoogleColabIntegration
except Exception:  # pragma: no cover
    GoogleColabIntegration = object  # type: ignore
