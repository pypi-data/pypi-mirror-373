"""Unified step timeline progress UI for CLI commands.

Provides a single, coherent live region that renders a compact list of steps,
with one active step at a time. Each step can optionally display a progress
bar when an estimated duration is available. Finished steps show a checkmark
and duration; failures show a cross and a short message.

This component is intentionally lightweight and self-contained so it can be
owned by one caller (e.g., `flow dev`) without conflicting with other Live
displays.
"""

from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass

from rich.console import Console
from rich.live import Live
from rich.text import Text

from flow.cli.utils.animations import animation_engine
from flow.cli.utils.theme_manager import theme_manager


@dataclass
class _Step:
    label: str
    show_bar: bool = False
    estimated_seconds: int | None = None
    status: str = "pending"  # pending | active | done | failed
    note: str = ""
    note_text: Text | None = None
    started_mono: float | None = None
    finished_mono: float | None = None
    last_percent: float | None = None
    last_speed: str | None = None
    last_eta: str | None = None
    # When resuming a wait step (e.g., SSH provisioning), seed the bar with prior elapsed seconds
    baseline_elapsed_seconds: int | None = None


class StepTimeline:
    """Render and control a multi-step timeline with minimal, tasteful UI.

    Adds tasteful animations for active labels and optional animated title using
    the centralized animation engine. Runs a lightweight render loop so that
    animations move even when no explicit progress updates are flowing.
    """

    def __init__(
        self,
        console: Console,
        title: str | None = None,
        *,
        enable_animations: bool = True,
        title_animation: str | None = None,  # "wave" | "pulse" | "shimmer" | None
        active_label_animation: str | None = "pulse",  # None to disable
    ):
        self.console = console
        self.title = title or ""
        self.steps: list[_Step] = []
        self._live: Live | None = None
        self._active_index: int | None = None
        # Minimum denominator to display (allows callers to stabilize N in "i/N")
        self._min_total: int = 0
        # Animation options
        self._enable_animations = enable_animations
        self._title_animation = title_animation
        self._active_label_animation = active_label_animation
        # Global environment overrides
        env_mode = os.getenv("FLOW_ANIMATIONS", "").strip().lower()
        # Respect simple output preference globally (calmer, non-animated)
        if os.getenv("FLOW_SIMPLE_OUTPUT", "").strip().lower() in {"1", "true", "yes"}:
            self._enable_animations = False
        if os.getenv("NO_COLOR"):
            self._enable_animations = False
        if env_mode in {"off", "0", "false", "disabled"}:
            self._enable_animations = False
        elif env_mode == "minimal":
            self._enable_animations = True
            # Keep spinner only; disable label/title animations
            self._title_animation = None
            self._active_label_animation = None
            # Slightly reduce cadence
            self._frame_interval = 0.1
        elif env_mode == "full":
            # Encourage richer animations if caller didn't explicitly set
            if self._title_animation is None:
                self._title_animation = "shimmer"
            if self._active_label_animation is None:
                self._active_label_animation = "wave"
        elif env_mode == "auto" or env_mode == "":
            # If caller didn't set explicit mode, enable auto
            if self._title_animation is None:
                self._title_animation = "auto"
            if self._active_label_animation is None:
                self._active_label_animation = "auto"
        # Animation cadence
        self._frame_interval = 0.08
        # Background render loop
        self._render_thread: threading.Thread | None = None
        self._stop_event: threading.Event | None = None
        # Prevent concurrent Live.update() from multiple threads
        self._render_lock: threading.Lock = threading.Lock()

    def add_step(
        self,
        label: str,
        *,
        show_bar: bool = False,
        estimated_seconds: int | None = None,
        baseline_elapsed_seconds: int | None = None,
    ) -> int:
        self.steps.append(
            _Step(
                label=label,
                show_bar=show_bar,
                estimated_seconds=estimated_seconds,
                baseline_elapsed_seconds=baseline_elapsed_seconds,
            )
        )
        return len(self.steps) - 1

    def start(self) -> None:
        if self._live is not None:
            return
        self._live = Live(Text(""), console=self.console, refresh_per_second=20, transient=True)
        self._live.__enter__()
        self._render()
        # Start lightweight render loop if animations are enabled
        if (
            self._enable_animations
            and getattr(self.console, "is_terminal", True)
            and not os.getenv("CI")
        ):
            self._stop_event = threading.Event()
            self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
            self._render_thread.start()

    def _render_loop(self) -> None:
        # Keep refreshing while live is active; only minimal work
        while self._live is not None and self._stop_event and not self._stop_event.is_set():
            has_active = self._active_index is not None
            if has_active or self._title_animation:
                # Re-render to advance spinner/animated text phases
                self._render()
            # Keep cadence light to avoid CPU burn
            time.sleep(self._frame_interval)

    def _format_bar(self, step: _Step) -> Text:
        if step.estimated_seconds and step.started_mono and step.status == "active":
            # Include baseline elapsed so bar resumes realistically, unless the baseline
            # dwarfs the estimate (e.g., very old instance age). In that case, anchor the
            # bar to the local session elapsed so the visual matches the displayed text.
            baseline = step.baseline_elapsed_seconds or 0
            elapsed = time.monotonic() - step.started_mono
            if baseline > (step.estimated_seconds or 0) * 2:
                pct = min(elapsed / step.estimated_seconds, 0.95)
            else:
                pct = min((baseline + elapsed) / step.estimated_seconds, 0.95)
        else:
            pct = step.last_percent if step.last_percent is not None else 0.0
        # Use gradient style with theme accent; add a subtle shimmer edge
        width = 28
        bar = animation_engine.progress_bar(pct, width=width, style="gradient", animated=True)
        # Ensure filled region uses theme accent (blue-ish) for clarity
        try:
            bar_color = (
                theme_manager.get_color("aep.accent") or theme_manager.get_color("accent") or "cyan"
            )
            # Compute filled region including the gradient edge block
            filled8 = int(pct * width * 8)
            full_blocks = filled8 // 8
            partial = filled8 % 8
            start = 1  # inside the leading '['
            end = 1 + full_blocks + (1 if (partial > 0 and full_blocks < width) else 0)
            if end > start:
                bar.stylize(bar_color, start, end)
        except Exception:
            pass
        # Compose status line pieces
        extra = []
        if step.estimated_seconds and step.started_mono:
            baseline = step.baseline_elapsed_seconds or 0
            wall = baseline + int(time.monotonic() - step.started_mono)

            # Format durations in human-friendly units and clamp display to estimate
            def _fmt(secs: int) -> str:
                try:
                    if secs < 90:
                        return f"{secs}s"
                    mins = secs // 60
                    if mins < 60:
                        return f"{mins}m"
                    hours = mins // 60
                    rem_m = mins % 60
                    return f"{hours}h {rem_m}m"
                except Exception:
                    return f"{secs}s"

            # When baseline (instance age) is very large, avoid showing inflated elapsed.
            # Show a simple session-local elapsed time instead, alongside the rough target.
            if wall > step.estimated_seconds * 2:
                local_only = int(time.monotonic() - step.started_mono)
                extra.append(f"{_fmt(local_only)} elapsed  ~{_fmt(int(step.estimated_seconds))}")
            else:
                shown_elapsed = min(wall, step.estimated_seconds)
                plus = "+" if wall > step.estimated_seconds else ""
                extra.append(
                    f"{_fmt(int(shown_elapsed))}{plus}/{_fmt(int(step.estimated_seconds))}"
                )
        if step.last_speed:
            extra.append(step.last_speed)
        if step.last_eta:
            extra.append(f"ETA {step.last_eta}")
        extra_text = ("  " + "  ".join(extra)) if extra else ""
        return Text.assemble("  ", bar, extra_text)

    def _format_line(self, idx: int, step: _Step) -> list[Text]:
        # Denominator reflects either the number of known steps or any reserved total
        total = max(len(self.steps), int(self._min_total or 0))
        prefix = f"{idx + 1}/{total} "
        lines: list[Text] = []

        if step.status == "pending":
            lines.append(Text(f"{prefix}[ ] {step.label}", style="dim"))
        elif step.status == "active":
            # ASCII-safe spinner selection
            ascii_only = False
            try:
                enc = getattr(self.console, "encoding", None)
                if not enc or "UTF" not in str(enc).upper() or os.getenv("FLOW_ASCII") == "1":
                    ascii_only = True
            except Exception:
                ascii_only = False
            spinner_frames = (
                animation_engine.SPINNERS["line"]
                if ascii_only
                else animation_engine.SPINNERS["dots"]
            )
            spinner_phase = animation_engine.get_phase(0.8)
            spinner = animation_engine.get_spinner_frame(spinner_frames, spinner_phase)

            # Animated active label (subtle)
            label_text = Text(step.label)
            chosen = self._select_active_label_animation(step)
            if chosen:
                phase = animation_engine.get_phase(1.6)
                if chosen == "wave":
                    label_text = animation_engine.wave_pattern(step.label, phase, intensity=0.6)
                elif chosen == "pulse":
                    label_text = animation_engine.pulse_effect(step.label, phase, intensity=0.7)
                elif chosen == "shimmer":
                    label_text = animation_engine.shimmer_effect(step.label, phase, intensity=0.5)

            accent = theme_manager.get_color("accent")
            header = Text(f"{prefix}") + Text(spinner, style=accent) + Text(" ") + label_text
            lines.append(header)
            if step.show_bar:
                lines.append(self._format_bar(step))
            if step.note_text is not None:
                lines.append(step.note_text)
        elif step.status == "done":
            # Duration display (human-friendly)
            dur = ""
            if step.started_mono and step.finished_mono:
                # Prefer showing wall-clock duration inclusive of any seeded baseline
                local_delta = int(step.finished_mono - step.started_mono)
                # Do NOT add baseline to the final duration to avoid confusing large values
                # when we seeded the bar with prior elapsed time (e.g., instance age).
                dur_secs = local_delta

                def _fmt(secs: int) -> str:
                    try:
                        if secs < 90:
                            return f"{secs}s"
                        mins = secs // 60
                        if mins < 60:
                            return f"{mins}m"
                        hours = mins // 60
                        rem_m = mins % 60
                        return f"{hours}h {rem_m}m"
                    except Exception:
                        return f"{secs}s"

                dur = f" ({_fmt(int(dur_secs))})"
            note = f" – {step.note}" if step.note else ""
            # Compose styled segments instead of markup so colors render in Live
            try:
                check_color = (
                    theme_manager.get_color("blue") or theme_manager.get_color("default") or "white"
                )
            except Exception:
                check_color = "white"
            line = Text(prefix) + Text("✓ ", style=check_color) + Text(f"{step.label}{dur}{note}")
            lines.append(line)
        else:  # failed
            note = f" – {step.note}" if step.note else ""
            from flow.cli.utils.theme_manager import theme_manager as _tm

            line = (
                Text(prefix)
                + Text("✗ ", style=_tm.get_color("error"))
                + Text(f"{step.label}{note}")
            )
            lines.append(line)

        return lines

    def _render(self) -> None:
        parts: list[Text] = []
        if self.title:
            chosen_title_anim = None
            if self._title_animation and self._enable_animations:
                if self._title_animation == "auto":
                    # Titles default to subtle shimmer for tasteful motion
                    chosen_title_anim = "shimmer"
                elif self._title_animation == "random":
                    # Avoid playful bounce for headers
                    chosen_title_anim = random.choice(["wave", "pulse", "shimmer"])
                else:
                    chosen_title_anim = self._title_animation
            if chosen_title_anim:
                phase = animation_engine.get_phase(2.4)
                if chosen_title_anim == "wave":
                    parts.append(animation_engine.wave_pattern(self.title, phase, intensity=0.5))
                elif chosen_title_anim == "pulse":
                    parts.append(animation_engine.pulse_effect(self.title, phase, intensity=0.6))
                elif chosen_title_anim == "shimmer":
                    parts.append(animation_engine.shimmer_effect(self.title, phase, intensity=0.5))
                else:
                    parts.append(Text(self.title))
            else:
                parts.append(Text(self.title))
        for i, step in enumerate(self.steps):
            for line in self._format_line(i, step):
                parts.append(line)
        display = Text("\n").join(parts) if parts else Text("")
        if self._live:
            # Guard Live.update from concurrent access by the background loop
            with self._render_lock:
                self._live.update(display)

    # Public refresh method to avoid reaching into private internals
    def refresh(self) -> None:
        self._render()

    def start_step(self, index: int) -> None:
        self._active_index = index
        step = self.steps[index]
        step.status = "active"
        step.started_mono = time.monotonic()
        self._render()

    def update_active(
        self,
        *,
        percent: float | None = None,
        speed: str | None = None,
        eta: str | None = None,
        message: str | None = None,
    ) -> None:
        if self._active_index is None:
            return
        step = self.steps[self._active_index]
        if percent is not None:
            # Keep within [0, 0.99] to avoid looking finished prematurely
            clamped = max(0.0, min(percent, 0.99))
            step.last_percent = clamped
        if speed is not None:
            step.last_speed = speed
        if eta is not None:
            step.last_eta = eta
        if message:
            # Augment label temporarily for extra context
            step.note = message
        self._render()

    def set_active_hint_text(self, text: Text) -> None:
        """Set a rich hint Text under the active step."""
        if self._active_index is None:
            return
        step = self.steps[self._active_index]
        step.note_text = text
        self._render()

    def complete_step(self, note: str | None = None) -> None:
        if self._active_index is None:
            return
        idx = self._active_index
        step = self.steps[idx]
        step.status = "done"
        step.finished_mono = time.monotonic()
        if note:
            step.note = note
        self._active_index = None
        self._render()

    def fail_step(self, message: str) -> None:
        if self._active_index is None:
            return
        step = self.steps[self._active_index]
        step.status = "failed"
        step.note = message
        self._active_index = None
        self._render()

    def finish(self) -> None:
        if self._live is None:
            return
        # Ensure no step remains marked active
        self._active_index = None
        # Final render without spinners/bars
        self._render()
        # Stop render loop first
        if self._stop_event is not None:
            self._stop_event.set()
        if self._render_thread is not None:
            try:
                self._render_thread.join(timeout=1.0)
                # If thread is still alive, try a short extra wait once more to ensure cleanup
                if self._render_thread.is_alive():
                    self._render_thread.join(timeout=0.5)
            except Exception:
                pass
        self._live.__exit__(None, None, None)
        self._live = None

    # Convenience to update title dynamically
    def set_title(self, title: str, *, animation: str | None = None) -> None:
        self.title = title
        if animation is not None:
            self._title_animation = animation
        self._render()

    # Allow callers to reserve a denominator so counts don't jump 1/1 → 2/2 → 3/3.
    # Uses a floor so the denominator can still grow if more steps are later discovered.
    def reserve_total(self, count: int) -> None:
        try:
            c = int(count or 0)
        except Exception:
            c = 0
        if c > self._min_total:
            self._min_total = c
            self._render()

    # Heuristic selection for active label animation
    def _select_active_label_animation(self, step: _Step) -> str | None:
        if not self._enable_animations:
            return None
        choice = self._active_label_animation
        if choice is None:
            return None
        if choice == "auto":
            # For long-running steps with a bar, prefer pulse; for short ones skip
            if step.show_bar and step.estimated_seconds:
                if step.estimated_seconds >= 120:
                    return "pulse"
                if step.estimated_seconds >= 30:
                    return "wave"
                return None
            # Non-bar steps are usually brief (e.g., Connecting); mild pulse
            return "pulse"
        if choice == "random":
            # Pick from subtle set to avoid playful bounce on labels
            return random.choice(["pulse", "wave", "shimmer"])
        return choice


