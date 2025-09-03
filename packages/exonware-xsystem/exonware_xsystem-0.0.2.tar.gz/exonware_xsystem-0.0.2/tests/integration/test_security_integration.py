"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Integration tests for security components working together.
"""

import pytest
import tempfile
import json
from pathlib import Path

from exonware.xsystem.security.path_validator import PathValidator, PathSecurityError
from exonware.xsystem.security.crypto import SymmetricEncryption, SecureStorage
from exonware.xsystem.io.atomic_file import AtomicFileWriter
from exonware.xsystem.validation.data_validator import DataValidator
from exonware.xsystem.serialization.jsonx import JsonSerializer
from exonware.xsystem.monitoring.error_recovery import ErrorRecoveryManager


@pytest.mark.xsystem_integration
class TestSecureFileOperations:
    """Test secure file operations with validation and encryption."""

    def test_secure_file_write_read_cycle(self):
        """Test complete secure file write/read cycle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Set up security components
            path_validator = PathValidator(base_path=base_path)
            data_validator = DataValidator()
            encryption = SymmetricEncryption()
            
            # Prepare secure data
            sensitive_data = {
                "user_id": 12345,
                "api_key": "secret_key_123",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
            
            # Validate data structure
            data_validator.validate_data_structure(sensitive_data)
            
            # Serialize and encrypt
            json_data = json.dumps(sensitive_data)
            encrypted_data = encryption.encrypt(json_data.encode('utf-8'))
            
            # Secure file path
            file_path = base_path / "secure_data.enc"
            path_validator.validate_path(str(file_path))
            
            # Write with atomic operations
            with AtomicFileWriter(file_path, mode='wb') as writer:
                writer.write(encrypted_data)
            
            # Read and decrypt
            with open(file_path, 'rb') as f:
                read_encrypted = f.read()
            
            decrypted_data = encryption.decrypt(read_encrypted)
            recovered_data = json.loads(decrypted_data.decode('utf-8'))
            
            assert recovered_data == sensitive_data

    def test_path_validation_with_file_operations(self):
        """Test path validation integrated with file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            validator = PathValidator(base_path=base_path)
            
            # Valid file operation
            safe_file = base_path / "safe_file.txt"
            validator.validate_path(str(safe_file))
            
            with AtomicFileWriter(safe_file) as writer:
                writer.write("safe content")
            
            assert safe_file.exists()
            
            # Invalid file operation should be blocked
            dangerous_path = "../../../etc/passwd"
            
            with pytest.raises(PathSecurityError):
                validator.validate_path(dangerous_path)

    def test_secure_json_serialization(self):
        """Test secure JSON serialization with validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "secure_data.json"
            
            # Secure JSON serializer with validation
            serializer = JsonSerializer(
                validate_input=True,
                max_depth=10,
                max_size_mb=1.0
            )
            
            # Valid data
            valid_data = {
                "level1": {
                    "level2": {
                        "values": [1, 2, 3, "safe_string"]
                    }
                }
            }
            
            # Should succeed
            serializer.save_file(valid_data, file_path)
            loaded_data = serializer.load_file(file_path)
            assert loaded_data == valid_data
            
            # Invalid data (too deep)
            too_deep = {}
            current = too_deep
            for i in range(15):  # Deeper than max_depth
                current["next"] = {}
                current = current["next"]
            
            with pytest.raises(Exception):  # Should be blocked by validation
                serializer.save_file(too_deep, file_path)


@pytest.mark.xsystem_integration
class TestSecureDataPipeline:
    """Test complete secure data processing pipeline."""

    def test_end_to_end_secure_pipeline(self):
        """Test end-to-end secure data pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Initialize security components
            path_validator = PathValidator(base_path=base_path)
            data_validator = DataValidator(max_dict_depth=5)
            secure_storage = SecureStorage()
            json_serializer = JsonSerializer(validate_input=True)
            
            # Input data (simulating user input)
            user_data = {
                "username": "testuser",
                "preferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": {
                        "email": True,
                        "push": False
                    }
                },
                "sensitive_info": {
                    "credit_card": "****-****-****-1234",
                    "ssn": "***-**-****"
                }
            }
            
            # Step 1: Validate data structure
            data_validator.validate_data_structure(user_data)
            
            # Step 2: Store in secure storage
            secure_storage.store(
                "user_123",
                user_data,
                metadata={"created": "2025-08-31", "level": "sensitive"}
            )
            
            # Step 3: Serialize and save to secure file
            file_path = base_path / "user_data.json"
            path_validator.validate_path(str(file_path))
            json_serializer.save_file(user_data, file_path)
            
            # Verification: Read back and compare
            retrieved_from_storage = secure_storage.retrieve("user_123")
            retrieved_from_file = json_serializer.load_file(file_path)
            
            assert retrieved_from_storage == user_data
            assert retrieved_from_file == user_data
            
            # Verify metadata
            metadata = secure_storage.get_metadata("user_123")
            assert metadata["level"] == "sensitive"

    def test_security_error_recovery(self):
        """Test error recovery in security operations."""
        error_manager = ErrorRecoveryManager()
        
        # Register error handler for security errors
        def security_error_handler(error: Exception) -> str:
            return f"Security breach detected: {type(error).__name__}"
        
        error_manager.register_degradation_strategy(
            "security_errors",
            security_error_handler
        )
        
        # Simulate security error
        with pytest.raises(PathSecurityError):
            validator = PathValidator()
            validator.validate_path("../../../etc/passwd")


@pytest.mark.xsystem_integration
class TestCrossModuleSecurityValidation:
    """Test security validation across multiple modules."""

    def test_atomic_file_with_path_validation(self):
        """Test atomic file operations with path validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            validator = PathValidator(base_path=base_path)
            
            # Create secure file path
            secure_file = base_path / "secure" / "data.txt"
            validator.validate_path(str(secure_file))
            
            # Ensure parent directory exists
            secure_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use atomic writer with validated path
            content = "sensitive data content"
            with AtomicFileWriter(secure_file) as writer:
                writer.write(content)
            
            # Verify file was created securely
            assert secure_file.exists()
            assert secure_file.read_text() == content
            
            # Try to write to invalid path
            invalid_file = base_path.parent / "escape.txt"
            with pytest.raises(PathSecurityError):
                validator.validate_path(str(invalid_file))

    def test_encryption_with_serialization(self):
        """Test encryption integrated with serialization."""
        encryption = SymmetricEncryption()
        serializer = JsonSerializer(validate_input=True)
        
        # Original data
        original_data = {
            "credentials": {
                "username": "admin",
                "password": "secret123"
            },
            "permissions": ["read", "write", "admin"]
        }
        
        # Serialize to JSON
        json_str = serializer.dumps(original_data)
        
        # Encrypt JSON
        encrypted_json = encryption.encrypt_string(json_str)
        
        # Decrypt and deserialize
        decrypted_json = encryption.decrypt_string(encrypted_json)
        recovered_data = serializer.loads(decrypted_json)
        
        assert recovered_data == original_data

    def test_validation_chain(self):
        """Test chained validation across multiple validators."""
        # Set up validation chain
        path_validator = PathValidator()
        data_validator = DataValidator(max_dict_depth=3)
        
        # Data that should pass all validations
        valid_data = {
            "file_path": "safe/path/file.txt",
            "content": {
                "level1": {
                    "level2": "safe_value"
                }
            }
        }
        
        # Validate path
        path_validator.validate_path(valid_data["file_path"])
        
        # Validate data structure
        data_validator.validate_data_structure(valid_data["content"])
        
        # Data that should fail validation
        invalid_data = {
            "file_path": "../../../etc/passwd",
            "content": {
                "l1": {"l2": {"l3": {"l4": "too_deep"}}}
            }
        }
        
        # Path validation should fail
        with pytest.raises(PathSecurityError):
            path_validator.validate_path(invalid_data["file_path"])
        
        # Data validation should fail
        with pytest.raises(Exception):
            data_validator.validate_data_structure(invalid_data["content"])


@pytest.mark.xsystem_integration
class TestSecurityConfiguration:
    """Test security configuration and policy enforcement."""

    def test_security_policy_enforcement(self):
        """Test enforcement of security policies across modules."""
        # Strict security configuration
        strict_path_validator = PathValidator(
            max_path_length=100,
            allow_absolute=False,
            check_existence=True
        )
        
        strict_data_validator = DataValidator(
            max_dict_depth=3,
            max_path_length=50
        )
        
        # Test policy enforcement
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            test_file = base_path / "test.txt"
            test_file.touch()
            
            # Should pass strict validation
            relative_path = str(test_file.relative_to(Path.cwd()))
            if len(relative_path) <= 100:
                strict_path_validator.validate_path(relative_path)
            
            # Should fail with too long path
            long_path = "a" * 150
            with pytest.raises(PathSecurityError):
                strict_path_validator.validate_path(long_path)
            
            # Should fail with too deep data
            deep_data = {"l1": {"l2": {"l3": {"l4": "value"}}}}
            with pytest.raises(Exception):
                strict_data_validator.validate_data_structure(deep_data)

    def test_security_monitoring_integration(self):
        """Test security monitoring integration."""
        # This would integrate with actual monitoring in a real system
        security_events = []
        
        def log_security_event(event_type: str, details: str) -> None:
            security_events.append({
                "type": event_type,
                "details": details,
                "timestamp": "2025-08-31T12:00:00Z"
            })
        
        # Simulate security events
        try:
            validator = PathValidator()
            validator.validate_path("../../../etc/passwd")
        except PathSecurityError as e:
            log_security_event("PATH_TRAVERSAL_ATTEMPT", str(e))
        
        # Verify security event was logged
        assert len(security_events) == 1
        assert security_events[0]["type"] == "PATH_TRAVERSAL_ATTEMPT"


@pytest.mark.xsystem_integration
class TestSecurityPerformance:
    """Test security operations under load."""

    def test_validation_performance(self):
        """Test validation performance with many operations."""
        validator = PathValidator()
        data_validator = DataValidator()
        
        # Test many path validations
        safe_paths = [f"safe/path/file_{i}.txt" for i in range(1000)]
        
        for path in safe_paths:
            validator.validate_path(path)  # Should be fast
        
        # Test many data validations
        safe_data_items = [
            {"id": i, "data": f"item_{i}"} for i in range(1000)
        ]
        
        for data in safe_data_items:
            data_validator.validate_data_structure(data)  # Should be fast

    def test_encryption_performance(self):
        """Test encryption performance with various data sizes."""
        encryption = SymmetricEncryption()
        
        # Test various data sizes
        data_sizes = [100, 1000, 10000]  # bytes
        
        for size in data_sizes:
            data = "x" * size
            encrypted = encryption.encrypt_string(data)
            decrypted = encryption.decrypt_string(encrypted)
            assert decrypted == data
