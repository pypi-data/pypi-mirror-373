from __future__ import annotations

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import (
    ensure_command_available,
    ensure_curl_available,
)


class GPUdHealthSection(ScriptSection):
    """Install and configure GPUd health monitoring for GPU instances.

    Template-only implementation to avoid inline heredocs in Python.
    """

    @property
    def name(self) -> str:
        return "gpud_health"

    @property
    def priority(self) -> int:
        return 55

    def should_include(self, context: ScriptContext) -> bool:
        # Centralized health gating when available; fallback to legacy env
        if hasattr(context, "health_enabled"):
            return context.has_gpu and bool(getattr(context, "health_enabled", False))
        # Legacy fallback
        health_enabled = (
            context.environment.get("FLOW_HEALTH_MONITORING", "false").lower() == "true"
        )
        return context.has_gpu and health_enabled

    def generate(self, context: ScriptContext) -> str:
        # Prefer centralized health config when present
        hc = getattr(context, "health", None) or {}
        gpud_version = str(
            hc.get("gpud_version") or context.environment.get("FLOW_GPUD_VERSION", "v0.5.1")
        )
        gpud_port = str(hc.get("gpud_port") or context.environment.get("FLOW_GPUD_PORT", "15132"))
        gpud_bind = str(
            hc.get("gpud_bind") or context.environment.get("FLOW_GPUD_BIND", "127.0.0.1")
        )

        metrics_endpoint = str(
            hc.get("metrics_endpoint") or context.environment.get("FLOW_METRICS_ENDPOINT", "")
        )
        metrics_interval = str(
            hc.get("metrics_interval") or context.environment.get("FLOW_METRICS_INTERVAL", "60")
        )
        metrics_auth_token = str(context.environment.get("FLOW_METRICS_AUTH_TOKEN", ""))
        metrics_batch_size = str(
            hc.get("metrics_batch_size") or context.environment.get("FLOW_METRICS_BATCH_SIZE", "10")
        )

        task_id = context.task_id or "unknown"
        task_name = context.task_name or "unknown"
        instance_type = context.instance_type or "unknown"

        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/gpud_health.sh.j2"),
                    {
                        "gpud_version": gpud_version,
                        "gpud_port": gpud_port,
                        "gpud_bind": gpud_bind,
                        "metrics_endpoint": metrics_endpoint,
                        "metrics_interval": metrics_interval,
                        "metrics_auth_token": metrics_auth_token,
                        "metrics_batch_size": metrics_batch_size,
                        "task_id": task_id,
                        "task_name": task_name,
                        "instance_type": instance_type,
                        "ensure_curl": ensure_curl_available(),
                        "ensure_python3": ensure_command_available("python3"),
                    },
                ).strip()
            except Exception:
                import logging as _log

                _log.debug(
                    "GPUdHealthSection: template render failed; skipping section", exc_info=True
                )
                return ""
        return ""

    def validate(self, context: ScriptContext) -> list[str]:
        errors: list[str] = []
        hc = getattr(context, "health", None) or {}
        port = str(hc.get("gpud_port") or context.environment.get("FLOW_GPUD_PORT", "15132"))
        try:
            port_num = int(port)
            if not 1 <= port_num <= 65535:
                errors.append(f"Invalid GPUd port: {port}")
        except ValueError:
            errors.append(f"GPUd port must be a number: {port}")

        endpoint = str(
            hc.get("metrics_endpoint") or context.environment.get("FLOW_METRICS_ENDPOINT", "")
        )
        if endpoint and not (endpoint.startswith("http://") or endpoint.startswith("https://")):
            errors.append("Metrics endpoint must be a valid HTTP(S) URL")

        return errors


__all__ = ["GPUdHealthSection"]
