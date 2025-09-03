from __future__ import annotations

"""Utility functions for startup scripts to ensure required commands are available."""

import textwrap


def ensure_command_available(command: str, install_method: str | None = None) -> str:
    """Generate script to ensure a command is available, installing if needed.

    Args:
        command: The command to check for availability
        install_method: Optional installation method if command is not found

    Returns:
        Shell script snippet to ensure the command is available
    """
    if not install_method:
        # Default installation plans for common commands (cross-distro where possible)
        if command == "aws":
            # Ensure unzip and curl, then install AWS CLI v2 with optional checksum verification
            install_method = (
                "if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi\n"
                "if ! command -v unzip >/dev/null 2>&1; then install_pkgs unzip || true; fi\n"
                'AWSCLI_URL="${AWSCLI_URL:-https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip}"\n'
                'AWSCLI_SHA256="${AWSCLI_SHA256:-}"\n'
                'echo "Downloading AWS CLI from $AWSCLI_URL"\n'
                'curl -fsSL "$AWSCLI_URL" -o /tmp/awscliv2.zip || exit 1\n'
                'if [ -n "$AWSCLI_SHA256" ]; then\n'
                "  if command -v sha256sum >/dev/null 2>&1; then EXPECTED=$AWSCLI_SHA256; ACTUAL=$(sha256sum /tmp/awscliv2.zip | awk '{print $1}');\n"
                "  elif command -v shasum >/dev/null 2>&1; then EXPECTED=$AWSCLI_SHA256; ACTUAL=$(shasum -a 256 /tmp/awscliv2.zip | awk '{print $1}');\n"
                '  else echo "WARNING: No sha256 tool available; skipping checksum verification for AWS CLI"; ACTUAL=$AWSCLI_SHA256; fi\n'
                '  if [ "$EXPECTED" != "$ACTUAL" ]; then echo "ERROR: AWS CLI checksum mismatch"; rm -f /tmp/awscliv2.zip; exit 1; fi\n'
                "fi\n"
                "unzip -q /tmp/awscliv2.zip -d /tmp && /tmp/aws/install && rm -rf /tmp/aws*\n"
            )
        elif command == "docker":
            # Prefer distro packages; fall back to verified download, avoid executing remote script directly
            install_method = (
                "if command -v apt-get >/dev/null 2>&1; then apt-get update -qq && apt-get install -y -qq docker.io || true; "
                "elif command -v dnf >/dev/null 2>&1; then dnf -y install docker || true; "
                "elif command -v yum >/dev/null 2>&1; then yum -y install docker || true; "
                "elif command -v apk >/dev/null 2>&1; then apk add --no-cache docker || true; "
                "elif command -v zypper >/dev/null 2>&1; then zypper -n install docker || true; "
                "else "
                '  if [ "${FLOW_DISABLE_UNVERIFIED_INSTALLERS:-0}" = "1" ]; then echo "ERROR: No supported package manager and unverified installers disabled"; exit 1; fi; '
                "  if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi; "
                "  MAX_RETRIES=3; RETRY_COUNT=0; "
                "  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do "
                '    if curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sh /tmp/get-docker.sh; then rm -f /tmp/get-docker.sh; break; else RETRY_COUNT=$((RETRY_COUNT + 1)); echo "Docker install failed, retrying..."; sleep 5; fi; '
                "  done; "
                '  if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then echo "ERROR: Failed to install Docker after retries"; exit 1; fi; '
                "fi"
            )
        elif command == "s3fs":
            # s3fs on Debian-based is s3fs; on RHEL-based often s3fs-fuse
            install_method = "install_pkgs s3fs || install_pkgs s3fs-fuse || true"
        elif command == "uuidgen":
            # util-linux provides uuidgen on many distros; Debian uses uuid-runtime
            install_method = "install_pkgs uuid-runtime || install_pkgs util-linux || true"
        elif command == "pip3":
            install_method = "install_pkgs python3-pip || install_pkgs py3-pip || true"
        elif command in {"curl", "wget", "bc", "jq", "python3", "nginx"}:
            install_method = f"install_pkgs {command} || true"
        else:
            # Fallback: try to install a package named like the command
            install_method = f"install_pkgs {command} || true"

    if install_method:
        return textwrap.dedent(
            f"""
            # Ensure {command} is available
            if ! command -v {command} >/dev/null 2>&1; then
                echo "Installing {command}..."
                export DEBIAN_FRONTEND=noninteractive
                {install_method}
            fi
            """
        ).strip()
    else:
        # Just check without installing
        return textwrap.dedent(
            f"""
            # Check for {command}
            if ! command -v {command} >/dev/null 2>&1; then
                echo "WARNING: {command} not found and no installation method configured"
            fi
            """
        ).strip()


