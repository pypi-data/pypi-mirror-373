"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

xSystem - Reusable system utilities framework.

This module provides common utilities that can be used across different
components including threading, security, I/O,
data structures, and design patterns.
"""

import logging

# Logging utilities
from .config.logging_setup import get_logger, setup_logging

# Serialization utilities (17 formats total)
from .serialization import (
    iSerialization,
    aSerialization,
    SerializationError,
    # Core 12 formats
    JsonSerializer, JsonError,
    YamlSerializer, YamlError,
    TomlSerializer, TomlError,
    XmlSerializer, XmlError,
    BsonSerializer, BsonError,
    MsgPackSerializer,
    CborSerializer, CborError,
    CsvSerializer, CsvError,
    PickleSerializer, PickleError,
    MarshalSerializer, MarshalError,
    FormDataSerializer, FormDataError,
    MultipartSerializer, MultipartError,
    # Built-in Python modules (5 additional formats)
    ConfigParserSerializer, ConfigParserError,
    Sqlite3Serializer, Sqlite3Error,
    DbmSerializer, DbmError,
    ShelveSerializer, ShelveError,
    PlistlibSerializer, PlistlibError,
)

# HTTP utilities
from .http import HttpClient, HttpError, RetryConfig

# Runtime utilities
from .runtime import EnvironmentManager, ReflectionUtils

# Plugin system
from .plugins import PluginManager, PluginBase, PluginRegistry

# I/O utilities
from .io.atomic_file import (
    AtomicFileWriter,
    FileOperationError,
    safe_read_bytes,
    safe_read_text,
    safe_read_with_fallback,
    safe_write_bytes,
    safe_write_text,
)
from .patterns.context_manager import (
    ContextualLogger,
    ThreadSafeSingleton,
    combine_contexts,
    create_operation_logger,
    enhanced_error_context,
)

# Pattern utilities
from .patterns.handler_factory import GenericHandlerFactory
from .patterns.import_registry import (
    register_imports_batch,
    register_imports_flat,
    register_imports_tree,
)

# Security utilities
from .security.path_validator import PathSecurityError, PathValidator
from .security.crypto import (
    AsymmetricEncryption,
    CryptoError,
    SecureHash,
    SecureRandom,
    SecureStorage,
    SymmetricEncryption,
    generate_api_key,
    generate_session_token,
    hash_password,
    verify_password,
)

# Data structure utilities
from .structures.circular_detector import (
    CircularReferenceDetector,
    CircularReferenceError,
)
from .structures.tree_walker import (
    TreeWalker,
    apply_user_defined_links,
    resolve_proxies_in_dict,
    walk_and_replace,
)
from .threading.locks import EnhancedRLock

# Threading utilities
from .threading.safe_factory import MethodGenerator, ThreadSafeFactory

# Performance management (imported separately to avoid circular imports)
# from .performance import GenericPerformanceManager, PerformanceRecommendation, HealthStatus


# Simple logging control
logging_enabled = True


def disable_logging() -> None:
    """Disable all logging."""
    global logging_enabled
    logging_enabled = False
    logging.disable(logging.CRITICAL)


def enable_logging() -> None:
    """Enable logging."""
    global logging_enabled
    logging_enabled = True
    logging.disable(logging.NOTSET)


# Configuration utilities
from .config import *
from .config.performance import (
    get_performance_config,
    configure_performance,
    get_serialization_limits,
    get_network_limits,
    get_security_limits,
)

# Monitoring utilities
from .monitoring import (  # Performance Monitor; Memory Monitoring; Error Recovery; Performance Validation
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    ErrorContext,
    ErrorRecoveryManager,
    MemoryLeakReport,
    MemoryMonitor,
    MemorySnapshot,
    PerformanceMetric,
    PerformanceMonitor,
    PerformanceReport,
    PerformanceStats,
    PerformanceThreshold,
    PerformanceValidator,
    calculate_performance_summary,
    circuit_breaker,
    create_performance_monitor,
    enhanced_error_context,
    force_memory_cleanup,
    format_performance_report,
    get_error_recovery_manager,
    get_memory_monitor,
    get_memory_stats,
    get_performance_statistics,
    get_performance_validator,
    graceful_degradation,
    handle_error,
    performance_context,
    performance_monitor,
    record_performance_metric,
    register_object_for_monitoring,
    retry_with_backoff,
    start_memory_monitoring,
    start_performance_validation,
    stop_memory_monitoring,
    stop_performance_validation,
    unregister_object_from_monitoring,
    validate_performance,
)

# Validation utilities
from .validation import *

__version__ = "0.0.1"
__all__ = [
        # Serialization (17 formats)
    "iSerialization",
    "aSerialization", 
    "SerializationError",
    # Core 12 formats
    "JsonSerializer", "JsonError",
    "YamlSerializer", "YamlError",
    "TomlSerializer", "TomlError",
    "XmlSerializer", "XmlError", 
    "BsonSerializer", "BsonError",
    "MsgPackSerializer",
    "CborSerializer", "CborError",
    "CsvSerializer", "CsvError",
    "PickleSerializer", "PickleError",
    "MarshalSerializer", "MarshalError",
    "FormDataSerializer", "FormDataError",
    "MultipartSerializer", "MultipartError",
    # Built-in Python modules (5 additional formats)
    "ConfigParserSerializer", "ConfigParserError",
    "Sqlite3Serializer", "Sqlite3Error",
    "DbmSerializer", "DbmError",
    "ShelveSerializer", "ShelveError",
    "PlistlibSerializer", "PlistlibError",
    # HTTP
    "HttpClient",
    "HttpError",
    "RetryConfig",
    # Runtime
    "EnvironmentManager",
    "ReflectionUtils",
    # Plugins
    "PluginManager",
    "PluginBase",
    "PluginRegistry",
    # Threading
    "ThreadSafeFactory",
    "MethodGenerator",
    "EnhancedRLock",
    # Security
    "PathValidator",
    "PathSecurityError",
    "AsymmetricEncryption",
    "CryptoError",
    "SecureHash",
    "SecureRandom",
    "SecureStorage",
    "SymmetricEncryption",
    "generate_api_key",
    "generate_session_token",
    "hash_password",
    "verify_password",
    # I/O
    "AtomicFileWriter",
    "FileOperationError",
    "safe_write_text",
    "safe_write_bytes",
    "safe_read_text",
    "safe_read_bytes",
    "safe_read_with_fallback",
    # Structures
    "CircularReferenceDetector",
    "CircularReferenceError",
    "TreeWalker",
    "resolve_proxies_in_dict",
    "apply_user_defined_links",
    "walk_and_replace",
    # Patterns
    "GenericHandlerFactory",
    "combine_contexts",
    "enhanced_error_context",
    "ContextualLogger",
    "create_operation_logger",
    "ThreadSafeSingleton",
    "register_imports_flat",
    "register_imports_tree",
    "register_imports_batch",
    # Performance Management (available via direct import)
    # 'GenericPerformanceManager',
    # 'PerformanceRecommendation',
    # 'HealthStatus',
    # Logging
    "setup_logging",
    "get_logger",
    "disable_logging",
    "enable_logging",
    # Performance Configuration
    "get_performance_config",
    "configure_performance",
    "get_serialization_limits",
    "get_network_limits",
    "get_security_limits",
    # Configuration
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
    # Performance Modes
    "PerformanceMode",
    "PerformanceProfile",
    "PerformanceProfiles",
    "PerformanceModeManager",
    # Validation
    "DataValidator",
    "check_data_depth",
    "validate_path_input",
    "validate_resolution_depth",
    "estimate_memory_usage",
    "ValidationError",
    "PathValidationError",
    "DepthValidationError",
    "MemoryValidationError",
    # Monitoring
    "PerformanceMonitor",
    "PerformanceStats",
    "create_performance_monitor",
    "performance_context",
    "enhanced_error_context",
    "calculate_performance_summary",
    "format_performance_report",
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
