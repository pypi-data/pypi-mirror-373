"""
Performance mode definitions for xSystem framework.

This module provides enums and utilities for managing performance optimization
modes across different components of the xSystem framework.
"""

import gc
import statistics
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil


class PerformanceMode(Enum):
    """Performance optimization modes for system operations."""

    GLOBAL = auto()  # Follow global system settings
    AUTO = auto()  # Automatic selection based on data characteristics
    PARENT = auto()  # Inherit from parent object
    DEFAULT = auto()  # Use default balanced settings
    FAST = auto()  # Prioritize speed over memory
    OPTIMIZED = auto()  # Prioritize memory efficiency
    MANUAL = auto()  # Use specific custom settings
    ADAPTIVE = auto()  # Runtime adaptation based on performance monitoring
    DUAL_ADAPTIVE = auto()  # Smart dual-phase: fast cruise + intelligent deep-dive

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str) -> "PerformanceMode":
        """Create PerformanceMode from string representation."""
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid performance mode: {value}")


@dataclass
class PerformanceProfile:
    """Configuration profile for different performance modes."""

    # Cache settings
    path_cache_size: int
    node_pool_size: int
    conversion_cache_size: int

    # Lazy loading thresholds
    lazy_threshold_dict: int
    lazy_threshold_list: int

    # Memory management
    enable_weak_refs: bool
    enable_object_pooling: bool

    # Performance features
    enable_path_caching: bool
    enable_conversion_caching: bool
    enable_optimized_iteration: bool

    # Threading
    enable_thread_safety: bool
    lock_timeout: float

    # Security limits (always enforced)
    max_depth: int
    max_nodes: int
    max_path_length: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "path_cache_size": self.path_cache_size,
            "node_pool_size": self.node_pool_size,
            "conversion_cache_size": self.conversion_cache_size,
            "lazy_threshold_dict": self.lazy_threshold_dict,
            "lazy_threshold_list": self.lazy_threshold_list,
            "enable_weak_refs": self.enable_weak_refs,
            "enable_object_pooling": self.enable_object_pooling,
            "enable_path_caching": self.enable_path_caching,
            "enable_conversion_caching": self.enable_conversion_caching,
            "enable_optimized_iteration": self.enable_optimized_iteration,
            "enable_thread_safety": self.enable_thread_safety,
            "lock_timeout": self.lock_timeout,
            "max_depth": self.max_depth,
            "max_nodes": self.max_nodes,
            "max_path_length": self.max_path_length,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceProfile":
        """Create profile from dictionary."""
        return cls(**data)


@dataclass
class AdaptiveProfile(PerformanceProfile):
    """Enhanced profile for ADAPTIVE mode with learning capabilities."""

    # Learning parameters
    learning_enabled: bool = True
    adaptation_threshold: float = 0.1  # 10% performance improvement threshold
    history_size: int = 1000  # Number of operations to remember

    # Monitoring settings
    monitor_interval: float = 1.0  # Check performance every second
    memory_pressure_threshold: float = 0.8  # 80% memory usage triggers adaptation
    cpu_usage_threshold: float = 0.7  # 70% CPU usage triggers adaptation

    # Hybrid strategy settings
    enable_hybrid_strategies: bool = True
    max_mode_switches_per_second: int = 10
    cooldown_period: float = 5.0  # Seconds between adaptations

    # Performance tracking
    operation_history: List[Dict[str, Any]] = field(default_factory=list)
    mode_performance: Dict[str, List[float]] = field(default_factory=dict)
    last_adaptation: float = field(default_factory=time.time)


