"""
Performance Validation and Monitoring for xSystem Library.

This module provides comprehensive performance validation, statistical analysis,
and regression detection for production deployment.
"""

import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.performance_validator")


@dataclass
class PerformanceMetric:
    """Performance metric data point."""

    operation_name: str
    duration: float  # seconds
    timestamp: float
    success: bool = True
    error_info: Optional[Dict[str, Any]] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""

    operation_name: str
    max_duration: float  # seconds
    max_error_rate: float = 0.1  # 10%
    min_throughput: float = 0.0  # operations per second
    percentile_95: Optional[float] = None  # 95th percentile threshold
    percentile_99: Optional[float] = None  # 99th percentile threshold


@dataclass
class PerformanceReport:
    """Performance analysis report."""

    operation_name: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    average_duration: float
    min_duration: float
    max_duration: float
    percentile_50: float  # median
    percentile_95: float
    percentile_99: float
    error_rate: float
    throughput: float  # operations per second
    threshold_violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class PerformanceValidator:
    """
    Comprehensive performance validation and monitoring system.

    Features:
    - Real-time performance monitoring
    - Statistical analysis (percentiles, averages)
    - Threshold validation
    - Regression detection
    - Performance reporting
    - Trend analysis
    """

    def __init__(
        self,
        max_metrics_per_operation: int = 1000,
        validation_interval: float = 60.0,
        enable_regression_detection: bool = True,
    ):
        """Initialize performance validator."""
        self.max_metrics_per_operation = max_metrics_per_operation
        self.validation_interval = validation_interval
        self.enable_regression_detection = enable_regression_detection

        # Performance data storage
        self._metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_metrics_per_operation)
        )
        self._thresholds: Dict[str, PerformanceThreshold] = {}
        self._baseline_performance: Dict[str, Dict[str, float]] = {}

        # Thread safety
        self._lock = threading.RLock()
        self._validation_thread: Optional[threading.Thread] = None
        self._stop_validation = threading.Event()

        # Statistics
        self._total_metrics_recorded = 0
        self._threshold_violations = 0
        self._regressions_detected = 0

        # Callbacks
        self._threshold_violation_callbacks: List[Callable] = []
        self._regression_detected_callbacks: List[Callable] = []

        logger.info("📊 Performance validator initialized")

    def register_threshold(self, threshold: PerformanceThreshold) -> None:
        """Register a performance threshold."""
        with self._lock:
            self._thresholds[threshold.operation_name] = threshold
            logger.info(f"📏 Registered threshold for '{threshold.operation_name}'")

    def record_metric(
        self,
        operation_name: str,
        duration: float,
        success: bool = True,
        error_info: Optional[Dict[str, Any]] = None,
        additional_data: Dict[str, Any] = None,
    ) -> None:
        """Record a performance metric."""
        if additional_data is None:
            additional_data = {}

        metric = PerformanceMetric(
            operation_name=operation_name,
            duration=duration,
            timestamp=time.time(),
            success=success,
            error_info=error_info,
            additional_data=additional_data,
        )

        with self._lock:
            self._metrics[operation_name].append(metric)
            self._total_metrics_recorded += 1

    def get_operation_metrics(self, operation_name: str) -> List[PerformanceMetric]:
        """Get all metrics for a specific operation."""
        with self._lock:
            return list(self._metrics.get(operation_name, []))

    def calculate_percentiles(self, durations: List[float]) -> Dict[str, float]:
        """Calculate percentiles for a list of durations."""
        if not durations:
            return {}

        sorted_durations = sorted(durations)
        n = len(sorted_durations)

        return {
            "min": sorted_durations[0],
            "max": sorted_durations[-1],
            "average": statistics.mean(sorted_durations),
            "median": statistics.median(sorted_durations),
            "percentile_50": sorted_durations[int(0.5 * n)],
            "percentile_90": sorted_durations[int(0.9 * n)],
            "percentile_95": sorted_durations[int(0.95 * n)],
            "percentile_99": sorted_durations[int(0.99 * n)],
        }

    def validate_performance(self, operation_name: str) -> PerformanceReport:
        """Validate performance for a specific operation."""
        metrics = self.get_operation_metrics(operation_name)
        if not metrics:
            return PerformanceReport(
                operation_name=operation_name,
                total_operations=0,
                successful_operations=0,
                failed_operations=0,
                average_duration=0.0,
                min_duration=0.0,
                max_duration=0.0,
                percentile_50=0.0,
                percentile_95=0.0,
                percentile_99=0.0,
                error_rate=0.0,
                throughput=0.0,
            )

        # Calculate basic statistics
        durations = [m.duration for m in metrics]
        successful = [m for m in metrics if m.success]
        failed = [m for m in metrics if not m.success]

        percentiles = self.calculate_percentiles(durations)

        # Calculate throughput (operations per second)
        if metrics:
            time_span = metrics[-1].timestamp - metrics[0].timestamp
            throughput = len(metrics) / time_span if time_span > 0 else 0.0
        else:
            throughput = 0.0

        # Create report
        report = PerformanceReport(
            operation_name=operation_name,
            total_operations=len(metrics),
            successful_operations=len(successful),
            failed_operations=len(failed),
            average_duration=percentiles.get("average", 0.0),
            min_duration=percentiles.get("min", 0.0),
            max_duration=percentiles.get("max", 0.0),
            percentile_50=percentiles.get("percentile_50", 0.0),
            percentile_95=percentiles.get("percentile_95", 0.0),
            percentile_99=percentiles.get("percentile_99", 0.0),
            error_rate=len(failed) / len(metrics) if metrics else 0.0,
            throughput=throughput,
        )

        # Check thresholds
        threshold = self._thresholds.get(operation_name)
        if threshold:
            violations = []

            if report.average_duration > threshold.max_duration:
                violations.append(
                    f"Average duration ({report.average_duration:.3f}s) exceeds threshold ({threshold.max_duration:.3f}s)"
                )

            if report.error_rate > threshold.max_error_rate:
                violations.append(
                    f"Error rate ({report.error_rate:.1%}) exceeds threshold ({threshold.max_error_rate:.1%})"
                )

            if report.throughput < threshold.min_throughput:
                violations.append(
                    f"Throughput ({report.throughput:.2f} ops/s) below threshold ({threshold.min_throughput:.2f} ops/s)"
                )

            if (
                threshold.percentile_95
                and report.percentile_95 > threshold.percentile_95
            ):
                violations.append(
                    f"95th percentile ({report.percentile_95:.3f}s) exceeds threshold ({threshold.percentile_95:.3f}s)"
                )

            if (
                threshold.percentile_99
                and report.percentile_99 > threshold.percentile_99
            ):
                violations.append(
                    f"99th percentile ({report.percentile_99:.3f}s) exceeds threshold ({threshold.percentile_99:.3f}s)"
                )

            report.threshold_violations = violations

            if violations:
                self._threshold_violations += 1
                logger.warning(
                    f"⚠️ Performance threshold violations for '{operation_name}': {violations}"
                )

                # Trigger callbacks
                for callback in self._threshold_violation_callbacks:
                    try:
                        callback(operation_name, violations, report)
                    except Exception as e:
                        logger.error(f"Error in threshold violation callback: {e}")

        return report

    def validate_all_operations(self) -> Dict[str, PerformanceReport]:
        """Validate performance for all operations."""
        with self._lock:
            operation_names = set(self._metrics.keys())

        reports = {}
        for operation_name in operation_names:
            reports[operation_name] = self.validate_performance(operation_name)

        return reports

    def detect_regression(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """Detect performance regression compared to baseline."""
        if not self.enable_regression_detection:
            return None

        baseline = self._baseline_performance.get(operation_name)
        if not baseline:
            return None

        current_report = self.validate_performance(operation_name)
        if current_report.total_operations < 10:  # Need sufficient data
            return None

        regression_info = {
            "operation_name": operation_name,
            "baseline": baseline,
            "current": {
                "average_duration": current_report.average_duration,
                "error_rate": current_report.error_rate,
                "throughput": current_report.throughput,
                "percentile_95": current_report.percentile_95,
            },
            "changes": {},
            "is_regression": False,
        }

        # Calculate changes
        for metric in ["average_duration", "error_rate", "percentile_95"]:
            baseline_value = baseline.get(metric, 0.0)
            current_value = regression_info["current"][metric]

            if baseline_value > 0:
                change_pct = ((current_value - baseline_value) / baseline_value) * 100
                regression_info["changes"][metric] = change_pct

                # Check for significant regression
                if metric == "average_duration" and change_pct > 20:  # 20% slower
                    regression_info["is_regression"] = True
                elif metric == "error_rate" and change_pct > 50:  # 50% more errors
                    regression_info["is_regression"] = True
                elif metric == "percentile_95" and change_pct > 25:  # 25% slower p95
                    regression_info["is_regression"] = True

        # Check throughput regression
        baseline_throughput = baseline.get("throughput", 0.0)
        current_throughput = current_report.throughput
        if baseline_throughput > 0:
            throughput_change = (
                (current_throughput - baseline_throughput) / baseline_throughput
            ) * 100
            regression_info["changes"]["throughput"] = throughput_change

            if throughput_change < -20:  # 20% lower throughput
                regression_info["is_regression"] = True

        if regression_info["is_regression"]:
            self._regressions_detected += 1
            logger.warning(
                f"📉 Performance regression detected for '{operation_name}': {regression_info['changes']}"
            )

            # Trigger callbacks
            for callback in self._regression_detected_callbacks:
                try:
                    callback(regression_info)
                except Exception as e:
                    logger.error(f"Error in regression detection callback: {e}")

        return regression_info

    def set_baseline(self, operation_name: str) -> None:
        """Set performance baseline for an operation."""
        report = self.validate_performance(operation_name)
        if report.total_operations < 10:
            logger.warning(
                f"⚠️ Insufficient data for baseline: {report.total_operations} operations"
            )
            return

        with self._lock:
            self._baseline_performance[operation_name] = {
                "average_duration": report.average_duration,
                "error_rate": report.error_rate,
                "throughput": report.throughput,
                "percentile_95": report.percentile_95,
                "timestamp": time.time(),
            }

        logger.info(
            f"📊 Baseline set for '{operation_name}': avg={report.average_duration:.3f}s, error_rate={report.error_rate:.1%}"
        )

    def start_validation(self) -> None:
        """Start continuous performance validation."""
        if self._validation_thread is not None and self._validation_thread.is_alive():
            logger.warning("Performance validation already running")
            return

        self._stop_validation.clear()
        self._validation_thread = threading.Thread(
            target=self._validation_loop, name="PerformanceValidator", daemon=True
        )
        self._validation_thread.start()
        logger.info("🚀 Performance validation started")

    def stop_validation(self) -> None:
        """Stop continuous performance validation."""
        if self._validation_thread is None or not self._validation_thread.is_alive():
            logger.warning("Performance validation not running")
            return

        self._stop_validation.set()
        self._validation_thread.join(timeout=5.0)
        logger.info("⏹️ Performance validation stopped")

    def _validation_loop(self) -> None:
        """Main validation loop."""
        while not self._stop_validation.is_set():
            try:
                # Validate all operations
                reports = self.validate_all_operations()

                # Detect regressions
                if self.enable_regression_detection:
                    for operation_name in reports.keys():
                        self.detect_regression(operation_name)

                # Wait for next interval
                self._stop_validation.wait(self.validation_interval)
            except Exception as e:
                logger.error(f"Error in validation loop: {e}")
                time.sleep(1.0)  # Brief pause on error

    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get overall performance statistics."""
        with self._lock:
            total_operations = sum(len(metrics) for metrics in self._metrics.values())
            total_thresholds = len(self._thresholds)
            total_baselines = len(self._baseline_performance)

            return {
                "total_metrics_recorded": self._total_metrics_recorded,
                "total_operations": total_operations,
                "operations_monitored": len(self._metrics),
                "thresholds_registered": total_thresholds,
                "baselines_set": total_baselines,
                "threshold_violations": self._threshold_violations,
                "regressions_detected": self._regressions_detected,
                "is_validating": self.is_validating(),
            }

    def add_threshold_violation_callback(self, callback: Callable) -> None:
        """Add a callback for threshold violation events."""
        self._threshold_violation_callbacks.append(callback)

    def add_regression_detection_callback(self, callback: Callable) -> None:
        """Add a callback for regression detection events."""
        self._regression_detected_callbacks.append(callback)

    def is_validating(self) -> bool:
        """Check if validation is currently active."""
        return (
            self._validation_thread is not None and self._validation_thread.is_alive()
        )

    def clear_metrics(self, operation_name: Optional[str] = None) -> None:
        """Clear performance metrics."""
        with self._lock:
            if operation_name:
                if operation_name in self._metrics:
                    self._metrics[operation_name].clear()
                    logger.info(f"🧹 Cleared metrics for '{operation_name}'")
            else:
                self._metrics.clear()
                logger.info("🧹 Cleared all performance metrics")


# Global instance for easy access
_performance_validator: Optional[PerformanceValidator] = None


def get_performance_validator() -> PerformanceValidator:
    """Get the global performance validator instance."""
    global _performance_validator
    if _performance_validator is None:
        _performance_validator = PerformanceValidator()
    return _performance_validator


def start_performance_validation(interval: float = 60.0) -> None:
    """Start global performance validation."""
    validator = get_performance_validator()
    validator.validation_interval = interval
    validator.start_validation()


def stop_performance_validation() -> None:
    """Stop global performance validation."""
    validator = get_performance_validator()
    validator.stop_validation()


def record_performance_metric(
    operation_name: str,
    duration: float,
    success: bool = True,
    error_info: Optional[Dict[str, Any]] = None,
    additional_data: Dict[str, Any] = None,
) -> None:
    """Record a global performance metric."""
    validator = get_performance_validator()
    validator.record_metric(
        operation_name, duration, success, error_info, additional_data
    )


def validate_performance(operation_name: str) -> PerformanceReport:
    """Validate performance for a specific operation."""
    validator = get_performance_validator()
    return validator.validate_performance(operation_name)


def get_performance_statistics() -> Dict[str, Any]:
    """Get global performance statistics."""
    validator = get_performance_validator()
    return validator.get_performance_statistics()


def performance_monitor(operation_name: str):
    """
    Decorator for automatic performance monitoring.

    Args:
        operation_name: Name of the operation to monitor
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            success = True
            error_info = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_info = {"error_type": type(e).__name__, "error_message": str(e)}
                raise
            finally:
                duration = time.perf_counter() - start_time
                record_performance_metric(operation_name, duration, success, error_info)

        return wrapper

    return decorator