class AllocationProgressAdapter:
    """Adapter to update the timeline during instance allocation."""

    def __init__(self, timeline: StepTimeline, step_index: int, estimated_seconds: int = 120):
        self.timeline = timeline
        self.step_index = step_index
        self.estimated_seconds = estimated_seconds
        self._start = None

    def __enter__(self):
        self.timeline.start_step(self.step_index)
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            self.timeline.complete_step()
        else:
            self.timeline.fail_step(str(exc))

    def tick(self):
        if self._start is None:
            return
        elapsed = time.monotonic() - self._start
        pct = min(elapsed / self.estimated_seconds, 0.95)
        self.timeline.update_active(percent=pct)


class SSHWaitProgressAdapter:
    """Adapter to update the timeline during SSH readiness wait."""

    def __init__(
        self,
        timeline: StepTimeline,
        step_index: int,
        estimated_seconds: int,
        baseline_elapsed_seconds: int | None = None,
    ):
        self.timeline = timeline
        self.step_index = step_index
        self.estimated_seconds = estimated_seconds
        self.baseline_elapsed_seconds = baseline_elapsed_seconds
        self._start = None

    def __enter__(self):
        self.timeline.start_step(self.step_index)
        # If provided, seed this step with a baseline elapsed so the bar resumes correctly
        try:
            step = self.timeline.steps[self.step_index]
            step.baseline_elapsed_seconds = self.baseline_elapsed_seconds
        except Exception:
            pass
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            self.timeline.complete_step()
        else:
            self.timeline.fail_step(str(exc))

    def update_eta(self, eta: str | None = None):
        if self._start is None:
            return
        base = self.baseline_elapsed_seconds or 0
        elapsed = time.monotonic() - self._start
        # Mirror bar logic for consistency, though provisioning steps now hide the bar.
        if base > (self.estimated_seconds or 0) * 2:
            pct = min(elapsed / self.estimated_seconds, 0.95)
            shown_elapsed = int(elapsed)
        else:
            pct = min((base + elapsed) / self.estimated_seconds, 0.95)
            shown_elapsed = int(base + elapsed)
        self.timeline.update_active(percent=pct, eta=eta)

        # Keep any hint set by the caller (e.g., Ctrl+C guidance + concise context).