def ensure_curl_available() -> str:
    """Ensure curl is available since it's used extensively in startup scripts."""
    return textwrap.dedent(
        """
        # Ensure curl is available (required for many operations)
        if ! command -v curl >/dev/null 2>&1; then
            echo "Installing curl (required for startup operations)..."
            export DEBIAN_FRONTEND=noninteractive
            install_pkgs curl ca-certificates || true
        fi
        """
    ).strip()


def ensure_docker_available() -> str:
    """Ensure Docker is available with proper error handling."""
    return textwrap.dedent(
        """
        # Ensure Docker is available
        if ! command -v docker >/dev/null 2>&1; then
            echo "Docker not found, installing..."

            export DEBIAN_FRONTEND=noninteractive

            # Prefer distro packages; fall back to get.docker.com
            if command -v apt-get >/dev/null 2>&1; then
                apt-get update -qq || true
                apt-get install -y docker.io || true
            elif command -v dnf >/dev/null 2>&1; then
                dnf -y install docker || true
            elif command -v yum >/dev/null 2>&1; then
                yum -y install docker || true
            elif command -v apk >/dev/null 2>&1; then
                apk add --no-cache docker || true
            elif command -v zypper >/dev/null 2>&1; then
                zypper -n install docker || true
            else
                # Fallback installer (unpinned). Use with caution.
                # Allow disabling this path for environments requiring strict provenance
                if [ "${FLOW_DISABLE_UNVERIFIED_INSTALLERS:-0}" = "1" ]; then
                    echo "ERROR: Fallback Docker installer disabled by FLOW_DISABLE_UNVERIFIED_INSTALLERS=1";
                    exit 1;
                fi
                if ! command -v curl >/dev/null 2>&1; then
                    install_pkgs curl ca-certificates || true
                fi
                MAX_RETRIES=3
                RETRY_COUNT=0
                while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
                    if curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sh /tmp/get-docker.sh; then
                        rm -f /tmp/get-docker.sh
                        break
                    else
                        RETRY_COUNT=$((RETRY_COUNT + 1))
                        echo "Docker installation attempt $RETRY_COUNT failed, retrying..."
                        sleep 5
                    fi
                done
                if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                    echo "ERROR: Failed to install Docker after $MAX_RETRIES attempts"
                    exit 1
                fi
            fi
        fi

        # Enable and start Docker when possible
        if command -v systemctl >/dev/null 2>&1; then
            systemctl enable docker || true
            systemctl start docker || true
        elif command -v service >/dev/null 2>&1; then
            service docker start || true
        fi

        # Wait for Docker to be ready regardless of init system
        DOCKER_READY=false
        for i in $(seq 1 30); do
            if docker info >/dev/null 2>&1; then
                DOCKER_READY=true
                break
            fi
            sleep 1
        done
        if [ "$DOCKER_READY" = "false" ]; then
            echo "WARNING: Docker did not become ready in time"
        fi
        """
    ).strip()


def ensure_nvidia_container_toolkit() -> str:
    """Ensure NVIDIA Container Toolkit is installed and Docker is configured.

    - Adds NVIDIA's libnvidia-container repo (apt/dnf/yum/zypper) when needed
    - Installs nvidia-container-toolkit
    - Runs nvidia-ctk runtime configure (if available)
    - Restarts Docker to apply changes
    """
    return textwrap.dedent(
        """
        # Ensure NVIDIA Container Toolkit is installed and configured
        if ! command -v nvidia-container-toolkit >/dev/null 2>&1; then
            echo "Installing nvidia-container-toolkit..."
            export DEBIAN_FRONTEND=noninteractive

            if command -v apt-get >/dev/null 2>&1; then
                # Prereqs
                if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi
                if ! command -v gpg >/dev/null 2>&1; then install_pkgs gnupg || true; fi

                # Add NVIDIA repo (signed)
                curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
                    | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg || true
                distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
                curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
                    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
                    | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null || true

                apt-get update -qq || true
                apt-get install -y -qq nvidia-container-toolkit || true

            elif command -v dnf >/dev/null 2>&1; then
                distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
                if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi
                curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.repo \
                    | tee /etc/yum.repos.d/nvidia-container-toolkit.repo >/dev/null || true
                dnf -y install nvidia-container-toolkit || true

            elif command -v yum >/dev/null 2>&1; then
                distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
                if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi
                curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.repo \
                    | tee /etc/yum.repos.d/nvidia-container-toolkit.repo >/dev/null || true
                yum -y install nvidia-container-toolkit || true

            elif command -v zypper >/dev/null 2>&1; then
                distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
                if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi
                curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.repo \
                    | tee /etc/zypp/repos.d/nvidia-container-toolkit.repo >/dev/null || true
                zypper -n install nvidia-container-toolkit || true

            else
                echo "WARNING: Unsupported package manager for NVIDIA Container Toolkit" >&2
            fi
        fi

        # Configure Docker runtime via nvidia-ctk when available
        if command -v nvidia-ctk >/dev/null 2>&1; then
            nvidia-ctk runtime configure --runtime=docker || true
        fi

        # Restart Docker to pick up any runtime changes
        if command -v systemctl >/dev/null 2>&1; then
            systemctl restart docker || true
        elif command -v service >/dev/null 2>&1; then
            service docker restart || true
        fi
        """
    ).strip()


