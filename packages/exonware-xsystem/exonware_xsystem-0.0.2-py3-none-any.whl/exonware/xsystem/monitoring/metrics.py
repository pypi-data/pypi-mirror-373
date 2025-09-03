"""
Generic performance metrics and monitoring system.

This module provides comprehensive performance tracking and reporting
for any library or application that needs performance monitoring.
"""

import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..config.logging_setup import get_logger


@dataclass
class OperationMetrics:
    """Metrics for a single operation type."""

    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_count: int = 0

    def add_timing(self, duration: float) -> None:
        """Add a timing measurement."""
        self.total_calls += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.recent_times.append(duration)

    def add_error(self) -> None:
        """Record an error occurrence."""
        self.error_count += 1

    @property
    def average_time(self) -> float:
        """Get average operation time."""
        return self.total_time / max(1, self.total_calls)

    @property
    def recent_average(self) -> float:
        """Get recent average operation time."""
        if not self.recent_times:
            return 0.0
        return sum(self.recent_times) / len(self.recent_times)

    @property
    def error_rate(self) -> float:
        """Get error rate as percentage."""
        return (self.error_count / max(1, self.total_calls)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_calls": self.total_calls,
            "total_time": self.total_time,
            "average_time": self.average_time,
            "recent_average": self.recent_average,
            "min_time": self.min_time if self.min_time != float("inf") else 0.0,
            "max_time": self.max_time,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
        }


