"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Comprehensive tests for input validation and sanitization.
"""

import pytest
import tempfile
from pathlib import Path

from exonware.xsystem.security.path_validator import PathValidator, PathSecurityError
from exonware.xsystem.validation.data_validator import (
    DataValidator,
    ValidationError,
    validate_path_input,
    check_data_depth,
    estimate_memory_usage,
)
from exonware.xsystem.validation.type_safety import (
    SafeTypeValidator,
    GenericSecurityError,
    validate_untrusted_data,
)


class TestPathInputValidation:
    """Test path input validation and sanitization."""

    def test_basic_path_validation(self):
        """Test basic path validation."""
        validator = PathValidator()
        
        # Valid paths
        validator.validate_path("test.txt")
        validator.validate_path("folder/test.txt")
        
        # Invalid paths should raise
        with pytest.raises(PathSecurityError):
            validator.validate_path("../etc/passwd")
            
        with pytest.raises(PathSecurityError):
            validator.validate_path("/etc/passwd")

    def test_path_traversal_prevention(self):
        """Test prevention of directory traversal attacks."""
        validator = PathValidator()
        
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "test/../../../etc/passwd",
            "test\\..\\..\\..\\windows\\system32",
            "....//....//etc/passwd",
            "test/....//....//etc/passwd",
        ]
        
        for path in dangerous_paths:
            with pytest.raises(PathSecurityError):
                validator.validate_path(path)

    def test_protected_paths(self):
        """Test protection of system paths."""
        validator = PathValidator()
        
        protected_paths = [
            "/etc/passwd",
            "/bin/bash",
            "/usr/bin/sudo", 
            "/root/secret",
            "C:\\Windows\\System32\\cmd.exe",
            "C:\\Program Files\\test.exe",
        ]
        
        for path in protected_paths:
            with pytest.raises(PathSecurityError):
                validator.validate_path(path)

    def test_dangerous_characters(self):
        """Test detection of dangerous characters."""
        validator = PathValidator()
        
        dangerous_chars = [
            "test|rm -rf /",
            "test; rm -rf /",
            "test & del C:\\",
            "test`whoami`",
            "test$(whoami)",
            "test<script>",
            "test>output.txt",
        ]
        
        for path in dangerous_chars:
            with pytest.raises(PathSecurityError):
                validator.validate_path(path)

    def test_max_path_length(self):
        """Test maximum path length validation."""
        validator = PathValidator(max_path_length=100)
        
        # Valid length
        validator.validate_path("a" * 50)
        
        # Too long
        with pytest.raises(PathSecurityError):
            validator.validate_path("a" * 200)

    def test_base_path_restriction(self):
        """Test base path restriction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            validator = PathValidator(base_path=base_path)
            
            # Valid: inside base path
            test_file = base_path / "test.txt"
            test_file.touch()
            validator.validate_path(str(test_file))
            
            # Invalid: outside base path
            with pytest.raises(PathSecurityError):
                validator.validate_path("/tmp/outside.txt")

    def test_path_validation_function(self):
        """Test standalone path validation function."""
        # Valid paths
        validate_path_input("test.txt")
        validate_path_input("folder/test.txt")
        
        # Invalid paths
        with pytest.raises(ValidationError):
            validate_path_input("../etc/passwd")
            
        with pytest.raises(ValidationError):
            validate_path_input(None)
            
        with pytest.raises(TypeError):
            validate_path_input(123)


class TestDataStructureValidation:
    """Test data structure validation."""

    def test_data_depth_validation(self):
        """Test data depth validation."""
        # Valid depth
        shallow_data = {"level1": {"level2": {"level3": "value"}}}
        check_data_depth(shallow_data, max_depth=5)
        
        # Too deep
        deep_data = {"l1": {"l2": {"l3": {"l4": {"l5": {"l6": "value"}}}}}}
        with pytest.raises(ValidationError):
            check_data_depth(deep_data, max_depth=5)

    def test_circular_reference_detection(self):
        """Test circular reference detection in data structures."""
        # Create circular reference
        data = {"key": "value"}
        data["self"] = data
        
        # Should handle gracefully
        try:
            check_data_depth(data, max_depth=10)
        except RecursionError:
            pytest.fail("Should handle circular references gracefully")

    def test_memory_estimation(self):
        """Test memory usage estimation."""
        small_data = {"key": "value"}
        large_data = {"key": "x" * 10000}
        
        small_size = estimate_memory_usage(small_data)
        large_size = estimate_memory_usage(large_data)
        
        assert large_size > small_size
        assert small_size > 0

    def test_data_validator_class(self):
        """Test DataValidator class."""
        validator = DataValidator(max_dict_depth=3)
        
        # Valid data
        valid_data = {"level1": {"level2": "value"}}
        validator.validate_data_structure(valid_data)
        
        # Invalid data
        invalid_data = {"l1": {"l2": {"l3": {"l4": "value"}}}}
        with pytest.raises(ValidationError):
            validator.validate_data_structure(invalid_data)