@dataclass
class DualAdaptiveProfile(PerformanceProfile):
    """Smart dual-phase adaptive profile: fast cruise + intelligent deep-dive."""

    # Phase 1: CRUISE (Fast, low-overhead monitoring)
    cruise_sample_rate: int = 50  # Sample every 50th operation
    cruise_monitor_interval: float = 5.0  # Check system every 5 seconds
    cruise_history_size: int = 200  # Keep only 200 operations in cruise

    # Phase 2: DEEP_DIVE (Intensive learning)
    deep_dive_trigger_threshold: float = (
        0.15  # 15% performance degradation triggers deep-dive
    )
    deep_dive_duration: int = 500  # Deep-dive for 500 operations
    deep_dive_sample_rate: int = 1  # Sample every operation in deep-dive
    deep_dive_history_size: int = 1000  # Keep detailed history during deep-dive

    # Smart triggers
    memory_pressure_threshold: float = 0.8  # 80% memory usage triggers deep-dive
    cpu_pressure_threshold: float = 0.7  # 70% CPU usage triggers deep-dive
    performance_degradation_threshold: float = 0.2  # 20% degradation triggers deep-dive

    # Learning parameters
    learning_enabled: bool = True
    adaptation_threshold: float = 0.1  # 10% improvement threshold
    cooldown_period: float = 10.0  # 10 seconds between adaptations

    # Performance tracking
    operation_history: List[Dict[str, Any]] = field(default_factory=list)
    mode_performance: Dict[str, List[float]] = field(default_factory=dict)
    last_adaptation: float = field(default_factory=time.time)

    # Phase tracking
    current_phase: str = "CRUISE"  # CRUISE or DEEP_DIVE
    phase_start_time: float = field(default_factory=time.time)
    operations_in_phase: int = 0
    deep_dive_trigger_count: int = 0


@dataclass
class PerformanceMetrics:
    """Container for performance metrics and statistics."""

    operation_type: str
    mode_used: PerformanceMode
    execution_time: float
    memory_usage: float
    cache_hits: int
    cache_misses: int
    timestamp: float = field(default_factory=time.time)

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def performance_score(self) -> float:
        """Calculate overall performance score (higher is better)."""
        # Weighted combination of speed and efficiency
        speed_score = 1.0 / (1.0 + self.execution_time)  # Faster = higher score
        memory_score = 1.0 / (1.0 + self.memory_usage)  # Less memory = higher score
        cache_score = self.cache_hit_rate

        return 0.4 * speed_score + 0.3 * memory_score + 0.3 * cache_score


