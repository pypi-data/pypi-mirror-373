"""Animated progress indicators for CLI operations.

Custom progress indicators with animated text, including dynamic ellipsis
animations for status messages.
"""

import os
import threading
import time
from datetime import datetime, timezone

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

from flow.cli.utils.animation_config import AnimationStyle
from flow.cli.utils.animations import animation_engine
from flow.resources.loader import DataLoader


class AnimatedEllipsisProgress:
    """Progress indicator with spinner and animated ellipsis.

    Creates a progress bar with rich's spinner and a message with
    cycling ellipsis animation (., .., ...).
    """

    def __init__(
        self,
        console: Console,
        message: str,
        transient: bool = True,
        animation_style: AnimationStyle | None = None,
        start_immediately: bool = False,
        estimated_seconds: int | None = None,
        show_progress_bar: bool = False,
        task_created_at: datetime | None = None,
        *,
        # Codex-style status line options (surgical, default-on)
        prefix: str | None = None,
        show_elapsed: bool = True,
        hint: str | None = None,
        # Visual padding before the status line
        pad_top: int | None = None,
    ):
        """Initialize animated progress.

        Args:
            console: Rich console instance
            message: Base message to display (without ellipsis)
            transient: Whether to clear progress when done
            animation_style: Type of text animation to use
            start_immediately: If True, start animation in __init__ for immediate feedback
            estimated_seconds: Estimated time in seconds for progress bar
            show_progress_bar: Whether to show filling progress bar
            task_created_at: Task creation time (for reconnecting to existing tasks)
            prefix: Leading glyph (defaults to themed bar)
            show_elapsed: Show elapsed seconds in status line
            hint: Right-side hint text (e.g., Ctrl+C)
            pad_top: Blank lines to print before the status line; default 1 or env FLOW_AEP_PAD_TOP
        """
        self.console = console
        self.base_message = message
        self.transient = transient
        # Top padding: default to env override or 1
        try:
            _env_pad = os.getenv("FLOW_AEP_PAD_TOP", "").strip()
            _env_pad_val = int(_env_pad) if _env_pad != "" else None
        except Exception:
            _env_pad_val = None
        self._pad_top: int = int(
            pad_top if pad_top is not None else (_env_pad_val if _env_pad_val is not None else 1)
        )
        self._pad_emitted = False
        # Resolve animation style and config from data files
        loader = DataLoader()
        # selection: request -> default from data (first style) -> fallback 'ellipsis'
        if animation_style is not None:
            self.animation_style = animation_style
        else:
            styles = loader.cli_animation.get("styles", {})
            self.animation_style = next(iter(styles.keys())) if styles else "ellipsis"  # type: ignore[assignment]
        style_cfg = loader.cli_animation.get("styles", {}).get(str(self.animation_style), {})
        # Provide defaults if file missing keys
        self.animation_config = type("_Cfg", (), {})()
        self.animation_config.duration = float(style_cfg.get("duration", 0.5))
        self.animation_config.intensity = float(style_cfg.get("intensity", 1.0))
        self._live: Live | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._ellipsis_count = 0
        # Track cadence for ellipsis updates using monotonic time
        self._last_ellipsis_ts = time.monotonic()
        # Lock for thread-safe message updates
        self._lock = threading.Lock()

        # Use task creation time if reconnecting, otherwise use current time
        if task_created_at:
            # Ensure timezone-aware comparison
            if task_created_at.tzinfo is None:
                task_created_at = task_created_at.replace(tzinfo=timezone.utc)
            self.start_time = task_created_at.timestamp()
        else:
            self.start_time = time.time()

        # Monotonic clock for animation/progress calculations
        self.start_time_monotonic = time.monotonic()

        self.estimated_seconds = estimated_seconds
        self.show_progress_bar = show_progress_bar and estimated_seconds is not None
        # Reset animation engine's start time for fresh animations (monotonic)
        animation_engine.start_time = time.monotonic()
        self._active = False
        self._started_immediately = False

        # Adaptive frame interval: keep high FPS for complex text effects
        self._frame_interval = 0.05 if self.animation_style in ("shimmer", "wave") else 0.08

        # --- Codex-style status line configuration ---
        # Feature toggle via env (default on). Any value in {"0","false","no"} disables.
        try:
            _env_toggle = str(os.getenv("FLOW_STATUS_LINE", "1")).strip().lower()
            self._status_line_enabled = _env_toggle not in {"0", "false", "no"}
        except Exception:
            self._status_line_enabled = True
        # Decide prefix with ASCII fallback
        self._ascii_only_prefix = False
        try:
            enc = getattr(self.console, "encoding", None)
            self._ascii_only_prefix = (
                (not enc) or ("UTF" not in str(enc).upper()) or os.getenv("FLOW_ASCII") == "1"
            )
        except Exception:
            self._ascii_only_prefix = False
        # Prefer simple "bar" look: heavy-left half block in Unicode; '|' in ASCII
        self._prefix_glyph = (
            prefix if prefix is not None else ("|" if self._ascii_only_prefix else "▌")
        ).strip()
        # Show elapsed seconds in status line
        self._show_elapsed = bool(show_elapsed)
        # Default hint (context-agnostic, safe everywhere)
        default_hint = "Ctrl+C cancel"
        try:
            _env_hint = os.getenv("FLOW_STATUS_HINT", "").strip()
        except Exception:
            _env_hint = ""
        self._hint = hint if hint is not None else (_env_hint or default_hint)

        # Start immediately if requested - provides instant feedback
        if start_immediately:
            self._start_immediate()

    def _emit_pad_if_needed(self) -> None:
        """Emit blank lines above the progress line exactly once."""
        if self._pad_top > 0 and not self._pad_emitted:
            try:
                for _ in range(self._pad_top):
                    self.console.print()
            except Exception:
                pass
            self._pad_emitted = True

    def _format_status_line(self, spinner: str, message: Text | str | None = None) -> Text:
        """Build a single-line, Codex-style status line with accent styling.

        Example: "▌ ⠏ Looking up… (7s • Ctrl+C cancel)".
        Applies theme accent to the leading bar and spinner for clearer affordance.
        """
        # Theme accent (best-effort; fall back to default)
        try:
            from flow.cli.utils.theme_manager import theme_manager as _tm_status

            # Allow overriding the AEP accent color to match a preferred variant
            _accent_override = (os.getenv("FLOW_AEP_COLOR", "") or "").strip()
            # Prefer theme's aep.accent for consistency across variants
            accent = (
                _accent_override
                or _tm_status.get_color("aep.accent")
                or _tm_status.get_color("accent")
            )
            muted = _tm_status.get_color("muted")
            default = _tm_status.get_color("default")
        except Exception:
            accent = (os.getenv("FLOW_AEP_COLOR", "") or "cyan").strip() or "cyan"
            muted = "bright_black"
            default = "white"

        # Choose message payload (may be styled Text)
        msg_payload: Text | str = self.base_message if message is None else message

        # Legacy, minimal formatting without status line
        if not self._status_line_enabled:
            t = Text(no_wrap=True, overflow="ellipsis")
            t.append(spinner, style=accent)
            t.append(" ")
            if isinstance(msg_payload, Text):
                # Preserve styling from animated Text
                t.append_text(msg_payload)
            else:
                t.append(msg_payload, style=default)
            return t

        # Bullet separator with ASCII fallback
        bullet = "-" if self._ascii_only_prefix else "•"

        # Compute elapsed seconds using monotonic clock
        try:
            elapsed_s = int(max(0, time.monotonic() - self.start_time_monotonic))
        except Exception:
            elapsed_s = 0

        # Compose styled line
        line = Text(no_wrap=True, overflow="ellipsis")
        # Prefix bar and spinner in accent
        line.append(self._prefix_glyph, style=accent)
        line.append(" ")
        line.append(spinner, style=accent)
        line.append(" ")
        # Message: preserve styling when a Text is provided
        if isinstance(msg_payload, Text):
            line.append_text(msg_payload)
        else:
            line.append(msg_payload, style=default)

        # Parenthetical suffix: (7s • Ctrl+C cancel)
        suffix_tokens: list[str] = []
        if self._show_elapsed:
            suffix_tokens.append(f"{elapsed_s}s")
        if self._hint:
            suffix_tokens.append(self._hint)
        if suffix_tokens:
            sep = f" {bullet} " if not self._ascii_only_prefix else " "
            suffix = f"({sep.join(suffix_tokens)})"
            line.append(" ")
            line.append(suffix, style=muted)

        return line

    def _animate(self) -> None:
        """Animation loop for updating display."""
        # Choose spinner set with ASCII fallback when needed
        ascii_only = False
        try:
            enc = getattr(self.console, "encoding", None)
            if not enc or "UTF" not in str(enc).upper() or os.getenv("FLOW_ASCII") == "1":
                ascii_only = True
        except Exception:
            ascii_only = False

        # Load spinner frames from data
        loader = DataLoader()
        spinners = loader.cli_animation.get("spinners", {})
        default = spinners.get("line", ["-", "|", "/", "-"])
        dots = spinners.get("dots", default)
        spinner_frames = default if ascii_only else dots

        while not self._stop_event.is_set():
            # Use monotonic time for animation stability
            elapsed_monotonic = time.monotonic() - self.start_time_monotonic

            # Get spinner frame
            spinner_phase = animation_engine.get_phase(0.8)
            spinner = animation_engine.get_spinner_frame(spinner_frames, spinner_phase)

            # Snapshot message under lock to avoid tearing mid-frame
            with self._lock:
                current_message = self.base_message

            # Show progress bar if enabled
            if self.show_progress_bar:
                # Calculate progress (cap at 95% to avoid false completion)
                progress_pct = min(elapsed_monotonic / self.estimated_seconds, 0.95)

                # Reuse existing progress_bar from animation_engine
                # Compact, responsive bar width
                bar_width = self._compute_bar_width()
                # Use square bracket caps to align with the blocky interior
                # Prefer high-fidelity unicode bar only when safe; fall back to ASCII otherwise
                use_unicode_bar = (not self._ascii_only_prefix) and os.getenv("FLOW_ASCII") != "1"
                # Prefer gradient style with theme accent in Unicode terminals
                bar_style = "gradient" if use_unicode_bar else "default"
                bar = animation_engine.progress_bar(
                    progress_pct,
                    width=bar_width,
                    style=bar_style,
                    animated=True,
                )

                # Format time display using wall clock (respects task_created_at)
                elapsed_wall = time.time() - self.start_time
                elapsed_str = f"{int(elapsed_wall)}s"
                estimate_str = f"{self.estimated_seconds}s"

                # Stack vertically: status line (spinner + message + elapsed/hint) then bar
                # Temporarily override base_message for status-line composition
                with self._lock:
                    self.base_message = current_message
                # Center status line to align visually with the centered bar below
                line1 = Align.center(self._format_status_line(spinner))

                # Accent the filled portion of the bar for better contrast
                try:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_acc

                    # Keep bar fill consistent with status line accent; allow override
                    accent = (
                        os.getenv("FLOW_AEP_COLOR", "")
                        or _tm_acc.get_color("aep.accent")
                        or _tm_acc.get_color("accent")
                        or "cyan"
                    ).strip()
                    filled8 = int(progress_pct * bar_width * 8)
                    full_blocks = filled8 // 8
                    partial = filled8 % 8
                    start = 1  # inside the leading '['
                    end = 1 + full_blocks + (1 if (partial > 0 and full_blocks < bar_width) else 0)
                    if end > start:
                        bar.stylize(accent, start, end)
                except Exception:
                    pass

                # Center the bar + time so it doesn't hang under the text
                # Add spaces around '/' and mute time text for balance
                try:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_time

                    time_style = _tm_time.get_color("muted")
                    bar_row = Text.assemble(bar, (f"  {elapsed_str} / {estimate_str}", time_style))
                except Exception:
                    bar_row = Text.assemble(bar, f"  {elapsed_str} / {estimate_str}")
                line2 = Align.center(bar_row)
                display = Group(line1, line2)

            elif self.animation_style == "ellipsis":
                # Classic ellipsis animation with time-based cadence
                now_mono = time.monotonic()
                if now_mono - self._last_ellipsis_ts >= self.animation_config.duration:
                    self._ellipsis_count = (self._ellipsis_count % 3) + 1
                    self._last_ellipsis_ts = now_mono
                dots = "." * self._ellipsis_count
                # Compose message with accent-tinted dots for clarity
                try:
                    from flow.cli.utils.theme_manager import (
                        theme_manager as _tm_ellipsis,
                    )

                    ellipsis_accent = _tm_ellipsis.get_color(
                        "aep.accent"
                    ) or _tm_ellipsis.get_color("accent")
                except Exception:
                    ellipsis_accent = "cyan"

                from rich.text import Text as _Text

                msg = _Text(current_message)
                if dots:
                    msg.append(dots, style=ellipsis_accent)
                display = self._format_status_line(spinner, msg)
            else:
                # Use rich animations - same as flow animations command
                phase = animation_engine.get_phase(duration=self.animation_config.duration)

                if self.animation_style == "wave":
                    animated_text = animation_engine.wave_pattern(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "pulse":
                    animated_text = animation_engine.pulse_effect(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "shimmer":
                    animated_text = animation_engine.shimmer_effect(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "bounce":
                    animated_text = animation_engine.bounce_effect(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                else:
                    animated_text = Text(current_message)

                # Display spinner + animated status line with animated text
                try:
                    # Avoid converting to str so we keep styling (shimmer/pulse)
                    display = self._format_status_line(spinner, animated_text)
                except Exception:
                    display = Text(f"{spinner} ") + animated_text

            if self._live and self._active:
                self._live.update(display)

            time.sleep(self._frame_interval)

    def _start_immediate(self):
        """Start animation immediately for instant feedback."""
        try:
            # Add spacing before the status line for visual separation
            self._emit_pad_if_needed()
            # TTY/CI-safe fallback: skip Live when not interactive
            prefer_no_anim = str(os.getenv("FLOW_NO_ANIMATION", "")).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            force_anim = str(os.getenv("FLOW_ANIMATE", "")).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            is_ci = bool(os.getenv("CI"))
            is_tty = bool(getattr(self.console, "is_terminal", True))
            if prefer_no_anim or ((is_ci or not is_tty) and not force_anim):
                # Show a static hint so users get feedback even without Live
                try:
                    # Static fallback: show a single status line without spinner
                    static_prefix = self._prefix_glyph if self._status_line_enabled else ""
                    hint = (
                        f" • {self._hint}"
                        if (
                            self._status_line_enabled and self._hint and not self._ascii_only_prefix
                        )
                        else (
                            f" - {self._hint}" if self._status_line_enabled and self._hint else ""
                        )
                    )
                    text = f"{static_prefix} {self.base_message}...{hint}".strip()
                    self.console.print(Text(text, overflow="crop"))
                except Exception:
                    pass
                self._live = None
                self._active = False
                self._started_immediately = True
                return
            self._live = Live(
                Text(""),  # Initial empty display
                console=self.console,
                refresh_per_second=20,
                transient=self.transient,
                redirect_stdout=True,
                redirect_stderr=True,
            )
            self._live.__enter__()
        except Exception as e:
            if "Only one live display may be active" in str(e):
                # There's already a Live display active, skip animation
                self._live = None
                self._active = False
                # Provide a static line in this case as well
                try:
                    self._emit_pad_if_needed()
                    static_prefix = self._prefix_glyph if self._status_line_enabled else ""
                    hint = (
                        f" • {self._hint}"
                        if (
                            self._status_line_enabled and self._hint and not self._ascii_only_prefix
                        )
                        else (
                            f" - {self._hint}" if self._status_line_enabled and self._hint else ""
                        )
                    )
                    text = f"{static_prefix} {self.base_message}...{hint}".strip()
                    self.console.print(Text(text, overflow="crop"))
                except Exception:
                    pass
                return
            raise

        if self._live:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self._active = True
        self._started_immediately = True

    def __enter__(self):
        """Start the animated display."""
        if self._started_immediately:
            # Already started, just return
            return self

        try:
            # Add spacing before the status line for visual separation
            self._emit_pad_if_needed()
            # TTY/CI-safe fallback: skip Live when not interactive
            prefer_no_anim = str(os.getenv("FLOW_NO_ANIMATION", "")).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            force_anim = str(os.getenv("FLOW_ANIMATE", "")).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            is_ci = bool(os.getenv("CI"))
            is_tty = bool(getattr(self.console, "is_terminal", True))
            if prefer_no_anim or ((is_ci or not is_tty) and not force_anim):
                self._live = None
                self._active = False
                # Ensure a static message is visible when animation is disabled
                try:
                    static_prefix = self._prefix_glyph if self._status_line_enabled else ""
                    hint = (
                        f" • {self._hint}"
                        if (
                            self._status_line_enabled and self._hint and not self._ascii_only_prefix
                        )
                        else (
                            f" - {self._hint}" if self._status_line_enabled and self._hint else ""
                        )
                    )
                    text = f"{static_prefix} {self.base_message}...{hint}".strip()
                    self.console.print(Text(text, overflow="crop"))
                except Exception:
                    pass
                return self
            self._live = Live(
                Text(""),  # Initial empty display
                console=self.console,
                refresh_per_second=20,
                transient=self.transient,
                redirect_stdout=True,
                redirect_stderr=True,
            )
            self._live.__enter__()
        except Exception as e:
            if "Only one live display may be active" in str(e):
                # There's already a Live display active, skip animation
                self._live = None
                self._active = False
                try:
                    self._emit_pad_if_needed()
                    static_prefix = self._prefix_glyph if self._status_line_enabled else ""
                    hint = (
                        f" • {self._hint}"
                        if (
                            self._status_line_enabled and self._hint and not self._ascii_only_prefix
                        )
                        else (
                            f" - {self._hint}" if self._status_line_enabled and self._hint else ""
                        )
                    )
                    text = f"{static_prefix} {self.base_message}...{hint}".strip()
                    self.console.print(Text(text, overflow="crop"))
                except Exception:
                    pass
                return self
            raise

        if self._live:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the animated display."""
        if not self._active:
            return  # Already stopped

        self._active = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)

    def update_message(self, new_message: str):
        """Update the progress message while animation is running.

        Args:
            new_message: New message to display
        """
        with self._lock:
            self.base_message = new_message

    # ----- sizing helpers -----
    def _get_console_width(self) -> int:
        try:
            if hasattr(self.console, "size") and self.console.size is not None:  # type: ignore[attr-defined]
                return int(self.console.size.width)  # type: ignore[attr-defined]
            if hasattr(self.console, "width"):
                return int(self.console.width)
        except Exception:
            pass
        return 80

    def _compute_bar_width(self) -> int:
        """Compute a compact progress bar width that doesn't hang under text.

        Rules:
        - Respect env override FLOW_STATUS_BAR_WIDTH when provided.
        - Default to ~22% of terminal width, clamped to [12, 24].
        """
        try:
            env_w = os.getenv("FLOW_STATUS_BAR_WIDTH")
            if env_w:
                w = max(6, min(60, int(env_w)))
                return w
        except Exception:
            pass

        cols = self._get_console_width()
        # 22% of current width, bounded for a tidy look
        w = int(cols * 0.22)
        if w < 12:
            w = 12
        if w > 24:
            w = 24
        return w