class UploadProgressReporter:
    """Bridge reporter that maps code transfer progress to the timeline."""

    def __init__(self, timeline: StepTimeline, step_index: int, on_start: callable | None = None):
        self.timeline = timeline
        self.step_index = step_index
        self._entered = False
        # Optional callback fired when transfer starts (after step becomes active)
        self._on_start = on_start

    def invoke_on_start(self) -> None:
        if callable(self._on_start):
            try:
                self._on_start()
            except Exception:
                pass

    def ensure_started(self) -> None:
        """Public API used by context helpers to start timeline step once."""
        if not self._entered:
            self.timeline.start_step(self.step_index)
            self._entered = True

    # Matches IProgressReporter, but we deliberately avoid importing it to prevent tight coupling
    def ssh_wait_progress(self, message: str):
        class _Ctx:
            def __init__(self, outer: UploadProgressReporter):
                self.outer = outer

            def __enter__(self):
                self.outer.ensure_started()
                self.outer.invoke_on_start()
                return self.outer

            def __exit__(self, exc_type, exc, tb):
                # Do not complete here; let transfer_progress complete
                return False

        return _Ctx(self)

    def transfer_progress(self, message: str):
        class _Ctx:
            def __init__(self, outer: UploadProgressReporter):
                self.outer = outer

            def __enter__(self):
                self.outer.ensure_started()
                return self.outer

            def __exit__(self, exc_type, exc, tb):
                if exc is None:
                    self.outer.timeline.complete_step()
                else:
                    self.outer.timeline.fail_step(str(exc))
                return False

        return _Ctx(self)

    def update_status(self, message: str) -> None:
        # Map to a subtle note; avoid excessive churn
        self.timeline.update_active(message=message)

    # Extended hook used when available by transfer manager
    def update_transfer(
        self, percentage: float | None, speed: str | None, eta: str | None, current_file: str | None
    ):
        note = None
        if current_file:
            note = f"Uploading: {current_file}"
        # Smoothly adopt real progress while keeping the visual continuous
        try:
            step = self.timeline.steps[self.step_index]
            if step.started_mono is not None and percentage is not None:
                # Estimate total seconds from elapsed/progress and smooth the bar continuity
                elapsed = max(0.0, float(__import__("time").monotonic() - step.started_mono))
                frac = max(0.001, float(percentage) / 100.0)
                new_total = max(elapsed / frac, elapsed + 1.0)
                # Compute current visual percent under existing estimate
                if step.estimated_seconds:
                    base = float(step.baseline_elapsed_seconds or 0)
                    current_pct = min((base + elapsed) / float(step.estimated_seconds), 0.95)
                else:
                    current_pct = min(elapsed / max(new_total, 1.0), 0.95)
                # Choose a baseline that preserves current_pct after we swap estimate
                new_base = max(0.0, current_pct * new_total - elapsed)
                step.baseline_elapsed_seconds = int(new_base)
                step.estimated_seconds = int(new_total)
        except Exception:
            # Best-effort smoothing only
            pass

        self.timeline.update_active(
            percent=(percentage / 100.0) if percentage is not None else None,
            speed=speed,
            eta=eta,
            message=note,
        )
        # Anchor the time-based progress bar to real transfer timing when possible.
        # If we receive a percentage and have an elapsed time, infer the expected
        # total duration so the time-driven bar matches actual progress.
        try:
            step = self.timeline.steps[self.step_index]
            if step.started_mono is not None:
                elapsed = time.monotonic() - step.started_mono
                if percentage is not None and percentage > 0:
                    frac = max(0.001, float(percentage) / 100.0)
                    expected_total = max(elapsed / frac, elapsed + 1.0)
                    step.estimated_seconds = int(expected_total)
                elif eta:
                    # Fallback to ETA when percentage is unavailable
                    try:
                        parts = [int(p) for p in str(eta).split(":")]
                        if len(parts) == 3:
                            eta_secs = parts[0] * 3600 + parts[1] * 60 + parts[2]
                        elif len(parts) == 2:
                            eta_secs = parts[0] * 60 + parts[1]
                        else:
                            eta_secs = int(parts[0])
                    except Exception:
                        eta_secs = None
                    if eta_secs and eta_secs > 0:
                        step.estimated_seconds = int(elapsed + eta_secs)
        except Exception:
            # Best-effort only; never allow progress rendering to raise
            pass

    # New: allow callers to annotate the completed step with a short note
    def set_completion_note(self, note: str) -> None:
        try:
            step = self.timeline.steps[self.step_index]
            step.note = note
            # Re-render so the note appears under the completed step
            self.timeline.refresh()
        except Exception:
            # Best-effort; never fail UX for note rendering
            pass

    # Provide a way for strategies to seed a realistic ETA before progress lines start
    def seed_estimated_seconds(self, seconds: int) -> None:
        try:
            step = self.timeline.steps[self.step_index]
            if not seconds or seconds <= 0:
                return
            # Smooth the transition: preserve current visual percentage if possible
            import time as _time

            if step.started_mono is not None and step.estimated_seconds:
                elapsed = max(0.0, float(_time.monotonic() - step.started_mono))
                base = float(step.baseline_elapsed_seconds or 0)
                current_pct = min((base + elapsed) / float(step.estimated_seconds), 0.95)
                new_base = max(0.0, current_pct * float(seconds) - elapsed)
                step.baseline_elapsed_seconds = int(new_base)
            step.estimated_seconds = int(seconds)
            self.timeline.refresh()
        except Exception:
            pass


