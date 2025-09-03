"""Demo mode utilities.

Centralized helpers to resolve and apply demo mode for the CLI. Ensures a
consistent banner and mode resolution across commands.
"""

from __future__ import annotations

import functools
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

_BANNER_SHOWN = False


def _truthy(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def is_demo_active() -> bool:
    """Return True if demo mode is active via env or config."""
    # Fast path: explicit env override
    if _truthy(os.environ.get("FLOW_DEMO_MODE")):
        return True
    if os.environ.get("FLOW_DEMO_MODE") == "0":
        # Explicitly disabled
        return False
    # Provider explicitly set to mock in env
    if (os.environ.get("FLOW_PROVIDER") or "").lower() == "mock":
        return True
    # Fallback: check config file provider when env not decisive
    try:
        from flow.application.config.manager import ConfigManager

        sources = ConfigManager().load_sources()
        return (sources.provider or "").lower() == "mock"
    except Exception:
        return False


def apply_demo_mode(demo: bool | None) -> bool:
    """Apply demo mode preference to environment and return resolved state.

    Precedence:
      - If demo is True/False: force that state for this process
      - Else, respect existing env (FLOW_DEMO_MODE / FLOW_PROVIDER)
      - Else, respect config provider (mock → demo active)
    """
    if demo is not None:
        # Explicit override per-invocation
        os.environ["FLOW_DEMO_MODE"] = "1" if demo else "0"
        return demo

    # No explicit flag: honor existing env/config
    active = is_demo_active()
    return active


def show_demo_banner_once() -> None:
    """Print a one-time banner indicating demo mode is active."""
    global _BANNER_SHOWN
    if _BANNER_SHOWN:
        return
    try:
        from flow.cli.utils.theme_manager import theme_manager

        if is_demo_active():
            console = theme_manager.create_console()
            try:
                from rich.panel import Panel as _Panel
            except Exception:
                _Panel = None  # type: ignore

            accent = theme_manager.get_color("accent")
            warn = theme_manager.get_color("warning")

            if _Panel is not None:
                body_lines = [
                    "[bold]Sandbox only — no real resources are created.[/bold]",
                    f"Provider: [{accent}]mock[/{accent}]",
                    f"Switch to real: [{accent}]flow init --provider mithril[/{accent}] or [{accent}]flow demo stop[/{accent}]",
                ]
                console.print(
                    _Panel(
                        "\n".join(body_lines),
                        title="[bold]DEMO MODE[/bold]",
                        border_style=warn,
                    )
                )
            else:
                console.print("[bold]DEMO MODE[/bold]")
                console.print("[bold]Sandbox only — no real resources are created.[/bold]")
                console.print("Provider: mock")
                console.print("Switch to real: flow init --provider mithril or flow demo stop")
            _BANNER_SHOWN = True
    except Exception:
        # Never fail CLI due to banner issues
        _BANNER_SHOWN = True


def load_persistent_demo_env() -> bool:
    """Load persisted demo environment from ~/.flow/demo.env into process env.

    Lines format: KEY=VALUE, supports # comments and blank lines.
    Does not overwrite keys already present in os.environ.
    Returns True if a file was loaded, False otherwise.
    """
    try:
        path = Path.home() / ".flow" / "demo.env"
        if not path.exists():
            return False
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            if key and key not in os.environ:
                os.environ[key] = val
        # Auto-resolve contradictions: if FLOW_PROVIDER is set explicitly and is not 'mock',
        # disable demo mode for this process to avoid leakage from persisted envs.
        try:
            provider = os.environ.get("FLOW_PROVIDER", "").strip().lower()
            if provider and provider != "mock":
                os.environ["FLOW_DEMO_MODE"] = "0"
        except Exception:
            pass
        return True
    except Exception:
        return False


def demo_aware_command(
    flag_param: str = "demo", show_banner: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to make a Click command demo-aware.

    - Resolves demo mode from the command's flag (if present), env, or config
    - Applies environment overrides before the command runs
    - Optionally prints a one-time banner
    """

    def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            explicit_demo = None
            if flag_param in kwargs:
                explicit_demo = kwargs.get(flag_param)

            # Respect an explicit provider argument by overriding any persisted demo env
            # for this process. If the provider is not 'mock', disable demo mode.
            try:
                provider_arg = kwargs.get("provider")
                if isinstance(provider_arg, str) and provider_arg.strip():
                    import os as _os

                    prov_lower = provider_arg.strip().lower()
                    _os.environ["FLOW_PROVIDER"] = provider_arg
                    if prov_lower != "mock":
                        _os.environ["FLOW_DEMO_MODE"] = "0"
                        # Inform users once when a persisted demo env exists, to avoid confusion
                        try:
                            from pathlib import Path as _Path

                            from flow.cli.utils.theme_manager import theme_manager as _tm

                            demo_env = _Path.home() / ".flow" / "demo.env"
                            if demo_env.exists():
                                console = _tm.create_console()
                                console.print(
                                    "[dim]Note: Found persisted demo env (~/.flow/demo.env). "
                                    "Using provider '" + provider_arg + "' for this session. "
                                    "Run 'flow demo stop' to disable demo mode for future sessions.[/dim]"
                                )
                        except Exception:
                            pass
            except Exception:
                pass

            active = apply_demo_mode(explicit_demo)
            # Suppress demo banner when command is emitting machine-readable output
            suppress_banner = kwargs.get("show", False) is True or kwargs.get("output_yaml", False)
            if show_banner and active and not suppress_banner:
                show_demo_banner_once()
            # Add a small initial delay in demo mode so progress/animations are visible
            if active and not suppress_banner:
                try:
                    # Skip when not a TTY or on CI to avoid slowing pipelines
                    if sys.stdout.isatty() and os.environ.get("CI", "").strip() == "":
                        # Configure via env; defaults chosen to be perceptible but snappy
                        base_ms = 0
                        try:
                            base_ms = int(os.environ.get("FLOW_MOCK_LATENCY_MS", "0") or 0)
                        except Exception:
                            base_ms = 0
                        raw_initial = os.environ.get("FLOW_MOCK_LATENCY_INITIAL_MS")
                        if raw_initial is not None and str(raw_initial).strip() != "":
                            try:
                                initial_ms = int(raw_initial)
                            except Exception:
                                initial_ms = 0
                        else:
                            # If a base latency is set, align the initial delay roughly with it (capped)
                            initial_ms = 200 if base_ms == 0 else max(150, min(400, base_ms))
                        if initial_ms > 0:
                            # Optional jitter aligned with global jitter pct
                            try:
                                jpct = float(
                                    os.environ.get("FLOW_MOCK_LATENCY_JITTER_PCT", "0") or 0.0
                                )
                            except Exception:
                                jpct = 0.0
                            if jpct > 0:
                                import random as _rand

                                delta = int(initial_ms * _rand.uniform(-jpct, jpct))
                                initial_ms = max(0, initial_ms + delta)
                            time.sleep(initial_ms / 1000.0)
                except Exception:
                    # Never impact command execution due to delay errors
                    pass
            return func(*args, **kwargs)

        return _wrapper

    return _decorator


def latency_ms(default: int = 0) -> int:
    """Get demo latency from env for mock operations."""
    try:
        return int(os.environ.get("FLOW_MOCK_LATENCY_MS", str(default)))
    except Exception:
        return default
