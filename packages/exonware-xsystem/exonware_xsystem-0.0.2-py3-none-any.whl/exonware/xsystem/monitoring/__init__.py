"""
xSystem Monitoring Package

Provides performance monitoring, metrics collection, system observation utilities,
memory monitoring, error recovery, and resilience mechanisms.
"""

from .error_recovery import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    ErrorContext,
    ErrorRecoveryManager,
    circuit_breaker,
    get_error_recovery_manager,
    graceful_degradation,
    handle_error,
    retry_with_backoff,
)

# Production-ready monitoring and recovery modules
from .memory_monitor import (
    MemoryLeakReport,
    MemoryMonitor,
    MemorySnapshot,
    force_memory_cleanup,
    get_memory_monitor,
    get_memory_stats,
    register_object_for_monitoring,
    start_memory_monitoring,
    stop_memory_monitoring,
    unregister_object_from_monitoring,
)
from .metrics import (
    GenericMetrics,
    OperationMetrics,
    create_component_metrics,
    get_metrics,
    reset_metrics,
)
from .performance_monitor import (
    PerformanceMonitor,
    PerformanceStats,
    calculate_performance_summary,
    create_performance_monitor,
    enhanced_error_context,
    format_performance_report,
    performance_context,
)
from .performance_validator import (
    PerformanceMetric,
    PerformanceReport,
    PerformanceThreshold,
    PerformanceValidator,
    get_performance_statistics,
    get_performance_validator,
    performance_monitor,
    record_performance_metric,
    start_performance_validation,
    stop_performance_validation,
    validate_performance,
)

__all__ = [
    # Performance Monitor
    "PerformanceMonitor",
    "PerformanceStats",
    "create_performance_monitor",
    "performance_context",
    "enhanced_error_context",
    "calculate_performance_summary",
    "format_performance_report",
    # Generic Metrics
    "GenericMetrics",
    "OperationMetrics",
    "get_metrics",
    "reset_metrics",
    "create_component_metrics",
    # Memory Monitoring
    "MemoryMonitor",
    "MemorySnapshot",
    "MemoryLeakReport",
    "get_memory_monitor",
    "start_memory_monitoring",
    "stop_memory_monitoring",
    "force_memory_cleanup",
    "get_memory_stats",
    "register_object_for_monitoring",
    "unregister_object_from_monitoring",
    # Error Recovery
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "ErrorRecoveryManager",
    "ErrorContext",
    "get_error_recovery_manager",
    "circuit_breaker",
    "retry_with_backoff",
    "graceful_degradation",
    "handle_error",
    # Performance Validation
    "PerformanceValidator",
    "PerformanceMetric",
    "PerformanceThreshold",
    "PerformanceReport",
    "get_performance_validator",
    "start_performance_validation",
    "stop_performance_validation",
    "record_performance_metric",
    "validate_performance",
    "get_performance_statistics",
    "performance_monitor",
]
