"""Deprecated location for masking utilities; re-exports canonical utils.

Use ``flow.utils.masking`` going forward. This module remains for backwards
compatibility and re-exports the canonical functions.
"""

from flow.utils.masking import (
    mask_api_key,
    mask_config_for_display,
    mask_sensitive_value,
    mask_ssh_key_fingerprint,
    mask_strict_last4,
)

__all__ = [
    "mask_sensitive_value",
    "mask_strict_last4",
    "mask_api_key",
    "mask_ssh_key_fingerprint",
    "mask_config_for_display",
]
