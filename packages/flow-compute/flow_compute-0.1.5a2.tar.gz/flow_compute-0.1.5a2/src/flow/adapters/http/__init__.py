"""HTTP client adapters consolidated from various locations.

This module consolidates HTTP functionality previously scattered across:
- flow._internal.io.http
- flow.core.http.http
- flow.adapters.transport.http
"""

# Re-export main client interface
from flow.adapters.http.client import *  # noqa: F403
