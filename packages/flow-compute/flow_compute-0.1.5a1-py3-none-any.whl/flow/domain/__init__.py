"""Domain layer: pure business logic and types.

Contains the core models, policies, and rules that define Flow's behavior.
This layer is deterministic and side-effect free: no network, file I/O, or
adapter dependencies.

Subpackages:
  - ``models``: provider-agnostic data structures
  - ``ir``: canonical Task/Resource/RunParams specifications
  - ``validators``: pure validation logic
  - ``services``: algorithms that don't belong on entities/values
  - ``pricing``/``ssh``/``parsers``: additional pure-domain utilities

Guidelines:
  - Do depend on stdlib and typing; avoid runtime-heavy imports.
  - Do not import from ``flow.adapters`` or ``flow.core``.
"""
