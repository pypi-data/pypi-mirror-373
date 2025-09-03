"""Manages the lifecycle of development VMs for the flow dev command."""

import hashlib
import logging
import os
import time

from flow.sdk.client import Flow, TaskConfig
from flow.sdk.models import Task, TaskStatus

logger = logging.getLogger(__name__)


class DevVMManager:
    """Manages the lifecycle of development VMs."""

    def __init__(self, flow_client: Flow):
        """Initialize VM manager.

        Args:
            flow_client: Flow SDK client instance
        """
        self.flow_client = flow_client
        self.dev_vm_prefix = "flow-dev"

    def get_dev_vm_name(self, force_unique: bool = False) -> str:
        """Generate consistent dev VM name for current user.

        Args:
            force_unique: If True, append a unique suffix to ensure uniqueness

        Returns:
            Unique dev VM name based on username
        """
        from flow.cli.utils.name_generator import generate_unique_name

        user = os.environ.get("USER", "default")
        # Create a short hash to ensure uniqueness
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        base_name = f"dev-{name_hash}"

        # Use shared utility for consistent unique name generation
        if force_unique:
            vm_name = generate_unique_name(prefix="dev", base_name=base_name, add_unique=True)
        else:
            vm_name = base_name

        logger.debug(f"Generated dev VM name: {vm_name} for user: {user}")
        return vm_name

    def find_dev_vm(self, include_not_ready: bool = False, region: str | None = None):
        """Find existing dev VM for current user.

        Args:
            include_not_ready: If True, also return VMs without SSH access yet

        Returns:
            Task object if found, None otherwise
        """
        base_vm_name = self.get_dev_vm_name()
        # Build the expected dev VM prefix for this user
        user = os.environ.get("USER", "default")
        # The prefix matches our new naming pattern
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        vm_prefix = f"dev-{name_hash}"

        # Also check for legacy naming pattern
        legacy_prefix = f"flow-dev-{user}"

        try:
            # Discover tasks (include provisioning if requested)
            logger.debug(
                f"Searching for existing dev VM with prefix: {vm_prefix} or {legacy_prefix}"
            )
            if include_not_ready:
                tasks = self.flow_client.tasks.list()
            else:
                tasks = self.flow_client.tasks.list(status=TaskStatus.RUNNING)

            logger.debug(f"Found {len(tasks)} tasks to inspect")

            # Find all tasks that match our dev VM naming patterns (old and new)
            # Since we can't reliably check config.env (it's not returned by list_tasks),
            # we rely on the naming convention which is unique per user
            dev_vm_candidates = []
            not_ready_vms = []

            for task in tasks:
                # Check both new and legacy naming patterns
                if task.name.startswith(vm_prefix) or task.name.startswith(legacy_prefix):
                    # Filter by region when specified
                    try:
                        if region and getattr(task, "region", None) and task.region != region:
                            continue
                    except Exception:
                        # If region not present on task, don't filter it out
                        pass
                    logger.debug(f"Found potential dev VM: {task.name} (ID: {task.task_id})")
                    # Separate ready and not-ready VMs
                    if task.ssh_host:
                        dev_vm_candidates.append(task)
                        logger.debug(f"  - Has SSH access: {task.ssh_host}:{task.ssh_port}")
                    else:
                        # Only consider as not-ready if in an active/provisioning status
                        from flow.cli.utils.status_utils import is_active_like

                        if is_active_like(task):
                            not_ready_vms.append(task)
                            logger.debug("  - No SSH access yet (provisioning/active)")

            # If we only have not-ready VMs and include_not_ready is True, return the newest
            if include_not_ready and not dev_vm_candidates and not_ready_vms:
                not_ready_vms.sort(key=lambda t: t.created_at, reverse=True)
                logger.info(f"Found {len(not_ready_vms)} dev VM(s) still provisioning")
                return not_ready_vms[0]

            if not dev_vm_candidates:
                logger.debug("No ready dev VMs found")
                return None

            # If we have multiple dev VMs, use the most recent one
            if len(dev_vm_candidates) > 1:
                logger.info(f"Found {len(dev_vm_candidates)} ready dev VMs - selecting most recent")
                # Sort by created_at timestamp (newest first)
                dev_vm_candidates.sort(key=lambda t: t.created_at, reverse=True)

            selected_vm = dev_vm_candidates[0]
            logger.info(f"Using existing dev VM: {selected_vm.name} (ID: {selected_vm.task_id})")
            return selected_vm

        except Exception as e:
            logger.warning(f"Error searching for dev VM: {e}")
            return None

    def create_dev_vm(
        self,
        instance_type: str = None,
        region: str | None = None,
        ssh_keys: list = None,
        max_price_per_hour: float = None,
        no_unique: bool = False,
        image: str | None = None,
    ) -> Task:
        """Create a new dev VM.

        Args:
            instance_type: GPU/CPU instance type
            ssh_keys: SSH keys for access
            max_price_per_hour: Maximum hourly price in USD
            no_unique: If True, don't add unique suffix on name conflict

        Returns:
            Task object for the new VM
        """
        # First try with consistent name
        vm_name = self.get_dev_vm_name()

        # Default instance type for dev
        if not instance_type:
            instance_type = os.environ.get("FLOW_DEV_INSTANCE_TYPE", "h100")

        # Create VM configuration
        # For dev VMs, we use a startup script that prepares the environment
        # Note: Since TaskConfig doesn't support Docker socket mounts or privileged mode,
        # the dev VM runs containers directly on the host VM, not nested inside another container
        dev_startup_script = """#!/bin/bash
set -e

# Install essential dev tools
apt-get update -qq
apt-get install -y -qq git vim htop curl wget python3-pip

# Install Docker in a more robust way
if ! command -v docker >/dev/null 2>&1; then
    echo "Installing Docker..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get install -y -qq docker.io || true
    elif command -v yum >/dev/null 2>&1; then
        yum install -y docker || true
        systemctl enable docker || true
        systemctl start docker || true
    fi
fi

# Verify Docker works
docker info >/dev/null 2>&1 || echo "Docker may not be ready yet"

# Keep VM running
exec sleep infinity
"""

        config_dict = {
            "name": vm_name,
            "unique_name": False,  # We handle uniqueness ourselves with get_dev_vm_name
            "instance_type": instance_type,
            # Use Docker image to trigger DockerSection which handles dev VM setup
            "image": image or os.environ.get("FLOW_DEV_IMAGE", "ubuntu:22.04"),
            "command": ["bash", "-c", dev_startup_script],
            "env": {
                "FLOW_DEV_VM": "true",
                "FLOW_DEV_USER": os.environ.get("USER", "default"),
                "DEBIAN_FRONTEND": "noninteractive",
            },
            "ssh_keys": ssh_keys or [],
            "priority": "high",  # High priority for dev VMs
        }

        # Respect explicit region preference when provided
        if region is not None:
            config_dict["region"] = region

        # Add max_price_per_hour if specified
        if max_price_per_hour is not None:
            config_dict["max_price_per_hour"] = max_price_per_hour

        config = TaskConfig(**config_dict)

        # Submit task
        logger.info(f"Creating dev VM with instance type: {instance_type}")
        try:
            return self.flow_client.run(config)
        except Exception as e:
            # Check if it's a name conflict - providers should raise NameConflictError
            # but also handle legacy string matching for backward compatibility
            error_msg = str(e)
            if "Name already used" in error_msg or "already exists" in error_msg.lower():
                # Prefer attaching to the existing dev VM rather than creating a new uniquely named one
                logger.info("Dev VM name already in use; attempting to use the existing VM")
                existing = self.find_dev_vm(include_not_ready=True)
                if existing:
                    return existing
                # Briefly wait and retry once to account for eventual consistency
                time.sleep(2)
                existing = self.find_dev_vm(include_not_ready=True)
                if existing:
                    return existing
                if no_unique:
                    # User explicitly doesn't want a uniquely-suffixed name
                    raise
                # As a last resort, we can generate a unique suffix to avoid blocking the user
                # But this will create a second dev VM; recommend using --force-new if that's desired.
                logger.info("Existing VM not discoverable; generating unique dev VM name")
                vm_name = self.get_dev_vm_name(force_unique=True)
                config.name = vm_name
                return self.flow_client.run(config)
            else:
                # Re-raise other errors
                raise

    def stop_dev_vm(self) -> bool:
        """Stop the current user's dev VM.

        This cancels the dev VM even if it is not SSH-ready yet (for example,
        when the task is in a PENDING or PROVISIONING state). This ensures that
        ``flow dev --stop`` is effective during startup as well as when the VM
        is fully running.

        Returns:
            bool: True if a dev VM was found and cancellation was requested;
            False if no dev VM was found for the current user.
        """
        # Include not-ready/provisioning states so users can stop a VM that
        # is still starting up (no SSH yet) or pending in the queue.
        vm = self.find_dev_vm(include_not_ready=True)
        if vm:
            self.flow_client.cancel(vm.task_id)
            return True
        return False
