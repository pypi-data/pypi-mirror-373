"""Health check command for diagnosing Flow SDK issues.

This command provides comprehensive diagnostics for common Flow SDK problems
including connectivity, authentication, state synchronization, and instance health.
"""

from __future__ import annotations

import hashlib
import json
import json as jsonlib
import math
import random
import subprocess
import time
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import click
import httpx
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

# SSHTunnelManager will be obtained from the provider at runtime
from flow.cli.commands.base import BaseCommand
from flow.cli.ui.facade.views import HealthRenderer, create_flow_table
from flow.cli.utils.animations import AnimatedEllipsisProgress
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.hyperlink_support import hyperlink_support
from flow.cli.utils.step_progress import StepTimeline
from flow.cli.utils.theme_manager import theme_manager
from flow.errors import FlowError
from flow.sdk.client import Flow
from flow.sdk.health import (
    GPUdStatus,
    GPUdStatusDiagnoser,
    GPUInstanceDetector,
    HealthCheckMessageHandler,
    MetricsAggregator,
    MetricsStore,
    NodeHealthSnapshotFactory,
    SSHConnectionHandler,
    TaskAgeCalculator,
)
from flow.sdk.health_models import (
    ComponentHealth,
    FleetHealthSummary,
    GPUMetric,
    GPUProcess,
    HealthState,
    HealthStatus,
    NodeHealthSnapshot,
    SystemEvent,
    SystemMetrics,
)
from flow.sdk.models import TaskStatus

console = theme_manager.create_console()


