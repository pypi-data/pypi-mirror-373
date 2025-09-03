"""Enable running the CLI as a module: python -m flow.cli"""

import sys

# Graceful message for unsupported Python versions before importing heavy modules
if sys.version_info < (3, 10):
    print(
        f"Error: Flow SDK requires Python 3.10 or later. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.\n\n"
        f"Recommended: Install and use 'uv' for automatic Python version management:\n"
        f"  curl -LsSf https://astral.sh/uv/install.sh | sh\n"
        f"  uv tool install flow-compute\n\n"
        f"Or install without uv:\n"
        f"  pipx install flow-compute\n"
        f"  # macOS/Linux one-liner: curl -fsSL https://raw.githubusercontent.com/mithrilcompute/flow/main/scripts/install.sh | sh\n\n"
        f"Alternative: Upgrade your Python installation to 3.10 or later.",
        file=sys.stderr,
    )
    sys.exit(1)

from flow.cli.app import main

if __name__ == "__main__":
    sys.exit(main())
