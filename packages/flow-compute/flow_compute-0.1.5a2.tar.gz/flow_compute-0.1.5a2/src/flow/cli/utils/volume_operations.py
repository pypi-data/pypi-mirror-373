"""Parallel volume operations handler.

Provides efficient parallel operations for volume management,
including bulk deletion with proper error handling and progress tracking.
"""

import re
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from re import Pattern
from typing import Any

from flow.sdk.client import Flow


@dataclass
class OperationResult:
    """Result of a single volume operation."""

    volume_id: str
    success: bool
    error: str | None = None
    volume_name: str | None = None


@dataclass
class BulkOperationResults:
    """Aggregated results from bulk operations."""

    total: int
    succeeded: int
    failed: int
    results: list[OperationResult]

    @property
    def all_succeeded(self) -> bool:
        """Check if all operations succeeded."""
        return self.failed == 0

    def get_failures(self) -> list[OperationResult]:
        """Get list of failed operations."""
        return [r for r in self.results if not r.success]

    def get_successes(self) -> list[OperationResult]:
        """Get list of successful operations."""
        return [r for r in self.results if r.success]


class VolumeFilter:
    """Filter volumes by various criteria."""

    def filter_by_pattern(self, volumes: list[Any], pattern: str) -> list[Any]:
        """Filter volumes by pattern matching.

        Args:
            volumes: List of volume objects (must have 'id' and optionally 'name' attributes)
            pattern: Pattern to match against volume ID and name.
                    Can be a regex or simple substring.

        Returns:
            Filtered list of volumes

        Examples:
            >>> filter = VolumeFilter()
            >>> volumes = [Volume(id="vol-test-123"), Volume(id="vol-prod-456")]
            >>> filter.filter_by_pattern(volumes, "test")
            [Volume(id="vol-test-123")]
        """
        if not pattern:
            return volumes

        filtered = []

        # Try to compile as regex first
        regex: Pattern | None = None
        try:
            regex = re.compile(pattern)
        except re.error:
            # If not valid regex, we'll use substring matching
            pass

        for volume in volumes:
            volume_id = getattr(volume, "id", "")
            volume_name = getattr(volume, "name", "") or ""

            if regex:
                # Regex matching
                if regex.search(volume_id) or (volume_name and regex.search(volume_name)):
                    filtered.append(volume)
            else:
                # Substring matching
                if pattern in volume_id or (volume_name and pattern in volume_name):
                    filtered.append(volume)

        return filtered


class VolumeOperations:
    """Handle volume operations with parallel execution support."""

    def __init__(self, client: Flow, max_workers: int = 10):
        """Initialize volume operations handler.

        Args:
            client: Flow API client
            max_workers: Maximum number of parallel operations
        """
        self.client = client
        self.max_workers = max_workers
        self.filter = VolumeFilter()

    def delete_volumes(
        self,
        volumes: list[Any],
        progress_callback: Callable[[OperationResult], None] | None = None,
    ) -> BulkOperationResults:
        """Delete multiple volumes in parallel.

        Args:
            volumes: List of volume objects to delete
            progress_callback: Optional callback for progress updates

        Returns:
            BulkOperationResults with success/failure details

        Example:
            >>> ops = VolumeOperations(flow_client)
            >>> results = ops.delete_volumes(volumes, lambda r: print(f"Deleted {r.volume_id}"))
        """
        if not volumes:
            return BulkOperationResults(total=0, succeeded=0, failed=0, results=[])

        results: list[OperationResult] = []
        succeeded = 0
        failed = 0

        # Limit workers to avoid overwhelming the API
        actual_workers = min(self.max_workers, len(volumes))

        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # Submit all deletion tasks
            future_to_volume: dict[Future, Any] = {
                executor.submit(self._delete_single_volume, volume): volume for volume in volumes
            }

            # Process results as they complete
            for future in as_completed(future_to_volume):
                volume = future_to_volume[future]
                try:
                    result = future.result()
                    results.append(result)

                    if result.success:
                        succeeded += 1
                    else:
                        failed += 1

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(result)

                except Exception as e:
                    # Handle unexpected errors
                    result = OperationResult(
                        volume_id=getattr(volume, "id", "unknown"),
                        success=False,
                        error=str(e),
                        volume_name=getattr(volume, "name", None),
                    )
                    results.append(result)
                    failed += 1

                    if progress_callback:
                        progress_callback(result)

        return BulkOperationResults(
            total=len(volumes), succeeded=succeeded, failed=failed, results=results
        )

    def _delete_single_volume(self, volume: Any) -> OperationResult:
        """Delete a single volume.

        Args:
            volume: Volume object to delete

        Returns:
            OperationResult indicating success or failure
        """
        volume_id = getattr(volume, "id", "unknown")
        volume_name = getattr(volume, "name", None)

        try:
            self.client.volumes.delete(volume_id)
            return OperationResult(volume_id=volume_id, success=True, volume_name=volume_name)
        except Exception as e:
            return OperationResult(
                volume_id=volume_id, success=False, error=str(e), volume_name=volume_name
            )

    def find_volumes_by_pattern(self, pattern: str | None = None) -> tuple[list[Any], int]:
        """Find volumes matching a pattern.

        Args:
            pattern: Optional pattern to filter volumes

        Returns:
            Tuple of (matching_volumes, total_volumes_count)
        """
        all_volumes = self.client.volumes.list()

        if pattern:
            matching_volumes = self.filter.filter_by_pattern(all_volumes, pattern)
        else:
            matching_volumes = all_volumes

        return matching_volumes, len(all_volumes)

    def format_volume_summary(self, volumes: list[Any]) -> list[str]:
        """Format volume list for display.

        Args:
            volumes: List of volume objects

        Returns:
            List of formatted strings for display
        """
        summary = []
        for volume in volumes:
            volume_id = getattr(volume, "volume_id", getattr(volume, "id", "unknown"))
            volume_name = getattr(volume, "name", None)

            if volume_name:
                summary.append(f"{volume_id} ({volume_name})")
            else:
                summary.append(volume_id)

        return summary