class AdaptiveLearningEngine:
    """Engine for learning and adapting performance strategies."""

    def __init__(self, profile: AdaptiveProfile):
        self.profile = profile
        self.metrics_history: List[PerformanceMetrics] = []
        # Initialize mode performance tracking without causing recursion
        self.mode_performance: Dict[str, List[float]] = {
            "AUTO": [],
            "DEFAULT": [],
            "FAST": [],
            "OPTIMIZED": [],
            "MANUAL": [],
            "PARENT": [],
            "ADAPTIVE": [],
            "DUAL_ADAPTIVE": [],
        }
        self.system_metrics: List[Dict[str, float]] = []
        self._lock = threading.RLock()
        self._last_system_check = 0.0

    def record_operation(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics for learning."""
        with self._lock:
            self.metrics_history.append(metrics)

            # Keep history size manageable
            if len(self.metrics_history) > self.profile.history_size:
                self.metrics_history.pop(0)

            # Track mode performance
            if metrics.mode_used != PerformanceMode.ADAPTIVE:
                self.mode_performance[metrics.mode_used.name].append(
                    metrics.performance_score
                )

                # Keep only recent performance data
                if len(self.mode_performance[metrics.mode_used.name]) > 100:
                    self.mode_performance[metrics.mode_used.name].pop(0)

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        current_time = time.time()

        # Cache system metrics for a short period
        if current_time - self._last_system_check < self.profile.monitor_interval:
            return self.system_metrics[-1] if self.system_metrics else {}

        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)

            metrics = {
                "memory_usage": memory.percent / 100.0,
                "cpu_usage": cpu / 100.0,
                "memory_available_mb": memory.available / (1024 * 1024),
                "timestamp": current_time,
            }

            self.system_metrics.append(metrics)
            self._last_system_check = current_time

            # Keep only recent system metrics
            if len(self.system_metrics) > 100:
                self.system_metrics.pop(0)

            return metrics
        except Exception:
            # Fallback if psutil is not available
            return {
                "memory_usage": 0.5,  # Assume moderate usage
                "cpu_usage": 0.3,  # Assume moderate usage
                "memory_available_mb": 1024,  # Assume 1GB available
                "timestamp": current_time,
            }

    def should_adapt(self) -> bool:
        """Determine if adaptation is needed."""
        current_time = time.time()

        # Check cooldown period
        if current_time - self.profile.last_adaptation < self.profile.cooldown_period:
            return False

        # Check system pressure
        system_metrics = self.get_system_metrics()
        if (
            system_metrics.get("memory_usage", 0)
            > self.profile.memory_pressure_threshold
            or system_metrics.get("cpu_usage", 0) > self.profile.cpu_usage_threshold
        ):
            return True

        # Check if we have enough data for learning
        if len(self.metrics_history) < 10:
            return False

        # Check for performance degradation
        recent_metrics = self.metrics_history[-10:]
        avg_performance = statistics.mean(m.performance_score for m in recent_metrics)

        # If recent performance is significantly worse than historical average
        if len(self.metrics_history) >= 50:
            historical_avg = statistics.mean(
                m.performance_score for m in self.metrics_history[:-10]
            )
            if avg_performance < historical_avg * (
                1 - self.profile.adaptation_threshold
            ):
                return True

        return False

    def get_optimal_mode(self, operation_type: str = "general") -> PerformanceMode:
        """Determine the optimal performance mode based on learning."""
        if not self.profile.learning_enabled or len(self.metrics_history) < 5:
            return PerformanceMode.AUTO

        # Get system metrics
        system_metrics = self.get_system_metrics()
        memory_pressure = system_metrics.get("memory_usage", 0.5)
        cpu_pressure = system_metrics.get("cpu_usage", 0.3)

        # Filter metrics by operation type if specified
        relevant_metrics = [
            m
            for m in self.metrics_history
            if operation_type == "general" or m.operation_type == operation_type
        ]

        if not relevant_metrics:
            return PerformanceMode.AUTO

        # Calculate mode performance scores
        mode_scores = {}
        for mode_name in self.mode_performance.keys():
            mode_metrics = [
                m for m in relevant_metrics if m.mode_used.name == mode_name
            ]
            if not mode_metrics:
                continue

            # Calculate weighted score based on recency and performance
            recent_metrics = mode_metrics[-20:]  # Last 20 operations
            avg_score = statistics.mean(m.performance_score for m in recent_metrics)

            # Adjust for system pressure
            if memory_pressure > 0.8:
                # Prefer memory-efficient modes under memory pressure
                if mode_name == "OPTIMIZED":
                    avg_score *= 1.2
                elif mode_name == "FAST":
                    avg_score *= 0.8
            elif cpu_pressure > 0.7:
                # Prefer fast modes under CPU pressure
                if mode_name == "FAST":
                    avg_score *= 1.2
                elif mode_name == "OPTIMIZED":
                    avg_score *= 0.9

            mode_scores[mode_name] = avg_score

        if not mode_scores:
            return PerformanceMode.AUTO

        # Return the best performing mode
        best_mode_name = max(mode_scores.items(), key=lambda x: x[1])[0]
        return PerformanceMode.from_string(best_mode_name)

    def adapt_profile(self, new_mode: PerformanceMode) -> None:
        """Adapt the profile based on the new optimal mode."""
        self.profile.last_adaptation = time.time()

        # Get the base profile for the new mode
        base_profile = PerformanceProfiles.get_profile(new_mode)

        # Update the adaptive profile with base settings
        for field in base_profile.__dataclass_fields__:
            if field != "operation_history" and field != "mode_performance":
                setattr(self.profile, field, getattr(base_profile, field))

        # Apply hybrid optimizations if enabled
        if self.profile.enable_hybrid_strategies:
            self._apply_hybrid_optimizations()

    def _apply_hybrid_optimizations(self) -> None:
        """Apply hybrid optimization strategies."""
        system_metrics = self.get_system_metrics()
        memory_pressure = system_metrics.get("memory_usage", 0.5)

        # Adjust cache sizes based on memory pressure
        if memory_pressure > 0.7:
            self.profile.path_cache_size = max(256, self.profile.path_cache_size // 2)
            self.profile.conversion_cache_size = max(
                128, self.profile.conversion_cache_size // 2
            )
        elif memory_pressure < 0.3:
            self.profile.path_cache_size = min(2048, self.profile.path_cache_size * 2)
            self.profile.conversion_cache_size = min(
                1024, self.profile.conversion_cache_size * 2
            )

        # Adjust lazy loading thresholds based on performance history
        if len(self.metrics_history) >= 20:
            recent_metrics = self.metrics_history[-20:]
            avg_memory = statistics.mean(m.memory_usage for m in recent_metrics)

            if avg_memory > 100:  # High memory usage
                self.profile.lazy_threshold_dict = max(
                    5, self.profile.lazy_threshold_dict // 2
                )
                self.profile.lazy_threshold_list = max(
                    10, self.profile.lazy_threshold_list // 2
                )
            elif avg_memory < 10:  # Low memory usage
                self.profile.lazy_threshold_dict = min(
                    30, self.profile.lazy_threshold_dict * 2
                )
                self.profile.lazy_threshold_list = min(
                    60, self.profile.lazy_threshold_list * 2
                )

    def get_adaptive_stats(self) -> Dict[str, Any]:
        """Get detailed adaptive learning statistics."""
        return {
            "metrics_count": len(self.metrics_history),
            "mode_performance": {
                mode_name: {
                    "count": len(scores),
                    "avg_score": statistics.mean(scores) if scores else 0.0,
                    "best_score": max(scores) if scores else 0.0,
                }
                for mode_name, scores in self.mode_performance.items()
            },
            "system_metrics": self.get_system_metrics(),
            "last_adaptation": self.profile.last_adaptation,
        }


class DualPhaseAdaptiveEngine:
    """Smart dual-phase adaptive engine: fast cruise + intelligent deep-dive."""

    def __init__(self, profile: DualAdaptiveProfile):
        self.profile = profile
        self.metrics_history: List[PerformanceMetrics] = []
        self.system_metrics: List[Dict[str, float]] = []
        self._lock = threading.RLock()
        self._last_system_check = 0.0
        self._operation_counter = 0

        # Initialize mode performance tracking
        self.mode_performance: Dict[str, List[float]] = {
            "AUTO": [],
            "DEFAULT": [],
            "FAST": [],
            "OPTIMIZED": [],
            "MANUAL": [],
            "PARENT": [],
            "ADAPTIVE": [],
        }

    def record_operation(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics with smart phase-based sampling."""
        with self._lock:
            self._operation_counter += 1
            self.profile.operations_in_phase += 1

            # Phase 1: CRUISE - Lightweight sampling
            if self.profile.current_phase == "CRUISE":
                if self._operation_counter % self.profile.cruise_sample_rate == 0:
                    self._record_cruise_metric(metrics)
                    self._check_cruise_triggers(metrics)

            # Phase 2: DEEP_DIVE - Intensive sampling
            elif self.profile.current_phase == "DEEP_DIVE":
                if self._operation_counter % self.profile.deep_dive_sample_rate == 0:
                    self._record_deep_dive_metric(metrics)
                    self._check_deep_dive_completion()

    def _record_cruise_metric(self, metrics: PerformanceMetrics) -> None:
        """Record metric in cruise phase (lightweight)."""
        self.metrics_history.append(metrics)

        # Keep cruise history small
        if len(self.metrics_history) > self.profile.cruise_history_size:
            self.metrics_history.pop(0)

        # Track mode performance
        if metrics.mode_used != PerformanceMode.DUAL_ADAPTIVE:
            mode_name = metrics.mode_used.name
            if mode_name not in self.mode_performance:
                self.mode_performance[mode_name] = []
            self.mode_performance[mode_name].append(metrics.performance_score)

            # Keep only recent data
            if len(self.mode_performance[mode_name]) > 50:
                self.mode_performance[mode_name] = self.mode_performance[mode_name][
                    -50:
                ]

    def _record_deep_dive_metric(self, metrics: PerformanceMetrics) -> None:
        """Record metric in deep-dive phase (intensive)."""
        self.metrics_history.append(metrics)

        # Keep detailed history during deep-dive
        if len(self.metrics_history) > self.profile.deep_dive_history_size:
            self.metrics_history.pop(0)

        # Track mode performance with more detail
        if metrics.mode_used != PerformanceMode.DUAL_ADAPTIVE:
            mode_name = metrics.mode_used.name
            if mode_name not in self.mode_performance:
                self.mode_performance[mode_name] = []
            self.mode_performance[mode_name].append(metrics.performance_score)

            # Keep more data during deep-dive
            if len(self.mode_performance[mode_name]) > 200:
                self.mode_performance[mode_name] = self.mode_performance[mode_name][
                    -200:
                ]

    def _check_cruise_triggers(self, metrics: PerformanceMetrics) -> None:
        """Check if we should trigger deep-dive from cruise phase."""
        # Check system pressure
        system_metrics = self.get_system_metrics()
        memory_pressure = system_metrics.get("memory_usage", 0.5)
        cpu_pressure = system_metrics.get("cpu_usage", 0.3)

        # Check performance degradation
        performance_degradation = self._calculate_performance_degradation()

        # Trigger deep-dive if any threshold is exceeded
        if (
            memory_pressure > self.profile.memory_pressure_threshold
            or cpu_pressure > self.profile.cpu_pressure_threshold
            or performance_degradation > self.profile.performance_degradation_threshold
        ):

            self._trigger_deep_dive(
                f"System pressure or performance degradation detected"
            )

    def _check_deep_dive_completion(self) -> None:
        """Check if deep-dive phase should complete."""
        if self.profile.operations_in_phase >= self.profile.deep_dive_duration:
            self._complete_deep_dive()

    def _trigger_deep_dive(self, reason: str) -> None:
        """Switch from cruise to deep-dive phase."""
        with self._lock:
            self.profile.current_phase = "DEEP_DIVE"
            self.profile.phase_start_time = time.time()
            self.profile.operations_in_phase = 0
            self.profile.deep_dive_trigger_count += 1

            # Log the transition
            print(f"🔬 DUAL_ADAPTIVE: Entering DEEP_DIVE phase - {reason}")

    def _complete_deep_dive(self) -> None:
        """Complete deep-dive and return to cruise with optimizations."""
        with self._lock:
            # Analyze deep-dive data and find optimal mode
            optimal_mode = self._analyze_deep_dive_data()

            # Apply optimizations
            self._apply_deep_dive_optimizations(optimal_mode)

            # Return to cruise phase
            self.profile.current_phase = "CRUISE"
            self.profile.phase_start_time = time.time()
            self.profile.operations_in_phase = 0

            print(
                f"🚗 DUAL_ADAPTIVE: Returning to CRUISE phase with {optimal_mode.name} optimizations"
            )

    def _calculate_performance_degradation(self) -> float:
        """Calculate recent performance degradation."""
        if len(self.metrics_history) < 10:
            return 0.0

        recent_metrics = self.metrics_history[-10:]
        current_avg = statistics.mean(m.performance_score for m in recent_metrics)

        if len(self.metrics_history) >= 50:
            historical_metrics = self.metrics_history[-50:-10]
            historical_avg = statistics.mean(
                m.performance_score for m in historical_metrics
            )

            if historical_avg > 0:
                return (historical_avg - current_avg) / historical_avg

        return 0.0

    def _analyze_deep_dive_data(self) -> PerformanceMode:
        """Analyze deep-dive data to find optimal performance mode."""
        if len(self.metrics_history) < 20:
            return PerformanceMode.OPTIMIZED  # Default to fastest

        # Calculate mode performance scores
        mode_scores = {}
        for mode_name, scores in self.mode_performance.items():
            if len(scores) >= 5:
                # Use recent scores with higher weight
                recent_scores = scores[-20:]
                avg_score = statistics.mean(recent_scores)
                mode_scores[mode_name] = avg_score

        if not mode_scores:
            return PerformanceMode.OPTIMIZED

        # Return the best performing mode
        best_mode_name = max(mode_scores.items(), key=lambda x: x[1])[0]
        return PerformanceMode.from_string(best_mode_name)

    def _apply_deep_dive_optimizations(self, optimal_mode: PerformanceMode) -> None:
        """Apply optimizations based on deep-dive analysis."""
        # Get the optimal profile
        optimal_profile = PerformanceProfiles.get_profile(optimal_mode)

        # Apply optimal settings to current profile
        for field in optimal_profile.__dataclass_fields__:
            if field not in [
                "operation_history",
                "mode_performance",
                "current_phase",
                "phase_start_time",
                "operations_in_phase",
                "deep_dive_trigger_count",
            ]:
                setattr(self.profile, field, getattr(optimal_profile, field))

        # Apply hybrid optimizations
        self._apply_hybrid_optimizations()

    def _apply_hybrid_optimizations(self) -> None:
        """Apply hybrid optimization strategies."""
        system_metrics = self.get_system_metrics()
        memory_pressure = system_metrics.get("memory_usage", 0.5)

        # Adjust cache sizes based on memory pressure
        if memory_pressure > 0.7:
            self.profile.path_cache_size = max(256, self.profile.path_cache_size // 2)
            self.profile.conversion_cache_size = max(
                128, self.profile.conversion_cache_size // 2
            )
        elif memory_pressure < 0.3:
            self.profile.path_cache_size = min(2048, self.profile.path_cache_size * 2)
            self.profile.conversion_cache_size = min(
                1024, self.profile.conversion_cache_size * 2
            )

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics (cached for efficiency)."""
        current_time = time.time()

        # Cache system metrics based on current phase
        cache_duration = (
            self.profile.cruise_monitor_interval
            if self.profile.current_phase == "CRUISE"
            else 1.0
        )

        if current_time - self._last_system_check < cache_duration:
            return self.system_metrics[-1] if self.system_metrics else {}

        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)

            metrics = {
                "memory_usage": memory.percent / 100.0,
                "cpu_usage": cpu / 100.0,
                "memory_available_mb": memory.available / (1024 * 1024),
                "timestamp": current_time,
            }

            self.system_metrics.append(metrics)
            self._last_system_check = current_time

            # Keep only recent system metrics
            if len(self.system_metrics) > 50:
                self.system_metrics.pop(0)

            return metrics
        except Exception:
            # Fallback if psutil is not available
            return {
                "memory_usage": 0.5,
                "cpu_usage": 0.3,
                "memory_available_mb": 1024,
                "timestamp": current_time,
            }

    def get_adaptive_stats(self) -> Dict[str, Any]:
        """Get detailed adaptive learning statistics."""
        return {
            "current_phase": self.profile.current_phase,
            "operations_in_phase": self.profile.operations_in_phase,
            "deep_dive_trigger_count": self.profile.deep_dive_trigger_count,
            "metrics_count": len(self.metrics_history),
            "phase_start_time": self.profile.phase_start_time,
            "mode_performance": {k: len(v) for k, v in self.mode_performance.items()},
            "system_metrics_count": len(self.system_metrics),
        }


class PerformanceProfiles:
    """Predefined performance profiles for different optimization strategies."""

    @staticmethod
    def get_profile(
        mode: PerformanceMode, data_size: Optional[int] = None
    ) -> PerformanceProfile:
        """Get performance profile based on mode and data characteristics."""

        if mode == PerformanceMode.ADAPTIVE:
            # Start with DEFAULT profile and enhance with adaptive features
            # Avoid recursion by directly creating the base profile
            base_profile = PerformanceProfile(
                path_cache_size=1024,
                node_pool_size=2000,
                conversion_cache_size=512,
                lazy_threshold_dict=15,
                lazy_threshold_list=30,
                enable_weak_refs=True,
                enable_object_pooling=True,
                enable_path_caching=True,
                enable_conversion_caching=True,
                enable_optimized_iteration=True,
                enable_thread_safety=True,
                lock_timeout=5.0,
                max_depth=100,
                max_nodes=1_000_000,
                max_path_length=1000,
            )
            return AdaptiveProfile(
                **base_profile.to_dict(),
                learning_enabled=True,
                adaptation_threshold=0.1,
                history_size=1000,
                monitor_interval=1.0,
                memory_pressure_threshold=0.8,
                cpu_usage_threshold=0.7,
                enable_hybrid_strategies=True,
                max_mode_switches_per_second=10,
                cooldown_period=5.0,
            )

        if mode == PerformanceMode.DUAL_ADAPTIVE:
            # Start with FAST profile for optimal cruise performance
            # Avoid recursion by directly creating the base profile
            base_profile = PerformanceProfile(
                path_cache_size=2048,
                node_pool_size=5000,
                conversion_cache_size=1024,
                lazy_threshold_dict=5,
                lazy_threshold_list=10,
                enable_weak_refs=False,
                enable_object_pooling=True,
                enable_path_caching=True,
                enable_conversion_caching=True,
                enable_optimized_iteration=True,
                enable_thread_safety=True,
                lock_timeout=2.0,
                max_depth=100,
                max_nodes=1_000_000,
                max_path_length=1000,
            )
            return DualAdaptiveProfile(
                **base_profile.to_dict(),
                # Cruise phase settings (fast, low-overhead)
                cruise_sample_rate=100,  # Sample every 100th operation (was 50)
                cruise_monitor_interval=10.0,  # Check system every 10 seconds (was 5.0)
                cruise_history_size=100,  # Keep only 100 operations (was 200)
                # Deep-dive phase settings (intensive learning)
                deep_dive_trigger_threshold=0.25,  # 25% degradation triggers deep-dive (was 0.15)
                deep_dive_duration=200,  # Deep-dive for 200 operations (was 500)
                deep_dive_sample_rate=5,  # Sample every 5th operation (was 1)
                deep_dive_history_size=500,  # Keep detailed history (was 1000)
                # Smart triggers
                memory_pressure_threshold=0.9,  # 90% memory usage triggers deep-dive (was 0.8)
                cpu_pressure_threshold=0.8,  # 80% CPU usage triggers deep-dive (was 0.7)
                performance_degradation_threshold=0.3,  # 30% degradation triggers deep-dive (was 0.2)
                # Learning parameters
                learning_enabled=True,
                adaptation_threshold=0.15,  # 15% improvement threshold (was 0.1)
                cooldown_period=15.0,  # 15 seconds between adaptations (was 10.0)
            )

        if mode == PerformanceMode.DEFAULT:
            return PerformanceProfile(
                path_cache_size=1024,
                node_pool_size=2000,
                conversion_cache_size=512,
                lazy_threshold_dict=15,
                lazy_threshold_list=30,
                enable_weak_refs=True,
                enable_object_pooling=True,
                enable_path_caching=True,
                enable_conversion_caching=True,
                enable_optimized_iteration=True,
                enable_thread_safety=True,
                lock_timeout=5.0,
                max_depth=100,
                max_nodes=1_000_000,
                max_path_length=1000,
            )

        elif mode == PerformanceMode.FAST:
            return PerformanceProfile(
                path_cache_size=2048,
                node_pool_size=5000,
                conversion_cache_size=1024,
                lazy_threshold_dict=5,
                lazy_threshold_list=10,
                enable_weak_refs=False,
                enable_object_pooling=True,
                enable_path_caching=True,
                enable_conversion_caching=True,
                enable_optimized_iteration=True,
                enable_thread_safety=False,
                lock_timeout=2.0,
                max_depth=100,
                max_nodes=1_000_000,
                max_path_length=1000,
            )

        elif mode == PerformanceMode.OPTIMIZED:
            return PerformanceProfile(
                path_cache_size=256,
                node_pool_size=500,
                conversion_cache_size=128,
                lazy_threshold_dict=25,
                lazy_threshold_list=50,
                enable_weak_refs=True,
                enable_object_pooling=False,
                enable_path_caching=False,
                enable_conversion_caching=False,
                enable_optimized_iteration=False,
                enable_thread_safety=True,
                lock_timeout=10.0,
                max_depth=100,
                max_nodes=1_000_000,
                max_path_length=1000,
            )

        elif mode == PerformanceMode.AUTO:
            if data_size is None:
                return PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)

            # Auto-selection based on data size
            if data_size < 1000:
                # For small data, use FAST mode but ensure thread safety is off
                fast_profile = PerformanceProfiles.get_profile(PerformanceMode.FAST)
                fast_profile.enable_thread_safety = False
                return fast_profile
            elif data_size > 100000:
                return PerformanceProfiles.get_profile(PerformanceMode.OPTIMIZED)
            else:
                return PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)

        elif mode == PerformanceMode.PARENT:
            # For PARENT mode, we'll need to get the parent's profile
            # This will be handled by the manager
            return PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)

        elif mode == PerformanceMode.MANUAL:
            # MANUAL mode requires explicit configuration
            return PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)

        else:
            return PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)

    @staticmethod
    def estimate_data_size(data: Any) -> int:
        """Estimate the size/complexity of data for mode selection."""
        if data is None:
            return 0

        if isinstance(data, (str, bytes)):
            return len(data)

        if isinstance(data, (int, float, bool)):
            return 1

        if isinstance(data, (list, tuple)):
            return sum(PerformanceProfiles.estimate_data_size(item) for item in data)

        if isinstance(data, dict):
            return sum(
                PerformanceProfiles.estimate_data_size(key)
                + PerformanceProfiles.estimate_data_size(value)
                for key, value in data.items()
            )

        # For other types, estimate based on string representation
        return len(str(data))


class PerformanceModeManager:
    """Manager for performance mode selection and adaptation."""

    def __init__(self, default_mode: PerformanceMode = PerformanceMode.DEFAULT):
        self._mode = default_mode
        self._parent_mode: Optional[PerformanceMode] = None
        self._manual_overrides: Dict[str, Any] = {}
        self._adaptive_engine: Optional[AdaptiveLearningEngine] = None
        self._dual_adaptive_engine: Optional[DualPhaseAdaptiveEngine] = None
        self._lock = threading.RLock()

    def set_mode(self, mode: PerformanceMode) -> None:
        """Set the current performance mode."""
        with self._lock:
            self._mode = mode
            if mode == PerformanceMode.ADAPTIVE and self._adaptive_engine is None:
                profile = PerformanceProfiles.get_profile(mode)
                if isinstance(profile, AdaptiveProfile):
                    self._adaptive_engine = AdaptiveLearningEngine(profile)
            elif (
                mode == PerformanceMode.DUAL_ADAPTIVE
                and self._dual_adaptive_engine is None
            ):
                profile = PerformanceProfiles.get_profile(mode)
                if isinstance(profile, DualAdaptiveProfile):
                    self._dual_adaptive_engine = DualPhaseAdaptiveEngine(profile)

    def get_mode(self) -> PerformanceMode:
        """Get the current performance mode."""
        return self._mode

    def set_parent_mode(self, mode: PerformanceMode) -> None:
        """Set the parent performance mode for inheritance."""
        with self._lock:
            self._parent_mode = mode

    def set_manual_override(self, key: str, value: Any) -> None:
        """Set a manual override for specific configuration."""
        with self._lock:
            self._manual_overrides[key] = value

    def get_profile(self, data_size: Optional[int] = None) -> PerformanceProfile:
        """Get the current performance profile."""
        with self._lock:
            effective_mode = self._get_effective_mode()
            profile = PerformanceProfiles.get_profile(effective_mode, data_size)

            # Apply manual overrides
            for key, value in self._manual_overrides.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            return profile

    def _get_effective_mode(self) -> PerformanceMode:
        """Get the effective mode considering inheritance and adaptation."""
        if self._mode == PerformanceMode.PARENT:
            return self._parent_mode or PerformanceMode.DEFAULT

        if self._mode == PerformanceMode.ADAPTIVE and self._adaptive_engine:
            # Check if adaptation is needed
            if self._adaptive_engine.should_adapt():
                optimal_mode = self._adaptive_engine.get_optimal_mode()
                self._adaptive_engine.adapt_profile(optimal_mode)
                return optimal_mode

        if self._mode == PerformanceMode.DUAL_ADAPTIVE and self._dual_adaptive_engine:
            # Check if dual adaptive is needed
            # For now, we'll just return the current mode, as dual adaptive is a separate engine
            # The dual adaptive engine handles its own adaptation logic
            return self._mode

        return self._mode

    def record_operation(
        self,
        operation_type: str,
        mode_used: PerformanceMode,
        execution_time: float,
        memory_usage: float,
        cache_hits: int,
        cache_misses: int,
    ) -> None:
        """Record operation metrics for adaptive learning."""
        if self._adaptive_engine:
            metrics = PerformanceMetrics(
                operation_type=operation_type,
                mode_used=mode_used,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
            )
            self._adaptive_engine.record_operation(metrics)

        if self._dual_adaptive_engine:
            metrics = PerformanceMetrics(
                operation_type=operation_type,
                mode_used=mode_used,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
            )
            self._dual_adaptive_engine.record_operation(metrics)

    def get_adaptive_stats(self) -> Dict[str, Any]:
        """Get adaptive learning statistics."""
        stats: Dict[str, Any] = {}

        if self._adaptive_engine:
            stats.update(self._adaptive_engine.get_adaptive_stats())

        if self._dual_adaptive_engine:
            stats.update(self._dual_adaptive_engine.get_adaptive_stats())

        return stats

    def reset(self) -> None:
        """Reset the manager to default state."""
        with self._lock:
            self._mode = PerformanceMode.DEFAULT
            self._parent_mode = None
            self._manual_overrides.clear()
            self._adaptive_engine = None
            self._dual_adaptive_engine = None
