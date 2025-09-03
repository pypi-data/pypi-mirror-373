"""Production-ready script size handler with monitoring and configuration."""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from flow.adapters.providers.builtin.mithril.runtime.script_size.exceptions import (
    ScriptTooLargeError,
)
from flow.adapters.providers.builtin.mithril.runtime.script_size.models import PreparedScript
from flow.adapters.providers.builtin.mithril.runtime.script_size.strategies import (
    CompressionStrategy,
    InlineStrategy,
    ITransferStrategy,
    SplitStrategy,
)
from flow.adapters.providers.builtin.mithril.storage import IStorageBackend

logger = logging.getLogger(__name__)


@dataclass
class ScriptSizeConfig:
    """Configuration for script size handling."""

    max_script_size: int = 10_000
    safety_margin: int = 1_000
    enable_compression: bool = True
    enable_split: bool = True
    compression_level: int = 9
    max_compression_attempts: int = 1
    enable_metrics: bool = True
    enable_detailed_logging: bool = False
    metric_callback: Callable[[str, dict[str, Any]], None] | None = None

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "ScriptSizeConfig":
        """Create config from dictionary."""
        return cls(
            max_script_size=config.get("max_script_size", 10_000),
            safety_margin=config.get("safety_margin", 1_000),
            enable_compression=config.get("enable_compression", True),
            enable_split=config.get("enable_split", True),
            compression_level=config.get("compression_level", 9),
            max_compression_attempts=config.get("max_compression_attempts", 1),
            enable_metrics=config.get("enable_metrics", True),
            enable_detailed_logging=config.get("enable_detailed_logging", False),
        )


