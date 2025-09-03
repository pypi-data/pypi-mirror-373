"""
Performance Monitoring Utilities for xSystem

These utilities provide performance monitoring, metrics collection, and analysis
capabilities. They were previously embedded in xData and have been extracted for
framework-wide reusability.
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, ContextManager, Dict, List, Optional

logger = logging.getLogger(__name__)

# ======================
# Performance Statistics
# ======================


class PerformanceStats:
    """
    Container for performance statistics and metrics.

    This class holds all performance data collected during monitoring,
    providing methods for analysis and reporting.
    """

    def __init__(self) -> None:
        """Initialize empty performance statistics."""
        self.operations_count = 0
        self.total_processing_time = 0.0
        self.memory_usage_samples: List[Dict[str, Any]] = []
        self.operation_history: List[Dict[str, Any]] = []
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def reset(self) -> None:
        """Reset all statistics to initial state."""
        self.operations_count = 0
        self.total_processing_time = 0.0
        self.memory_usage_samples.clear()
        self.operation_history.clear()
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def to_native(self) -> Dict[str, Any]:
        """Convert statistics to dictionary format."""
        return {
            "operations_count": self.operations_count,
            "total_processing_time": self.total_processing_time,
            "memory_usage_samples": self.memory_usage_samples.copy(),
            "operation_history": self.operation_history.copy(),
            "error_count": self.error_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }

    def add_operation(
        self,
        operation_name: str,
        duration: float,
        success: bool = True,
        error_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a completed operation.

        Args:
            operation_name: Name of the operation
            duration: Time taken in seconds
            success: Whether the operation succeeded
            error_info: Optional error information if operation failed
        """
        self.operations_count += 1
        self.total_processing_time += duration

        if not success:
            self.error_count += 1

        # Record in operation history
        operation_record = {
            "operation": operation_name,
            "duration": duration,
            "timestamp": time.perf_counter(),
            "success": success,
        }

        if error_info:
            operation_record.update(error_info)

        self.operation_history.append(operation_record)

        # Keep history manageable (last 100 operations)
        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-100:]

    def add_memory_sample(
        self, operation_name: str, memory_delta_mb: float, peak_memory_mb: float
    ) -> None:
        """
        Record a memory usage sample.

        Args:
            operation_name: Name of the operation being monitored
            memory_delta_mb: Memory change in MB
            peak_memory_mb: Peak memory usage in MB
        """
        self.memory_usage_samples.append(
            {
                "operation": operation_name,
                "memory_delta_mb": memory_delta_mb,
                "peak_memory_mb": peak_memory_mb,
                "timestamp": time.perf_counter(),
            }
        )

        # Keep samples manageable
        if len(self.memory_usage_samples) > 100:
            self.memory_usage_samples = self.memory_usage_samples[-100:]

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.cache_misses += 1


