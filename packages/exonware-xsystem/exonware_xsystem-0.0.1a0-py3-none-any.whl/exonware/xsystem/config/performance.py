"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Performance Configuration Management

Centralized configuration for xSystem performance limits, timeouts, and optimization settings.
"""

from typing import Any, Dict, Final, Optional
from dataclasses import dataclass, field
import os
from pathlib import Path

from ..config.logging_setup import get_logger

logger = get_logger(__name__)


@dataclass
class SerializationLimits:
    """Configuration limits for serialization operations."""
    
    # Data size limits
    max_size_mb: float = 50.0                    # Maximum data size in MB
    max_depth: int = 100                         # Maximum nesting depth
    max_string_length: int = 1_000_000          # Maximum string length
    max_list_items: int = 100_000               # Maximum list/array items
    max_dict_keys: int = 10_000                 # Maximum dictionary keys
    
    # File operation limits
    max_file_size_mb: float = 100.0             # Maximum file size for operations
    max_path_length: int = 4096                 # Maximum file path length
    
    # Performance settings
    use_atomic_writes: bool = True              # Use atomic file operations by default
    validate_input: bool = True                 # Enable input validation by default
    validate_paths: bool = True                 # Enable path validation by default
    
    # Memory management
    max_memory_mb: float = 200.0                # Maximum memory usage for operations
    enable_compression: bool = False            # Enable compression by default


@dataclass
class NetworkLimits:
    """Configuration limits for network operations."""
    
    # Timeout settings (seconds)
    connect_timeout: float = 30.0               # Connection timeout
    read_timeout: float = 60.0                  # Read timeout
    total_timeout: float = 300.0                # Total request timeout
    
    # Retry settings
    max_retries: int = 3                        # Maximum retry attempts
    retry_backoff_factor: float = 2.0           # Exponential backoff factor
    retry_max_delay: float = 60.0               # Maximum retry delay
    
    # Size limits
    max_response_size_mb: float = 100.0         # Maximum response size
    max_request_size_mb: float = 50.0           # Maximum request size
    
    # Connection pool settings
    max_connections: int = 100                  # Maximum connections in pool
    max_keepalive_connections: int = 20         # Maximum keep-alive connections


@dataclass
class SecurityLimits:
    """Configuration limits for security operations."""
    
    # Path validation
    allow_absolute_paths: bool = False          # Allow absolute paths
    allow_symlinks: bool = False                # Allow symbolic links
    blocked_extensions: tuple = field(default_factory=lambda: (
        '.exe', '.bat', '.cmd', '.com', '.scr', '.dll', '.sys'
    ))
    
    # Input validation
    max_input_complexity: int = 1000            # Maximum input complexity score
    enable_xss_protection: bool = True          # Enable XSS protection
    enable_injection_protection: bool = True   # Enable injection protection
    
    # Cryptography settings
    min_key_size: int = 2048                    # Minimum key size for RSA
    hash_iterations: int = 100_000              # PBKDF2 iterations
    salt_length: int = 32                       # Salt length in bytes


@dataclass
class PerformanceLimits:
    """Master configuration for all xSystem performance limits."""
    
    # Component-specific limits
    serialization: SerializationLimits = field(default_factory=SerializationLimits)
    network: NetworkLimits = field(default_factory=NetworkLimits)
    security: SecurityLimits = field(default_factory=SecurityLimits)
    
    # Global settings
    enable_monitoring: bool = True              # Enable performance monitoring
    enable_metrics: bool = True                 # Enable metrics collection
    log_performance_warnings: bool = True      # Log performance warnings
    
    # Memory management
    max_total_memory_mb: float = 500.0          # Maximum total memory usage
    gc_threshold_mb: float = 100.0              # Garbage collection threshold
    
    # Concurrency settings
    max_threads: int = 50                       # Maximum thread pool size
    max_async_tasks: int = 100                  # Maximum async tasks


# Default configuration instance
DEFAULT_LIMITS: Final[PerformanceLimits] = PerformanceLimits()


class PerformanceConfig:
    """
    Centralized performance configuration manager.
    
    Manages performance limits, timeouts, and optimization settings for xSystem.
    Supports environment variable overrides and runtime configuration updates.
    """
    
    def __init__(self, config_file: Optional[str] = None) -> None:
        """
        Initialize performance configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self._limits = PerformanceLimits()
        self._config_file = config_file
        self._load_from_environment()
        
        if config_file:
            self._load_from_file(config_file)
        
        logger.info("Performance configuration initialized")
    
    def _load_from_environment(self) -> None:
        """Load configuration overrides from environment variables."""
        
        # Serialization limits
        if val := os.getenv('XSYSTEM_MAX_SIZE_MB'):
            self._limits.serialization.max_size_mb = float(val)
        
        if val := os.getenv('XSYSTEM_MAX_DEPTH'):
            self._limits.serialization.max_depth = int(val)
        
        if val := os.getenv('XSYSTEM_MAX_FILE_SIZE_MB'):
            self._limits.serialization.max_file_size_mb = float(val)
        
        # Network limits
        if val := os.getenv('XSYSTEM_CONNECT_TIMEOUT'):
            self._limits.network.connect_timeout = float(val)
        
        if val := os.getenv('XSYSTEM_READ_TIMEOUT'):
            self._limits.network.read_timeout = float(val)
        
        if val := os.getenv('XSYSTEM_MAX_RETRIES'):
            self._limits.network.max_retries = int(val)
        
        # Security limits
        if val := os.getenv('XSYSTEM_ALLOW_ABSOLUTE_PATHS'):
            self._limits.security.allow_absolute_paths = val.lower() in ('true', '1', 'yes')
        
        if val := os.getenv('XSYSTEM_MIN_KEY_SIZE'):
            self._limits.security.min_key_size = int(val)
        
        # Global settings
        if val := os.getenv('XSYSTEM_MAX_MEMORY_MB'):
            self._limits.max_total_memory_mb = float(val)
        
        if val := os.getenv('XSYSTEM_MAX_THREADS'):
            self._limits.max_threads = int(val)
    
    def _load_from_file(self, config_file: str) -> None:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file (JSON/YAML/TOML)
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning(f"Configuration file not found: {config_file}")
                return
            
            # Import here to avoid circular imports
            from ..serialization import JsonSerializer, YamlSerializer, TomlSerializer
            
            # Determine format by extension
            if config_path.suffix.lower() in ('.json',):
                serializer = JsonSerializer(validate_paths=False)
            elif config_path.suffix.lower() in ('.yaml', '.yml'):
                serializer = YamlSerializer(validate_paths=False)
            elif config_path.suffix.lower() in ('.toml',):
                serializer = TomlSerializer(validate_paths=False)
            else:
                logger.warning(f"Unsupported config file format: {config_path.suffix}")
                return
            
            config_data = serializer.load_file(config_file)
            self._apply_config_data(config_data)
            
            logger.info(f"Loaded configuration from: {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration file {config_file}: {e}")
    
    def _apply_config_data(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data to limits."""
        
        if 'serialization' in config_data:
            ser_config = config_data['serialization']
            for key, value in ser_config.items():
                if hasattr(self._limits.serialization, key):
                    setattr(self._limits.serialization, key, value)
        
        if 'network' in config_data:
            net_config = config_data['network']
            for key, value in net_config.items():
                if hasattr(self._limits.network, key):
                    setattr(self._limits.network, key, value)
        
        if 'security' in config_data:
            sec_config = config_data['security']
            for key, value in sec_config.items():
                if hasattr(self._limits.security, key):
                    setattr(self._limits.security, key, value)
        
        # Global settings
        for key in ['enable_monitoring', 'enable_metrics', 'max_total_memory_mb', 'max_threads']:
            if key in config_data:
                setattr(self._limits, key, config_data[key])
    
    @property
    def limits(self) -> PerformanceLimits:
        """Get current performance limits."""
        return self._limits
    
    def get_serialization_config(self) -> Dict[str, Any]:
        """Get serialization configuration dictionary."""
        return {
            'max_size_mb': self._limits.serialization.max_size_mb,
            'max_depth': self._limits.serialization.max_depth,
            'max_file_size_mb': self._limits.serialization.max_file_size_mb,
            'use_atomic_writes': self._limits.serialization.use_atomic_writes,
            'validate_input': self._limits.serialization.validate_input,
            'validate_paths': self._limits.serialization.validate_paths,
        }
    
    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration dictionary."""
        return {
            'connect_timeout': self._limits.network.connect_timeout,
            'read_timeout': self._limits.network.read_timeout,
            'total_timeout': self._limits.network.total_timeout,
            'max_retries': self._limits.network.max_retries,
            'max_response_size_mb': self._limits.network.max_response_size_mb,
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration dictionary."""
        return {
            'allow_absolute_paths': self._limits.security.allow_absolute_paths,
            'allow_symlinks': self._limits.security.allow_symlinks,
            'blocked_extensions': self._limits.security.blocked_extensions,
            'min_key_size': self._limits.security.min_key_size,
        }
    
    def update_limits(self, **kwargs) -> None:
        """
        Update performance limits at runtime.
        
        Args:
            **kwargs: Limit values to update
        """
        for key, value in kwargs.items():
            if '.' in key:
                # Handle nested attributes like 'serialization.max_size_mb'
                parts = key.split('.')
                obj = self._limits
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], value)
            else:
                # Handle top-level attributes
                if hasattr(self._limits, key):
                    setattr(self._limits, key, value)
        
        logger.info(f"Updated performance limits: {kwargs}")
    
    def export_config(self, format: str = 'json') -> Dict[str, Any]:
        """
        Export current configuration.
        
        Args:
            format: Export format ('json', 'yaml', 'toml')
            
        Returns:
            Configuration dictionary
        """
        return {
            'serialization': {
                'max_size_mb': self._limits.serialization.max_size_mb,
                'max_depth': self._limits.serialization.max_depth,
                'max_file_size_mb': self._limits.serialization.max_file_size_mb,
                'use_atomic_writes': self._limits.serialization.use_atomic_writes,
                'validate_input': self._limits.serialization.validate_input,
                'validate_paths': self._limits.serialization.validate_paths,
            },
            'network': {
                'connect_timeout': self._limits.network.connect_timeout,
                'read_timeout': self._limits.network.read_timeout,
                'total_timeout': self._limits.network.total_timeout,
                'max_retries': self._limits.network.max_retries,
                'max_response_size_mb': self._limits.network.max_response_size_mb,
            },
            'security': {
                'allow_absolute_paths': self._limits.security.allow_absolute_paths,
                'allow_symlinks': self._limits.security.allow_symlinks,
                'min_key_size': self._limits.security.min_key_size,
            },
            'global': {
                'enable_monitoring': self._limits.enable_monitoring,
                'enable_metrics': self._limits.enable_metrics,
                'max_total_memory_mb': self._limits.max_total_memory_mb,
                'max_threads': self._limits.max_threads,
            }
        }


# Global configuration instance
_global_config: Optional[PerformanceConfig] = None


def get_performance_config() -> PerformanceConfig:
    """Get the global performance configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = PerformanceConfig()
    return _global_config


def configure_performance(config_file: Optional[str] = None, **kwargs) -> None:
    """
    Configure global performance settings.
    
    Args:
        config_file: Optional configuration file path
        **kwargs: Performance limit overrides
    """
    global _global_config
    _global_config = PerformanceConfig(config_file)
    
    if kwargs:
        _global_config.update_limits(**kwargs)


# Convenience functions for getting specific limits
def get_serialization_limits() -> SerializationLimits:
    """Get current serialization limits."""
    return get_performance_config().limits.serialization


def get_network_limits() -> NetworkLimits:
    """Get current network limits."""
    return get_performance_config().limits.network


def get_security_limits() -> SecurityLimits:
    """Get current security limits."""
    return get_performance_config().limits.security