class ScriptSizeHandler:
    """Production-ready handler for Mithril script size limitations."""

    def __init__(
        self,
        storage_backend: IStorageBackend | None = None,
        config: ScriptSizeConfig | None = None,
        strategies: list[ITransferStrategy] | None = None,
    ):
        """Initialize with configuration and monitoring.

        Args:
            storage_backend: Storage backend for external script storage
            config: Configuration for script size handling
            strategies: Custom strategies (uses defaults if None)
        """
        self.storage_backend = storage_backend
        self.config = config or ScriptSizeConfig()

        # Initialize metrics
        self._metrics = {
            "scripts_processed": 0,
            "scripts_inline": 0,
            "scripts_compressed": 0,
            "scripts_split": 0,
            "scripts_failed": 0,
            "total_bytes_processed": 0,
            "total_bytes_output": 0,
            "compression_ratio_sum": 0.0,
            "processing_time_sum": 0.0,
            "errors_by_type": {},
        }

        # Initialize strategies
        if strategies is None:
            self.strategies = self._create_default_strategies()
        else:
            self.strategies = strategies

        self._log_initialization()

    def _create_default_strategies(self) -> list[ITransferStrategy]:
        """Create default strategies based on configuration."""
        strategies = [InlineStrategy()]

        if self.config.enable_compression:
            strategies.append(CompressionStrategy())

        if self.config.enable_split and self.storage_backend:
            strategies.append(SplitStrategy(self.storage_backend))
        elif self.config.enable_split and not self.storage_backend:
            logger.warning(
                "Split strategy enabled but no storage backend configured. "
                "Large scripts requiring external storage will fail."
            )

        return strategies

    def _log_initialization(self):
        """Log initialization details."""
        strategy_names = [s.name for s in self.strategies]
        logger.info(
            f"ScriptSizeHandler initialized: "
            f"max_size={self.config.max_script_size:,} bytes, "
            f"strategies={strategy_names}, "
            f"storage={'configured' if self.storage_backend else 'none'}"
        )

    def prepare_script(self, script: str) -> PreparedScript:
        """Prepare script with monitoring and detailed error handling.

        Args:
            script: The startup script content

        Returns:
            PreparedScript ready for submission

        Raises:
            ScriptTooLargeError: If no strategy can handle the script
        """
        start_time = time.time()
        script_size = len(script.encode("utf-8"))

        # Record metrics
        self._record_metric("scripts_processed", 1)
        self._record_metric("total_bytes_processed", script_size)

        if self.config.enable_detailed_logging:
            logger.debug(
                f"Processing script: size={script_size:,} bytes, first_100_chars={script[:100]!r}"
            )

        # Track attempts for error reporting
        strategies_tried = []
        strategy_errors = {}

        for strategy in self.strategies:
            strategy_name = strategy.name
            strategies_tried.append(strategy_name)

            if self.config.enable_detailed_logging:
                logger.debug(f"Trying {strategy_name} strategy...")

            try:
                # Check if strategy can handle
                if not strategy.can_handle(script, self.config.max_script_size):
                    if self.config.enable_detailed_logging:
                        logger.debug(f"{strategy_name} cannot handle script size")
                    continue

                # Prepare with strategy
                strategy_start = time.time()
                prepared = strategy.prepare(script, self.config.max_script_size)
                strategy_time = time.time() - strategy_start

                # Validate result
                if prepared.size_bytes > self.config.max_script_size:
                    error_msg = (
                        f"{strategy_name} produced oversized script: "
                        f"{prepared.size_bytes:,} > {self.config.max_script_size:,}"
                    )
                    logger.error(error_msg)
                    strategy_errors[strategy_name] = error_msg
                    continue

                # Success - record metrics
                total_time = time.time() - start_time
                self._record_script_success(
                    strategy_name=strategy_name,
                    original_size=script_size,
                    final_size=prepared.size_bytes,
                    strategy_time=strategy_time,
                    total_time=total_time,
                    prepared=prepared,
                )

                return prepared

            except Exception as e:
                error_msg = f"Error in {strategy_name} strategy: {e!s}"
                logger.error(error_msg, exc_info=True)
                strategy_errors[strategy_name] = error_msg
                self._record_metric("errors_by_type", {strategy_name: 1})
                continue

        # All strategies failed
        self._record_metric("scripts_failed", 1)

        # Build detailed error message
        error_details = []
        for strategy, error in strategy_errors.items():
            error_details.append(f"  - {strategy}: {error}")

        error_message = (
            f"Script size ({script_size:,} bytes) cannot be handled by any strategy.\n"
            f"Strategies tried: {', '.join(strategies_tried)}\n"
        )

        if error_details:
            error_message += "Errors:\n" + "\n".join(error_details)

        # Provide actionable suggestions
        suggestions = self.get_failure_suggestions(script_size, strategies_tried)

        raise ScriptTooLargeError(
            script_size=script_size,
            max_size=self.config.max_script_size,
            strategies_tried=strategies_tried,
        )

    def _record_script_success(
        self,
        strategy_name: str,
        original_size: int,
        final_size: int,
        strategy_time: float,
        total_time: float,
        prepared: PreparedScript,
    ):
        """Record detailed metrics for successful script preparation."""
        # Update strategy-specific counter
        self._record_metric(f"scripts_{strategy_name}", 1)
        self._record_metric("total_bytes_output", final_size)
        self._record_metric("processing_time_sum", total_time)

        # Calculate compression ratio if applicable
        if prepared.compression_ratio:
            self._record_metric("compression_ratio_sum", prepared.compression_ratio)

        # Log success details
        reduction_pct = (
            ((original_size - final_size) / original_size * 100) if original_size > 0 else 0
        )

        log_msg = (
            f"Script prepared successfully: "
            f"strategy={strategy_name}, "
            f"original={original_size:,} bytes, "
            f"final={final_size:,} bytes, "
            f"reduction={reduction_pct:.1f}%, "
            f"time={total_time:.3f}s"
        )

        if prepared.requires_network:
            log_msg += ", requires_network=True"

        if prepared.compression_ratio:
            log_msg += f", compression_ratio={prepared.compression_ratio:.2f}x"

        logger.info(log_msg)

        # Call metric callback if configured
        if self.config.metric_callback:
            self.config.metric_callback(
                "script_prepared",
                {
                    "strategy": strategy_name,
                    "original_size": original_size,
                    "final_size": final_size,
                    "reduction_percent": reduction_pct,
                    "compression_ratio": prepared.compression_ratio,
                    "processing_time": total_time,
                    "strategy_time": strategy_time,
                    "requires_network": prepared.requires_network,
                },
            )

    def _get_failure_suggestions(self, script_size: int, strategies_tried: list[str]) -> list[str]:
        """Get actionable suggestions for script size failures."""
        suggestions = []

        if script_size > 100_000_000:  # 100MB
            suggestions.append(
                "Script exceeds 100MB hard limit. Consider using a different deployment method."
            )

        if "split" not in strategies_tried and not self.storage_backend:
            # External cloud storage backends (S3/GCS/Azure) are not available in this SDK yet.
            # Recommend SCP-based upload which has no size limit.
            suggestions.append("Use upload_strategy='scp' to avoid inline script size limits")

        if "compressed" in strategies_tried:
            suggestions.append("Script doesn't compress well. Consider:")
            suggestions.append("  - Remove embedded binary data or base64-encoded content")
            suggestions.append("  - Use external storage for large data files")
            suggestions.append("  - Minimize repetitive code sections")

        # Primary suggestions - these are usually the best solutions
        primary_suggestions = [
            "Use upload_strategy='scp' to transfer project files after the instance starts",
            "Set upload_code=False if your image already contains the necessary files",
            "Use a Docker image with dependencies pre-installed: flow.run('cmd', image='myimage:latest')",
            "Add .flowignore to exclude unnecessary files (like .git, node_modules, __pycache__)",
        ]

        # Additional suggestions
        additional_suggestions = [
            "Mount large data from S3/GCS instead of embedding in script",
            "Split your application into smaller, focused scripts",
            "Use environment variables instead of embedding configuration",
        ]

        # Add primary suggestions first
        suggestions.extend(primary_suggestions)
        suggestions.extend(additional_suggestions)

        return suggestions

    # Public wrapper to avoid callers accessing private method
    def get_failure_suggestions(self, script_size: int, strategies_tried: list[str]) -> list[str]:
        return self._get_failure_suggestions(script_size, strategies_tried)

    def _record_metric(self, name: str, value: Any):
        """Record a metric if metrics are enabled."""
        if not self.config.enable_metrics:
            return

        if isinstance(value, dict):
            # For nested metrics like errors_by_type
            if name not in self._metrics:
                self._metrics[name] = {}
            for k, v in value.items():
                self._metrics[name][k] = self._metrics[name].get(k, 0) + v
        else:
            self._metrics[name] = self._metrics.get(name, 0) + value

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics with calculated values."""
        metrics = self._metrics.copy()

        # Calculate averages
        if metrics["scripts_processed"] > 0:
            metrics["avg_compression_ratio"] = (
                metrics["compression_ratio_sum"] / metrics.get("scripts_compressed", 1)
                if metrics.get("scripts_compressed", 0) > 0
                else 0
            )
            metrics["avg_processing_time_ms"] = (
                metrics["processing_time_sum"] / metrics["scripts_processed"] * 1000
            )
            metrics["avg_input_size"] = (
                metrics["total_bytes_processed"] / metrics["scripts_processed"]
            )
            metrics["avg_output_size"] = (
                metrics["total_bytes_output"] / metrics["scripts_processed"]
            )

        return metrics

    def validate_script_size(self, script: str) -> tuple[bool, str | None]:
        """Pre-validate if a script can be handled.

        Args:
            script: The script to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        script_size = len(script.encode("utf-8"))

        # Quick check against hard limits
        if script_size > 100_000_000:  # 100MB hard limit
            return False, (
                f"Script size ({script_size:,} bytes) exceeds hard limit of 100MB. "
                "This is too large for any strategy."
            )

        # Check each strategy
        for strategy in self.strategies:
            try:
                if strategy.can_handle(script, self.config.max_script_size):
                    return True, None
            except Exception as e:
                logger.debug(f"Error checking {strategy.name} strategy: {e}")

        # No strategy can handle it
        available_strategies = [s.name for s in self.strategies]
        suggestions = self.get_failure_suggestions(script_size, available_strategies)

        error_msg = (
            f"Script size ({script_size:,} bytes) cannot be handled by "
            f"available strategies: {', '.join(available_strategies)}. "
            f"Suggestions: {'; '.join(suggestions[:3])}"
        )
        # Include explicit hint about configuring a local storage backend when split is not available
        if "split" not in available_strategies:
            error_msg += ";   - Configure local storage backend for split strategy"

        return False, error_msg

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the handler and its dependencies."""
        health = {
            "status": "healthy",
            "strategies": [s.name for s in self.strategies],
            "max_script_size": self.config.max_script_size,
            "storage_backend": "configured" if self.storage_backend else "none",
        }

        # Check storage backend health if available
        if self.storage_backend and hasattr(self.storage_backend, "health_check"):
            try:
                storage_health = self.storage_backend.health_check()
                health["storage_health"] = storage_health
                if storage_health.get("status") != "healthy":
                    health["status"] = "degraded"
            except Exception as e:
                health["storage_health"] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"

        # Add metrics if enabled
        if self.config.enable_metrics:
            health["metrics"] = self.get_metrics()

        return health


def create_script_size_handler(
    storage_backend: IStorageBackend | None = None,
    config: dict[str, Any] | None = None,
) -> ScriptSizeHandler:
    """Factory function to create a production-ready script size handler.

    Args:
        storage_backend: Optional storage backend for large scripts
        config: Optional configuration dictionary

    Returns:
        Configured ScriptSizeHandler
    """
    handler_config = ScriptSizeConfig.from_dict(config or {})

    return ScriptSizeHandler(
        storage_backend=storage_backend,
        config=handler_config,
    )