# ======================
# Performance Monitor
# ======================


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.

    This class provides a unified interface for performance monitoring
    with configurable features and detailed statistics collection.
    """

    def __init__(self, enabled: bool = True, enable_memory_monitoring: bool = True):
        """
        Initialize performance monitor.

        Args:
            enabled: Whether monitoring is enabled
            enable_memory_monitoring: Whether to monitor memory usage
        """
        self.enabled = enabled
        self.enable_memory_monitoring = enable_memory_monitoring
        self.stats = PerformanceStats()
        self._psutil_available = False

        # Try to import psutil for memory monitoring
        if enable_memory_monitoring:
            try:
                import psutil

                self._psutil_available = True
                self._process = psutil.Process()
            except ImportError:
                logger.debug("psutil not available - memory monitoring disabled")
                self._psutil_available = False

    def is_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self.enabled

    def enable(self) -> None:
        """Enable monitoring."""
        self.enabled = True

    def disable(self) -> None:
        """Disable monitoring."""
        self.enabled = False

    def reset_stats(self) -> None:
        """Reset all performance statistics."""
        self.stats.reset()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics with derived metrics.

        Returns:
            Dictionary containing performance metrics
        """
        if not self.enabled:
            return {}

        stats_dict = self.stats.to_native()

        # Calculate derived metrics
        if stats_dict["operations_count"] > 0:
            stats_dict["average_operation_time"] = (
                stats_dict["total_processing_time"] / stats_dict["operations_count"]
            )
        else:
            stats_dict["average_operation_time"] = 0.0

        # Memory statistics
        if stats_dict["memory_usage_samples"]:
            memory_deltas = [
                sample["memory_delta_mb"]
                for sample in stats_dict["memory_usage_samples"]
            ]
            peak_memories = [
                sample["peak_memory_mb"]
                for sample in stats_dict["memory_usage_samples"]
            ]

            stats_dict["memory_stats"] = {
                "average_memory_delta_mb": sum(memory_deltas) / len(memory_deltas),
                "max_memory_delta_mb": max(memory_deltas),
                "peak_memory_usage_mb": max(peak_memories),
                "memory_samples_count": len(memory_deltas),
            }

        # Error rate
        if stats_dict["operations_count"] > 0:
            stats_dict["error_rate"] = (
                stats_dict["error_count"] / stats_dict["operations_count"]
            )
        else:
            stats_dict["error_rate"] = 0.0

        # Cache efficiency
        total_cache_ops = stats_dict["cache_hits"] + stats_dict["cache_misses"]
        if total_cache_ops > 0:
            stats_dict["cache_hit_rate"] = stats_dict["cache_hits"] / total_cache_ops
        else:
            stats_dict["cache_hit_rate"] = 0.0

        return stats_dict

    @contextmanager
    def monitor_operation(self, operation_name: str):
        """
        Context manager for monitoring a single operation.

        Args:
            operation_name: Name of the operation being monitored

        Usage:
            with monitor.monitor_operation("load_file"):
                # Operation to monitor
                result = load_file(path)
        """
        if not self.enabled:
            yield
            return

        start_time = time.perf_counter()
        start_memory = 0

        # Memory monitoring setup
        if self.enable_memory_monitoring and self._psutil_available:
            try:
                start_memory = self._process.memory_info().rss / 1024 / 1024  # MB
            except Exception:
                start_memory = 0

        success = True
        error_info = None

        try:
            yield
        except Exception as e:
            success = False
            error_info = {"error_type": type(e).__name__, "error_message": str(e)}
            raise
        finally:
            # Record operation completion
            end_time = time.perf_counter()
            duration = end_time - start_time

            # Record operation
            self.stats.add_operation(operation_name, duration, success, error_info)

            # Record memory usage if available
            if (
                self.enable_memory_monitoring
                and self._psutil_available
                and start_memory > 0
            ):
                try:
                    end_memory = self._process.memory_info().rss / 1024 / 1024  # MB
                    memory_delta = end_memory - start_memory
                    self.stats.add_memory_sample(
                        operation_name, memory_delta, end_memory
                    )
                except Exception:
                    pass

    def record_cache_operation(self, hit: bool) -> None:
        """
        Record a cache operation.

        Args:
            hit: True for cache hit, False for cache miss
        """
        if not self.enabled:
            return

        if hit:
            self.stats.record_cache_hit()
        else:
            self.stats.record_cache_miss()


# ======================
# Factory Functions
# ======================


def create_performance_monitor(
    enabled: bool = True, enable_memory_monitoring: bool = True
) -> PerformanceMonitor:
    """
    Factory function to create a performance monitor.

    Args:
        enabled: Whether monitoring should be enabled
        enable_memory_monitoring: Whether to enable memory monitoring

    Returns:
        Configured PerformanceMonitor instance
    """
    return PerformanceMonitor(
        enabled=enabled, enable_memory_monitoring=enable_memory_monitoring
    )


# ======================
# Context Managers
# ======================


@contextmanager
def performance_context(monitor: PerformanceMonitor, operation_name: str):
    """
    Context manager for performance monitoring.

    Args:
        monitor: PerformanceMonitor instance
        operation_name: Name of the operation being monitored

    Usage:
        with performance_context(monitor, "operation_name"):
            # Code to monitor
            do_something()
    """
    with monitor.monitor_operation(operation_name):
        yield


