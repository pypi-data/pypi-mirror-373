"""
xSystem Validation Package

Provides data validation utilities for type safety and security.
"""

from .data_validator import (
    DataValidator, 
    ValidationError,
    PathValidationError,
    DepthValidationError,
    MemoryValidationError,
    check_data_depth,
    validate_path_input,
    validate_resolution_depth,
    estimate_memory_usage
)
from .type_safety import (
    GenericSecurityError,
    SafeTypeValidator,
    is_immutable_type,
    is_safe_type,
    validate_untrusted_data,
)

__all__ = [
    # Data Validator
    "DataValidator",
    "ValidationError",
    "PathValidationError",
    "DepthValidationError", 
    "MemoryValidationError",
    "check_data_depth",
    "validate_path_input",
    "validate_resolution_depth",
    "estimate_memory_usage",
    # Type Safety
    "SafeTypeValidator",
    "GenericSecurityError",
    "validate_untrusted_data",
    "is_safe_type",
    "is_immutable_type",
]
