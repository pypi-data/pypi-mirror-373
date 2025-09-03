"""Bootstrap script templates for Mithril startup scripts.

Centralized template system for generating bootstrap scripts used by various
script size strategies. Templates are versioned and parameterized for
maintainability and testability.
"""

from datetime import datetime, timezone


class BootstrapTemplates:
    """Centralized bootstrap script templates with versioning."""

    VERSION = "1.0"

    # Base template with common header and error handling
    BASE_TEMPLATE = """#!/bin/bash
{origin_header}
# Mithril Bootstrap Script v{version}
# Generated: {timestamp}
# Strategy: {strategy}
# Size: {size_info}

set -euo pipefail

# Error handling
handle_error() {{
    local exit_code=$1
    local line_no=$2
    echo "ERROR: Bootstrap failed at line $line_no with exit code $exit_code" >&2
    exit $exit_code
}}
trap 'handle_error $? $LINENO' ERR

# Environment setup
export DEBIAN_FRONTEND=noninteractive
export PATH="/usr/local/bin:/usr/bin:/bin"

{body}
"""

    # Template for compressed scripts
    COMPRESSION_TEMPLATE = """# Compressed script bootstrap
# Original size: {original_size:,} bytes
# Compressed size: {compressed_size:,} bytes
# Compression ratio: {compression_ratio:.1f}%

echo "[$(date)] Starting compressed script extraction..."

# Decode and decompress
COMPRESSED_SCRIPT=$(cat << 'EOF_COMPRESSED_SCRIPT'
{compressed_data}
EOF_COMPRESSED_SCRIPT
)

# Verify integrity
EXPECTED_HASH="{script_hash}"
ACTUAL_HASH=$(echo "$COMPRESSED_SCRIPT" | base64 -d | sha256sum | cut -d' ' -f1)

if [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
    echo "ERROR: Script integrity check failed!" >&2
    echo "Expected: $EXPECTED_HASH" >&2
    echo "Actual: $ACTUAL_HASH" >&2
    exit 1
fi

# Extract and execute
echo "$COMPRESSED_SCRIPT" | base64 -d | gzip -d > /tmp/startup_script.sh
chmod +x /tmp/startup_script.sh

echo "[$(date)] Executing decompressed script..."
exec /tmp/startup_script.sh
"""

    # Template for external storage
    STORAGE_TEMPLATE = """# External storage bootstrap
# Script size: {script_size:,} bytes
# Storage URL: {storage_url}
# Hash: {script_hash}

echo "[$(date)] Downloading script from external storage..."

# Ensure curl is available
if ! command -v curl >/dev/null 2>&1; then
    echo "Installing curl..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq && apt-get install -y -qq curl ca-certificates
fi

# Download with retries
MAX_RETRIES=3
RETRY_DELAY=5

download_script() {{
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "[$(date)] Download attempt $attempt/$MAX_RETRIES..."
        
        if curl -fsSL --connect-timeout 30 --max-time 300 \\
            -o /tmp/startup_script.sh \\
            "{storage_url}"; then
            echo "[$(date)] Download successful"
            return 0
        fi
        
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "[$(date)] Download failed, retrying in $RETRY_DELAY seconds..."
            sleep $RETRY_DELAY
            RETRY_DELAY=$((RETRY_DELAY * 2))
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "ERROR: Failed to download script after $MAX_RETRIES attempts" >&2
    return 1
}}

# Download and verify
if ! download_script; then
    exit 1
fi

# Verify integrity
EXPECTED_HASH="{script_hash}"
ACTUAL_HASH=$(sha256sum /tmp/startup_script.sh | cut -d' ' -f1)

if [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
    echo "ERROR: Script integrity check failed!" >&2
    echo "Expected: $EXPECTED_HASH" >&2
    echo "Actual: $ACTUAL_HASH" >&2
    exit 1
fi

# Make executable and run
chmod +x /tmp/startup_script.sh
echo "[$(date)] Executing downloaded script..."
exec /tmp/startup_script.sh
"""

    # Template for split scripts (future enhancement)
    SPLIT_TEMPLATE = """# Split script bootstrap
# Total parts: {total_parts}
# Part size: {part_size:,} bytes

echo "[$(date)] Assembling split script..."

# Download all parts
{download_parts}

# Combine parts
cat {part_files} > /tmp/startup_script.sh

# Verify combined script
EXPECTED_HASH="{script_hash}"
ACTUAL_HASH=$(sha256sum /tmp/startup_script.sh | cut -d' ' -f1)

if [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
    echo "ERROR: Combined script integrity check failed!" >&2
    exit 1
fi

# Execute
chmod +x /tmp/startup_script.sh
exec /tmp/startup_script.sh
"""

    @classmethod
    def render(cls, template_name: str, **kwargs) -> str:
        """Render a bootstrap script from a template.

        Args:
            template_name: Name of the template to use.
            **kwargs: Template parameters.

        Returns:
            Rendered bootstrap script.

        Raises:
            ValueError: If template not found or required parameters missing.
        """
        templates = {
            "compression": cls.COMPRESSION_TEMPLATE,
            "storage": cls.STORAGE_TEMPLATE,
            "split": cls.SPLIT_TEMPLATE,
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")

        # Add common parameters
        common_params = {
            "version": cls.VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strategy": template_name,
        }

        # Merge with provided parameters
        params = {**common_params, **kwargs}

        # Inject Flow origin header
        try:
            from flow.adapters.providers.builtin.mithril.runtime.startup.origin import (
                get_flow_origin_header,
            )

            params["origin_header"] = get_flow_origin_header()
        except Exception:
            # If header utility is unavailable for any reason, omit header
            params["origin_header"] = "# FLOW_ORIGIN: flow-cli"

        # Get template body
        body = templates[template_name].format(**params)

        # Render full template
        return cls.BASE_TEMPLATE.format(body=body, **params)

    @classmethod
    def render_compression_bootstrap(
        cls, compressed_data: str, script_hash: str, original_size: int, compressed_size: int
    ) -> str:
        """Render a compression strategy bootstrap script.

        Args:
            compressed_data: Base64 encoded compressed script.
            script_hash: SHA256 hash of compressed data.
            original_size: Original script size in bytes.
            compressed_size: Compressed size in bytes.

        Returns:
            Rendered bootstrap script.
        """
        compression_ratio = (1 - compressed_size / original_size) * 100

        return cls.render(
            "compression",
            compressed_data=compressed_data,
            script_hash=script_hash,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            size_info=f"Original: {original_size:,} bytes, Compressed: {compressed_size:,} bytes",
        )

    @classmethod
    def render_storage_bootstrap(cls, storage_url: str, script_hash: str, script_size: int) -> str:
        """Render a storage strategy bootstrap script.

        Args:
            storage_url: URL to download the script from.
            script_hash: SHA256 hash of the script.
            script_size: Script size in bytes.

        Returns:
            Rendered bootstrap script.
        """
        return cls.render(
            "storage",
            storage_url=storage_url,
            script_hash=script_hash,
            script_size=script_size,
            size_info=f"{script_size:,} bytes (external)",
        )
