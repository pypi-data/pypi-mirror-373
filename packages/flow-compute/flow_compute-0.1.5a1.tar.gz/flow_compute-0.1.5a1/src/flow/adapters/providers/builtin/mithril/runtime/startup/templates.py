"""Template engine for script generation.

Provides a clean abstraction for template rendering with proper
separation of concerns between logic and presentation.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ITemplateEngine(ABC):
    """Abstract template engine interface."""

    @abstractmethod
    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render a template with the given context."""
        pass

    @abstractmethod
    def render_file(self, template_path: Path, context: dict[str, Any]) -> str:
        """Render a template file with the given context."""
        pass


class SimpleTemplateEngine(ITemplateEngine):
    """Simple template engine using Python string formatting.

    This is a lightweight alternative when Jinja2 is not available.
    Supports basic variable substitution with ${variable} syntax.
    """

    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render template with context using safe string substitution."""
        # Convert ${var} to {var} for Python formatting
        formatted = re.sub(r"\$\{(\w+)\}", r"{\1}", template)

        # Safe formatting - missing keys are left as-is
        class SafeDict(dict):
            def __missing__(self, key):
                return f"${{{key}}}"

        safe_context = SafeDict(context)
        return formatted.format_map(safe_context)

    def render_file(self, template_path: Path, context: dict[str, Any]) -> str:
        """Render a template file."""
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path) as f:
            template = f.read()

        return self.render(template, context)


class Jinja2TemplateEngine(ITemplateEngine):
    """Jinja2-based template engine for advanced templating needs."""

    def __init__(self, template_dir: Path | None = None):
        """Initialize with optional template directory."""
        try:
            import jinja2
        except ImportError:
            raise ImportError("Jinja2 is required for Jinja2TemplateEngine")

        self.template_dir = template_dir
        common_kwargs = dict(
            autoescape=False,  # We're generating shell scripts
            trim_blocks=True,
            lstrip_blocks=True,
            variable_start_string="[[",
            variable_end_string="]]",
        )
        if template_dir:
            self.env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(template_dir)),
                **common_kwargs,
            )
        else:
            self.env = jinja2.Environment(
                **common_kwargs,
            )

    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render template string with context."""
        tmpl = self.env.from_string(template)
        return tmpl.render(context)

    def render_file(self, template_path: Path, context: dict[str, Any]) -> str:
        """Render a template file."""
        if self.template_dir:
            # Use relative path from template directory
            tmpl = self.env.get_template(str(template_path))
            return tmpl.render(context)
        else:
            # Load template directly
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")

            with open(template_path) as f:
                template = f.read()

            return self.render(template, context)


class CachedTemplateEngine(ITemplateEngine):
    """Template engine decorator that adds caching."""

    def __init__(self, engine: ITemplateEngine):
        """Wrap an existing template engine with caching."""
        self.engine = engine
        self._cache: dict[str, str] = {}

    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render with caching based on template and context hash."""
        # For simple strings, just delegate (caching overhead not worth it)
        return self.engine.render(template, context)

    def render_file(self, template_path: Path, context: dict[str, Any]) -> str:
        """Render file with caching based on file mtime."""
        cache_key = f"{template_path}:{template_path.stat().st_mtime}"

        if cache_key not in self._cache:
            self._cache[cache_key] = template_path.read_text()

        template = self._cache[cache_key]
        return self.engine.render(template, context)

    def clear_cache(self):
        """Clear the template cache."""
        self._cache.clear()


def create_template_engine(engine_type: str = "simple", **kwargs) -> ITemplateEngine:
    """Factory function to create template engines.

    Args:
        engine_type: Type of engine ("simple" or "jinja2")
        **kwargs: Additional arguments for the engine

    Returns:
        Template engine instance
    """
    if engine_type == "simple":
        return SimpleTemplateEngine()
    elif engine_type == "jinja2":
        return Jinja2TemplateEngine(**kwargs)
    else:
        raise ValueError(f"Unknown template engine type: {engine_type}")
