"""FinOps: pricing configuration and tiers.

Shows base per‑GPU tiers, your overrides, and per‑instance limit prices. Designed to be
simple by default for 90% of cases, with clear next steps.
"""

from __future__ import annotations

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.presentation.table_styles import create_flow_table, wrap_table_in_panel
from flow.cli.utils.telemetry import Telemetry
from flow.cli.utils.theme_manager import theme_manager
from flow.domain.pricing.insights import (
    DefaultsInsight,
    build_defaults_insight,
    per_instance_caps,
)
from flow.resources import get_gpu_pricing as get_pricing_data
from flow.utils.links import WebLinks


class FinOpsCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "finops"

    @property
    def help(self) -> str:
        return "Show pricing tiers, overrides, and per‑instance limit prices"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--gpu", help="Filter to a GPU (e.g., h100, a100)")
        @click.option(
            "--explain/--no-explain",
            default=False,
            help="Show where prices are set and how to change them",
        )
        def finops(gpu: str | None = None, explain: bool = False) -> None:
            try:
                Telemetry().log_event("finops_view_shown", {"gpu": gpu or ""})
            except Exception:
                pass

            # Header
            try:
                accent = theme_manager.get_color("accent")
                console.print(f"[bold {accent}]Flow FinOps[/bold {accent}]")
            except Exception:
                pass

            # Load base and overrides
            try:
                base_table = get_pricing_data()
            except Exception:
                base_table = {"default": {"low": 2.0, "med": 4.0, "high": 8.0}}

            overrides_table: dict[str, dict[str, float]] = {}
            user_config_path: str | None = None
            try:
                from pathlib import Path

                from flow.application.config.config import Config  # local import

                cfg = Config.from_env(require_auth=False)
                overrides_table = cfg.provider_config.get("limit_prices") or {}
                # Conventional config path for user clarity
                user_config_path = str(Path.home() / ".flow" / "config.yaml")
            except Exception:
                overrides_table = {}

            insight: DefaultsInsight = build_defaults_insight(
                base=base_table, overrides=overrides_table
            )

            # Build table (more compact, avoids wrapping)
            table = create_flow_table(title=None, show_borders=True, padding=1, expand=True)
            table.add_column("GPU", style=theme_manager.get_color("accent"), no_wrap=True)
            table.add_column("Low", justify="right")
            table.add_column("Med", justify="right")
            table.add_column("High", justify="right")
            # Show per-instance limit prices as separate columns to avoid long wrapped cells
            table.add_column("1x", justify="right", no_wrap=True)
            table.add_column("4x", justify="right", no_wrap=True)
            table.add_column("8x", justify="right", no_wrap=True)

            keys: list[str] = []
            preferred = [k for k in ("h100", "a100") if k in insight.table]
            keys = preferred + (["default"] if "default" in insight.table else [])
            if not keys:
                keys = sorted(insight.table.keys())
            if gpu:
                gk = gpu.lower()
                keys = [k for k in keys if k == gk]

            for g in keys:
                prices: dict[str, float] = insight.table.get(g, {})
                low = prices.get("low")
                med = prices.get("med")
                high = prices.get("high")
                c1 = c4 = c8 = "-"
                if isinstance(med, (int, float)):
                    caps_dict = per_instance_caps(float(med), [1, 4, 8])
                    c1 = f"${caps_dict[1]:.2f}"
                    c4 = f"${caps_dict[4]:.2f}"
                    c8 = f"${caps_dict[8]:.2f}"
                table.add_row(
                    g,
                    f"${low:.2f}/hr" if isinstance(low, (int, float)) else "-",
                    f"${med:.2f}/hr" if isinstance(med, (int, float)) else "-",
                    f"${high:.2f}/hr" if isinstance(high, (int, float)) else "-",
                    c1,
                    c4,
                    c8,
                )

            wrap_table_in_panel(table, "Per‑GPU tiers and per‑instance limit prices", console)

            # Overrides delta
            # Summarize overrides vs defaults and show clear instructions
            try:
                deltas: list[str] = []
                for g, tiers in (insight.overrides or {}).items():
                    for k in ("low", "med", "high"):
                        try:
                            b = float(insight.base.get(g, {}).get(k))
                            o = float(tiers.get(k))
                            if o != b:
                                sign = "+" if o > b else ""
                                deltas.append(f"{g} {k} {sign}{o - b:.2f}")
                        except Exception:
                            continue
                if deltas:
                    console.print(
                        "Overrides in effect: "
                        + ", ".join(deltas)
                        + "  [dim](~/.flow/config.yaml → mithril.limit_prices)[/dim]"
                    )
                else:
                    console.print(
                        "No overrides set. Using SDK defaults  "
                        + "[dim](packaged in flow.resources.data.pricing.json)[/dim]"
                    )
            except Exception:
                pass

            # Explain where and how to change prices (concise by default, detailed with --explain)
            try:
                precedence = "Precedence: CLI --max-price > YAML overrides (mithril.limit_prices) > SDK defaults"
                console.print(precedence)
                if explain:
                    cfg_path = user_config_path or "~/.flow/config.yaml"
                    snippet = (
                        "\n# ~/.flow/config.yaml\n"
                        "provider: mithril\n"
                        "mithril:\n"
                        "  # Per-GPU default prices (USD/hr)\n"
                        "  limit_prices:\n"
                        "    h100: {low: 4.0, med: 8.0, high: 16.0}\n"
                        "    a100: {low: 3.0, med: 6.0, high: 12.0}\n"
                        "    a10:  {low: 1.0, med: 2.0, high: 4.0}\n"
                    )
                    console.print(
                        f"\nTo change prices, edit {cfg_path} under 'mithril.limit_prices'.\n"
                        "Example:\n"
                    )
                    console.print(snippet)
            except Exception:
                pass

            console.print(
                f"Run with medium tier: flow run <task.yaml> -p med  •  Price chart: {WebLinks.price_chart()}"
            )

        return finops


command = FinOpsCommand()