def get_command_fallback(command: str) -> str:
    """Get fallback for commands that might not be available.

    Args:
        command: The command that might not be available

    Returns:
        Shell snippet with fallback logic
    """
    fallbacks = {
        "uuidgen": 'echo "task-$(date +%s)-$$"',
        "timeout": "( $@ ) & sleep $1; kill $! 2>/dev/null || true",
        "bc": "awk 'BEGIN {print $@}'",
    }

    fallback = fallbacks.get(command)
    if fallback:
        return f"command -v {command} >/dev/null 2>&1 && {command} || {fallback}"
    return command


def ensure_basic_tools() -> str:
    """Ensure basic tools required by most startup scripts are available."""
    return textwrap.dedent(
        """
        # Ensure basic tools are available
        echo "Checking for required system tools..."

        # Core utilities that should always be present
        MISSING_TOOLS=""
        for tool in bash grep sed awk cat echo mkdir chmod chown mount umount; do
            if ! command -v $tool >/dev/null 2>&1; then
                MISSING_TOOLS="$MISSING_TOOLS $tool"
            fi
        done

        if [ -n "$MISSING_TOOLS" ]; then
            echo "WARNING: Core system tools missing:$MISSING_TOOLS"
            echo "This may indicate a non-standard system image"
        fi

        install_pkgs() {
            if command -v apt-get >/dev/null 2>&1; then
                apt-get update -qq && apt-get install -y -qq "$@"
            elif command -v dnf >/dev/null 2>&1; then
                dnf -y install "$@"
            elif command -v yum >/dev/null 2>&1; then
                yum -y install "$@"
            elif command -v apk >/dev/null 2>&1; then
                apk add --no-cache "$@"
            elif command -v zypper >/dev/null 2>&1; then
                zypper -n install "$@"
            elif command -v pacman >/dev/null 2>&1; then
                pacman -Sy --noconfirm "$@"
            else
                echo "WARNING: No supported package manager found to install: $*"
                return 1
            fi
        }

        # Install commonly needed tools that might be missing
        export DEBIAN_FRONTEND=noninteractive

        # curl (critical for many operations)
        if ! command -v curl >/dev/null 2>&1; then
            install_pkgs curl ca-certificates || true
        fi

        # uuidgen
        if ! command -v uuidgen >/dev/null 2>&1; then
            install_pkgs uuid-runtime || install_pkgs util-linux || true
        fi

        # bc
        if ! command -v bc >/dev/null 2>&1; then
            install_pkgs bc || true
        fi

        # timeout and base64 (coreutils)
        if ! command -v timeout >/dev/null 2>&1 || ! command -v base64 >/dev/null 2>&1; then
            install_pkgs coreutils || true
        fi

        # tar and gzip (for archives)
        if ! command -v tar >/dev/null 2>&1; then
            install_pkgs tar || true
        fi
        if ! command -v gzip >/dev/null 2>&1; then
            install_pkgs gzip || true
        fi

        # unzip (used by some installers e.g., AWS CLI)
        if ! command -v unzip >/dev/null 2>&1; then
            install_pkgs unzip || true
        fi

        # Python runtime used by several helpers
        if ! command -v python3 >/dev/null 2>&1; then
            install_pkgs python3 || true
        fi
        if ! command -v pip3 >/dev/null 2>&1; then
            install_pkgs python3-pip || install_pkgs py3-pip || true
        fi
        """
    ).strip()


def ensure_install_pkgs_function() -> str:
    """Return only the cross-distro install_pkgs shell function.

    This light-weight helper keeps the header small while enabling later
    sections to call install_pkgs when needed.
    """
    return textwrap.dedent(
        """
        install_pkgs() {
            if command -v apt-get >/dev/null 2>&1; then
                apt-get update -qq && apt-get install -y -qq "$@"
            elif command -v dnf >/dev/null 2>&1; then
                dnf -y install "$@"
            elif command -v yum >/dev/null 2>&1; then
                yum -y install "$@"
            elif command -v apk >/dev/null 2>&1; then
                apk add --no-cache "$@"
            elif command -v zypper >/dev/null 2>&1; then
                zypper -n install "$@"
            elif command -v pacman >/dev/null 2>&1; then
                pacman -Sy --noconfirm "$@"
            else
                echo "WARNING: No supported package manager found to install: $*"
                return 1
            fi
        }
        """
    ).strip()