@contextmanager
def enhanced_error_context(operation: str, **context_data: Any):
    """
    Context manager for enhanced error handling with context information.

    Args:
        operation: Name of the operation being performed
        **context_data: Additional context data to include in errors

    Usage:
        with enhanced_error_context("file_parsing", file_path=path):
            # Operation that might fail
            result = parse_content(content)
    """
    try:
        yield
    except Exception as e:
        # Enhance the exception with context information
        context_info = f"Operation: {operation}"
        if context_data:
            context_parts = [f"{k}={v}" for k, v in context_data.items()]
            context_info += f" | Context: {', '.join(context_parts)}"

        # Add context to the exception message if possible
        if hasattr(e, "args") and e.args:
            enhanced_message = f"{e.args[0]} | {context_info}"
            e.args = (enhanced_message,) + e.args[1:]

        logger.error(f"Enhanced error context - {context_info}: {e}")
        raise


# ======================
# Analysis Functions
# ======================


def calculate_performance_summary(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a performance summary from statistics.

    Args:
        stats: Performance statistics dictionary

    Returns:
        Dictionary containing performance summary
    """
    if not stats:
        return {"status": "No performance data available"}

    summary = {
        "status": "active" if stats.get("operations_count", 0) > 0 else "inactive",
        "total_operations": stats.get("operations_count", 0),
        "total_time_seconds": stats.get("total_processing_time", 0.0),
        "average_operation_time": stats.get("average_operation_time", 0.0),
        "error_rate_percentage": stats.get("error_rate", 0.0) * 100,
        "cache_hit_rate_percentage": stats.get("cache_hit_rate", 0.0) * 100,
    }

    # Memory summary if available
    memory_stats = stats.get("memory_stats")
    if memory_stats:
        summary["memory_summary"] = {
            "peak_usage_mb": memory_stats.get("peak_memory_usage_mb", 0.0),
            "average_delta_mb": memory_stats.get("average_memory_delta_mb", 0.0),
            "max_delta_mb": memory_stats.get("max_memory_delta_mb", 0.0),
        }

    return summary


def format_performance_report(
    stats: Dict[str, Any], title: str = "Performance Report"
) -> str:
    """
    Format performance statistics into a human-readable report.

    Args:
        stats: Performance statistics dictionary
        title: Title for the report

    Returns:
        Formatted performance report string
    """
    if not stats:
        return f"{title}\n{'=' * len(title)}\nNo performance data available."

    summary = calculate_performance_summary(stats)

    report_lines = [
        title,
        "=" * len(title),
        "",
        f"Status: {summary['status']}",
        f"Total Operations: {summary['total_operations']}",
        f"Total Processing Time: {summary['total_time_seconds']:.3f}s",
        f"Average Operation Time: {summary['average_operation_time']:.3f}s",
        f"Error Rate: {summary['error_rate_percentage']:.1f}%",
        f"Cache Hit Rate: {summary['cache_hit_rate_percentage']:.1f}%",
    ]

    # Add memory information if available
    if "memory_summary" in summary:
        memory = summary["memory_summary"]
        report_lines.extend(
            [
                "",
                "Memory Usage:",
                f"  Peak Usage: {memory['peak_usage_mb']:.1f}MB",
                f"  Average Delta: {memory['average_delta_mb']:.1f}MB",
                f"  Max Delta: {memory['max_delta_mb']:.1f}MB",
            ]
        )

    # Add recent operations if available
    operation_history = stats.get("operation_history", [])
    if operation_history:
        report_lines.extend(
            [
                "",
                f"Recent Operations (last {min(5, len(operation_history))}):",
            ]
        )

        for op in operation_history[-5:]:
            status = "✓" if op.get("success", True) else "✗"
            report_lines.append(
                f"  {status} {op.get('operation', 'unknown')}: {op.get('duration', 0.0):.3f}s"
            )

    return "\n".join(report_lines)
