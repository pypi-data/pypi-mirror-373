"""
Data Validation Utilities for xSystem

These utilities provide data structure validation, path validation, and memory estimation
capabilities. They were previously embedded in xData and have been extracted for
framework-wide reusability.
"""

import sys
from typing import Any, Optional

from ..config import (
    DEFAULT_MAX_DICT_DEPTH,
    DEFAULT_MAX_PATH_DEPTH,
    DEFAULT_MAX_PATH_LENGTH,
    DEFAULT_MAX_RESOLUTION_DEPTH,
)

# ======================
# Validation Exceptions
# ======================


class ValidationError(Exception):
    """Base class for validation errors."""

    pass


class PathValidationError(ValidationError):
    """Raised when path validation fails."""

    pass


class DepthValidationError(ValidationError):
    """Raised when depth validation fails."""

    pass


class MemoryValidationError(ValidationError):
    """Raised when memory validation fails."""

    pass


# ======================
# Data Structure Validation
# ======================


def check_data_depth(
    data: Any, current_depth: int = 0, max_depth: Optional[int] = None
) -> None:
    """
    Check data structure depth to prevent excessive nesting.

    Args:
        data: Data structure to check
        current_depth: Current nesting depth
        max_depth: Maximum allowed depth (uses default if None)

    Raises:
        DepthValidationError: If data structure exceeds maximum depth
    """
    if max_depth is None:
        max_depth = DEFAULT_MAX_DICT_DEPTH

    if current_depth > max_depth:
        raise DepthValidationError(
            f"Data structure depth ({current_depth}) exceeds maximum allowed "
            f"({max_depth}). This may indicate malformed or malicious data."
        )

    if isinstance(data, dict):
        for key, value in data.items():
            check_data_depth(value, current_depth + 1, max_depth)
    elif isinstance(data, list):
        for item in data:
            check_data_depth(item, current_depth + 1, max_depth)


# ======================
# Path Validation
# ======================


def validate_path_input(path: str, operation_name: str = "path_operation") -> None:
    """
    Validate path input for operations to prevent attacks and errors.

    Args:
        path: Path string to validate
        operation_name: Name of the operation for error context

    Raises:
        PathValidationError: If path is invalid or potentially malicious
        TypeError: If path is not a string
    """
    # Check for None/empty after string conversion
    if path is None:
        raise PathValidationError(f"{operation_name}: Path cannot be None")

    if not isinstance(path, str):
        raise TypeError(f"{operation_name}: Path must be a string, got {type(path)}")

    # Check path length to prevent memory exhaustion
    if len(path) > DEFAULT_MAX_PATH_LENGTH:
        raise PathValidationError(
            f"{operation_name}: Path length ({len(path)}) exceeds maximum allowed "
            f"({DEFAULT_MAX_PATH_LENGTH}). This may indicate malicious input."
        )

    # Check for potentially malicious patterns
    malicious_patterns = [
        "../" * 10,  # Directory traversal
        "/" * 100,  # Excessive separators
        "." * 100,  # Excessive dots
        "\\" * 100,  # Excessive backslashes
    ]

    for pattern in malicious_patterns:
        if pattern in path:
            raise PathValidationError(
                f"{operation_name}: Path contains potentially malicious pattern: {pattern[:20]}..."
            )


def validate_path_depth(
    path_parts: list, operation_name: str = "path_operation"
) -> None:
    """
    Validate path depth to prevent excessive traversal.

    Args:
        path_parts: List of path segments
        operation_name: Name of the operation for error context

    Raises:
        PathValidationError: If path depth exceeds limits
    """
    if len(path_parts) > DEFAULT_MAX_PATH_DEPTH:
        raise PathValidationError(
            f"{operation_name}: Path depth ({len(path_parts)}) exceeds maximum allowed "
            f"({DEFAULT_MAX_PATH_DEPTH}). This may indicate malicious input."
        )


# ======================
# Resolution Depth Validation
# ======================


