"""Centralized animation configuration for Flow CLI.

Provides a single source of truth for animation settings and selection logic,
ensuring consistency across the application while maintaining flexibility.
"""

import random
from dataclasses import dataclass
from typing import Literal

AnimationStyle = Literal["ellipsis", "wave", "pulse", "shimmer", "bounce"]

# Available animation styles for random selection
AVAILABLE_ANIMATIONS: list[AnimationStyle] = ["wave", "shimmer", "pulse", "bounce"]


@dataclass
class AnimationConfig:
    """Configuration for an animation style."""

    duration: float
    intensity: float
    description: str


# Animation configurations with optimal settings for each style
ANIMATION_CONFIGS: dict[AnimationStyle, AnimationConfig] = {
    "wave": AnimationConfig(
        duration=2.0, intensity=0.8, description="Smooth wave pattern across text"
    ),
    "shimmer": AnimationConfig(duration=2.5, intensity=0.6, description="Subtle shimmer effect"),
    "pulse": AnimationConfig(
        duration=1.5, intensity=0.7, description="Rhythmic pulsing brightness"
    ),
    "bounce": AnimationConfig(duration=2.0, intensity=0.8, description="Playful bounce effect"),
    "ellipsis": AnimationConfig(
        duration=0.5,  # Time between ellipsis updates
        intensity=1.0,
        description="Classic ellipsis animation",
    ),
}


class AnimationSelector:
    """Manages animation style selection with configurable behavior."""

    def __init__(self, default_style: AnimationStyle | None = None):
        """Initialize the animation selector.

        Args:
            default_style: Default animation style. If None, random selection is used.
        """
        self._default_style = default_style
        self._override_style: AnimationStyle | None = None

    def select(self, requested_style: AnimationStyle | None = None) -> AnimationStyle:
        """Select an animation style based on configuration and request.

        Priority order:
        1. Override style (if set)
        2. Requested style (if provided)
        3. Default style (if configured)
        4. Random selection from available animations

        Args:
            requested_style: Explicitly requested animation style

        Returns:
            Selected animation style
        """
        # Check override first
        if self._override_style:
            return self._override_style

        # Use requested style if provided
        if requested_style:
            return requested_style

        # Use default if configured
        if self._default_style:
            return self._default_style

        # Random selection from available animations
        return random.choice(AVAILABLE_ANIMATIONS)

    def set_override(self, style: AnimationStyle | None) -> None:
        """Set a global override for all animations.

        Useful for testing or enforcing consistency.

        Args:
            style: Animation style to use everywhere, or None to disable override
        """
        self._override_style = style

    def get_config(self, style: AnimationStyle) -> AnimationConfig:
        """Get configuration for a specific animation style.

        Args:
            style: Animation style

        Returns:
            Animation configuration
        """
        return ANIMATION_CONFIGS[style]


# Global animation selector instance
animation_selector = AnimationSelector()


def get_animation_style(requested: AnimationStyle | None = None) -> AnimationStyle:
    """Get the animation style to use.

    This is the primary interface for getting animation styles throughout
    the application. It respects global configuration while allowing
    local overrides.

    Args:
        requested: Explicitly requested style (optional)

    Returns:
        Animation style to use
    """
    return animation_selector.select(requested)


def get_animation_config(style: AnimationStyle) -> AnimationConfig:
    """Get configuration for an animation style.

    Args:
        style: Animation style

    Returns:
        Configuration for the style
    """
    return animation_selector.get_config(style)
