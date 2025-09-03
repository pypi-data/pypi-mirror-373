"""
Memory Monitoring and Leak Detection for xSystem Library.

This module provides comprehensive memory monitoring, leak detection,
and automatic cleanup mechanisms for production deployment.
"""

import gc
import sys
import threading
import time
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

import psutil

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.memory_monitor")


@dataclass
class MemorySnapshot:
    """Memory usage snapshot for tracking."""

    timestamp: float
    memory_usage: int  # bytes
    object_count: int
    gc_stats: Dict[str, Any]
    node_count: int
    edge_count: int
    cache_size: int
    pool_size: int


@dataclass
class MemoryLeakReport:
    """Report of detected memory leaks."""

    leak_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    affected_objects: int
    memory_increase: int  # bytes
    time_period: float  # seconds
    recommendations: List[str] = field(default_factory=list)


class MemoryMonitor:
    """
    Comprehensive memory monitoring and leak detection system.

    Features:
    - Real-time memory usage tracking
    - Automatic leak detection
    - Object lifecycle monitoring
    - Garbage collection optimization
    - Memory pressure alerts
    - Automatic cleanup triggers
    """

    def __init__(
        self,
        monitoring_interval: float = 30.0,
        leak_detection_threshold: float = 0.1,  # 10% increase
        max_memory_usage: int = 1024 * 1024 * 1024,  # 1GB
        enable_auto_cleanup: bool = True,
    ):
        """Initialize memory monitor."""
        self.monitoring_interval = monitoring_interval
        self.leak_detection_threshold = leak_detection_threshold
        self.max_memory_usage = max_memory_usage
        self.enable_auto_cleanup = enable_auto_cleanup

        # Monitoring state
        self._snapshots: deque = deque(maxlen=100)  # Keep last 100 snapshots
        self._object_registry: Dict[int, Dict[str, Any]] = {}
        self._weak_refs: Set[weakref.ReferenceType] = set()
        self._leak_reports: List[MemoryLeakReport] = []

        # Thread safety
        self._lock = threading.RLock()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

        # Statistics
        self._total_objects_created = 0
        self._total_objects_destroyed = 0
        self._peak_memory_usage = 0
        self._cleanup_count = 0

        # Callbacks for external systems
        self._memory_pressure_callbacks: List[Callable] = []
        self._leak_detected_callbacks: List[Callable] = []

        logger.info("🔍 Memory monitor initialized")

    def start_monitoring(self) -> None:
        """Start continuous memory monitoring."""
        if self._monitoring_thread is not None and self._monitoring_thread.is_alive():
            logger.warning("Memory monitoring already running")
            return

        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, name="MemoryMonitor", daemon=True
        )
        self._monitoring_thread.start()
        logger.info("🚀 Memory monitoring started")

    def stop_monitoring(self) -> None:
        """Stop continuous memory monitoring."""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            logger.warning("Memory monitoring not running")
            return

        self._stop_monitoring.set()
        self._monitoring_thread.join(timeout=5.0)
        logger.info("⏹️ Memory monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_monitoring.is_set():
            try:
                self._take_snapshot()
                self._detect_leaks()
                self._check_memory_pressure()

                # Wait for next interval
                self._stop_monitoring.wait(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)  # Brief pause on error

    def _take_snapshot(self) -> None:
        """Take a memory usage snapshot."""
        try:
            # Get current memory usage
            process = psutil.Process()
            memory_info = process.memory_info()

            # Get garbage collection stats
            gc_stats = {
                "collections": gc.get_stats(),
                "counts": gc.get_count(),
                "objects": len(gc.get_objects()),
            }

            # Create snapshot
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                memory_usage=memory_info.rss,
                object_count=len(gc.get_objects()),
                gc_stats=gc_stats,
                node_count=len(self._object_registry),
                edge_count=0,  # Will be updated by specific implementations
                cache_size=0,  # Will be updated by specific implementations
                pool_size=0,  # Will be updated by specific implementations
            )

            with self._lock:
                self._snapshots.append(snapshot)
                self._peak_memory_usage = max(self._peak_memory_usage, memory_info.rss)

        except Exception as e:
            logger.error(f"Error taking memory snapshot: {e}")

    def _detect_leaks(self) -> None:
        """Detect potential memory leaks."""
        if len(self._snapshots) < 3:
            return  # Need at least 3 snapshots for trend analysis

        try:
            recent_snapshots = list(self._snapshots)[-10:]  # Last 10 snapshots
            if len(recent_snapshots) < 3:
                return

            # Calculate memory growth trend
            memory_values = [s.memory_usage for s in recent_snapshots]
            time_values = [s.timestamp for s in recent_snapshots]

            # Simple linear regression for trend
            n = len(memory_values)
            if n < 3:
                return

            sum_x = sum(time_values)
            sum_y = sum(memory_values)
            sum_xy = sum(x * y for x, y in zip(time_values, memory_values))
            sum_x2 = sum(x * x for x in time_values)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

            # Check for significant growth
            if slope > self.leak_detection_threshold * memory_values[0]:
                leak_report = MemoryLeakReport(
                    leak_type="memory_growth",
                    severity="medium" if slope < 0.5 * memory_values[0] else "high",
                    description=f"Memory usage growing at {slope:.2f} bytes/second",
                    affected_objects=recent_snapshots[-1].object_count,
                    memory_increase=memory_values[-1] - memory_values[0],
                    time_period=time_values[-1] - time_values[0],
                    recommendations=[
                        "Check for unclosed resources",
                        "Review object lifecycle management",
                        "Consider implementing object pooling",
                    ],
                )

                with self._lock:
                    self._leak_reports.append(leak_report)

                logger.warning(
                    f"🚨 Potential memory leak detected: {leak_report.description}"
                )

                # Trigger callbacks
                for callback in self._leak_detected_callbacks:
                    try:
                        callback(leak_report)
                    except Exception as e:
                        logger.error(f"Error in leak detection callback: {e}")

        except Exception as e:
            logger.error(f"Error detecting memory leaks: {e}")

    def _check_memory_pressure(self) -> None:
        """Check for memory pressure and trigger cleanup if needed."""
        if not self._snapshots:
            return

        current_memory = self._snapshots[-1].memory_usage

        # Check if memory usage is high
        if current_memory > self.max_memory_usage:
            logger.warning(f"⚠️ High memory usage: {current_memory / 1024 / 1024:.1f}MB")

            if self.enable_auto_cleanup:
                self._auto_cleanup_if_needed()

            # Trigger callbacks
            for callback in self._memory_pressure_callbacks:
                try:
                    callback(current_memory, self.max_memory_usage)
                except Exception as e:
                    logger.error(f"Error in memory pressure callback: {e}")

    def _auto_cleanup_if_needed(self) -> None:
        """Perform automatic cleanup if memory pressure is detected."""
        try:
            # Force garbage collection
            collected = gc.collect()

            # Clear weak references
            self._weak_refs.clear()

            # Clear old snapshots if too many
            if len(self._snapshots) > 50:
                with self._lock:
                    # Keep only the most recent 25 snapshots
                    self._snapshots = deque(list(self._snapshots)[-25:], maxlen=100)

            self._cleanup_count += 1
            logger.info(f"🧹 Auto-cleanup performed: {collected} objects collected")

        except Exception as e:
            logger.error(f"Error during auto-cleanup: {e}")

    def force_cleanup(self) -> None:
        """Force immediate cleanup."""
        try:
            # Force garbage collection
            collected = gc.collect()

            # Clear all weak references
            self._weak_refs.clear()

            # Clear old leak reports
            with self._lock:
                if len(self._leak_reports) > 20:
                    self._leak_reports = self._leak_reports[-10:]

            logger.info(f"🧹 Force cleanup completed: {collected} objects collected")

        except Exception as e:
            logger.error(f"Error during force cleanup: {e}")

    def register_object(self, obj: Any, obj_type: str = "unknown") -> None:
        """Register an object for lifecycle monitoring."""
        obj_id = id(obj)

        with self._lock:
            self._object_registry[obj_id] = {
                "type": obj_type,
                "created_at": time.time(),
                "memory_usage": sys.getsizeof(obj),
            }

            # Create weak reference for cleanup detection
            weak_ref = weakref.ref(obj, self._object_cleanup_callback)
            self._weak_refs.add(weak_ref)

            self._total_objects_created += 1

    def unregister_object(self, obj: Any) -> None:
        """Unregister an object from lifecycle monitoring."""
        obj_id = id(obj)

        with self._lock:
            if obj_id in self._object_registry:
                del self._object_registry[obj_id]
                self._total_objects_destroyed += 1

    def _object_cleanup_callback(self, weak_ref: weakref.ReferenceType) -> None:
        """Callback when a monitored object is garbage collected."""
        self._weak_refs.discard(weak_ref)
        self._total_objects_destroyed += 1

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        if not self._snapshots:
            return {}

        latest = self._snapshots[-1]

        return {
            "current_memory_mb": latest.memory_usage / 1024 / 1024,
            "peak_memory_mb": self._peak_memory_usage / 1024 / 1024,
            "object_count": latest.object_count,
            "monitored_objects": len(self._object_registry),
            "total_objects_created": self._total_objects_created,
            "total_objects_destroyed": self._total_objects_destroyed,
            "cleanup_count": self._cleanup_count,
            "leak_reports_count": len(self._leak_reports),
            "snapshots_count": len(self._snapshots),
        }

    def get_leak_reports(self) -> List[MemoryLeakReport]:
        """Get all memory leak reports."""
        with self._lock:
            return self._leak_reports.copy()

    def add_memory_pressure_callback(self, callback: Callable) -> None:
        """Add a callback for memory pressure events."""
        self._memory_pressure_callbacks.append(callback)

    def add_leak_detection_callback(self, callback: Callable) -> None:
        """Add a callback for leak detection events."""
        self._leak_detected_callbacks.append(callback)

    def is_monitoring(self) -> bool:
        """Check if monitoring is currently active."""
        return (
            self._monitoring_thread is not None and self._monitoring_thread.is_alive()
        )


# Global instance for easy access
_memory_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """Get the global memory monitor instance."""
    global _memory_monitor
    if _memory_monitor is None:
        _memory_monitor = MemoryMonitor()
    return _memory_monitor


def start_memory_monitoring(interval: float = 30.0) -> None:
    """Start global memory monitoring."""
    monitor = get_memory_monitor()
    monitor.monitoring_interval = interval
    monitor.start_monitoring()


def stop_memory_monitoring() -> None:
    """Stop global memory monitoring."""
    monitor = get_memory_monitor()
    monitor.stop_monitoring()


def force_memory_cleanup() -> None:
    """Force global memory cleanup."""
    monitor = get_memory_monitor()
    monitor.force_cleanup()


def get_memory_stats() -> Dict[str, Any]:
    """Get global memory statistics."""
    monitor = get_memory_monitor()
    return monitor.get_memory_stats()


def register_object_for_monitoring(obj: Any, obj_type: str = "unknown") -> None:
    """Register an object for global monitoring."""
    monitor = get_memory_monitor()
    monitor.register_object(obj, obj_type)


def unregister_object_from_monitoring(obj: Any) -> None:
    """Unregister an object from global monitoring."""
    monitor = get_memory_monitor()
    monitor.unregister_object(obj)