class HealthChecker:
    """Performs comprehensive health checks on Flow SDK setup."""

    def __init__(self, flow_client: Flow):
        self.flow_client = flow_client
        self.issues = []
        self.warnings = []
        self.successes = []
        self.renderer = HealthRenderer()
        self.metrics_store = MetricsStore()
        self.gpud_diagnoser = GPUdStatusDiagnoser()
        self.snapshot_factory = NodeHealthSnapshotFactory()
        self.message_handler = HealthCheckMessageHandler(self.issues, self.warnings, self.successes)
        self.gpu_detector = GPUInstanceDetector()
        self.age_calculator = TaskAgeCalculator()
        # Load health config and reuse HTTP client for GPUd calls
        self._http = httpx.Client(headers={"User-Agent": "flow-compute-health/1.0"})

        # Configurable health settings
        cfg = getattr(flow_client, "config", None)
        hc = getattr(cfg, "health_config", {}) or {}
        # Endpoints ordered preference
        self.health_endpoints: list[str] = list(
            hc.get("endpoints", ["/healthz", "/readyz", "/livez", "/health"])
        )
        # Timeouts
        self.gpud_health_timeout: int = int(hc.get("gpud_health_timeout", 2))
        self.gpud_http_timeout: int = int(hc.get("gpud_http_timeout", 5))
        self.ssh_curl_timeout: int = int(hc.get("ssh_curl_timeout", 5))
        self.tunnel_timeout_seconds: int = int(hc.get("tunnel_timeout", 10))
        # Port/bind
        self.gpud_port: int = int(hc.get("gpud_port", 15132))
        # Thresholds table
        thresholds = hc.get("thresholds", {})
        self.thresholds = dict(thresholds) if isinstance(thresholds, dict) else {}

    def add_issue(self, category: str, message: str, suggestion: str = None):
        """Add a critical issue."""
        self.issues.append({"category": category, "message": message, "suggestion": suggestion})

    def add_warning(self, category: str, message: str, suggestion: str = None):
        """Add a warning."""
        self.warnings.append({"category": category, "message": message, "suggestion": suggestion})

    def add_success(self, category: str, message: str):
        """Add a success."""
        self.successes.append({"category": category, "message": message})

    def check_connectivity(self) -> bool:
        """Check API connectivity."""
        try:
            # Demo mode: treat connectivity as OK
            if getattr(self.flow_client.config, "provider", "") == "mock":
                self.add_success("Connectivity", "Demo mode (mock): connectivity OK")
                return True
            # Try a simple API call to verify connectivity
            # Use tasks.list with limit=1 as a lightweight connectivity check
            self.flow_client.tasks.list(limit=1)
            self.add_success("Connectivity", "Successfully connected to Flow API")
            return True
        except FlowError as e:
            self.add_issue(
                "Connectivity",
                f"Cannot connect to Flow API: {e!s}",
                "Check your internet connection and API endpoint configuration",
            )
            return False

    def check_authentication(self) -> bool:
        """Check authentication status."""
        try:
            # Demo mode: reflect demo API key and basic project/region
            if getattr(self.flow_client.config, "provider", "") == "mock":
                cfg = getattr(self.flow_client, "config", None)
                demo_cfg = {}
                project = None
                region = None
                if cfg and isinstance(getattr(cfg, "provider_config", None), dict):
                    project = cfg.provider_config.get("project")
                    region = cfg.provider_config.get("region")
                    demo_cfg = cfg.provider_config.get("demo", {}) or {}
                has_demo_key = bool(demo_cfg.get("api_key"))
                if has_demo_key:
                    self.add_success(
                        "Authentication",
                        f"Demo mode (mock): demo API key configured • project='{project or 'demo'}' region='{region or 'demo-region-1'}'",
                    )
                else:
                    self.add_success(
                        "Authentication",
                        "Demo mode (mock): no authentication required (demo API key optional)",
                    )
                return True
            # Get current config
            config = self.flow_client.config
            if config and config.provider_config:
                project = config.provider_config.get("project", "unknown")
                region = config.provider_config.get("region", "unknown")
                if project != "unknown":
                    self.add_success(
                        "Authentication",
                        f"Authenticated to project '{project}' in region '{region}'",
                    )
                    return True
                else:
                    self.add_issue(
                        "Authentication",
                        "No project configured",
                        "Run 'flow init' to configure project",
                    )
                    return False
            else:
                self.add_issue(
                    "Authentication",
                    "No authentication configured",
                    "Run 'flow init' to configure authentication",
                )
                return False
        except Exception as e:  # noqa: BLE001 - provider config surface can vary
            self.add_issue(
                "Authentication",
                f"Authentication error: {e!s}",
                "Run 'flow init' to reconfigure authentication",
            )
            return False

    def check_ssh_keys(self) -> bool:
        """Check SSH key configuration."""
        try:
            # Demo mode: skip SSH key checks
            if getattr(self.flow_client.config, "provider", "") == "mock":
                self.add_success("SSH Keys", "Demo mode (mock): SSH keys not required")
                return True
            config_path = Path.home() / ".flow" / "config.yaml"
            if not config_path.exists():
                self.add_issue(
                    "SSH Keys",
                    "Flow configuration file not found",
                    "Run 'flow init' to set up Flow SDK",
                )
                return False

            # Read config to check SSH keys
            import yaml

            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            ssh_key_path = config.get("ssh_key_path")
            if not ssh_key_path:
                self.add_warning(
                    "SSH Keys",
                    "No SSH key path configured",
                    "SSH keys will be auto-generated when needed",
                )
            else:
                # Expand path and check if it exists
                key_path = Path(ssh_key_path).expanduser()
                if key_path.exists():
                    self.add_success("SSH Keys", f"SSH key found at {key_path}")
                else:
                    self.add_issue(
                        "SSH Keys",
                        f"SSH key not found at {key_path}",
                        "Generate a new SSH key or update the path in ~/.flow/config.yaml",
                    )
                    return False

            return True
        except Exception as e:  # noqa: BLE001 - tolerate YAML/env variations and continue
            self.add_warning(
                "SSH Keys",
                f"Could not check SSH keys: {e!s}",
                "SSH functionality may be limited",
            )
            return True

    def check_instance_sync(self) -> dict[str, list[dict]]:
        """Check for state synchronization issues between Flow and provider.

        Uses the same TaskFetcher as 'flow status' for consistency.
        Early returns on provider connectivity issues to avoid false positives.
        """
        # Use the same task fetcher as status command for consistency
        from flow.cli.utils.task_fetcher import TaskFetcher

        fetcher = TaskFetcher(self.flow_client)

        # Get active tasks using proven logic from status command
        active_tasks = [
            task
            for task in fetcher.fetch_all_tasks(limit=100, prioritize_active=True)
            if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]
        ]

        # Early return if no active tasks
        if not active_tasks:
            self.add_success("State Sync", "No active tasks to synchronize")
            return {"flow_tasks": [], "provider_instances": [], "orphaned": [], "missing": []}

        # Build Flow task list
        flow_task_map = {
            task.task_id: {
                "id": task.task_id,
                "name": task.name,
                "status": task.status.value if hasattr(task.status, "value") else str(task.status),
            }
            for task in active_tasks
        }

        # Get provider state - fail fast if provider is unreachable
        provider_task_ids = self._get_provider_task_ids()
        if provider_task_ids is None:
            # Provider unreachable - return early to avoid false "missing" reports
            return {
                "flow_tasks": list(flow_task_map.values()),
                "provider_instances": [],
                "orphaned": [],
                "missing": [],
            }

        # Find discrepancies
        missing = [
            task_data
            for task_id, task_data in flow_task_map.items()
            if task_id not in provider_task_ids
        ]

        # Report results
        if missing:
            self.add_issue(
                "State Sync",
                f"Found {len(missing)} tasks missing from provider",
                "These tasks are tracked by Flow but don't exist in the provider. Try 'flow status --force-refresh'.",
            )
        else:
            self.add_success(
                "State Sync",
                f"State is synchronized: {len(active_tasks)} active tasks",
            )

        return {
            "flow_tasks": list(flow_task_map.values()),
            "provider_instances": [{"task_id": tid} for tid in provider_task_ids],
            "orphaned": [],  # Could be extended to check for orphaned provider tasks
            "missing": missing,
        }

    def _get_provider_task_ids(self) -> set[str] | None:
        """Get task IDs from provider, returns None if provider unreachable.

        This is a focused method that just gets task IDs, making it easy to test
        and reason about. Returns None to signal provider connectivity issues.
        """
        try:
            task_ids = set()

            # Fetch both running and pending tasks
            for status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
                try:
                    tasks = self.flow_client.list_tasks(status=status, limit=100)
                    task_ids.update(task.task_id for task in tasks)
                except Exception as e:  # noqa: BLE001 - provider SDK exceptions vary
                    # Log but continue - partial data is better than none
                    self.add_warning(
                        "State Sync",
                        f"Could not list {status.value} tasks from provider: {e!s}",
                    )

            # If we got no tasks at all, assume provider is unreachable
            if not task_ids:
                self.add_issue(
                    "State Sync",
                    "Could not retrieve any tasks from provider",
                    "Provider may be unreachable or authentication may have failed. Check provider connectivity.",
                )
                return None

            return task_ids

        except Exception as e:  # noqa: BLE001 - provider SDK exceptions vary
            self.add_issue(
                "State Sync",
                f"Failed to connect to provider: {e!s}",
                "Check your provider configuration and network connectivity.",
            )
            return None

    def check_instance_health(self, task_id: str) -> dict[str, any]:
        """Check health of a specific instance."""
        health = {
            "task_id": task_id,
            "reachable": False,
            "ssh_ready": False,
            "age_hours": None,
            "issues": [],
        }

        try:
            task = self.flow_client.get_task(task_id)

            # Calculate age
            if task.created_at:
                # Ensure both datetimes are timezone-aware
                now = datetime.now(timezone.utc)
                # If created_at is naive (no timezone), assume UTC
                if task.created_at.tzinfo is None:
                    created_at = task.created_at.replace(tzinfo=timezone.utc)
                else:
                    created_at = task.created_at
                age = now - created_at
                health["age_hours"] = age.total_seconds() / 3600

            # Check if we have SSH info
            if not task.ssh_host:
                health["issues"].append("No SSH host assigned")
                return health

            # Check network reachability (cross-platform) using TCP connect to SSH port
            try:
                import socket

                ssh_port = int(getattr(task, "ssh_port", 22) or 22)
                with socket.create_connection((task.ssh_host, ssh_port), timeout=3):
                    health["reachable"] = True
            except OSError:
                health["reachable"] = False
                health["issues"].append("SSH port unreachable (network/firewall)")

            # Check SSH readiness
            if health["reachable"]:
                try:
                    # Quick SSH test
                    ssh_test = subprocess.run(
                        [
                            "ssh",
                            "-o",
                            "ConnectTimeout=5",
                            "-o",
                            "StrictHostKeyChecking=no",
                            "-o",
                            "UserKnownHostsFile=/dev/null",
                            "-o",
                            "PasswordAuthentication=no",
                            "-o",
                            "BatchMode=yes",
                            f"{task.ssh_user}@{task.ssh_host}",
                            "echo",
                            "OK",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if ssh_test.returncode == 0:
                        health["ssh_ready"] = True
                    else:
                        stderr = ssh_test.stderr.lower()
                        if "connection reset" in stderr or "kex_exchange" in stderr:
                            health["issues"].append("SSH service is still starting up")
                        elif "connection refused" in stderr:
                            health["issues"].append("SSH port is closed")
                        elif "permission denied" in stderr:
                            health["issues"].append("SSH authentication failed")
                        else:
                            health["issues"].append(f"SSH test failed: {ssh_test.stderr.strip()}")
                except subprocess.TimeoutExpired:
                    health["issues"].append("SSH connection timed out")
                except Exception as e:  # noqa: BLE001 - capture unexpected ssh client failures
                    health["issues"].append(f"SSH test error: {e!s}")

        except FlowError as e:
            health["issues"].append(f"Could not fetch task details: {e!s}")

        return health

    def check_gpu_health(
        self, task_id: str, _demo_scenario: str | None = None
    ) -> NodeHealthSnapshot | None:
        """Check GPU health for a specific task using GPUd API.

        Args:
            task_id: Task ID to check

        Returns:
            NodeHealthSnapshot if successful, None otherwise
        """
        try:
            task = self.flow_client.get_task(task_id)

            # Demo mode: do not attempt any SSH or network operations
            try:
                if getattr(self.flow_client.config, "provider", "") == "mock":
                    # Produce realistic demo snapshot with synthetic but deterministic data
                    return self._create_demo_snapshot(task, scenario_override=_demo_scenario)
            except Exception:
                # If demo detection fails, continue with normal path
                pass

            # Skip non-GPU instances
            if not self.gpu_detector.is_gpu_instance(task.instance_type):
                self.add_warning("GPU Health", f"Task {task_id} is not using a GPU instance type")
                return None

            # Calculate task age
            task_age_hours = self.age_calculator.get_age_hours(task.created_at)

            # Default GPUd port (configurable)
            gpud_port = self.gpud_port

            # Use SSHTunnelManager (from provider) with context manager for automatic cleanup
            try:
                # Try a quick SSH connectivity check first (optional marker check)
                marker_status = None
                try:
                    ssh_prefix = self._build_ssh_command_prefix(task)
                    marker_status = self.gpud_diagnoser.check_gpud_marker(ssh_prefix)
                except Exception:
                    # Skip marker check if SSH is problematic
                    pass

                # Add timeout protection for SSH tunnel using cross-platform approach
                # Use threading.Timer for cross-platform timeout
                import threading

                tunnel_timeout = threading.Event()

                def timeout_handler():
                    tunnel_timeout.set()

                # Set timer for tunnel creation (configurable)
                timer = threading.Timer(float(self.tunnel_timeout_seconds), timeout_handler)
                timer.start()

                # Initialize for use in finally
                diagnosis = None
                snapshot_result: NodeHealthSnapshot | None = None

                try:
                    # Try to get SSHTunnelManager from provider
                    try:
                        ssh_tunnel_manager = self.flow_client.get_ssh_tunnel_manager()
                        use_tunnel_manager = True
                    except Exception:
                        # Provider doesn't support SSH tunnels, fall back to direct query
                        ssh_tunnel_manager = None
                        use_tunnel_manager = False

                    # Create tunnel with timeout check
                    tunnel = None
                    api_url = None

                    if use_tunnel_manager:
                        # Keep tunnel open while we diagnose and fetch metrics
                        with ssh_tunnel_manager.tunnel_context(
                            task=task,
                            remote_port=gpud_port,
                            local_port=0,  # Auto-allocate local port
                        ) as tunnel:
                            # Cancel timer once tunnel is established
                            timer.cancel()

                            if tunnel_timeout.is_set():
                                raise TimeoutError("SSH tunnel creation timed out")

                            api_url = f"http://localhost:{tunnel.local_port}"

                            # Diagnose GPUd status with marker info
                            diagnosis = self._diagnose_with_marker(
                                api_url, task_age_hours, marker_status
                            )

                            # If healthy, fetch metrics before closing tunnel
                            if diagnosis and diagnosis.status == GPUdStatus.HEALTHY:
                                snapshot = self._query_gpud_api(api_url, task)
                                if snapshot:
                                    self.metrics_store.write_snapshot(snapshot)
                                    self._analyze_gpu_health(snapshot)
                                snapshot_result = snapshot
                    else:
                        # Fallback: Use direct SSH command to query GPUd
                        timer.cancel()  # Cancel timer since we're not using tunnel
                        diagnosis = self._check_gpud_via_ssh(task, task_age_hours, marker_status)
                finally:
                    # Cancel timer if still running
                    timer.cancel()

                    # If we already built a snapshot via tunnel, return it first
                    if snapshot_result is not None:
                        return snapshot_result

                    # Handle diagnosis result
                    if diagnosis:
                        self.message_handler.handle_diagnosis(diagnosis, task_id)

                        # Create appropriate snapshot based on diagnosis
                        if diagnosis.status == GPUdStatus.LEGACY:
                            return self.snapshot_factory.create_legacy_snapshot(task)
                        elif diagnosis.status == GPUdStatus.NOT_INSTALLED:
                            return self.snapshot_factory.create_not_installed_snapshot(task)
                        elif diagnosis.status == GPUdStatus.FAILED:
                            return self.snapshot_factory.create_failed_snapshot(
                                task, diagnosis.reason
                            )
                        elif diagnosis.status == GPUdStatus.STARTING:
                            return self.snapshot_factory.create_starting_snapshot(task)
                        elif diagnosis.status == GPUdStatus.HEALTHY:
                            # HEALTHY via SSH fallback: fetch metrics via SSH
                            snapshot = self._query_gpud_api_via_ssh(task)
                            if snapshot:
                                self.metrics_store.write_snapshot(snapshot)
                                self._analyze_gpu_health(snapshot)
                                return snapshot
                            # If fetching fails, fall through to a minimal healthy placeholder
                            return self.snapshot_factory.create_failed_snapshot(
                                task, "GPUd healthy but metrics fetch failed"
                            )
                        else:
                            return self.snapshot_factory.create_failed_snapshot(
                                task, "Unknown GPUd status"
                            )

                    # No diagnosis obtained -> tunnel creation likely failed
                    return self.snapshot_factory.create_unreachable_snapshot(
                        task, "SSH tunnel creation failed"
                    )

            except TimeoutError:
                # SSH tunnel timed out
                self.add_warning(
                    "GPU Health",
                    f"SSH connection to {task_id} timed out",
                    "Node may be unreachable or under heavy load",
                )
                return self.snapshot_factory.create_unreachable_snapshot(
                    task, "SSH connection timeout"
                )
            except Exception as e:
                # SSH connection failed - analyze the error
                ssh_diagnosis = SSHConnectionHandler.analyze_ssh_error(e, task_age_hours)
                self.message_handler.handle_diagnosis(ssh_diagnosis, task_id)

                # Create appropriate snapshot
                if ssh_diagnosis.status == GPUdStatus.LEGACY:
                    return self.snapshot_factory.create_legacy_snapshot(task)
                else:
                    return self.snapshot_factory.create_unreachable_snapshot(
                        task, ssh_diagnosis.reason
                    )

        except Exception as e:
            self.add_issue("GPU Health", f"Failed to check GPU health: {e!s}")
            return None

    def _create_demo_snapshot(
        self, task: Any, scenario_override: str | None = None
    ) -> NodeHealthSnapshot:
        """Create a realistic demo snapshot matching production schema.

        Data is deterministic per-task to provide a stable experience across runs.
        """
        from flow.sdk.health_models import (
            ComponentHealth,
            GPUMetric,
            GPUProcess,
            HealthState,
            SystemEvent,
            SystemMetrics,
        )

        # Deterministic RNG per task
        seed_int = int(hashlib.md5((task.task_id or task.name or "").encode()).hexdigest()[:8], 16)
        rng = random.Random(seed_int)

        # Choose gpu count based on instance_type hint, aligned with status view logic
        # Prefer the shared GPUFormatter.parse_gpu_count for consistency; default to 1
        gpu_count = 1
        try:
            it = (task.instance_type or "").lower()
            try:
                from flow.cli.ui.formatters import GPUFormatter as _GPUFormatter
            except Exception:
                from flow.cli.ui.presentation.gpu_formatter import GPUFormatter as _GPUFormatter

                parsed = _GPUFormatter.parse_gpu_count(it)
                if parsed and parsed > 0:
                    gpu_count = parsed
            except Exception:
                # Fallback simple heuristics
                if any(x in it for x in ["8x", "x8", "8g", "8gpu"]):
                    gpu_count = 8
                elif any(x in it for x in ["2x", "x2", "2g", "2gpu"]):
                    gpu_count = 2
                elif any(x in it for x in ["1x", "x1", "1g", "1gpu"]):
                    gpu_count = 1

            # NVL topology (e.g., gb200nvl72) implies that many GPUs per node
            import re as _re

            m = _re.search(r"nvl(\d{1,3})", it)
            if m:
                try:
                    nvl_count = int(m.group(1))
                    if nvl_count > 0:
                        gpu_count = nvl_count
                except Exception:
                    pass
        except Exception:
            pass

        # Scenario: healthy / degraded / critical split
        scenario_roll = rng.random()
        scenario = (
            scenario_override
            if scenario_override in {"healthy", "degraded", "critical"}
            else (
                "healthy"
                if scenario_roll < 0.6
                else ("degraded" if scenario_roll < 0.85 else "critical")
            )
        )

        # GPU template values
        gpu_name = rng.choice(
            ["NVIDIA A100 80GB", "NVIDIA H100 80GB", "NVIDIA L4"]
        )  # visual variety
        mem_total = 81920 if "100" in gpu_name or "A100" in gpu_name else 24576
        power_limit = 300 if "100" in gpu_name or "A100" in gpu_name else 120
        max_clock = 1410 if "100" in gpu_name or "A100" in gpu_name else 1530

        gpu_metrics: list[GPUMetric] = []
        for idx in range(gpu_count):
            base = rng.random()
            # Utilization per scenario
            if scenario == "healthy":
                utilization = 40 + base * 45  # 40-85%
                ecc = 0
                xid = []
            elif scenario == "degraded":
                utilization = 70 + base * 25  # 70-95%
                ecc = 0 if base < 0.8 else 1
                xid = []
            else:  # critical
                utilization = 85 + base * 15  # 85-100%
                ecc = 1 if base < 0.6 else 2
                xid = ["Xid 79"] if base < 0.5 else ["Xid 13"]

            # Memory/power/clock
            mem_used = int((0.35 + base * 0.55) * mem_total)
            power_draw = min(power_limit, round((0.5 + base * 0.5) * power_limit, 1))
            clock = int(0.9 * max_clock + base * 0.1 * max_clock)

            # Temperature model tied to workload intensity (utilization and memory pressure)
            mem_pct = (mem_used / max(1, mem_total)) * 100.0
            # Base temp: idle ~35-40C, increases with util and memory
            temp = 30.0 + 0.6 * utilization + 0.15 * mem_pct
            # Scenario-based adjustments and bounded noise
            if scenario == "healthy":
                temp += rng.uniform(-3.0, 3.0)
            elif scenario == "degraded":
                temp += rng.uniform(5.0, 9.0)
            else:  # critical
                temp += rng.uniform(10.0, 14.0)
            # Clamp to realistic range
            temp = max(40.0, min(90.0, temp))

            # Processes
            processes: list[GPUProcess] = []
            proc_count = 1 + int(base * 3)
            remaining = mem_used
            for p in range(proc_count):
                if p == proc_count - 1:
                    mem_p = max(128, remaining // 2)
                else:
                    mem_p = max(128, int(remaining * (0.2 + rng.random() * 0.4)))
                remaining = max(0, remaining - mem_p)
                processes.append(
                    GPUProcess(
                        pid=10000 + idx * 100 + p,
                        name=rng.choice(["python", "torchrun", "trainer", "inference-server"]),
                        memory_mb=mem_p,
                        gpu_index=idx,
                    )
                )

            gpu_metrics.append(
                GPUMetric(
                    gpu_index=idx,
                    uuid=f"GPU-{idx}-{task.task_id[:8]}",
                    name=gpu_name,
                    temperature_c=temp,
                    power_draw_w=power_draw,
                    power_limit_w=power_limit,
                    memory_used_mb=mem_used,
                    memory_total_mb=mem_total,
                    gpu_utilization_pct=utilization,
                    sm_occupancy_pct=max(0.0, min(100.0, utilization - 5 + rng.random() * 10)),
                    clock_mhz=clock,
                    max_clock_mhz=max_clock,
                    ecc_errors=ecc,
                    xid_events=xid,
                    nvlink_status=(
                        "healthy"
                        if scenario != "critical"
                        else ("degraded" if base < 0.5 else "healthy")
                    ),
                    processes=processes,
                )
            )

        # System metrics
        if scenario == "healthy":
            cpu = 30 + rng.random() * 40
            mem_used_gb = 45 + rng.random() * 30
            disk = 50 + rng.random() * 20
        elif scenario == "degraded":
            cpu = 60 + rng.random() * 35
            mem_used_gb = 60 + rng.random() * 35
            disk = 70 + rng.random() * 20
        else:
            cpu = 85 + rng.random() * 10
            mem_used_gb = 90 + rng.random() * 30
            disk = 85 + rng.random() * 10

        system_metrics = SystemMetrics(
            cpu_usage_pct=cpu,
            memory_used_gb=mem_used_gb,
            memory_total_gb=128.0,
            disk_usage_pct=disk,
            network_rx_mbps=round(50 + rng.random() * 150, 1),
            network_tx_mbps=round(40 + rng.random() * 120, 1),
            open_file_descriptors=400 + int(rng.random() * 800),
            load_average=[round(cpu / 100 * (1.0 + rng.random()), 2) for _ in range(3)],
        )

        # Health states and events
        health_states: list[HealthState] = []
        events: list[SystemEvent] = []
        now = datetime.now(timezone.utc)

        if scenario == "healthy":
            health_states.append(
                HealthState(
                    component="gpud",
                    health=ComponentHealth.HEALTHY,
                    message="GPUd OK",
                    timestamp=now,
                )
            )
        elif scenario == "degraded":
            health_states.append(
                HealthState(
                    component="nvml",
                    health=ComponentHealth.DEGRADED,
                    message="ECC correctable errors detected",
                    timestamp=now,
                )
            )
            events.append(
                SystemEvent(
                    timestamp=now,
                    component="driver",
                    level="warning",
                    message="Thermal throttling observed",
                    details={},
                )
            )
            # Provider proactive response note for demos
            health_states.append(
                HealthState(
                    component="provider",
                    health=ComponentHealth.HEALTHY,
                    message="Hot-swap node pre-warmed; automatic migration available",
                    timestamp=now,
                )
            )
            events.append(
                SystemEvent(
                    timestamp=now,
                    component="provider",
                    level="info",
                    message="Provider alerted: thermal hotspot detected; replacement node ready",
                    details={"action": "hot-swap-standby", "eta": "<30s"},
                )
            )
        else:
            health_states.append(
                HealthState(
                    component="gpu",
                    health=ComponentHealth.UNHEALTHY,
                    message="High temperature and XID errors",
                    timestamp=now,
                )
            )
            events.append(
                SystemEvent(
                    timestamp=now,
                    component="gpu",
                    level="error",
                    message="Xid error reported",
                    details={"xid": rng.choice([79, 13])},
                )
            )

        # Machine info
        machine_info = {
            "gpud_version": "v0.5.1",
            "hostname": (task.name or task.task_id)[:20],
            "gpu_driver": rng.choice(["550.54", "535.129", "470.223"]),
            "cuda_version": rng.choice(["12.4", "12.1", "11.8"]),
            "note": "Demo mode: synthetic metrics",
        }

        # Annotate cluster topology for accurate totals in demo
        try:
            nodes = int(getattr(task, "num_instances", 1) or 1)
        except Exception:
            nodes = 1
        try:
            machine_info["nodes"] = nodes
            machine_info["gpus_per_node"] = gpu_count
            machine_info["total_gpus"] = nodes * gpu_count
        except Exception:
            pass

        snapshot = NodeHealthSnapshot(
            task_id=task.task_id,
            task_name=task.name or task.task_id,
            instance_id=getattr(task, "instance_id", "demo-instance"),
            instance_type=task.instance_type or "demo.gpu",
            timestamp=datetime.now(timezone.utc),
            gpud_healthy=True,
            gpud_version=machine_info.get("gpud_version"),
            machine_info=machine_info,
            gpu_metrics=gpu_metrics,
            system_metrics=system_metrics,
            health_states=health_states,
            events=events,
        )

        # Compute derived health
        snapshot.health_score = self._calculate_health_score(snapshot)
        snapshot.health_status = self._determine_health_status(snapshot.health_score)

        # In demo, make scenario classification explicit for clarity
        if scenario == "degraded":
            from flow.sdk.health_models import HealthStatus as _HS

            snapshot.health_status = _HS.DEGRADED
            snapshot.health_score = min(snapshot.health_score, 0.72)
        elif scenario == "critical":
            from flow.sdk.health_models import HealthStatus as _HS

            snapshot.health_status = _HS.CRITICAL
            snapshot.health_score = min(snapshot.health_score, 0.55)
        return snapshot

    def _build_ssh_command_prefix(self, task: Any) -> list[str]:
        """Build SSH command prefix for remote commands (centralized)."""
        from flow.cli.utils.ssh_helpers import SshStack

        key_path = SshStack.find_fallback_private_key()
        return SshStack.build_ssh_command(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=key_path,
        )

    def _check_gpud_via_ssh(
        self, task: Any, task_age_hours: float | None, marker_status: str | None
    ) -> Any:
        """Check GPUd health via direct SSH commands (fallback method).

        Args:
            task: Task object with SSH details
            task_age_hours: Age of task in hours
            marker_status: GPUd marker file status

        Returns:
            GPUdDiagnosis object
        """
        from flow.sdk.health import GPUdDiagnosis, GPUdStatus

        try:
            # Build SSH command to check GPUd
            ssh_cmd = self._build_ssh_command_prefix(task)

            # Check if GPUd is responding using configured endpoints
            result = None
            for path in self.health_endpoints:
                check_cmd = ssh_cmd + [
                    "curl",
                    "-s",
                    "-f",
                    "-m",
                    str(self.ssh_curl_timeout),
                    f"http://localhost:{self.gpud_port}{path}",
                ]
                result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    break

            if result and result.returncode == 0:
                # GPUd is healthy - we could fetch more data but for now just mark as healthy
                return GPUdDiagnosis(
                    GPUdStatus.HEALTHY,
                    "GPUd is responding to health checks",
                    {"method": "ssh_fallback"},
                )
            else:
                # Check if GPUd process exists
                ps_cmd = ssh_cmd + ["ps", "aux", "|", "grep", "gpud", "|", "grep", "-v", "grep"]
                ps_result = subprocess.run(
                    ssh_cmd + ["sh", "-c", "ps aux | grep gpud | grep -v grep"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if ps_result.returncode == 0 and "gpud" in ps_result.stdout:
                    return GPUdDiagnosis(
                        GPUdStatus.STARTING,
                        "GPUd process is running but not responding to health checks yet",
                    )
                else:
                    # Check marker status to understand why
                    if marker_status in ["install_failed", "start_failed"]:
                        return GPUdDiagnosis(
                            GPUdStatus.FAILED, f"GPUd setup failed: {marker_status}"
                        )
                    elif task_age_hours and task_age_hours > 24:
                        return GPUdDiagnosis(
                            GPUdStatus.LEGACY, "Task started before GPU monitoring was available"
                        )
                    else:
                        return GPUdDiagnosis(
                            GPUdStatus.NOT_INSTALLED, "GPUd not installed or not running"
                        )

        except subprocess.TimeoutExpired:
            return GPUdDiagnosis(GPUdStatus.FAILED, "SSH command timed out")
        except Exception as e:
            return GPUdDiagnosis(GPUdStatus.FAILED, f"Failed to check GPUd via SSH: {e!s}")

    def _diagnose_with_marker(
        self, api_url: str, task_age_hours: float | None, marker_status: str | None
    ) -> Any:
        """Diagnose GPUd status using both API check and marker file."""
        from flow.sdk.health import GPUdDiagnosis, GPUdStatus

        # Handle explicit failure states
        if marker_status in ["install_failed", "start_failed"]:
            return GPUdDiagnosis(
                GPUdStatus.FAILED,
                f"GPUd setup failed: {marker_status}",
                {"marker_status": marker_status},
            )

        # Handle transitional states
        if marker_status == "not_ready":
            # If recent task, still starting
            if task_age_hours and task_age_hours < 0.1:  # Less than 6 minutes
                return GPUdDiagnosis(
                    GPUdStatus.STARTING,
                    "GPUd is initializing",
                    {"marker_status": marker_status},
                )
            else:
                return GPUdDiagnosis(
                    GPUdStatus.FAILED,
                    "GPUd failed to become ready",
                    {"marker_status": marker_status},
                )

        # Handle "attempted" state - GPUd setup was tried but outcome uncertain
        if marker_status == "attempted":
            # For young tasks, assume still starting
            if task_age_hours and task_age_hours < 0.1:  # Less than 6 minutes
                return GPUdDiagnosis(
                    GPUdStatus.STARTING,
                    "GPUd setup in progress",
                    {"marker_status": marker_status},
                )
            else:
                # For older tasks, assume timeout/failure
                return GPUdDiagnosis(
                    GPUdStatus.FAILED,
                    "GPUd setup timed out",
                    {"marker_status": marker_status},
                )

        # If marker shows running, defer to API check
        if marker_status == "running":
            return self.gpud_diagnoser.diagnose(
                api_url,
                task_age_hours,
                endpoints=self.health_endpoints,
                timeout=self.gpud_health_timeout,
            )

        # If no marker (None), GPUd was never attempted
        if marker_status is None:
            # Could be legacy or manual start
            if task_age_hours and task_age_hours > 24:
                return GPUdDiagnosis(
                    GPUdStatus.LEGACY, "Task started before GPU monitoring was available"
                )
            else:
                return GPUdDiagnosis(
                    GPUdStatus.NOT_INSTALLED,
                    "GPUd not installed (instance started without Flow startup script)",
                )

        # Default to standard diagnosis
        return self.gpud_diagnoser.diagnose(
            api_url,
            task_age_hours,
            endpoints=self.health_endpoints,
            timeout=self.gpud_health_timeout,
        )

    def _query_gpud_api(self, api_url: str, task: Any) -> NodeHealthSnapshot | None:
        """Query GPUd API endpoints to build health snapshot.

        Args:
            api_url: GPUd API base URL
            task: Task object with instance info

        Returns:
            NodeHealthSnapshot if successful
        """
        try:
            # Check if GPUd is running using configured endpoints
            gpud_healthy = False
            for path in self.health_endpoints:
                try:
                    health_resp = (self._http or httpx).get(
                        f"{api_url}{path}", timeout=self.gpud_http_timeout
                    )
                    if health_resp.status_code == 200:
                        gpud_healthy = True
                        break
                except Exception:
                    continue

            if not gpud_healthy:
                self.add_issue(
                    "GPU Health",
                    "GPUd is not responding",
                    "Check if GPUd is running on the instance",
                )
                return None

            # Get machine info
            machine_info = {}
            try:
                resp = (self._http or httpx).get(
                    f"{api_url}/machine-info", timeout=self.gpud_http_timeout
                )
                if resp.status_code == 200:
                    machine_info = resp.json()
            except Exception:
                pass

            # Get GPU metrics from v1/metrics endpoint
            gpu_metrics = []
            try:
                resp = (self._http or httpx).get(
                    f"{api_url}/v1/metrics", timeout=self.gpud_http_timeout
                )
                if resp.status_code == 200:
                    metrics_data = resp.json()
                    # Convert to our GPUMetric format from metrics endpoint
                    for gpu_data in metrics_data.get("gpu_metrics", []):
                        processes = []
                        for p in gpu_data.get("processes", []) or []:
                            try:
                                processes.append(
                                    GPUProcess(
                                        pid=int(p.get("pid", 0)),
                                        name=str(p.get("name", "")),
                                        memory_mb=int(p.get("memory_mb", 0)),
                                        gpu_index=int(p.get("gpu_index", gpu_data.get("index", 0))),
                                    )
                                )
                            except Exception:
                                continue

                        metric = GPUMetric(
                            gpu_index=gpu_data.get("index", 0),
                            uuid=gpu_data.get("uuid", ""),
                            name=gpu_data.get("name", "Unknown"),
                            temperature_c=gpu_data.get("temperature", 0),
                            power_draw_w=gpu_data.get("power_draw", 0),
                            power_limit_w=gpu_data.get("power_limit", 0),
                            memory_used_mb=gpu_data.get("memory_used_mb", 0),
                            memory_total_mb=gpu_data.get("memory_total_mb", 0),
                            gpu_utilization_pct=gpu_data.get("gpu_utilization", 0),
                            sm_occupancy_pct=gpu_data.get("sm_occupancy", 0),
                            clock_mhz=gpu_data.get("clock_mhz", 0),
                            max_clock_mhz=gpu_data.get("max_clock_mhz", 0),
                            ecc_errors=int(gpu_data.get("ecc_errors", 0) or 0),
                            xid_events=list(gpu_data.get("xid_events", []) or []),
                            nvlink_status=str(
                                gpu_data.get("nvlink_status", "healthy") or "healthy"
                            ),
                            processes=processes,
                        )
                        gpu_metrics.append(metric)
            except Exception as e:
                self.add_warning("GPU Health", f"Failed to get GPU metrics: {e!s}")

            # Get system metrics and component states from v1/states endpoint
            system_metrics = None
            health_states: list[HealthState] = []
            try:
                resp = (self._http or httpx).get(
                    f"{api_url}/v1/states", timeout=self.gpud_http_timeout
                )
                if resp.status_code == 200:
                    states_data = resp.json()
                    # Extract system metrics
                    cpu_data = states_data.get("cpu", {})
                    memory_data = states_data.get("memory", {})
                    system_metrics = SystemMetrics(
                        cpu_usage_pct=cpu_data.get("usage_percent", 0),
                        memory_used_gb=memory_data.get("used_gb", 0),
                        memory_total_gb=memory_data.get("total_gb", 0),
                        disk_usage_pct=float(states_data.get("disk", {}).get("usage_pct", 0) or 0),
                        load_average=cpu_data.get("load_average", []),
                    )

                    # Component health
                    components = (
                        states_data.get("health_states")
                        or states_data.get("states")
                        or states_data.get("components")
                        or []
                    )
                    from datetime import datetime as _dt

                    for comp in components:
                        try:
                            health_str = str(comp.get("health", "unknown")).lower()
                            health_enum = (
                                ComponentHealth(health_str)
                                if health_str in ComponentHealth._value2member_map_
                                else ComponentHealth.UNKNOWN
                            )
                            ts_raw = comp.get("timestamp")
                            ts = None
                            if ts_raw:
                                try:
                                    ts = _dt.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                                except Exception:
                                    ts = None
                            health_states.append(
                                HealthState(
                                    component=str(
                                        comp.get("component", comp.get("name", "unknown"))
                                    ),
                                    health=health_enum,
                                    message=str(comp.get("message", "")),
                                    severity=str(comp.get("severity", "info")),
                                    timestamp=ts,
                                )
                            )
                        except Exception:
                            continue
            except Exception:
                pass

            # Get recent events
            events: list[SystemEvent] = []
            try:
                resp = (self._http or httpx).get(
                    f"{api_url}/v1/events", timeout=self.gpud_http_timeout
                )
                if resp.status_code == 200:
                    events_data = resp.json() or {}
                    items = events_data.get(
                        "events", events_data if isinstance(events_data, list) else []
                    )
                    from datetime import datetime as _dt

                    for ev in items:
                        try:
                            ts = _dt.fromisoformat(
                                str(ev.get("timestamp", "")).replace("Z", "+00:00")
                            )
                        except Exception:
                            ts = datetime.now(timezone.utc)
                        events.append(
                            SystemEvent(
                                timestamp=ts,
                                component=str(ev.get("component", "unknown")),
                                level=str(ev.get("level", "info")),
                                message=str(ev.get("message", "")),
                                details=dict(ev.get("details", {})),
                            )
                        )
            except Exception:
                pass

            # Enrich machine_info with cluster topology
            try:
                nodes = int(getattr(task, "num_instances", 1) or 1)
            except Exception:
                nodes = 1
            try:
                machine_info = dict(machine_info or {})
                machine_info.setdefault("nodes", nodes)
                gpn = (
                    len(gpu_metrics)
                    if gpu_metrics
                    else int(machine_info.get("gpus_per_node", 0) or 0)
                )
                machine_info.setdefault("gpus_per_node", gpn)
                if gpn and nodes:
                    machine_info["total_gpus"] = gpn * nodes
            except Exception:
                pass

            # Create snapshot
            snapshot = NodeHealthSnapshot(
                task_id=task.task_id,
                task_name=task.name or task.task_id,
                instance_id=getattr(task, "instance_id", "unknown"),
                instance_type=task.instance_type or "unknown",
                timestamp=datetime.now(timezone.utc),
                gpud_healthy=gpud_healthy,
                gpud_version=machine_info.get("gpud_version"),
                machine_info=machine_info,
                gpu_metrics=gpu_metrics,
                system_metrics=system_metrics,
                health_states=health_states,
                events=events,
            )

            # Calculate health score
            snapshot.health_score = self._calculate_health_score(snapshot)
            snapshot.health_status = self._determine_health_status(snapshot.health_score)

            return snapshot

        except Exception as e:
            self.add_issue("GPU Health", f"Failed to query GPUd API: {e!s}")
            return None

    def _query_gpud_api_via_ssh(self, task: Any) -> NodeHealthSnapshot | None:
        """Query GPUd API via direct SSH curl commands when tunneling is unavailable.

        Args:
            task: Task object with SSH details

        Returns:
            NodeHealthSnapshot if successful, None otherwise
        """
        import json as _json
        import subprocess

        try:
            ssh_cmd = self._build_ssh_command_prefix(task)

            def ssh_curl(path: str) -> tuple[int, str]:
                cmd = ssh_cmd + [
                    "sh",
                    "-c",
                    f"curl -s -f -m {int(self.ssh_curl_timeout)} http://localhost:{int(self.gpud_port)}{path}",
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return res.returncode, res.stdout

            # Health check using configured endpoints
            rc = 1
            for path in self.health_endpoints:
                rc, _ = ssh_curl(path)
                if rc == 0:
                    break
            if rc != 0:
                self.add_issue("GPU Health", "GPUd is not responding via SSH")
                return None

            # Machine info
            machine_info = {}
            try:
                rc, out = ssh_curl("/machine-info")
                if rc == 0 and out:
                    machine_info = _json.loads(out)
            except _json.JSONDecodeError:
                machine_info = {}

            # Metrics
            gpu_metrics: list[GPUMetric] = []
            try:
                rc, out = ssh_curl("/v1/metrics")
                if rc == 0 and out:
                    metrics_data = _json.loads(out)
                    for gpu_data in metrics_data.get("gpu_metrics", []):
                        gpu_metrics.append(
                            GPUMetric(
                                gpu_index=gpu_data.get("index", 0),
                                uuid=gpu_data.get("uuid", ""),
                                name=gpu_data.get("name", "Unknown"),
                                temperature_c=gpu_data.get("temperature", 0),
                                power_draw_w=gpu_data.get("power_draw", 0),
                                power_limit_w=gpu_data.get("power_limit", 0),
                                memory_used_mb=gpu_data.get("memory_used_mb", 0),
                                memory_total_mb=gpu_data.get("memory_total_mb", 0),
                                gpu_utilization_pct=gpu_data.get("gpu_utilization", 0),
                                sm_occupancy_pct=gpu_data.get("sm_occupancy", 0),
                                clock_mhz=gpu_data.get("clock_mhz", 0),
                                max_clock_mhz=gpu_data.get("max_clock_mhz", 0),
                            )
                        )
            except _json.JSONDecodeError:
                gpu_metrics = []

            # System metrics
            system_metrics = None
            try:
                rc, out = ssh_curl("/v1/states")
                if rc == 0 and out:
                    states_data = _json.loads(out)
                    cpu_data = states_data.get("cpu", {})
                    memory_data = states_data.get("memory", {})
                    system_metrics = SystemMetrics(
                        cpu_usage_pct=cpu_data.get("usage_percent", 0),
                        memory_used_gb=memory_data.get("used_gb", 0),
                        memory_total_gb=memory_data.get("total_gb", 0),
                        disk_usage_pct=0,
                        load_average=cpu_data.get("load_average", []),
                    )
            except _json.JSONDecodeError:
                system_metrics = None

            # Enrich machine info with cluster topology
            try:
                nodes = int(getattr(task, "num_instances", 1) or 1)
            except Exception:
                nodes = 1
            try:
                machine_info = dict(machine_info or {})
                machine_info.setdefault("nodes", nodes)
                gpn = (
                    len(gpu_metrics)
                    if gpu_metrics
                    else int(machine_info.get("gpus_per_node", 0) or 0)
                )
                machine_info.setdefault("gpus_per_node", gpn)
                if gpn and nodes:
                    machine_info["total_gpus"] = gpn * nodes
            except Exception:
                pass

            snapshot = NodeHealthSnapshot(
                task_id=task.task_id,
                task_name=task.name or task.task_id,
                instance_id=getattr(task, "instance_id", "unknown"),
                instance_type=task.instance_type or "unknown",
                timestamp=datetime.now(timezone.utc),
                gpud_healthy=True,
                gpud_version=machine_info.get("gpud_version"),
                machine_info=machine_info,
                gpu_metrics=gpu_metrics,
                system_metrics=system_metrics,
            )

            snapshot.health_score = self._calculate_health_score(snapshot)
            snapshot.health_status = self._determine_health_status(snapshot.health_score)
            return snapshot
        except Exception as e:
            self.add_issue("GPU Health", f"Failed to query GPUd API via SSH: {e!s}")
            return None

    def _calculate_health_score(self, snapshot: NodeHealthSnapshot) -> float:
        """Calculate overall health score (v2) with component weights and time-decayed events."""

        # Helper: time-decay for events (hours)
        def decay(age_hours: float, tau: float | None = None) -> float:
            if tau is None:
                try:
                    tau = float(getattr(self, "thresholds", {}).get("event_tau_hours", 6.0))
                except Exception:
                    tau = 6.0
            if age_hours is None or age_hours < 0:
                return 1.0
            try:
                return math.exp(-float(age_hours) / float(tau))
            except Exception:
                return 1.0

        # Helper: compute event penalty
        def event_penalty(
            match_terms: list[str], base_penalty: float = 0.3, tau: float = 6.0
        ) -> float:
            if not snapshot.events:
                return 0.0
            penalty = 0.0
            now = datetime.now(timezone.utc)
            for ev in snapshot.events:
                comp = (ev.component or "").lower()
                msg = (ev.message or "").lower()
                text = comp + " " + msg
                if any(term in text for term in match_terms):
                    severity = (ev.level or "info").lower()
                    sev_weight = (
                        1.0 if severity == "error" else 0.5 if severity == "warning" else 0.2
                    )
                    age_h = None
                    try:
                        age_h = (now - ev.timestamp).total_seconds() / 3600.0
                    except Exception:
                        age_h = None
                    penalty += base_penalty * sev_weight * decay(age_h, tau)
            return min(penalty, 0.8)

        # Thresholds (configurable)
        thresholds = getattr(self, "thresholds", {}) if hasattr(self, "thresholds") else {}
        temp_warn_c = float(thresholds.get("temperature_warning_c", 75))
        temp_crit_c = float(thresholds.get("temperature_critical_c", 85))
        mem_warn_pct = float(thresholds.get("gpu_memory_warning_pct", 90))
        mem_crit_pct = float(thresholds.get("gpu_memory_critical_pct", 98))
        host_cpu_crit_pct = float(thresholds.get("host_cpu_critical_pct", 95))
        host_mem_crit_pct = float(thresholds.get("host_memory_critical_pct", 95))
        host_disk_crit_pct = float(thresholds.get("host_disk_critical_pct", 95))

        # Component: GPU hardware
        if snapshot.gpu_metrics:
            gpu_scores = []
            for g in snapshot.gpu_metrics:
                score = 1.0
                if g.temperature_c >= temp_crit_c:
                    score *= 0.4
                elif g.temperature_c >= temp_warn_c:
                    score *= 0.75
                if g.is_throttling:
                    score *= 0.75
                if getattr(g, "ecc_errors", 0) and g.ecc_errors > 0:
                    score *= 0.6
                if getattr(g, "xid_events", None):
                    score *= 0.7
                gpu_scores.append(score)
            gpu_hardware = sum(gpu_scores) / len(gpu_scores)
        else:
            gpu_hardware = 0.5

        # Component: Memory
        if snapshot.gpu_metrics:
            mem_scores = []
            for g in snapshot.gpu_metrics:
                score = 1.0
                mem_pct = getattr(g, "memory_utilization_pct", 0.0)
                if mem_pct >= mem_crit_pct:
                    score *= 0.7
                elif mem_pct >= mem_warn_pct:
                    score *= 0.85
                if getattr(g, "ecc_errors", 0) and g.ecc_errors > 0:
                    score *= 0.7
                mem_scores.append(score)
            memory_component = sum(mem_scores) / len(mem_scores)
        else:
            memory_component = 0.7

        # Component: Interconnect
        interconnect = 1.0
        nvlink_bad = any(
            str(getattr(g, "nvlink_status", "healthy")).lower() not in ("healthy", "ok")
            for g in (snapshot.gpu_metrics or [])
        )
        if nvlink_bad:
            interconnect *= 0.75
        interconnect -= event_penalty(["nvlink", "nvswitch"], base_penalty=0.25)
        interconnect -= event_penalty(
            ["infiniband", "ib", "rdma", "roce", "nic", "ethernet"], base_penalty=0.25
        )
        interconnect = max(0.0, interconnect)

        # Component: Host
        host = 1.0
        if snapshot.system_metrics:
            if snapshot.system_metrics.cpu_usage_pct >= host_cpu_crit_pct:
                host *= 0.9
            if snapshot.system_metrics.memory_utilization_pct >= host_mem_crit_pct:
                host *= 0.85
            disk = getattr(snapshot.system_metrics, "disk_usage_pct", None)
            if isinstance(disk, (int, float)) and disk >= host_disk_crit_pct:
                host *= 0.9
        else:
            host = 0.8

        # Component: Software
        software = 1.0
        software -= event_penalty(["nccl", "watchdog", "timeout"], base_penalty=0.35)
        software -= event_penalty(["driver", "reset", "xid", "sxid"], base_penalty=0.2)
        software = max(0.0, software)

        weights = {
            "gpu": 0.55,
            "memory": 0.15,
            "interconnect": 0.10,
            "host": 0.10,
            "software": 0.10,
        }
        score = (
            weights["gpu"] * gpu_hardware
            + weights["memory"] * memory_component
            + weights["interconnect"] * interconnect
            + weights["host"] * host
            + weights["software"] * software
        )

        # Confidence annotation
        signals = 0
        present = 0
        for present_flag in [
            bool(snapshot.gpu_metrics),
            True,
            snapshot.system_metrics is not None,
            bool(snapshot.events),
        ]:
            signals += 1
            if present_flag:
                present += 1
        confidence = present / max(1, signals)
        snapshot.machine_info = dict(snapshot.machine_info or {})
        snapshot.machine_info["health_score_breakdown"] = {
            "gpu": round(gpu_hardware, 3),
            "memory": round(memory_component, 3),
            "interconnect": round(interconnect, 3),
            "host": round(host, 3),
            "software": round(software, 3),
            "confidence": round(confidence, 3),
        }

        return max(0.0, min(1.0, score))

    def _determine_health_status(self, score: float) -> HealthStatus:
        """Determine health status from score."""
        if score >= 0.8:
            return HealthStatus.HEALTHY
        elif score >= 0.6:
            return HealthStatus.DEGRADED
        elif score > 0:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.UNKNOWN

    def _analyze_gpu_health(self, snapshot: NodeHealthSnapshot) -> None:
        """Analyze GPU health and add appropriate issues/warnings."""
        if not snapshot.gpu_metrics:
            return

        for gpu in snapshot.gpu_metrics:
            # Temperature warnings
            if gpu.temperature_c >= 85:
                self.add_issue(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} temperature critical: {gpu.temperature_c}°C",
                    "Check cooling and reduce workload",
                )
            elif gpu.temperature_c >= 75:
                self.add_warning(
                    "GPU Health", f"GPU {gpu.gpu_index} temperature high: {gpu.temperature_c}°C"
                )

            # Memory pressure
            if gpu.memory_utilization_pct >= 95:
                self.add_warning(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} memory nearly full: {gpu.memory_utilization_pct:.0f}%",
                    "Consider using gradient checkpointing or smaller batch sizes",
                )

            # Throttling
            if gpu.is_throttling:
                self.add_issue(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} is throttling (clock: {gpu.clock_mhz}MHz, max: {gpu.max_clock_mhz}MHz)",
                    "Check power limits and thermal conditions",
                )

            # ECC errors
            if gpu.ecc_errors > 0:
                self.add_issue(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} has {gpu.ecc_errors} ECC errors",
                    "Monitor for increasing errors; may indicate hardware issues",
                )

        # Overall status
        if snapshot.health_status == HealthStatus.HEALTHY:
            self.add_success("GPU Health", f"All {len(snapshot.gpu_metrics)} GPUs are healthy")

    def _create_live_display_table(self, tasks: list, snapshots: list) -> Table:
        """Create a live-updating table for health display via shared renderer."""
        return self.renderer.render_live_table(tasks, snapshots)

    def _add_live_table_row(self, table: Table, snapshot: NodeHealthSnapshot) -> None:
        """Deprecated: handled by renderer now."""
        return self.renderer.add_live_table_row(table, snapshot)

    def _create_fleet_summary_panel(
        self, snapshots: list, total_tasks: int, current_node: str = None, animation_frame: int = 0
    ) -> Panel:
        """Delegate to renderer to build scan progress panel."""
        return self.renderer.render_scan_progress_panel(
            total_tasks=total_tasks,
            checked_snapshots=snapshots,
            current_node_label=current_node,
            animation_frame=animation_frame,
        )

    def _create_progress_bar(self, percentage: float):
        """Create a gradient progress bar using the shared animation engine.

        Returns a Rich Text renderable so shimmer/edge styling is preserved.
        """
        from rich.text import Text

        from flow.cli.utils.animations import animation_engine

        progress = max(0.0, min(1.0, percentage / 100.0))
        bar = animation_engine.progress_bar(progress, width=35, style="gradient", animated=True)

        # Dynamic color/icon based on progress
        if percentage >= 100:
            color = "green"
            icon = "✓"
        elif percentage >= 75:
            color = "cyan"
            icon = "◉"
        elif percentage >= 50:
            color = "yellow"
            icon = "◉"
        else:
            color = "blue"
            icon = "◉"

        line = Text()
        line.append(icon + " ", style=color)
        line.append_text(bar)
        line.append(f" {percentage:.0f}%")
        return line

    def check_fleet_gpu_health(
        self,
        show_all: bool = False,
        json_mode: bool = False,
        name_filter: str | None = None,
        limit: int | None = None,
        watch_interval: int | None = None,
    ) -> FleetHealthSummary:
        """Check GPU health across all running tasks.

        Args:
            show_all: Include non-GPU tasks
            json_mode: Skip animations if True

        Returns:
            Fleet health summary
        """
        # Get running tasks; include recent large clusters that might have completed
        tasks = self.flow_client.tasks.list(status=TaskStatus.RUNNING, limit=100)
        if not tasks:
            # If nothing is running (common right after reseed), show top recent completed clusters
            try:
                recent = self.flow_client.tasks.list(status=None, limit=200)

                # Prefer largest multi-node clusters
                def score(t: Any) -> int:
                    try:
                        nodes = int(getattr(t, "num_instances", 1) or 1)
                    except Exception:
                        nodes = 1
                    return nodes

                # Pick a handful of the biggest recent clusters for visibility
                recent_sorted = sorted(recent, key=score, reverse=True)
                tasks = [t for t in recent_sorted if score(t) > 1][:5]
            except Exception:
                pass

        if not show_all:
            # Filter GPU tasks using the detector
            tasks = [t for t in tasks if self.gpu_detector.is_gpu_instance(t.instance_type)]

        # Optional substring filter on task name or ID
        if name_filter:
            try:
                nf = name_filter.lower()
                tasks = [
                    t
                    for t in tasks
                    if (t.name and nf in str(t.name).lower())
                    or (t.task_id and nf in str(t.task_id).lower())
                ]
            except Exception:
                # Best-effort filter; ignore errors and proceed
                pass

        # Optional limit
        if limit is not None and isinstance(limit, int) and limit > 0:
            tasks = tasks[:limit]

        if not tasks:
            if not json_mode:
                console.print("[warning]No GPU tasks are currently running[/warning]")
            self.add_warning("GPU Health", "No GPU tasks are currently running")
            return FleetHealthSummary(
                timestamp=datetime.now(timezone.utc),
                total_nodes=0,
                healthy_nodes=0,
                degraded_nodes=0,
                critical_nodes=0,
                total_gpus=0,
                healthy_gpus=0,
                avg_gpu_temperature=0,
                avg_gpu_utilization=0,
                avg_gpu_memory_utilization=0,
            )

        # Collect health snapshots with live display
        snapshots = []
        if json_mode:
            # No animation in JSON mode
            for task in tasks:
                snapshot = self.check_gpu_health(task.task_id)
                if snapshot:
                    snapshots.append(snapshot)
                time.sleep(0.1)  # Rate limiting
        else:
            # Show initial loading with animated progress
            console.print()  # Add spacing
            # Show a short discovery animation before the live view
            with AnimatedEllipsisProgress(
                console,
                f"🔍 Discovering {len(tasks)} GPU nodes",
                animation_style="shimmer",
                start_immediately=True,
            ) as init_progress:
                time.sleep(0.6)
                init_progress.update_message(f"📡 Connecting to {len(tasks)} nodes")
                time.sleep(0.6)
            console.print()

            # Use Rich Live display with continuous animation and parallel checks
            import threading
            from concurrent.futures import ThreadPoolExecutor, as_completed

            animation_frame = 0
            current_checking_node = None
            check_complete = threading.Event()

            def run_checks_parallel():
                nonlocal current_checking_node
                # Bounded concurrency to avoid overwhelming systems
                max_workers = min(8, max(1, len(tasks)))
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # In demo mode, force scenario so that exactly one node is non-healthy in a realistic way
                    is_demo = False
                    is_demo = False
                    with suppress(Exception):
                        is_demo = getattr(self.flow_client.config, "provider", "") == "mock"

                    nonhealthy_idx = 0 if not is_demo else (len(tasks) // 2)

                    future_to_task = {}
                    for idx, t in enumerate(tasks):
                        if is_demo:
                            scenario = "healthy" if idx != nonhealthy_idx else "degraded"
                            future = executor.submit(self.check_gpu_health, t.task_id, scenario)
                        else:
                            future = executor.submit(self.check_gpu_health, t.task_id)
                        future_to_task[future] = t
                    for future in as_completed(future_to_task):
                        t = future_to_task[future]
                        current_checking_node = t.name or t.task_id[:12]
                        try:
                            snapshot = future.result()
                            if snapshot:
                                snapshots.append(snapshot)
                        except Exception:  # noqa: BLE001 - aggregate worker failures and continue
                            pass
                        time.sleep(0.05)
                current_checking_node = None
                check_complete.set()

            checker_thread = threading.Thread(target=run_checks_parallel, daemon=True)
            checker_thread.start()

            with Live(console=console, refresh_per_second=20, vertical_overflow="crop") as live:
                while not check_complete.is_set() or animation_frame < 10:
                    # Update display with animation
                    layout = Layout()
                    layout.split_column(
                        Layout(
                            self._create_fleet_summary_panel(
                                snapshots, len(tasks), current_checking_node, animation_frame
                            ),
                            size=13,
                        ),
                        Layout(self._create_live_display_table(tasks, snapshots)),
                    )
                    live.update(layout)

                    animation_frame += 1
                    time.sleep(0.05)  # 20fps for smooth animation

                # Ensure thread completes
                checker_thread.join(timeout=1.0)

                # Final state is already rendered by the last loop iteration

        # Calculate summary
        summary = self._calculate_fleet_summary(snapshots)

        # Add informative message if nodes lack monitoring
        if snapshots and not json_mode:
            unmonitored = [s for s in snapshots if s.health_status == HealthStatus.UNKNOWN]
            if unmonitored:
                # Concise, actionable message
                install_url = "https://pkg.gpud.dev/install.sh"
                install_link = hyperlink_support.create_link("Install GPUd", install_url)
                info_content = f"""[warning]{len(unmonitored)} of {len(snapshots)} nodes lack GPU monitoring[/warning]

[bold]To enable monitoring:[/bold]
• Future tasks: Use [accent]flow run[/accent] (includes GPUd)
• Current tasks: SSH and run:
  [accent]curl -fsSL {install_url} | bash[/accent]

[bold]Quick action:[/bold] {install_link}
"""
                info_panel = Panel(
                    info_content,
                    title="[bold yellow]⚠ Action Needed[/bold yellow]",
                    border_style=_tm.get_color("warning"),
                    padding=(1, 1),
                    expand=False,
                )
                console.print("\n")
                console.print(info_panel)

        return summary

    def _calculate_fleet_summary(self, snapshots: list[NodeHealthSnapshot]) -> FleetHealthSummary:
        """Calculate fleet-wide health summary from snapshots.

        Args:
            snapshots: List of node health snapshots

        Returns:
            Fleet health summary
        """
        # Separate different types of nodes
        monitored_snapshots = [s for s in snapshots if s.health_status != HealthStatus.UNKNOWN]
        unmonitored_snapshots = [s for s in snapshots if s.health_status == HealthStatus.UNKNOWN]

        # Further categorize unmonitored nodes
        legacy_snapshots = [
            s for s in unmonitored_snapshots if "legacy" in s.machine_info.get("note", "").lower()
        ]
        not_installed_snapshots = [
            s
            for s in unmonitored_snapshots
            if "not installed" in s.machine_info.get("note", "").lower()
        ]

        # Count nodes by status (excluding unmonitored)
        total_nodes = len(monitored_snapshots)
        healthy_nodes = sum(
            1 for s in monitored_snapshots if s.health_status == HealthStatus.HEALTHY
        )
        degraded_nodes = sum(
            1 for s in monitored_snapshots if s.health_status == HealthStatus.DEGRADED
        )
        critical_nodes = sum(
            1 for s in monitored_snapshots if s.health_status == HealthStatus.CRITICAL
        )

        # GPU metrics scaled by nodes to approximate fleet totals
        total_gpus = 0
        healthy_gpus = 0
        sum_temp = 0.0
        sum_util = 0.0
        sum_mem = 0.0
        for s in monitored_snapshots:
            try:
                nodes = int((s.machine_info or {}).get("nodes", 1) or 1)
            except Exception:
                nodes = 1
            gpn = len(s.gpu_metrics)
            if gpn == 0:
                gpn = int((s.machine_info or {}).get("gpus_per_node", 0) or 0)
            total_gpus += nodes * gpn
            for g in s.gpu_metrics:
                if g.temperature_c < 75 and not getattr(g, "is_throttling", False):
                    healthy_gpus += nodes
                sum_temp += g.temperature_c * nodes
                sum_util += g.gpu_utilization_pct * nodes
                sum_mem += getattr(g, "memory_utilization_pct", 0.0) * nodes

        if total_gpus > 0:
            avg_temp = sum_temp / total_gpus
            avg_util = sum_util / total_gpus
            avg_mem = sum_mem / total_gpus
        else:
            avg_temp = 0
            avg_util = 0
            avg_mem = 0

        # Collect critical issues
        critical_issues = []
        warnings = []

        for snapshot in snapshots:
            if snapshot.health_status == HealthStatus.CRITICAL:
                for issue in self.issues:
                    if issue["category"] == "GPU Health":
                        critical_issues.append(
                            {
                                "task_name": snapshot.task_name,
                                "component": "GPU",
                                "message": issue["message"],
                            }
                        )

            for gpu in snapshot.gpu_metrics:
                if gpu.temperature_c >= 85:
                    critical_issues.append(
                        {
                            "task_name": snapshot.task_name,
                            "component": f"GPU {gpu.gpu_index}",
                            "message": f"Critical temperature: {gpu.temperature_c}°C",
                        }
                    )
                elif gpu.temperature_c >= 75:
                    warnings.append(
                        {
                            "task_name": snapshot.task_name,
                            "component": f"GPU {gpu.gpu_index}",
                            "message": f"High temperature: {gpu.temperature_c}°C",
                        }
                    )

        # Add notes about unmonitored tasks
        if legacy_snapshots:
            warnings.append(
                {
                    "task_name": "Legacy Tasks",
                    "component": "GPU Monitoring",
                    "message": f"{len(legacy_snapshots)} task(s) started before GPU monitoring was available",
                }
            )

        if not_installed_snapshots:
            warnings.insert(
                0,
                {
                    "task_name": "Manual Tasks",
                    "component": "GPU Monitoring",
                    "message": f"{len(not_installed_snapshots)} task(s) without GPU monitoring (started manually or via console)",
                },
            )

        return FleetHealthSummary(
            timestamp=datetime.now(timezone.utc),
            total_nodes=total_nodes,
            healthy_nodes=healthy_nodes,
            degraded_nodes=degraded_nodes,
            critical_nodes=critical_nodes,
            total_gpus=total_gpus,
            healthy_gpus=healthy_gpus,
            avg_gpu_temperature=avg_temp,
            avg_gpu_utilization=avg_util,
            avg_gpu_memory_utilization=avg_mem,
            critical_issues=critical_issues[:10],  # Limit to 10
            warnings=warnings[:10],  # Limit to 10
            legacy_nodes=len(legacy_snapshots),  # Track legacy nodes
        )

    def generate_report(self) -> dict[str, any]:
        """Generate comprehensive health report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "issues": len(self.issues),
                "warnings": len(self.warnings),
                "successes": len(self.successes),
            },
            "details": {
                "issues": self.issues,
                "warnings": self.warnings,
                "successes": self.successes,
            },
        }


class HealthCommand(BaseCommand):
    """Health check command implementation."""

    @property
    def name(self) -> str:
        return "health"

    @property
    def help(self) -> str:
        return """Run comprehensive health checks - Diagnose connectivity, auth, GPU monitoring and task health

Subcommands:
  flow health overview                 # Connectivity/auth/SSH/sync checks
  flow health gpu [--watch --filter --limit --json --all]  # GPUd fleet monitoring
  flow health task <id> [--history H --json]               # Task deep dive & history
  flow health storage [--json]         # Local metrics storage stats
"""

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help, invoke_without_command=True)
        @click.option("--json", is_flag=True, help="Output results as JSON")
        @click.option("--fix", is_flag=True, help="Attempt to fix issues automatically")
        @click.option(
            "--verbose", "-v", is_flag=True, help="Show detailed diagnostics and explanations"
        )
        # @demo_aware_command()
        @click.pass_context
        @cli_error_guard(self)
        def health(ctx: click.Context, json: bool, fix: bool, verbose: bool) -> None:
            # When invoked without a subcommand, run the overview checks by default
            if ctx.invoked_subcommand is None:
                if verbose and not json and not fix:
                    console.print("\n[bold]Flow Health Check Details:[/bold]\n")
                    console.print("What it checks:")
                    console.print("  • API connectivity and response times")
                    console.print("  • Authentication and credential validity")
                    console.print("  • SSH key configuration and access")
                    console.print("  • Running instance synchronization")
                    console.print("  • GPU health metrics (temperature, memory, utilization)")
                    console.print("  • Task state consistency\n")
                    return
                self._execute(
                    json,
                    fix,
                    task_id=None,
                    gpu=False,
                    show_all=False,
                    history=None,
                    verbose=verbose,
                )

        # overview subcommand
        @health.command(name="overview", help="Connectivity/auth/SSH/sync checks")
        @click.option("--json", is_flag=True, help="Output results as JSON")
        @click.option("--fix", is_flag=True, help="Attempt to fix issues automatically")
        @click.option(
            "--verbose", "-v", is_flag=True, help="Show detailed diagnostics and explanations"
        )
        # @demo_aware_command()
        @cli_error_guard(self)
        def overview(json: bool, fix: bool, verbose: bool) -> None:
            if verbose and not json and not fix:
                console.print("\n[bold]Flow Health Check Details:[/bold]\n")
                console.print("What it checks:")
                console.print("  • API connectivity and response times")
                console.print("  • Authentication and credential validity")
                console.print("  • SSH key configuration and access")
                console.print("  • Running instance synchronization")
                console.print("  • GPU health metrics (temperature, memory, utilization)")
                console.print("  • Task state consistency\n")
                return
            self._execute(
                json, fix, task_id=None, gpu=False, show_all=False, history=None, verbose=verbose
            )

        # gpu subcommand
        @health.command(name="gpu", help="GPUd fleet monitoring")
        @click.option("--json", is_flag=True, help="Output results as JSON")
        @click.option(
            "--watch", type=int, help="Refresh interval in seconds for continuous monitoring"
        )
        @click.option(
            "--filter", "name_filter", type=str, help="Substring filter for task name or ID"
        )
        @click.option("--limit", type=int, help="Limit number of tasks scanned")
        @click.option("--all", "show_all", is_flag=True, help="Include non-GPU tasks")
        # @demo_aware_command()
        @cli_error_guard(self)
        def gpu(
            json: bool,
            watch: int | None,
            name_filter: str | None,
            limit: int | None,
            show_all: bool,
        ) -> None:
            self._execute(
                json,
                fix=False,
                task_id=None,
                gpu=True,
                show_all=show_all,
                history=None,
                verbose=False,
                watch_interval=watch,
                name_filter=name_filter,
                limit=limit,
            )

        # task subcommand
        @health.command(name="task", help="Task deep dive & history")
        @click.argument("task_id")
        @click.option("--json", is_flag=True, help="Output results as JSON")
        @click.option("--history", type=int, help="Show health history for last N hours")
        # @demo_aware_command()
        @cli_error_guard(self)
        def task(task_id: str, json: bool, history: int | None) -> None:
            self._execute(
                json,
                fix=False,
                task_id=task_id,
                gpu=False,
                show_all=False,
                history=history,
                verbose=False,
            )

        # storage subcommand (local metrics storage stats)
        @health.command(name="storage", help="Local metrics storage stats")
        @click.option("--json", is_flag=True, help="Output results as JSON")
        @cli_error_guard(self)
        def storage(json: bool) -> None:
            store = MetricsStore()
            stats = store.get_storage_stats()
            if json:
                print(jsonlib.dumps(stats, indent=2))
            else:
                table = create_flow_table(show_borders=True)
                table.add_column("Key")
                table.add_column("Value")
                for k, v in stats.items():
                    table.add_row(str(k), str(v))
            console.print(
                Panel(
                    table,
                    title="[bold accent]Metrics Storage[/bold accent]",
                    border_style=theme_manager.get_color("accent"),
                )
            )

        return health

    def _execute(
        self,
        output_json: bool,
        fix: bool,
        task_id: str | None,
        gpu: bool,
        show_all: bool,
        history: int | None,
        verbose: bool = False,
        watch_interval: int | None = None,
        name_filter: str | None = None,
        limit: int | None = None,
    ) -> None:
        """Execute health check command."""
        try:
            from flow.sdk.factory import create_client as _create

            flow_client = _create(auto_init=True)
            checker = HealthChecker(flow_client)

            # GPU health check mode
            if gpu:
                # Check fleet GPU health (has its own animation)
                fleet_summary = checker.check_fleet_gpu_health(
                    show_all=show_all,
                    json_mode=output_json,
                    name_filter=name_filter,
                    limit=limit,
                    watch_interval=watch_interval,
                )

                # No need to display summary here - already shown in live display
                # Just keep JSON output for automation

                # Generate report
                report = checker.generate_report()
                report["fleet_summary"] = {
                    "timestamp": fleet_summary.timestamp.isoformat(),
                    "total_nodes": fleet_summary.total_nodes,
                    "healthy_nodes": fleet_summary.healthy_nodes,
                    "degraded_nodes": fleet_summary.degraded_nodes,
                    "critical_nodes": fleet_summary.critical_nodes,
                    "total_gpus": fleet_summary.total_gpus,
                    "healthy_gpus": fleet_summary.healthy_gpus,
                    "avg_gpu_temperature": fleet_summary.avg_gpu_temperature,
                    "avg_gpu_utilization": fleet_summary.avg_gpu_utilization,
                    "avg_gpu_memory_utilization": fleet_summary.avg_gpu_memory_utilization,
                    "critical_issues": fleet_summary.critical_issues,
                    "warnings": fleet_summary.warnings,
                }

                if output_json:
                    print(json.dumps(report, indent=2))

                return

            # Task health history mode
            if task_id and history:
                if not output_json:
                    with AnimatedEllipsisProgress(
                        console, f"Fetching health history for {task_id}", start_immediately=True
                    ) as progress:
                        # Read historical snapshots
                        snapshots = list(
                            checker.metrics_store.read_snapshots(
                                start_date=datetime.now(timezone.utc) - timedelta(hours=history),
                                task_id=task_id,
                            )
                        )
                else:
                    # JSON mode - no animation
                    snapshots = list(
                        checker.metrics_store.read_snapshots(
                            start_date=datetime.now(timezone.utc) - timedelta(hours=history),
                            task_id=task_id,
                        )
                    )

                if snapshots:
                    # Get latest snapshot for detailed view
                    latest = max(snapshots, key=lambda s: s.timestamp)

                    if not output_json:
                        checker.renderer.render_node_details(latest)

                        # Show history summary
                        if len(snapshots) > 1:
                            aggregator = MetricsAggregator(checker.metrics_store)
                            summary = aggregator.get_task_summary(task_id, history)

                            console.print("\n[bold]Historical Summary[/bold]")
                            console.print(f"Snapshots: {summary['snapshot_count']}")
                            console.print(
                                f"Average Health Score: {summary['health_score']['average']:.1%}"
                            )
                            console.print(
                                f"Min/Max: {summary['health_score']['min']:.1%} / {summary['health_score']['max']:.1%}"
                            )
                            console.print(f"Unhealthy Periods: {summary['unhealthy_periods']}")
                    else:
                        report = {
                            "task_id": task_id,
                            "hours": history,
                            "snapshots": [s.to_dict() for s in snapshots],
                            "latest": latest.to_dict(),
                        }
                        print(json.dumps(report, indent=2))
                else:
                    if not output_json:
                        console.print(
                            f"[warning]No health history found for task {task_id}[/warning]"
                        )
                    else:
                        print(
                            json.dumps(
                                {"error": f"No health history found for task {task_id}"}, indent=2
                            )
                        )

                return

            # Regular health check mode
            if not output_json:
                # Unified step timeline for checks
                timeline = StepTimeline(console)
                timeline.start()
                # Hint for safe skipping
                try:
                    from rich.text import Text

                    from flow.cli.utils.theme_manager import theme_manager

                    accent = theme_manager.get_color("accent")
                    hint = Text()
                    hint.append("  Press ")
                    hint.append("Ctrl+C", style=accent)
                    hint.append(" to skip remaining checks. You can re-run with ")
                    hint.append("flow health --verbose", style=accent)
                    timeline.set_active_hint_text(hint)
                except Exception:
                    pass

                # 1. Connectivity check
                idx_conn = timeline.add_step("Connectivity", show_bar=False)
                timeline.start_step(idx_conn)
                checker.check_connectivity()
                timeline.complete_step()

                # 2. Authentication check
                idx_auth = timeline.add_step("Authentication", show_bar=False)
                timeline.start_step(idx_auth)
                checker.check_authentication()
                timeline.complete_step()

                # 3. SSH keys check
                idx_ssh = timeline.add_step("SSH keys", show_bar=False)
                timeline.start_step(idx_ssh)
                checker.check_ssh_keys()
                timeline.complete_step()

                # 4. Instance sync check
                idx_sync = timeline.add_step("State synchronization", show_bar=False)
                timeline.start_step(idx_sync)
                sync_status = checker.check_instance_sync()
                timeline.complete_step()
                timeline.finish()
            else:
                # JSON mode - no progress indicator
                # 1. Connectivity check
                checker.check_connectivity()

                # 2. Authentication check
                checker.check_authentication()

                # 3. SSH keys check
                checker.check_ssh_keys()

                # 4. Instance sync check
                sync_status = checker.check_instance_sync()

            # 5. Specific task check if requested
            task_health = None
            gpu_health = None
            if task_id:
                task_health = checker.check_instance_health(task_id)

                # Add task-specific findings
                if task_health["ssh_ready"]:
                    checker.add_success("Task Health", f"Task {task_id} is healthy and SSH-ready")
                else:
                    issues_str = (
                        ", ".join(task_health["issues"]) if task_health["issues"] else "Unknown"
                    )
                    checker.add_issue(
                        "Task Health",
                        f"Task {task_id} has issues: {issues_str}",
                        "Check logs with 'flow logs' or try restarting the task",
                    )

                # Also check GPU health for this task
                gpu_health = checker.check_gpu_health(task_id)
                if gpu_health and not output_json:
                    console.print("\n")
                    checker.renderer.render_node_details(gpu_health)

            # Generate report
            report = checker.generate_report()
            # Add schema version for automation stability
            report["schema_version"] = "1.0"
            report["sync_status"] = sync_status
            if task_health:
                report["task_health"] = task_health

            # Output results
            if output_json:
                print(json.dumps(report, indent=2))
            else:
                # Delegate rendering to HealthRenderer for consistency
                self.renderer.render_report_sections(
                    report.get("summary", {}), report.get("details", {})
                )
                if "sync_status" in report:
                    self.renderer.render_orphaned_instances(report["sync_status"], fix)

                # Exit policy: return non-zero codes for automation when requested via env var
                # FLOW_HEALTH_FAIL_ON=never|warnings|issues (default: never)
                import os
                import sys

                fail_on = (os.environ.get("FLOW_HEALTH_FAIL_ON") or "never").lower()
                issues = report["summary"].get("issues", 0)
                warnings = report["summary"].get("warnings", 0)
                if fail_on == "issues" and issues > 0:
                    sys.exit(2)
                if fail_on == "warnings" and (issues > 0 or warnings > 0):
                    sys.exit(1)

        except Exception as e:
            if output_json:
                error_report = {
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                print(json.dumps(error_report, indent=2))
            else:
                console.print(f"[error]✗ Health check failed: {e!s}[/error]")

    def _display_report(self, report: dict, fix: bool) -> None:
        """Backwards-compat wrapper (now routed to renderer)."""
        self.renderer.render_report_sections(report.get("summary", {}), report.get("details", {}))
        if "sync_status" in report:
            self.renderer.render_orphaned_instances(report["sync_status"], fix)
        if "task_health" in report:
            self.renderer.render_task_health_details(report["task_health"])

        # Next steps and optional auto-fixes
        console.print("\n[bold]Next Steps:[/bold]")
        details = report.get("details", {})
        summary = report.get("summary", {"issues": 0})
        if summary.get("issues", 0) > 0:
            console.print("  • Review and address the issues listed above")
            # Offer targeted fixes when possible
            if fix:
                try:
                    applied: list[str] = []
                    # If authentication missing, hint to run init (non-interactive guidance only)
                    if any(
                        i.get("category") == "Authentication" for i in details.get("issues", [])
                    ):
                        console.print(
                            "  • Configure credentials: flow init --provider mithril --api-key <key> --project <project> --region <region>"
                        )
                    # If SSH key issues detected, try to ensure keys via provider manager
                    if any(i.get("category") == "SSH Keys" for i in details.get("issues", [])):
                        # Avoid provider-specific imports; prefer provider helper if available
                        try:
                            from flow.sdk.factory import create_client as _create

                            provider = _create(auto_init=True).provider
                            key_id = None
                            if hasattr(provider, "ensure_default_ssh_key"):
                                try:
                                    key_id = self.flow_client.ensure_default_ssh_key()
                                except Exception:
                                    key_id = None
                            if key_id:
                                applied.append(f"Auto-generated SSH key: {key_id}")
                        except Exception:
                            pass
                    # If state sync issues, refresh local caches
                    if any(i.get("category") == "State Sync" for i in details.get("issues", [])):
                        try:
                            from flow.cli.utils.prefetch import (
                                refresh_active_task_caches as _refresh_active,
                            )
                            from flow.cli.utils.prefetch import (
                                refresh_all_tasks_cache as _refresh_all,
                            )

                            _refresh_active()
                            _refresh_all()
                            applied.append("Refreshed local task caches")
                        except Exception:
                            pass

                    if applied:
                        console.print("\n[bold]Applied fixes:[/bold]")
                        for action in applied:
                            console.print(f"  • {action}")
                except Exception:
                    pass

            console.print("  • Run 'flow health --fix' to attempt automatic fixes")
            console.print(
                "  • Check logs with 'flow logs [task.name]<task-name>[/task.name]' for more details"
            )
        else:
            console.print("  • Your Flow SDK setup is healthy!")
            console.print("  • Run 'flow status' to see your tasks")
            console.print("  • Submit new tasks with 'flow run'")


# Export command instance
command = HealthCommand()
