"""Local metrics storage with JSONL format and rotation support.

Efficient local storage for health metrics using JSONL (JSON Lines) format,
with automatic rotation and cleanup.
"""

import gzip
import json
import logging
import shutil
import threading
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from flow.sdk.health_models import NodeHealthSnapshot

logger = logging.getLogger(__name__)


class MetricsStore:
    """Local storage for health metrics with rotation support."""

    def __init__(
        self,
        base_path: Path | None = None,
        retention_days: int = 7,
        compress_after_days: int = 1,
    ):
        """Initialize metrics store.

        Args:
            base_path: Base directory for metrics storage (default: ~/.flow/metrics)
            retention_days: Number of days to retain metrics
            compress_after_days: Compress files older than this many days
        """
        self.base_path = base_path or Path.home() / ".flow" / "metrics"
        self.retention_days = retention_days
        self.compress_after_days = compress_after_days

        # Ensure directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_snapshot(self, snapshot: NodeHealthSnapshot) -> None:
        """Write a health snapshot to storage.

        Args:
            snapshot: Health snapshot to store
        """
        # Determine file path based on date
        date_str = snapshot.timestamp.strftime("%Y%m%d")
        file_path = self._get_metrics_file(date_str)

        # Convert to dict and write as JSONL
        snapshot_dict = snapshot.to_dict()

        try:
            with open(file_path, "a") as f:
                json.dump(snapshot_dict, f, separators=(",", ":"))
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to write metrics: {e}")

    def write_raw_metrics(self, metrics: dict[str, Any]) -> None:
        """Write raw metrics dict to storage.

        Args:
            metrics: Raw metrics dictionary
        """
        # Extract timestamp or use current time
        timestamp_str = metrics.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.now(timezone.utc)

        # Determine file path based on date
        date_str = timestamp.strftime("%Y%m%d")
        file_path = self._get_metrics_file(date_str)

        try:
            with open(file_path, "a") as f:
                json.dump(metrics, f, separators=(",", ":"))
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to write raw metrics: {e}")

    def read_snapshots(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        task_id: str | None = None,
    ) -> Iterator[NodeHealthSnapshot]:
        """Read health snapshots from storage.

        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            task_id: Filter by specific task ID

        Yields:
            Health snapshots matching filters
        """
        # Default to last 24 hours if no dates specified
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=1)

        # Iterate through relevant files
        for file_path in self._get_files_in_range(start_date, end_date):
            try:
                if file_path.suffix == ".gz":
                    # Read compressed file
                    with gzip.open(file_path, "rt") as f:
                        for line in f:
                            snapshot_dict = json.loads(line.strip())
                            if not task_id or snapshot_dict.get("task_id") == task_id:
                                # Convert back to model (simplified for now)
                                yield self._dict_to_snapshot(snapshot_dict)
                else:
                    # Read uncompressed file
                    with open(file_path) as f:
                        for line in f:
                            snapshot_dict = json.loads(line.strip())
                            if not task_id or snapshot_dict.get("task_id") == task_id:
                                yield self._dict_to_snapshot(snapshot_dict)
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")

    def cleanup(self) -> tuple[int, int]:
        """Clean up old metrics files.

        Returns:
            Tuple of (files_deleted, files_compressed)
        """
        files_deleted = 0
        files_compressed = 0

        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=self.retention_days)
        compress_date = now - timedelta(days=self.compress_after_days)

        for file_path in self.base_path.glob("health-metrics-*.jsonl*"):
            try:
                # Extract date from filename
                date_str = file_path.stem.split("-")[-1].split(".")[0]
                file_date = datetime.strptime(date_str, "%Y%m%d")

                if file_date < cutoff_date:
                    # Delete old files
                    file_path.unlink()
                    files_deleted += 1
                    logger.debug(f"Deleted old metrics file: {file_path}")
                elif file_date < compress_date and file_path.suffix == ".jsonl":
                    # Compress files older than threshold
                    self._compress_file(file_path)
                    files_compressed += 1
                    logger.debug(f"Compressed metrics file: {file_path}")
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {e}")

        return files_deleted, files_compressed

    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        total_size = 0
        file_count = 0
        compressed_count = 0

        for file_path in self.base_path.glob("health-metrics-*"):
            file_count += 1
            total_size += file_path.stat().st_size
            if file_path.suffix == ".gz":
                compressed_count += 1

        return {
            "base_path": str(self.base_path),
            "file_count": file_count,
            "compressed_count": compressed_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "retention_days": self.retention_days,
            "compress_after_days": self.compress_after_days,
        }

    def _get_metrics_file(self, date_str: str) -> Path:
        """Get metrics file path for a given date.

        Args:
            date_str: Date string in YYYYMMDD format

        Returns:
            Path to metrics file
        """
        return self.base_path / f"health-metrics-{date_str}.jsonl"

    def _get_files_in_range(self, start_date: datetime, end_date: datetime) -> list[Path]:
        """Get all metrics files in date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of file paths
        """
        files = []
        current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        while current <= end:
            date_str = current.strftime("%Y%m%d")

            # Check for both compressed and uncompressed files
            for suffix in [".jsonl", ".jsonl.gz"]:
                file_path = self.base_path / f"health-metrics-{date_str}{suffix}"
                if file_path.exists():
                    files.append(file_path)

            current += timedelta(days=1)

        return sorted(files)

    def _compress_file(self, file_path: Path) -> None:
        """Compress a metrics file using gzip.

        Args:
            file_path: Path to file to compress
        """
        compressed_path = file_path.with_suffix(".jsonl.gz")

        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb", compresslevel=6) as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove original file
        file_path.unlink()

    def _dict_to_snapshot(self, data: dict[str, Any]) -> NodeHealthSnapshot:
        """Convert dictionary to NodeHealthSnapshot.

        This is a simplified conversion - in production you'd want
        full deserialization of nested objects.

        Args:
            data: Dictionary representation

        Returns:
            NodeHealthSnapshot instance
        """
        # Extract timestamp
        timestamp_str = data.get("timestamp", datetime.now(timezone.utc).isoformat())
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Deserialize nested types
        from flow.sdk.health_models import (
            ComponentHealth,
            GPUMetric,
            GPUProcess,
            HealthState,
            SystemEvent,
            SystemMetrics,
        )

        gpu_metrics = []
        for g in data.get("gpu_metrics", []) or []:
            try:
                processes = []
                for p in g.get("processes", []) or []:
                    processes.append(
                        GPUProcess(
                            pid=int(p.get("pid", 0)),
                            name=str(p.get("name", "")),
                            memory_mb=int(p.get("memory_mb", 0)),
                            gpu_index=int(p.get("gpu_index", g.get("gpu_index", 0))),
                        )
                    )
                gpu_metrics.append(
                    GPUMetric(
                        gpu_index=int(g.get("gpu_index", g.get("index", 0))),
                        uuid=str(g.get("uuid", "")),
                        name=str(g.get("name", "Unknown")),
                        temperature_c=float(g.get("temperature_c", g.get("temperature", 0))),
                        power_draw_w=float(g.get("power_draw_w", g.get("power_draw", 0))),
                        power_limit_w=float(g.get("power_limit_w", g.get("power_limit", 0))),
                        memory_used_mb=int(g.get("memory_used_mb", 0)),
                        memory_total_mb=int(g.get("memory_total_mb", 0)),
                        gpu_utilization_pct=float(
                            g.get("gpu_utilization_pct", g.get("gpu_utilization", 0))
                        ),
                        sm_occupancy_pct=float(g.get("sm_occupancy_pct", g.get("sm_occupancy", 0))),
                        clock_mhz=int(g.get("clock_mhz", 0)),
                        max_clock_mhz=int(g.get("max_clock_mhz", 0)),
                        ecc_errors=int(g.get("ecc_errors", 0)),
                        xid_events=list(g.get("xid_events", []) or []),
                        nvlink_status=str(g.get("nvlink_status", "healthy")),
                        processes=processes,
                    )
                )
            except Exception:
                continue

        system_metrics = None
        try:
            sm = data.get("system_metrics")
            if sm:
                system_metrics = SystemMetrics(
                    cpu_usage_pct=float(sm.get("cpu_usage_pct", 0)),
                    memory_used_gb=float(sm.get("memory_used_gb", 0)),
                    memory_total_gb=float(sm.get("memory_total_gb", 0)),
                    disk_usage_pct=float(sm.get("disk_usage_pct", 0)),
                    network_rx_mbps=float(sm.get("network_rx_mbps", 0)),
                    network_tx_mbps=float(sm.get("network_tx_mbps", 0)),
                    open_file_descriptors=int(sm.get("open_file_descriptors", 0)),
                    load_average=list(sm.get("load_average", []) or []),
                )
        except Exception:
            system_metrics = None

        health_states = []
        try:
            for hs in data.get("health_states", []) or []:
                try:
                    ts = None
                    ts_raw = hs.get("timestamp")
                    if ts_raw:
                        ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                    health = str(hs.get("health", "unknown")).lower()
                    health_enum = (
                        ComponentHealth(health)
                        if health in ComponentHealth._value2member_map_
                        else ComponentHealth.UNKNOWN
                    )
                    health_states.append(
                        HealthState(
                            component=str(hs.get("component", "unknown")),
                            health=health_enum,
                            message=str(hs.get("message", "")),
                            severity=str(hs.get("severity", "info")),
                            timestamp=ts,
                        )
                    )
                except Exception:
                    continue
        except Exception:
            health_states = []

        events = []
        try:
            for ev in data.get("events", []) or []:
                try:
                    ts = datetime.fromisoformat(str(ev.get("timestamp", "")).replace("Z", "+00:00"))
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
            events = []

        # Create snapshot with full fields
        snapshot = NodeHealthSnapshot(
            task_id=data.get("task_id", "unknown"),
            task_name=data.get("task_name", "unknown"),
            instance_id=data.get("instance_id", "unknown"),
            instance_type=data.get("instance_type", "unknown"),
            timestamp=timestamp,
            gpud_healthy=data.get("gpud_healthy", False),
            gpud_version=data.get("gpud_version"),
            machine_info=data.get("machine_info", {}),
            gpu_metrics=gpu_metrics,
            system_metrics=system_metrics,
            health_states=health_states,
            events=events,
            health_score=data.get("health_score", 0.0),
        )

        # Restore health status if present
        try:
            from flow.sdk.health_models import HealthStatus

            status_str = data.get("health_status")
            if status_str:
                snapshot.health_status = HealthStatus(status_str)
        except Exception:
            pass

        return snapshot


