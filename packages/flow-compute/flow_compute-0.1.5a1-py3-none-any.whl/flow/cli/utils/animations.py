"""Rich animation patterns for Flow CLI.

Provides various animation effects including wave patterns, pulse effects,
and state-based animations for enhanced visual feedback.

Key implementation notes:
- All animation timing uses monotonic clocks to avoid pauses / jumps if the
  system wall clock changes (e.g., NTP adjustments or sleep / resume).
"""

import math
import os
import time
from dataclasses import dataclass
from enum import Enum

from rich.style import Style
from rich.text import Text

from flow.resources.loader import DataLoader


class AnimationType(Enum):
    """Available animation types."""

    WAVE = "wave"
    PULSE = "pulse"
    SPINNER = "spinner"
    PROGRESS = "progress"
    SHIMMER = "shimmer"
    BOUNCE = "bounce"


@dataclass
class AnimationPattern:
    """Defines an animation pattern."""

    type: AnimationType
    duration: float  # Duration in seconds for one cycle
    intensity: float = 1.0  # Animation intensity (0.0 to 1.0)
    delay: float = 0.0  # Delay between elements
    custom_chars: list[str] | None = None  # For spinner animations


class AnimationEngine:
    """Manages animation patterns and states for Flow CLI."""

    # Built-in defaults; instance will override from data loader when available
    SPINNERS = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "dots2": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        "line": ["-", "\\", "|", "/"],
        "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "pulse": ["◯", "◉", "●", "◉"],
        "wave": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],
        "bounce": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
        "bar": ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"],
    }

    STATUS_ANIMATIONS = {
        "pending": AnimationPattern(AnimationType.PULSE, duration=2.0, intensity=0.6),
        "preparing": AnimationPattern(
            AnimationType.SPINNER, duration=0.8, custom_chars=SPINNERS["dots"]
        ),
        "running": AnimationPattern(AnimationType.WAVE, duration=3.0, intensity=0.8),
        "preempting": AnimationPattern(AnimationType.PULSE, duration=1.0, intensity=1.0),
        "completed": AnimationPattern(AnimationType.SHIMMER, duration=2.0, intensity=0.5),
        "failed": AnimationPattern(AnimationType.PULSE, duration=0.5, intensity=1.0),
    }

    def __init__(self):
        """Initialize animation engine and load data-driven config."""
        # Monotonic base time avoids freezes when wall clock changes
        self.start_time = time.monotonic()
        # Load spinners and status animations from data files (safe fallbacks)
        try:
            loader = DataLoader()
            spinners = loader.cli_animation.get("spinners", {})
            if isinstance(spinners, dict) and spinners:
                # Normalize keys to str and values to list[str]
                for name, frames in spinners.items():
                    if isinstance(frames, list) and frames:
                        self.SPINNERS[name] = [str(c) for c in frames]
            status_cfg = loader.cli_animation.get("status", {})
            if isinstance(status_cfg, dict) and status_cfg:
                new_map: dict[str, AnimationPattern] = {}
                for status, cfg in status_cfg.items():
                    t = str(cfg.get("type", "pulse")).lower()
                    duration = float(cfg.get("duration", 1.0))
                    intensity = float(cfg.get("intensity", 1.0))
                    if t == "wave":
                        new_map[status] = AnimationPattern(
                            AnimationType.WAVE, duration=duration, intensity=intensity
                        )
                    elif t == "shimmer":
                        new_map[status] = AnimationPattern(
                            AnimationType.SHIMMER, duration=duration, intensity=intensity
                        )
                    elif t == "bounce":
                        new_map[status] = AnimationPattern(
                            AnimationType.BOUNCE, duration=duration, intensity=intensity
                        )
                    elif t == "spinner":
                        spinner_name = str(cfg.get("spinner", "dots"))
                        frames = self.SPINNERS.get(
                            spinner_name, self.SPINNERS.get("dots", ["-", "|", "/", "-"])
                        )
                        new_map[status] = AnimationPattern(
                            AnimationType.SPINNER, duration=duration, custom_chars=frames
                        )
                    else:
                        new_map[status] = AnimationPattern(
                            AnimationType.PULSE, duration=duration, intensity=intensity
                        )
                # Override defaults
                self.STATUS_ANIMATIONS = new_map
        except Exception:
            # Keep defaults on any error
            pass

    def get_phase(self, duration: float, delay: float = 0.0) -> float:
        """Calculate current animation phase.

        Args:
            duration: Duration of one animation cycle in seconds
            delay: Delay offset in seconds

        Returns:
            Phase value between 0.0 and 1.0
        """
        # Use monotonic time for smooth, uninterrupted animation
        elapsed = time.monotonic() - self.start_time + delay
        return (elapsed % duration) / duration

    def wave_pattern(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate wave animation for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Wave intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        result = Text()
        text_len = len(text)

        for i, char in enumerate(text):
            # Calculate wave position for this character
            char_phase = (phase + i / text_len) % 1.0

            # Sine wave for smooth animation
            brightness = 0.5 + 0.5 * math.sin(char_phase * 2 * math.pi) * intensity

            # Convert brightness to color
            if brightness > 0.75:
                style = Style(color="bright_white", bold=True)
            elif brightness > 0.5:
                style = Style(color="white")
            elif brightness > 0.25:
                style = Style(color="bright_black")
            else:
                style = Style(color="black")

            result.append(char, style=style)

        return result

    def pulse_effect(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate pulse effect for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Pulse intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        # Smooth pulse using sine wave
        brightness = 0.5 + 0.5 * math.sin(phase * 2 * math.pi) * intensity

        if brightness > 0.75:
            style = Style(color="bright_white", bold=True)
        elif brightness > 0.5:
            style = Style(color="white")
        elif brightness > 0.25:
            style = Style(color="bright_black")
        else:
            style = Style(dim=True)

        return Text(text, style=style)

    def shimmer_effect(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate shimmer effect for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Shimmer intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        result = Text()
        text_len = len(text)
        shimmer_width = 0.2  # Width of shimmer band

        for i, char in enumerate(text):
            # Calculate position in shimmer cycle
            char_pos = i / text_len
            shimmer_pos = phase

            # Calculate distance from shimmer center
            distance = abs(char_pos - shimmer_pos)
            if distance > 0.5:  # Handle wrap-around
                distance = 1.0 - distance

            # Apply shimmer effect based on distance
            if distance < shimmer_width:
                brightness = 1.0 - (distance / shimmer_width)
                brightness *= intensity

                if brightness > 0.5:
                    style = Style(color="bright_white", bold=True)
                else:
                    style = Style(color="white")
            else:
                style = Style()

            result.append(char, style=style)

        return result

    def bounce_effect(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate bounce effect for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Bounce intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        result = Text()
        text_len = len(text)

        for i, char in enumerate(text):
            # Calculate bounce position for this character
            char_phase = (phase + i / text_len * 0.5) % 1.0

            # Bounce curve (parabola)
            if char_phase < 0.5:
                height = 4 * char_phase * (1 - char_phase)
            else:
                height = 0

            # Apply vertical offset using Unicode combining characters
            if height > 0.5 * intensity and char != " ":
                # Use superscript for bounce effect
                result.append(char, style=Style(bold=True))
            else:
                result.append(char)

        return result

    def get_spinner_frame(self, pattern: list[str], phase: float) -> str:
        """Get current spinner frame.

        Args:
            pattern: List of spinner characters
            phase: Current phase (0.0 to 1.0)

        Returns:
            Current spinner character
        """
        frame_index = int(phase * len(pattern))
        return pattern[frame_index % len(pattern)]

    def state_animation(self, status: str, text: str) -> Text:
        """Get appropriate animation for task status.

        Args:
            status: Task status
            text: Text to animate

        Returns:
            Animated text based on status
        """
        pattern = self.STATUS_ANIMATIONS.get(status.lower())
        if not pattern:
            return Text(text)

        phase = self.get_phase(pattern.duration, pattern.delay)

        if pattern.type == AnimationType.WAVE:
            return self.wave_pattern(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.PULSE:
            return self.pulse_effect(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.SHIMMER:
            return self.shimmer_effect(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.BOUNCE:
            return self.bounce_effect(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.SPINNER and pattern.custom_chars:
            spinner = self.get_spinner_frame(pattern.custom_chars, phase)
            return Text(f"{spinner} {text}")
        else:
            return Text(text)

    def progress_bar(
        self,
        progress: float,
        width: int = 20,
        animated: bool = True,
        style: str = "gradient",
        color: str | None = None,
    ) -> Text:
        """Create an animated progress bar.

        Args:
            progress: Progress value (0.0 to 1.0)
            width: Bar width in characters
            animated: Whether to animate the bar
            style: Bar style ("default", "smooth", "blocks", "gradient")

        Returns:
            Progress bar as Rich Text
        """
        # Respect ASCII-only output if requested; override style conservatively
        ascii_only = os.getenv("FLOW_ASCII") == "1"

        # Select bracket/cap characters based on style
        left_cap = "["
        right_cap = "]"
        if style == "rounded":
            # Safe, widely supported caps for a pill-like look
            left_cap, right_cap = "(", ")"

        if style == "smooth" and not ascii_only or style == "rounded" and not ascii_only:
            chars = " ▏▎▍▌▋▊▉█"
            filled = int(progress * width * 8)
            full_blocks = filled // 8
            partial_block = filled % 8

            bar = "█" * full_blocks
            if partial_block > 0 and full_blocks < width:
                bar += chars[partial_block]
            bar += " " * (width - len(bar))

        elif style == "gradient" and not ascii_only:
            # Gradient style inspired by the health command
            # Uses '█' for filled, '▓' for leading edge, and '░' for empty
            full_blocks = int(progress * width)
            if full_blocks <= 0:
                bar = "░" * width
            elif full_blocks >= width:
                bar = "█" * width
            else:
                bar = "█" * full_blocks + "▓" + "░" * (width - full_blocks - 1)
            # Keep a variable named `filled` for the shimmer logic below
            filled = full_blocks

        elif style == "blocks":
            filled = int(progress * width)
            bar = "■" * filled + "□" * (width - filled)

        else:  # default
            filled = int(progress * width)
            bar = "=" * filled + "-" * (width - filled)

        result = Text(f"{left_cap}{bar}{right_cap}")

        # Apply theme accent color to the filled portion for visual consistency.
        # Prefer explicit color arg, otherwise use theme's AEP accent then accent.
        try:
            if color is None:
                from flow.cli.utils.theme_manager import theme_manager as _tm

                accent = _tm.get_color("aep.accent") or _tm.get_color("accent")
            else:
                accent = color
        except Exception:
            accent = "cyan"

        try:
            # Compute filled span indices inside the [ ... ] caps.
            # Handle both smooth/rounded (8-level) and whole-block/gradient bars.
            if style in {"smooth", "rounded"} and not ascii_only:
                filled8 = int(progress * width * 8)
                full_blocks = filled8 // 8
                partial = filled8 % 8
                start = 1  # inside '['
                end = 1 + full_blocks + (1 if (partial > 0 and full_blocks < width) else 0)
            elif style == "gradient" and not ascii_only:
                full_blocks = int(progress * width)
                include_edge = 1 if (progress > 0 and full_blocks < width) else 0
                start = 1
                end = 1 + full_blocks + include_edge
            elif style == "blocks":
                filled_simple = int(progress * width)
                start = 1
                end = 1 + filled_simple
            else:
                filled_simple = int(progress * width)
                start = 1
                end = 1 + filled_simple

            if end > start:
                result.stylize(accent, start, end)
        except Exception:
            # Never let styling break the bar rendering
            pass

        if animated and progress < 1.0:
            # Add shimmer effect to the progress edge
            phase = self.get_phase(1.0)
            if filled > 0 and filled < width:
                edge_pos = filled - 1
                if phase > 0.5:
                    result.stylize(Style(bold=True), edge_pos + 1, edge_pos + 2)

        return result


class AnimatedEllipsisProgress:
    """Minimal context manager used by health/task commands for a simple animated line.

    This avoids a separate module import and keeps CLI decoupled from providers.
    """

    def __init__(self, console, message: str, start_immediately: bool = True):
        self.console = console
        self.message = message
        self._running = False
        self._thread = None
        self._stop = False
        self._start_immediately = start_immediately

    def __enter__(self):
        if self._start_immediately:
            self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
        return False

    def start(self):
        if self._running:
            return
        self._running = True
        import threading
        import time

        def _loop():
            frames = ["", ".", "..", "..."]
            i = 0
            try:
                while not self._stop:
                    suffix = frames[i % len(frames)]
                    self.console.print(f"{self.message}{suffix}", end="\r")
                    time.sleep(0.25)
                    i += 1
            except Exception:
                pass

        self._stop = False
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self._running:
            return
        self._stop = True
        try:
            if self._thread is not None:
                self._thread.join(timeout=1.0)
        except Exception:
            pass
        self._running = False
        try:
            self.console.print(" " * (len(self.message) + 4), end="\r")
        except Exception:
            pass


# Global animation engine instance
animation_engine = AnimationEngine()
