"""
xSystem Configuration Package

Provides configuration management and performance mode utilities.
"""

from .defaults import *
from .logging import *
from .logging_setup import get_logger, setup_logging
from .performance_modes import (
    PerformanceMode,
    PerformanceModeManager,
    PerformanceProfile,
    PerformanceProfiles,
)
from .performance import (
    PerformanceConfig,
    PerformanceLimits,
    SerializationLimits,
    NetworkLimits,
    SecurityLimits,
    get_performance_config,
    configure_performance,
    get_serialization_limits,
    get_network_limits,
    get_security_limits,
)

__all__ = [
    # Defaults
    "DEFAULT_ENCODING",
    "DEFAULT_PATH_DELIMITER",
    "DEFAULT_LOCK_TIMEOUT",
    "DEFAULT_MAX_FILE_SIZE_MB",
    "DEFAULT_MAX_MEMORY_USAGE_MB",
    "DEFAULT_MAX_DICT_DEPTH",
    "DEFAULT_MAX_PATH_DEPTH",
    "DEFAULT_MAX_PATH_LENGTH",
    "DEFAULT_MAX_RESOLUTION_DEPTH",
    "DEFAULT_MAX_TO_DICT_SIZE_MB",
    "DEFAULT_MAX_CIRCULAR_DEPTH",
    "DEFAULT_MAX_EXTENSION_LENGTH",
    "DEFAULT_CONTENT_SNIPPET_LENGTH",
    "DEFAULT_MAX_TRAVERSAL_DEPTH",
    "URI_SCHEME_SEPARATOR",
    "JSON_POINTER_PREFIX",
    "PATH_SEPARATOR_FORWARD",
    "PATH_SEPARATOR_BACKWARD",
    "CIRCULAR_REFERENCE_PLACEHOLDER",
    "MAX_DEPTH_EXCEEDED_PLACEHOLDER",
    "LOGGING_ENABLED",
    "LOGGING_LEVEL",
    # Logging Setup
    "setup_logging",
    "get_logger",
    # Performance Modes
    "PerformanceMode",
    "PerformanceProfile",
    "PerformanceProfiles",
    "PerformanceModeManager",
    # Performance Configuration
    "PerformanceConfig",
    "PerformanceLimits",
    "SerializationLimits",
    "NetworkLimits",
    "SecurityLimits",
    "get_performance_config",
    "configure_performance",
    "get_serialization_limits",
    "get_network_limits",
    "get_security_limits",
]
