"""Backwards-compatible shim for the refactored GenericSetupWizard.

The implementation has moved into the modular package at
`flow.core.setup_wizard`. Importing from this module remains supported.
"""

from flow.core.setup_wizard import GenericSetupWizard

__all__ = ["GenericSetupWizard"]