class MetricsAggregator:
    """Aggregate metrics for analysis and reporting."""

    def __init__(self, store: MetricsStore):
        """Initialize aggregator with metrics store.

        Args:
            store: Metrics store instance
        """
        self.store = store

    def get_task_summary(
        self,
        task_id: str,
        hours: int = 24,
    ) -> dict[str, Any]:
        """Get summary statistics for a specific task.

        Args:
            task_id: Task ID to summarize
            hours: Number of hours to look back

        Returns:
            Summary statistics
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(hours=hours)

        snapshots = list(
            self.store.read_snapshots(
                start_date=start_date,
                end_date=end_date,
                task_id=task_id,
            )
        )

        if not snapshots:
            return {
                "task_id": task_id,
                "snapshot_count": 0,
                "hours": hours,
            }

        # Calculate statistics
        health_scores = [s.health_score for s in snapshots]
        gpu_counts = [s.gpu_count for s in snapshots]

        return {
            "task_id": task_id,
            "snapshot_count": len(snapshots),
            "hours": hours,
            "health_score": {
                "current": health_scores[-1] if health_scores else 0.0,
                "average": sum(health_scores) / len(health_scores) if health_scores else 0.0,
                "min": min(health_scores) if health_scores else 0.0,
                "max": max(health_scores) if health_scores else 0.0,
            },
            "gpu_count": max(gpu_counts) if gpu_counts else 0,
            "critical_events": sum(1 for s in snapshots if s.has_critical_events),
            "unhealthy_periods": self._count_unhealthy_periods(snapshots),
        }

    def _count_unhealthy_periods(self, snapshots: list[NodeHealthSnapshot]) -> int:
        """Count number of unhealthy periods in snapshots.

        Args:
            snapshots: List of snapshots

        Returns:
            Number of unhealthy periods
        """
        if not snapshots:
            return 0

        periods = 0
        was_healthy = True

        for snapshot in sorted(snapshots, key=lambda s: s.timestamp):
            is_healthy = snapshot.health_score >= 0.8
            if was_healthy and not is_healthy:
                periods += 1
            was_healthy = is_healthy

        return periods


class MetricsBatcher:
    """Batch metrics for efficient storage and optional remote streaming.

    This class provides:
    - In-memory batching to reduce I/O operations
    - Optional remote endpoint streaming with retry logic
    - Automatic fallback to local storage on failures
    - Thread-safe operations for concurrent metric collection
    """

    def __init__(
        self,
        store: MetricsStore,
        endpoint: str | None = None,
        batch_size: int = 100,
        flush_interval: int = 60,
        api_key: str | None = None,
    ):
        """Initialize metrics batcher.

        Args:
            store: Local metrics store for fallback
            endpoint: Remote metrics endpoint URL
            batch_size: Number of metrics to batch before sending
            flush_interval: Seconds between automatic flushes
            api_key: Optional API key for authentication
        """
        self.store = store
        self.endpoint = endpoint
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.api_key = api_key

        # Thread-safe batch storage
        self.batch = []
        self.lock = threading.Lock()

        # HTTP client for connection reuse
        self.session = None
        if self.endpoint:
            self.session = httpx.Client(
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "flow-compute/1.0",
                }
            )
            if self.api_key:
                self.session.headers["Authorization"] = f"Bearer {self.api_key}"

        # Start flush timer
        self._start_flush_timer()

        # Track metrics
        self.metrics_sent = 0
        self.metrics_failed = 0

    def add(self, metrics: dict[str, Any]) -> None:
        """Add metrics to batch, flush if threshold reached.

        Args:
            metrics: Metrics dictionary to batch
        """
        with self.lock:
            # Add timestamp if not present
            if "timestamp" not in metrics:
                metrics["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"

            self.batch.append(metrics)

            # Check if we should flush
            if len(self.batch) >= self.batch_size:
                self._flush_locked()

    def flush(self) -> None:
        """Manually flush all pending metrics."""
        with self.lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        """Internal flush method (assumes lock is held)."""
        if not self.batch:
            return

        # Copy batch for processing
        metrics_to_send = self.batch.copy()
        self.batch.clear()

        # Try remote endpoint first
        if self.endpoint and self.session:
            success = self._send_to_remote(metrics_to_send)
            if success:
                self.metrics_sent += len(metrics_to_send)
                return
            else:
                self.metrics_failed += len(metrics_to_send)

        # Fallback to local storage
        for metric in metrics_to_send:
            try:
                self.store.write_raw_metrics(metric)
            except Exception as e:
                logger.error(f"Failed to write metric locally: {e}")

    def _send_to_remote(self, metrics: list[dict[str, Any]]) -> bool:
        """Send metrics to remote endpoint.

        Args:
            metrics: List of metrics to send

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare payload
            payload = {
                "source": "flow-compute",
                "version": "1.0",
                "metrics": metrics,
            }

            # Send with retry
            for attempt in range(3):
                try:
                    response = self.session.post(
                        self.endpoint,
                        json=payload,
                        timeout=10,
                    )

                    if response.status_code == 200:
                        logger.debug(f"Successfully sent {len(metrics)} metrics to {self.endpoint}")
                        return True
                    elif response.status_code == 429:  # Rate limited
                        # Exponential backoff
                        import time

                        time.sleep(2**attempt)
                        continue
                    else:
                        logger.warning(
                            f"Failed to send metrics: HTTP {response.status_code} - {response.text}"
                        )
                        return False

                except httpx.TimeoutException:
                    logger.warning(f"Timeout sending metrics (attempt {attempt + 1}/3)")
                    continue
                except httpx.ConnectError as e:
                    logger.warning(f"Connection error: {e}")
                    return False

            return False

        except Exception as e:
            logger.error(f"Unexpected error sending metrics: {e}")
            return False

    def _start_flush_timer(self) -> None:
        """Start periodic flush timer."""

        def flush_periodically():
            self.flush()
            # Schedule next flush
            timer = threading.Timer(self.flush_interval, flush_periodically)
            timer.daemon = True
            timer.start()

        # Start timer
        timer = threading.Timer(self.flush_interval, flush_periodically)
        timer.daemon = True
        timer.start()

    def get_stats(self) -> dict[str, Any]:
        """Get batcher statistics.

        Returns:
            Dictionary with stats
        """
        with self.lock:
            return {
                "pending_metrics": len(self.batch),
                "metrics_sent": self.metrics_sent,
                "metrics_failed": self.metrics_failed,
                "remote_endpoint": self.endpoint is not None,
                "batch_size": self.batch_size,
                "flush_interval": self.flush_interval,
            }

    def close(self) -> None:
        """Close batcher and flush remaining metrics."""
        self.flush()
        if self.session:
            self.session.close()
