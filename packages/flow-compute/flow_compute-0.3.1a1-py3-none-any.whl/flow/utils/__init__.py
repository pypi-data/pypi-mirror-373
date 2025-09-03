"""Shared, lightweight utilities with no side effects.

Pure helpers used across the SDK for paths, masking, caching, and small
algorithmic utilities. Keep functions deterministic, well-typed, and free of
network or subprocess calls.

Guidelines:
  - Safe to import anywhere; do not import heavy dependencies here.
  - Prefer small, composable helpers; avoid domain or adapter logic.
"""

__all__: list[str] = []
