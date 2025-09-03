"""SDK facade for health integrations (GPUd diagnostics and metrics storage).

Uses dynamic imports to avoid static SDK→adapters dependencies.
"""

from __future__ import annotations

import importlib


def _gpu_health_module():
    return importlib.import_module("flow.adapters.integrations.health.gpu_health_checker")


def _storage_module():
    return importlib.import_module("flow.adapters.integrations.health.storage")


# Expose classes by resolving dynamically at import time (no static import lines)
try:
    GPUdStatus = _gpu_health_module().GPUdStatus
    GPUdDiagnosis = _gpu_health_module().GPUdDiagnosis
    GPUdStatusDiagnoser = _gpu_health_module().GPUdStatusDiagnoser
    GPUInstanceDetector = _gpu_health_module().GPUInstanceDetector
    HealthCheckMessageHandler = _gpu_health_module().HealthCheckMessageHandler
    NodeHealthSnapshotFactory = _gpu_health_module().NodeHealthSnapshotFactory
    SSHConnectionHandler = _gpu_health_module().SSHConnectionHandler
    TaskAgeCalculator = _gpu_health_module().TaskAgeCalculator
except Exception:  # pragma: no cover - keep module importable even if health adapters missing
    GPUdStatus = object  # type: ignore
    GPUdDiagnosis = object  # type: ignore
    GPUdStatusDiagnoser = object  # type: ignore
    GPUInstanceDetector = object  # type: ignore
    HealthCheckMessageHandler = object  # type: ignore
    NodeHealthSnapshotFactory = object  # type: ignore
    SSHConnectionHandler = object  # type: ignore
    TaskAgeCalculator = object  # type: ignore

try:
    MetricsAggregator = _storage_module().MetricsAggregator
    MetricsStore = _storage_module().MetricsStore
except Exception:  # pragma: no cover
    MetricsAggregator = object  # type: ignore
    MetricsStore = object  # type: ignore
