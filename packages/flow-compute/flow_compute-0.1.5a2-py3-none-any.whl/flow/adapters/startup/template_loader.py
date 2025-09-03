"""Template loader with provider override support (zip-safe).

This module provides a template loading mechanism that checks provider-specific
overrides before falling back to canonical templates, using importlib.resources
to remain zip-safe.
"""

from __future__ import annotations

from pathlib import Path

from flow.resources.templates import template_search_paths


class TemplateLoader:
    """Template loader with fallback to canonical templates."""

    def __init__(self, provider_templates_pkg: str | None = None):
        """Initialize with optional provider-specific templates package.

        Args:
            provider_templates_pkg: Dotted package containing provider templates
                (e.g., "flow.adapters.providers.builtin.mithril.runtime.startup.templates")
        """
        self.provider_templates_pkg = provider_templates_pkg

    def get_template_search_paths(self) -> list[Path]:
        """Get resolved search paths (provider first, then canonical)."""
        pkgs: list[str] = []
        if self.provider_templates_pkg:
            pkgs.append(self.provider_templates_pkg)
        # Canonical templates location
        pkgs.append("flow.resources.templates")
        return list(template_search_paths(*pkgs))

    def get_template_path(self, template_name: str) -> Path:
        """Resolve a template path across search locations."""
        for base in self.get_template_search_paths():
            candidate = base / template_name
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"Template '{template_name}' not found in search paths")

    def list_templates(self, pattern: str = "*.j2") -> list[str]:
        """List templates available across search paths (unique by relative path)."""
        seen: set[str] = set()
        results: list[str] = []
        for base in self.get_template_search_paths():
            for p in base.rglob(pattern):
                rel = p.relative_to(base).as_posix()
                if rel not in seen:
                    seen.add(rel)
                    results.append(rel)
        return sorted(results)
