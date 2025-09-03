"""Constants for Mithril startup script generation.

This module centralizes constants used in startup script generation,
making it easier to maintain and adjust thresholds.
"""

# Script size thresholds
SCRIPT_COMPRESSION_THRESHOLD_BYTES = 10 * 1024  # 10KB - Scripts larger than this are compressed
SCRIPT_MAX_UNCOMPRESSED_SIZE_BYTES = 50 * 1024  # 50KB - Maximum size before compression is required
SCRIPT_ABSOLUTE_MAX_SIZE_BYTES = (
    128 * 1024
)  # 128KB - Absolute maximum script size (compressed or not)

# Script compression settings
COMPRESSION_LEVEL = 9  # Maximum compression for startup scripts
COMPRESSION_ENCODING = "utf-8"

# Script validation limits
MAX_ENVIRONMENT_VARIABLES = 1000
MAX_ENVIRONMENT_VARIABLE_NAME_LENGTH = 255
MAX_ENVIRONMENT_VARIABLE_VALUE_LENGTH = 32 * 1024  # 32KB per value
MAX_TOTAL_ENVIRONMENT_SIZE_BYTES = 1024 * 1024  # 1MB total for all env vars

# Docker settings
DOCKER_STARTUP_TIMEOUT_SECONDS = 300  # 5 minutes
DOCKER_HEALTH_CHECK_INTERVAL_SECONDS = 30
DOCKER_PULL_RETRY_ATTEMPTS = 3
DOCKER_PULL_RETRY_DELAY_SECONDS = 10

# Script execution settings
STARTUP_SCRIPT_TIMEOUT_SECONDS = 600  # 10 minutes
STARTUP_SCRIPT_LOG_FILE = "/var/log/foundry/startup_script.log"
STARTUP_SCRIPT_ERROR_LOG_FILE = "/var/log/foundry/startup_script.error.log"

# User data limits
USER_SCRIPT_MAX_SIZE_BYTES = 64 * 1024  # 64KB for user-provided scripts
USER_COMMAND_MAX_LENGTH = 32 * 1024  # 32KB for command strings

# Script section priorities (lower number = higher priority)
SECTION_PRIORITY = {
    "header": 0,
    "logging": 10,
    "environment": 20,
    "monitoring": 30,
    "volumes": 40,
    "docker": 50,
    "user_script": 60,
    "health": 70,
    "completion": 80,
}

# Template markers
TEMPLATE_MARKER_START = "{{{"
TEMPLATE_MARKER_END = "}}}"

# Script encoding
SCRIPT_ENCODING = "utf-8"
SCRIPT_SHEBANG = "#!/bin/bash"

# Error handling
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5
ERROR_REPORT_MAX_LENGTH = 4096  # Maximum error message length to report

# Volume mount settings
VOLUME_MOUNT_TIMEOUT_SECONDS = 120
VOLUME_MOUNT_RETRY_ATTEMPTS = 5
VOLUME_MOUNT_RETRY_DELAY_SECONDS = 10

# GPU-specific settings
GPU_VERIFICATION_TIMEOUT_SECONDS = 60
NVIDIA_CONTAINER_TOOLKIT_INSTALL_TIMEOUT_SECONDS = 300
GPU_DRIVER_LOAD_TIMEOUT_SECONDS = 120

# Network settings
NETWORK_READY_TIMEOUT_SECONDS = 180
SSH_READY_TIMEOUT_SECONDS = 300
PORT_CHECK_INTERVAL_SECONDS = 5

# Instance metadata
METADATA_FETCH_TIMEOUT_SECONDS = 10
METADATA_FETCH_RETRY_ATTEMPTS = 3

# Logging settings
LOG_ROTATION_SIZE_MB = 100
LOG_ROTATION_COUNT = 5
LOG_BUFFER_SIZE_BYTES = 8192

# Health monitoring
HEALTH_CHECK_INTERVAL_SECONDS = 60
HEALTH_METRIC_BATCH_SIZE = 100
HEALTH_METRIC_FLUSH_INTERVAL_SECONDS = 300

# Script validation regex patterns
VALID_ENVIRONMENT_VARIABLE_NAME_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
VALID_VOLUME_MOUNT_PATH_PATTERN = r"^/[a-zA-Z0-9/_\-\.]+$"

# Error messages
ERROR_SCRIPT_TOO_LARGE = "Startup script exceeds maximum size limit of {max_size}KB"
ERROR_INVALID_ENV_VAR_NAME = "Invalid environment variable name: {name}"
ERROR_COMMAND_TOO_LONG = "Command exceeds maximum length of {max_length} characters"
ERROR_TOO_MANY_ENV_VARS = "Too many environment variables: {count} (max: {max_count})"
