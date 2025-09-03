"""Setup Wizard package.

Provides a modular implementation of the GenericSetupWizard split into:
- prompter: low-level terminal input utilities
- menu_selector: interactive and fallback menus
- ui_renderer: presentation and rendering helpers
- field_configurator: per-field configuration logic
- wizard: orchestration and high-level flow
"""

from flow.core.setup_wizard.wizard import GenericSetupWizard  # re-export for convenience

__all__ = ["GenericSetupWizard"]