class NullConsole:
    """Console that discards prints to avoid duplicate provider messages."""

    def print(self, *_args, **_kwargs):
        return None


# Shared hint builders for consistent Ctrl+C/resume and dashboard/watch copy
def build_wait_hints(
    subject: str,
    resume_command: str,
    *,
    include_watch_dashboard: bool = True,
    extra_action: tuple[str, str] | None = None,
) -> Text:
    """Build a two-line hint block for long waits.

    Line 1: "Ctrl+C to exit; {subject} continues. Resume: {resume_command}"
            Optionally: "  •  {extra_label}{extra_command}"
    Line 2 (optional): "Watch live: flow status -w  •  Dashboard"

    Args:
        subject: Noun describing what continues (e.g., "VM", "job", "instance").
        resume_command: Command users should run to resume.
        include_watch_dashboard: Whether to include the second line.
        extra_action: Optional tuple (label, command) appended after a separator on line 1,
                      e.g., ("Upload later: ", "flow upload-code").

    Returns:
        Rich Text object with styles applied.
    """
    try:
        accent = theme_manager.get_color("accent")
    except Exception:
        accent = "cyan"

    hint = Text()

    # Line 1: Ctrl+C + resume
    hint.append("  ")
    hint.append("Ctrl+C", style=accent)
    hint.append(" to exit; ")
    hint.append(f"{subject} continues. Resume: ")
    hint.append(resume_command, style=accent)

    if extra_action and isinstance(extra_action, tuple) and len(extra_action) == 2:
        label, command = extra_action
        hint.append("  •  ")
        hint.append(label)
        hint.append(command, style=accent)

    if include_watch_dashboard:
        # Line break
        hint.append("\n")

        # Line 2: Watch + Dashboard
        hint.append("  Watch live: ")
        hint.append("flow status -w", style=accent)
        hint.append("  •  ")

        # Prefer hyperlink style when supported by Rich
        base_url = None
        try:
            # Ask active provider for base URL if available
            from flow.sdk.client import Flow as _Flow

            _flow = _Flow()
            _provider = getattr(_flow, "provider", None)
            base_url = getattr(_provider, "get_web_base_url", lambda: None)() if _provider else None
        except Exception:
            base_url = None
        if not base_url:
            base_url = "https://app.mithril.ai"

        # Render "Dashboard" as a hyperlink styled with the accent color
        try:
            hint.append("Dashboard", style=f"link {base_url}")
        except Exception:
            # Fallback without hyperlink style
            hint.append("Dashboard", style=accent)

    return hint