class GenericMetrics:
    """Generic performance metrics collection system."""

    def __init__(self, component_name: str = "generic"):
        self.component_name = component_name
        self._logger = get_logger(f"{component_name}.metrics")
        self._operations: Dict[str, OperationMetrics] = defaultdict(OperationMetrics)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._start_time = time.time()
        self._lock = threading.RLock()

        # Cache metrics
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_evictions = 0

        # Resource creation metrics
        self._resources_created = 0
        self._pool_hits = 0
        self._pool_misses = 0

        # Memory metrics
        self._peak_memory_usage = 0.0
        self._current_memory_usage = 0.0

        self._logger.debug(f"Initialized {component_name} metrics collection")

    @contextmanager
    def measure_operation(self, operation_name: str):
        """Context manager to measure operation duration."""
        start_time = time.perf_counter()
        success = True

        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = time.perf_counter() - start_time

            with self._lock:
                if success:
                    self._operations[operation_name].add_timing(duration)
                else:
                    self._operations[operation_name].add_error()

    def record_timing(self, operation_name: str, duration: float) -> None:
        """Record a timing measurement for an operation."""
        with self._lock:
            self._operations[operation_name].add_timing(duration)

    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        with self._lock:
            self._counters[counter_name] += value

    def set_gauge(self, gauge_name: str, value: float) -> None:
        """Set a gauge metric value."""
        with self._lock:
            self._gauges[gauge_name] = value

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        with self._lock:
            self._cache_misses += 1

    def record_cache_eviction(self) -> None:
        """Record a cache eviction."""
        with self._lock:
            self._cache_evictions += 1

    def record_resource_creation(self, from_pool: bool = False) -> None:
        """Record resource creation metrics."""
        with self._lock:
            self._resources_created += 1
            if from_pool:
                self._pool_hits += 1
            else:
                self._pool_misses += 1

    def update_memory_usage(self, current: float) -> None:
        """Update memory usage metrics."""
        with self._lock:
            self._current_memory_usage = current
            self._peak_memory_usage = max(self._peak_memory_usage, current)

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage."""
        total = self._cache_hits + self._cache_misses
        return (self._cache_hits / max(1, total)) * 100

    @property
    def pool_efficiency(self) -> float:
        """Get pool efficiency as percentage."""
        total = self._pool_hits + self._pool_misses
        return (self._pool_hits / max(1, total)) * 100

    @property
    def uptime(self) -> float:
        """Get uptime in seconds."""
        return time.time() - self._start_time

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        with self._lock:
            if operation_name in self._operations:
                return self._operations[operation_name].to_dict()
            return {}

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        with self._lock:
            operations_summary = {}
            for op_name, metrics in self._operations.items():
                operations_summary[op_name] = metrics.to_dict()

            return {
                "component": self.component_name,
                "uptime_seconds": self.uptime,
                "cache_metrics": {
                    "hits": self._cache_hits,
                    "misses": self._cache_misses,
                    "evictions": self._cache_evictions,
                    "hit_rate_percent": self.cache_hit_rate,
                },
                "resource_creation": {
                    "total_created": self._resources_created,
                    "pool_hits": self._pool_hits,
                    "pool_misses": self._pool_misses,
                    "pool_efficiency_percent": self.pool_efficiency,
                },
                "memory": {
                    "current_usage": self._current_memory_usage,
                    "peak_usage": self._peak_memory_usage,
                },
                "operations": operations_summary,
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
            }

    def get_performance_report(self) -> str:
        """Generate a human-readable performance report."""
        summary = self.get_summary()

        lines = [
            f"🎯 {self.component_name.title()} Performance Report",
            "=" * 50,
            f"⏱️  Uptime: {summary['uptime_seconds']:.2f} seconds",
            "",
            "📊 Cache Performance:",
            f"  Hit Rate: {summary['cache_metrics']['hit_rate_percent']:.1f}%",
            f"  Total Hits: {summary['cache_metrics']['hits']}",
            f"  Total Misses: {summary['cache_metrics']['misses']}",
            f"  Evictions: {summary['cache_metrics']['evictions']}",
            "",
            "🏭 Resource Creation:",
            f"  Total Created: {summary['resource_creation']['total_created']}",
            f"  Pool Efficiency: {summary['resource_creation']['pool_efficiency_percent']:.1f}%",
            f"  Pool Hits: {summary['resource_creation']['pool_hits']}",
            f"  Pool Misses: {summary['resource_creation']['pool_misses']}",
            "",
            "💾 Memory Usage:",
            f"  Current: {summary['memory']['current_usage']:.2f} MB",
            f"  Peak: {summary['memory']['peak_usage']:.2f} MB",
            "",
            "⚡ Operation Performance:",
        ]

        for op_name, op_metrics in summary["operations"].items():
            if op_metrics["total_calls"] > 0:
                lines.extend(
                    [
                        f"  {op_name}:",
                        f"    Calls: {op_metrics['total_calls']}",
                        f"    Avg Time: {op_metrics['average_time']*1000:.3f}ms",
                        f"    Recent Avg: {op_metrics['recent_average']*1000:.3f}ms",
                        f"    Min/Max: {op_metrics['min_time']*1000:.3f}ms / {op_metrics['max_time']*1000:.3f}ms",
                        f"    Error Rate: {op_metrics['error_rate']:.1f}%",
                    ]
                )

        if summary["counters"]:
            lines.extend(["", "📈 Counters:"])
            for name, value in summary["counters"].items():
                lines.append(f"  {name}: {value}")

        if summary["gauges"]:
            lines.extend(["", "📏 Gauges:"])
            for name, value in summary["gauges"].items():
                lines.append(f"  {name}: {value}")

        return "\n".join(lines)

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._operations.clear()
            self._counters.clear()
            self._gauges.clear()
            self._cache_hits = 0
            self._cache_misses = 0
            self._cache_evictions = 0
            self._resources_created = 0
            self._pool_hits = 0
            self._pool_misses = 0
            self._peak_memory_usage = 0.0
            self._current_memory_usage = 0.0
            self._start_time = time.time()
            self._logger.info(f"Reset all {self.component_name} metrics")


# Global metrics registry
_metrics_registry: Dict[str, GenericMetrics] = {}
_registry_lock = threading.Lock()


def get_metrics(component_name: str = "generic") -> GenericMetrics:
    """Get metrics instance for a specific component."""
    global _metrics_registry
    if component_name not in _metrics_registry:
        with _registry_lock:
            if component_name not in _metrics_registry:
                _metrics_registry[component_name] = GenericMetrics(component_name)
    return _metrics_registry[component_name]


def reset_metrics(component_name: str = None) -> None:
    """Reset metrics for a component or all components."""
    global _metrics_registry
    with _registry_lock:
        if component_name:
            if component_name in _metrics_registry:
                _metrics_registry[component_name].reset()
        else:
            for metrics in _metrics_registry.values():
                metrics.reset()


# Convenience functions for component-specific usage
def create_component_metrics(component_name: str):
    """Create convenience functions for a specific component."""
    metrics = get_metrics(component_name)

    def measure_operation(operation_name: str):
        return metrics.measure_operation(operation_name)

    def record_timing(operation_name: str, duration: float) -> None:
        metrics.record_timing(operation_name, duration)

    def increment_counter(counter_name: str, value: int = 1) -> None:
        metrics.increment_counter(counter_name, value)

    def record_cache_hit() -> None:
        metrics.record_cache_hit()

    def record_cache_miss() -> None:
        metrics.record_cache_miss()

    def record_resource_creation(from_pool: bool = False) -> None:
        metrics.record_resource_creation(from_pool)

    return {
        "measure_operation": measure_operation,
        "record_timing": record_timing,
        "increment_counter": increment_counter,
        "record_cache_hit": record_cache_hit,
        "record_cache_miss": record_cache_miss,
        "record_resource_creation": record_resource_creation,
        "get_metrics": lambda: metrics,
    }