def validate_resolution_depth(
    current_depth: int, operation_name: str = "resolution"
) -> None:
    """
    Validate reference resolution depth to prevent infinite recursion.

    Args:
        current_depth: Current resolution depth
        operation_name: Name of the operation for error context

    Raises:
        DepthValidationError: If depth limit exceeded
    """
    if current_depth > DEFAULT_MAX_RESOLUTION_DEPTH:
        raise DepthValidationError(
            f"{operation_name}: Resolution depth ({current_depth}) exceeds maximum allowed "
            f"({DEFAULT_MAX_RESOLUTION_DEPTH}). This may indicate circular references or malicious data."
        )


# ======================
# Memory Estimation
# ======================


def estimate_memory_usage(data: Any) -> float:
    """
    Estimate memory usage of data structure in MB.

    Args:
        data: Data structure to estimate

    Returns:
        float: Estimated memory usage in MB
    """
    try:
        if isinstance(data, (dict, list)):
            # Rough estimation for containers
            size_bytes = sys.getsizeof(data)
            if isinstance(data, dict):
                for key, value in data.items():
                    size_bytes += sys.getsizeof(key) + sys.getsizeof(value)
                    if isinstance(value, (dict, list)):
                        size_bytes += sys.getsizeof(value) * 2  # Rough estimation
            elif isinstance(data, list):
                for item in data:
                    size_bytes += sys.getsizeof(item)
                    if isinstance(item, (dict, list)):
                        size_bytes += sys.getsizeof(item) * 2  # Rough estimation
            return size_bytes / (1024 * 1024)  # Convert to MB
        else:
            return sys.getsizeof(data) / (1024 * 1024)
    except Exception:
        # If estimation fails, return conservative estimate
        return 1.0  # 1MB conservative estimate


# ======================
# DataValidator Class
# ======================


class DataValidator:
    """
    Comprehensive data validator with configurable limits.

    This class provides a unified interface for all data validation
    operations with customizable limits and consistent error handling.
    """

    def __init__(
        self,
        max_dict_depth: Optional[int] = None,
        max_path_length: Optional[int] = None,
        max_path_depth: Optional[int] = None,
        max_resolution_depth: Optional[int] = None,
    ):
        """
        Initialize validator with custom limits.

        Args:
            max_dict_depth: Maximum data structure nesting depth
            max_path_length: Maximum path string length
            max_path_depth: Maximum path segment count
            max_resolution_depth: Maximum reference resolution depth
        """
        self.max_dict_depth = max_dict_depth or DEFAULT_MAX_DICT_DEPTH
        self.max_path_length = max_path_length or DEFAULT_MAX_PATH_LENGTH
        self.max_path_depth = max_path_depth or DEFAULT_MAX_PATH_DEPTH
        self.max_resolution_depth = max_resolution_depth or DEFAULT_MAX_RESOLUTION_DEPTH

    def validate_data_structure(
        self, data: Any, operation_name: str = "data_validation"
    ) -> None:
        """Validate data structure depth and complexity."""
        try:
            check_data_depth(data, max_depth=self.max_dict_depth)
        except DepthValidationError as e:
            raise ValidationError(f"{operation_name}: {e}")

    def validate_path(self, path: str, operation_name: str = "path_validation") -> None:
        """Validate path string and depth."""
        validate_path_input(path, operation_name)

        # Also validate path depth if it's a delimited path
        if "." in path:
            path_parts = path.split(".")
            validate_path_depth(path_parts, operation_name)

    def validate_resolution(
        self, depth: int, operation_name: str = "resolution_validation"
    ) -> None:
        """Validate resolution depth."""
        try:
            validate_resolution_depth(depth, operation_name)
        except DepthValidationError as e:
            raise ValidationError(f"{operation_name}: {e}")

    def estimate_memory(self, data: Any) -> float:
        """Estimate memory usage of data structure."""
        return estimate_memory_usage(data)

    def validate_memory_usage(
        self, data: Any, max_memory_mb: float, operation_name: str = "memory_validation"
    ) -> None:
        """Validate that data structure doesn't exceed memory limits."""
        estimated_mb = self.estimate_memory(data)
        if estimated_mb > max_memory_mb:
            raise MemoryValidationError(
                f"{operation_name}: Estimated memory usage ({estimated_mb:.2f}MB) exceeds "
                f"maximum allowed ({max_memory_mb}MB)"
            )
