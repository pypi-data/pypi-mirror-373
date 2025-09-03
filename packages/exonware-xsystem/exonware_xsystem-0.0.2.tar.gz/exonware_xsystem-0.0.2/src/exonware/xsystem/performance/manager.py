#!/usr/bin/env python3
"""
Generic Performance Management for xSystem.

This module provides a generic performance management framework that can be used
by any library in the xComBot framework. It handles performance mode management,
health monitoring, and recommendations without being tied to specific implementations.
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ..config import PerformanceMode, PerformanceProfiles
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.performance.manager")


@dataclass
class PerformanceRecommendation:
    """A performance recommendation with priority and action."""

    type: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    message: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Performance health status information."""

    status: str  # 'excellent', 'good', 'fair', 'poor', 'critical'
    health_score: int  # 0-100
    warnings: Dict[str, bool] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


class GenericPerformanceManager:
    """
    Generic performance management framework.

    This class provides reusable performance management functionality that can be
    inherited by library-specific performance managers (like xNode's PerformanceModes).
    """

    def __init__(self, component_name: str):
        """Initialize generic performance manager."""
        self.component_name = component_name
        self._lock = threading.RLock()
        self._mode_history: List[Dict[str, Any]] = []
        self._performance_stats: Dict[str, Any] = {}
        self._last_mode_change = time.time()
        self._local_mode = None
        self._local_config = None

        logger.info(f"🔧 Generic performance manager initialized for {component_name}")

    # ============================================================================
    # GENERIC PERFORMANCE MODE MANAGEMENT
    # ============================================================================

    def set_performance_mode(
        self, mode: PerformanceMode
    ) -> "GenericPerformanceManager":
        """Set the performance mode for this component."""
        with self._lock:
            old_mode = self.get_performance_mode()
            if mode != old_mode:
                if mode == PerformanceMode.GLOBAL:
                    # Follow global settings
                    self._local_mode = None
                    self._local_config = None
                else:
                    # Use local settings
                    self._local_mode = mode
                    self._local_config = self._create_local_config(mode)

                self._mode_history.append(
                    {
                        "timestamp": time.time(),
                        "old_mode": old_mode,
                        "new_mode": mode,
                        "component": self.component_name,
                    }
                )
                self._last_mode_change = time.time()
                logger.info(
                    f"Performance mode changed from {old_mode} to {mode} for {self.component_name}"
                )

        return self

    def get_performance_mode(self) -> PerformanceMode:
        """Get the current performance mode (local or global)."""
        if hasattr(self, "_local_mode") and self._local_mode is not None:
            return self._local_mode
        # This should be overridden by subclasses to get global mode
        return PerformanceMode.FAST  # Default fallback

    def get_effective_config(self) -> Optional[PerformanceConfig]:
        """Get effective config (local or global)."""
        if hasattr(self, "_local_config") and self._local_config is not None:
            return self._local_config
        # This should be overridden by subclasses to get global config
        return None

    def _create_local_config(self, mode: PerformanceMode) -> PerformanceConfig:
        """Create local configuration for the given mode."""
        # This should be overridden by subclasses
        return {"performance_mode": mode}

    def get_mode_history(self) -> List[Dict[str, Any]]:
        """Get the history of performance mode changes."""
        with self._lock:
            return self._mode_history.copy()

    def reset_mode_history(self) -> "GenericPerformanceManager":
        """Reset the performance mode history."""
        with self._lock:
            self._mode_history.clear()
        return self

    # ============================================================================
    # GENERIC PERFORMANCE STATISTICS
    # ============================================================================

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self._lock:
            current_mode = self.get_performance_mode()

            stats = {
                "component_name": self.component_name,
                "current_mode": current_mode.name,
                "mode_type": (
                    "local"
                    if hasattr(self, "_local_mode") and self._local_mode is not None
                    else "global"
                ),
                "mode_uptime": time.time() - self._last_mode_change,
                "mode_history_count": len(self._mode_history),
                "cache_stats": self._get_cache_stats(),
                "memory_stats": self._get_memory_stats(),
                "operation_stats": self._get_operation_stats(),
            }

            # Add adaptive learning statistics if in ADAPTIVE mode
            if current_mode == PerformanceMode.ADAPTIVE:
                stats["adaptive_learning"] = self._get_adaptive_stats()

            # Add dual adaptive learning statistics if in DUAL_ADAPTIVE mode
            if current_mode == PerformanceMode.DUAL_ADAPTIVE:
                stats["dual_adaptive_learning"] = self._get_adaptive_stats()

            return stats

    def get_health_status(self) -> HealthStatus:
        """Get performance health status."""
        stats = self.get_performance_stats()

        # Determine health based on various metrics
        health_score = 100
        warnings = {}

        # Check cache hit rate
        cache_stats = stats.get("cache_stats", {})
        cache_hit_rate = cache_stats.get("hit_rate", 0)
        if cache_hit_rate < 0.5:
            health_score -= 20
            warnings["low_cache_hit_rate"] = True

        # Check memory usage
        memory_stats = stats.get("memory_stats", {})
        memory_percent = memory_stats.get("memory_percent", 0)
        if memory_percent > 80:
            health_score -= 30
            warnings["high_memory_usage"] = True

        # Check error rates
        error_rate = stats.get("error_rate", 0)
        if error_rate > 5:
            health_score -= 25
            warnings["high_error_rate"] = True

        # Check mode changes
        mode_history_count = stats.get("mode_history_count", 0)
        if mode_history_count > 10:
            health_score -= 10
            warnings["frequent_mode_changes"] = True

        # Determine status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        elif health_score >= 25:
            status = "poor"
        else:
            status = "critical"

        return HealthStatus(
            status=status, health_score=health_score, warnings=warnings, details=stats
        )

    def optimize_for_workload(
        self, workload_type: str, **kwargs
    ) -> "GenericPerformanceManager":
        """Optimize performance mode for a specific workload type."""
        workload_configs = {
            "read_heavy": PerformanceMode.FAST,
            "write_heavy": PerformanceMode.OPTIMIZED,
            "mixed": PerformanceMode.ADAPTIVE,
            "large_data": PerformanceMode.DUAL_ADAPTIVE,
            "real_time": PerformanceMode.FAST,
            "batch_processing": PerformanceMode.OPTIMIZED,
        }

        if workload_type in workload_configs:
            mode = workload_configs[workload_type]
            self.set_performance_mode(mode)
            logger.info(
                f"Optimized {self.component_name} for {workload_type} workload using {mode} mode"
            )
        else:
            logger.warning(f"Unknown workload type: {workload_type}")

        return self

    def auto_optimize(self) -> "GenericPerformanceManager":
        """Automatically optimize performance based on current usage patterns."""
        stats = self.get_performance_stats()

        # Simple auto-optimization logic
        memory_percent = stats.get("memory_stats", {}).get("memory_percent", 0)
        cache_hit_rate = stats.get("cache_stats", {}).get("hit_rate", 0)

        current_mode = self.get_performance_mode()

        if memory_percent > 80:
            # High memory usage - switch to optimized mode
            if current_mode != PerformanceMode.OPTIMIZED:
                self.set_performance_mode(PerformanceMode.OPTIMIZED)
        elif cache_hit_rate < 0.3:
            # Low cache hit rate - switch to adaptive mode
            if current_mode not in [
                PerformanceMode.ADAPTIVE,
                PerformanceMode.DUAL_ADAPTIVE,
            ]:
                self.set_performance_mode(PerformanceMode.ADAPTIVE)
        elif memory_percent < 30 and cache_hit_rate > 0.8:
            # Good conditions - can use fast mode
            if current_mode != PerformanceMode.FAST:
                self.set_performance_mode(PerformanceMode.FAST)

        return self

    # ============================================================================
    # GENERIC PERFORMANCE MONITORING
    # ============================================================================

    def start_performance_monitoring(self) -> "GenericPerformanceManager":
        """Start performance monitoring."""
        logger.info(f"Performance monitoring started for {self.component_name}")
        return self

    def stop_performance_monitoring(self) -> "GenericPerformanceManager":
        """Stop performance monitoring."""
        logger.info(f"Performance monitoring stopped for {self.component_name}")
        return self

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        stats = self.get_performance_stats()
        health = self.get_health_status()

        return {
            "component_name": self.component_name,
            "timestamp": time.time(),
            "health_status": health,
            "performance_stats": stats,
            "recommendations": self._generate_recommendations(stats, health),
        }

    def benchmark_performance(
        self, test_operations: List[callable] = None
    ) -> Dict[str, Any]:
        """Run performance benchmarks."""
        if test_operations is None:
            test_operations = []

        results = {}

        # Test different modes
        for mode in [
            PerformanceMode.FAST,
            PerformanceMode.OPTIMIZED,
            PerformanceMode.ADAPTIVE,
        ]:
            self.set_performance_mode(mode)
            time.sleep(0.1)  # Let mode settle

            start_time = time.time()
            # Run test operations
            for operation in test_operations:
                try:
                    operation()
                except Exception as e:
                    logger.warning(f"Benchmark operation failed: {e}")
            end_time = time.time()

            results[mode.name] = {
                "execution_time": end_time - start_time,
                "operations_per_second": (
                    len(test_operations) / (end_time - start_time)
                    if test_operations
                    else 0
                ),
            }

        return results

    # ============================================================================
    # GENERIC HELPER METHODS (to be overridden by subclasses)
    # ============================================================================

    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics. Override in subclasses."""
        return {"hit_rate": 0.0, "miss_rate": 0.0, "size": 0, "max_size": 0}

    def _get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "memory_percent": process.memory_percent(),
                "available_memory": psutil.virtual_memory().available,
            }
        except Exception as e:
            logger.warning(f"Failed to get memory stats: {e}")
            return {"error": str(e)}

    def _get_operation_stats(self) -> Dict[str, Any]:
        """Get operation statistics. Override in subclasses."""
        return {
            "total_operations": 0,
            "average_operation_time": 0.0,
            "slowest_operation": None,
            "fastest_operation": None,
        }

    def _get_adaptive_stats(self) -> Dict[str, Any]:
        """Get adaptive learning statistics. Override in subclasses."""
        return {"learning_rate": 0.0, "adaptation_count": 0, "last_adaptation": None}

    def _generate_recommendations(
        self, stats: Dict[str, Any], health: HealthStatus
    ) -> List[PerformanceRecommendation]:
        """Generate performance recommendations."""
        recommendations = []

        # Check cache performance
        cache_hit_rate = stats.get("cache_stats", {}).get("hit_rate", 0)
        if cache_hit_rate < 0.5:
            recommendations.append(
                PerformanceRecommendation(
                    type="cache",
                    priority="high",
                    message="Cache hit rate is low. Consider increasing cache size or optimizing access patterns.",
                    action="increase_cache_size",
                    details={"current_hit_rate": cache_hit_rate},
                )
            )

        # Check memory usage
        memory_percent = stats.get("memory_stats", {}).get("memory_percent", 0)
        if memory_percent > 80:
            recommendations.append(
                PerformanceRecommendation(
                    type="memory",
                    priority="high",
                    message="Memory usage is high. Consider switching to optimized mode or reducing data size.",
                    action="switch_to_optimized_mode",
                    details={"current_memory_percent": memory_percent},
                )
            )

        # Check error rates
        error_rate = stats.get("error_rate", 0)
        if error_rate > 5:
            recommendations.append(
                PerformanceRecommendation(
                    type="stability",
                    priority="medium",
                    message="High error rate detected. Check for data consistency issues.",
                    action="check_data_consistency",
                    details={"current_error_rate": error_rate},
                )
            )

        # Check mode changes
        mode_history_count = stats.get("mode_history_count", 0)
        if mode_history_count > 10:
            recommendations.append(
                PerformanceRecommendation(
                    type="stability",
                    priority="medium",
                    message="Frequent performance mode changes detected. Consider using adaptive mode.",
                    action="use_adaptive_mode",
                    details={"mode_changes": mode_history_count},
                )
            )

        return recommendations

    # ============================================================================
    # GENERIC PERFORMANCE MODE ALIASES
    # ============================================================================

    def fast_mode(self) -> "GenericPerformanceManager":
        """Switch to fast performance mode."""
        return self.set_performance_mode(PerformanceMode.FAST)

    def optimized_mode(self) -> "GenericPerformanceManager":
        """Switch to optimized performance mode."""
        return self.set_performance_mode(PerformanceMode.OPTIMIZED)

    def adaptive_mode(self) -> "GenericPerformanceManager":
        """Switch to adaptive performance mode."""
        return self.set_performance_mode(PerformanceMode.ADAPTIVE)

    def dual_adaptive_mode(self) -> "GenericPerformanceManager":
        """Switch to dual adaptive performance mode."""
        return self.set_performance_mode(PerformanceMode.DUAL_ADAPTIVE)

    def manual_mode(self, **config_overrides) -> "GenericPerformanceManager":
        """Switch to manual performance mode with custom configuration."""
        self.set_performance_mode(PerformanceMode.MANUAL)

        # Apply overrides - to be implemented by subclasses
        self._apply_manual_overrides(config_overrides)

        return self

    def _apply_manual_overrides(self, config_overrides: Dict[str, Any]) -> None:
        """Apply manual configuration overrides. Override in subclasses."""
        pass