def build_provisioning_hint(
    subject: str,
    resume_command: str,
    *,
    include_watch_dashboard: bool = True,
    extra_action: tuple[str, str] | None = None,
) -> Text:
    """Build a standardized provisioning hint block.

    Extends build_wait_hints with a concise capacity note used consistently
    across commands (dev, ssh, logs, run).

    Args:
        subject: Noun describing what continues (e.g., "VM", "job", "instance").
        resume_command: Command users should run to resume.
        include_watch_dashboard: Whether to include the second line.
        extra_action: Optional tuple (label, command) appended on line 1.

    Returns:
        Rich Text object with styles applied.
    """
    hint = build_wait_hints(
        subject,
        resume_command,
        include_watch_dashboard=include_watch_dashboard,
        extra_action=extra_action,
    )
    try:
        hint.append("\n")
        hint.append(
            "  Provisioning can take a few minutes as capacity is prepared; we may preempt and safely live-migrate lower-priority workloads to free capacity. We aim to keep migrations minimally disruptive; work can be checkpointed.",
        )
    except Exception:
        pass
    return hint


def build_allocation_hint(
    resume_command: str,
    *,
    subject: str = "allocation",
    include_watch_dashboard: bool = True,
    extra_action: tuple[str, str] | None = None,
) -> Text:
    """Build a standardized allocation hint block.

    Meant for steps like "Allocating instance" where capacity is being
    prepared in the background. Keeps copy concise and consistent with
    provisioning hints but without the extra capacity paragraph.

    Args:
        resume_command: Command to resume/monitor after exiting.
        subject: Noun for what continues (default: "allocation").
        include_watch_dashboard: Whether to include the second line.
        extra_action: Optional tuple (label, command) appended on line 1.
    """
    return build_wait_hints(
        subject,
        resume_command,
        include_watch_dashboard=include_watch_dashboard,
        extra_action=extra_action,
    )


def build_sync_check_hint() -> Text:
    """Two-line hint shown while preflighting code sync.

    Line 1: Checking working directory for changes
    Line 2: Only changed files will be uploaded (respects .flowignore)
    """
    try:
        accent = theme_manager.get_color("accent")
    except Exception:
        accent = "cyan"

    t = Text()
    t.append("  Checking working directory for changes\n")
    t.append("  Only changed files will be uploaded (respects ")
    t.append(".flowignore", style=accent)
    t.append(")")
    return t