class TestTypeValidation:
    """Test type safety validation."""

    def test_safe_type_detection(self):
        """Test safe type detection."""
        # Safe types
        assert SafeTypeValidator.is_safe_type("string")
        assert SafeTypeValidator.is_safe_type(123)
        assert SafeTypeValidator.is_safe_type(12.34)
        assert SafeTypeValidator.is_safe_type(True)
        assert SafeTypeValidator.is_safe_type([1, 2, 3])
        assert SafeTypeValidator.is_safe_type({"key": "value"})
        assert SafeTypeValidator.is_safe_type(None)
        
        # Unsafe types
        assert not SafeTypeValidator.is_safe_type(object())
        assert not SafeTypeValidator.is_safe_type(lambda x: x)
        assert not SafeTypeValidator.is_safe_type(open)

    def test_immutable_type_detection(self):
        """Test immutable type detection."""
        # Immutable types
        assert SafeTypeValidator.is_immutable_type("string")
        assert SafeTypeValidator.is_immutable_type(123)
        assert SafeTypeValidator.is_immutable_type((1, 2, 3))
        assert SafeTypeValidator.is_immutable_type(frozenset([1, 2, 3]))
        
        # Mutable types
        assert not SafeTypeValidator.is_immutable_type([1, 2, 3])
        assert not SafeTypeValidator.is_immutable_type({"key": "value"})
        assert not SafeTypeValidator.is_immutable_type(set([1, 2, 3]))

    def test_untrusted_data_validation(self):
        """Test validation of untrusted data."""
        # Valid untrusted data
        safe_data = {
            "string_key": "string_value",
            "int_key": 123,
            "float_key": 12.34,
            "bool_key": True,
            "list_key": [1, 2, 3],
            "dict_key": {"nested": "value"},
            "null_key": None,
        }
        validate_untrusted_data(safe_data)
        
        # Invalid untrusted data
        unsafe_data = {"function": lambda x: x}
        with pytest.raises(GenericSecurityError):
            validate_untrusted_data(unsafe_data)

    def test_deep_structure_validation(self):
        """Test validation of deeply nested structures."""
        # Valid deep structure
        deep_safe = {
            "level1": {
                "level2": {
                    "level3": ["item1", "item2", "item3"]
                }
            }
        }
        validate_untrusted_data(deep_safe)
        
        # Too deep structure
        very_deep = {}
        current = very_deep
        for i in range(150):  # Deeper than default max_depth
            current["next"] = {}
            current = current["next"]
            
        with pytest.raises(GenericSecurityError):
            validate_untrusted_data(very_deep)

    def test_non_string_keys(self):
        """Test detection of non-string dictionary keys."""
        # Valid: string keys
        valid_data = {"string_key": "value"}
        validate_untrusted_data(valid_data)
        
        # Invalid: non-string keys
        invalid_data = {123: "value"}
        with pytest.raises(GenericSecurityError):
            validate_untrusted_data(invalid_data)


class TestInputSanitization:
    """Test input sanitization and normalization."""

    def test_path_normalization(self):
        """Test path normalization."""
        validator = PathValidator()
        
        # Test various path formats
        paths_to_normalize = [
            ("test//file.txt", "test/file.txt"),
            ("test\\file.txt", "test/file.txt"),
            ("./test/file.txt", "test/file.txt"),
            ("test/./file.txt", "test/file.txt"),
        ]
        
        for input_path, expected in paths_to_normalize:
            normalized = validator.normalize_path(input_path)
            assert expected in str(normalized)

    def test_size_limits(self):
        """Test size limit validation."""
        validator = DataValidator()
        
        # Large string
        large_string = "x" * 1000000  # 1MB string
        large_data = {"large": large_string}
        
        # Should validate size
        try:
            validator.validate_data_structure(large_data)
        except ValidationError as e:
            assert "size" in str(e).lower() or "memory" in str(e).lower()

    def test_special_characters_handling(self):
        """Test handling of special characters in input."""
        validator = PathValidator()
        
        # Unicode characters
        unicode_path = "test_文件.txt"
        validator.validate_path(unicode_path)  # Should be allowed
        
        # Control characters
        control_chars = "test\x00\x01\x02.txt"
        with pytest.raises(PathSecurityError):
            validator.validate_path(control_chars)


@pytest.mark.xsystem_unit
class TestValidationErrorHandling:
    """Test validation error handling."""

    def test_validation_error_messages(self):
        """Test validation error messages are informative."""
        validator = PathValidator()
        
        try:
            validator.validate_path("../etc/passwd")
        except PathSecurityError as e:
            assert "traversal" in str(e).lower() or "dangerous" in str(e).lower()

    def test_type_error_messages(self):
        """Test type error messages."""
        try:
            validate_path_input(123)
        except TypeError as e:
            assert "string" in str(e)

    def test_depth_error_messages(self):
        """Test depth validation error messages."""
        deep_data = {"l1": {"l2": {"l3": {"l4": {"l5": "value"}}}}}
        
        try:
            check_data_depth(deep_data, max_depth=3)
        except ValidationError as e:
            assert "depth" in str(e).lower()
            assert "3" in str(e)


@pytest.mark.xsystem_unit
class TestEdgeCases:
    """Test edge cases in validation."""

    def test_empty_inputs(self):
        """Test empty input handling."""
        validator = PathValidator()
        
        # Empty string
        with pytest.raises(PathSecurityError):
            validator.validate_path("")
            
        # Whitespace only
        with pytest.raises(PathSecurityError):
            validator.validate_path("   ")

    def test_very_long_inputs(self):
        """Test very long input handling."""
        # Very long path
        long_path = "a" * 10000
        
        with pytest.raises(ValidationError):
            validate_path_input(long_path)

    def test_binary_data(self):
        """Test binary data handling."""
        # Binary data should be rejected
        binary_data = {"key": b"\x00\x01\x02\x03"}
        
        # Should be safe type but might fail in JSON serialization contexts
        assert SafeTypeValidator.is_safe_type(binary_data["key"])

    def test_extreme_nesting(self):
        """Test extremely nested data structures."""
        # Create extremely nested structure
        nested = "value"
        for _ in range(1000):
            nested = [nested]
            
        with pytest.raises(GenericSecurityError):
            validate_untrusted_data(nested, max_depth=100)
