"""Safety guard for real provider provisioning.

Shows a clear, one-time confirmation banner on the first interactive run with a
real provider (anything other than 'mock') to prevent accidental spend.

Design goals:
- Centralized logic used by provisioning commands (run, dev, colab)
- Only triggers in interactive TTY sessions (never blocks CI/pipes)
- Persists an acknowledgment marker so subsequent runs do not re-prompt
- Displays pricing context derived from config and defaults
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from typing import Any as _Any

import click

from flow.cli.commands.base import console
from flow.cli.utils.theme_manager import theme_manager
from flow.domain.pricing import calculator as pricing_core

ACK_BASENAME = "ack_real_provider_v1"


def _get_ack_path() -> Path:
    return Path.home() / ".flow" / ACK_BASENAME


def _is_tty() -> bool:
    try:
        return sys.stdout.isatty() and sys.stdin.isatty()
    except Exception:
        return False


def _load_sources() -> _Any | None:
    try:
        from flow.cli.utils.lazy_imports import import_attr as _import_attr

        ConfigManager = _import_attr(
            "flow.application.config.manager", "ConfigManager", default=None
        )
        if ConfigManager:
            return ConfigManager().load_sources()
        return None
    except Exception:
        return None


def is_real_provider_active() -> bool:
    """Return True when the effective provider is not 'mock'."""
    prov = (os.environ.get("FLOW_PROVIDER") or "").strip().lower()
    if prov:
        return prov != "mock"
    sources = _load_sources()
    if not sources:
        # Default provider is mithril; treat as real
        return True
    return (sources.provider or "mithril").strip().lower() != "mock"


def has_acknowledged_real_provider() -> bool:
    """Check whether the user has acknowledged real-provider guard previously."""
    if os.environ.get("FLOW_SUPPRESS_REAL_PROVIDER_GUARD") in {"1", "true", "yes"}:
        return True
    try:
        return _get_ack_path().exists()
    except Exception:
        return False


def write_real_provider_ack() -> None:
    """Persist the acknowledgment marker."""
    try:
        p = _get_ack_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch(exist_ok=True)
    except Exception:
        # Non-fatal
        pass


def _estimate_hourly_limit(
    instance_type: str | None,
    priority: str | None,
    max_price_per_hour: float | None,
    num_instances: int,
) -> tuple[float | None, dict[str, Any]]:
    """Compute best-effort hourly limit prices and details.

    Returns (total_limit_per_hour, details_dict)
    """
    details: dict[str, Any] = {
        "priority": (priority or "med"),
        "num_instances": int(max(1, num_instances)),
    }
    if max_price_per_hour is not None:
        try:
            per_inst = float(max_price_per_hour)
            total = per_inst * details["num_instances"]
            details["source"] = "explicit"
            details["per_instance_limit"] = per_inst
            details["per_gpu_table"] = None
            return total, details
        except Exception:
            pass

    if not instance_type:
        return None, details

    try:
        from flow.resources import get_gpu_pricing as _get_pricing_data

        merged_table = pricing_core.get_pricing_table(
            overrides=_get_pricing_data().get("gpu_pricing", {})
        )
        per_inst = pricing_core.calculate_instance_price(
            instance_type, priority=(priority or "med"), pricing_table=merged_table
        )
        total = per_inst * details["num_instances"]
        details["source"] = "derived"
        details["per_instance_limit"] = per_inst
        details["per_gpu_table"] = merged_table
        return total, details
    except Exception:
        return None, details


def _render_guard_panel(
    instance_type: str | None,
    priority: str | None,
    max_price_per_hour: float | None,
    num_instances: int,
) -> None:
    """Print a high-contrast guard panel with pricing summary."""
    from rich.panel import Panel

    warn = theme_manager.get_color("warning")
    accent = theme_manager.get_color("accent")

    total_cap, details = _estimate_hourly_limit(
        instance_type=instance_type,
        priority=priority,
        max_price_per_hour=max_price_per_hour,
        num_instances=num_instances,
    )

    bullet = f"[{accent}]•[/{accent}]"

    lines: list[str] = []
    lines.append("[bold]This will launch real GPU instances on your provider.[/bold]")
    lines.append(
        "You will incur real charges once capacity is allocated. Spot capacity can be preempted."
    )
    if instance_type:
        lines.append(f"{bullet} Instance type: [accent]{instance_type}[/accent]")
    if priority:
        lines.append(f"{bullet} Priority: [accent]{(priority or 'med')}[/accent]")
    if num_instances and num_instances != 1:
        lines.append(f"{bullet} Instances: [accent]{num_instances}[/accent]")
    if max_price_per_hour is not None:
        lines.append(
            f"{bullet} Max price per instance: [accent]${max_price_per_hour:.2f}/hr[/accent] (explicit)"
        )
    else:
        try:
            # Per-instance derived limit
            per_inst = details.get("per_instance_limit")
            if isinstance(per_inst, (int, float)):
                lines.append(
                    f"{bullet} Derived limit per instance: [accent]${per_inst:.2f}/hr[/accent]"
                )
        except Exception:
            pass
    if isinstance(total_cap, (int, float)) and total_cap > 0:
        lines.append(
            f"{bullet} Estimated total hourly limit price: [accent]${total_cap:.2f}/hr[/accent]"
        )

    # Config path hint
    cfg_path = str((Path.home() / ".flow" / "config.yaml").resolve())
    lines.append(f"{bullet} Pricing overrides: edit [accent]{cfg_path}[/accent] under provider")

    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]REAL PROVIDER ACTIVE[/bold]",
            border_style=warn,
        )
    )


def ensure_real_provider_ack(
    *,
    instance_type: str | None,
    priority: str | None,
    max_price_per_hour: float | None,
    num_instances: int,
    auto_confirm: bool = False,
) -> bool:
    """Ensure the user acknowledges real-provider provisioning.

    Returns True if execution may proceed.
    """
    # Skip in non-interactive contexts and when explicitly suppressed
    if not is_real_provider_active():
        return True
    if has_acknowledged_real_provider():
        return True
    if os.environ.get("CI") or not _is_tty():
        # Non-interactive: do not block; allow proceed
        return True
    if auto_confirm:
        write_real_provider_ack()
        return True

    # Render panel and ask for confirmation
    _render_guard_panel(instance_type, priority, max_price_per_hour, num_instances)
    ok = click.confirm("\nProceed and acknowledge this warning?", default=False)
    if ok:
        write_real_provider_ack()
        return True
    return False
