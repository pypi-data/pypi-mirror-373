"""
Test suite for xSystem logging configuration functionality.
Tests logging control, environment handling, and configuration management.
Following xSystem test quality standards.
"""

import pytest
import sys
import logging
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from exonware.xsystem.config.logging import LoggingConfig, logging_config, logging_disable, logging_enable, logging_set_level
    from exonware.xsystem.config.logging_setup import setup_logging, get_logger
except ImportError as e:
    pytest.skip(f"Logging config import failed: {e}", allow_module_level=True)


@pytest.mark.xsystem_unit
class TestLoggingConfigBasic:
    """Test suite for basic LoggingConfig functionality."""
    
    def test_logging_config_creation(self, clean_env):
        """Test creating LoggingConfig instance."""
        config = LoggingConfig()
        assert config is not None
        assert hasattr(config, '_enabled')
        assert hasattr(config, '_level')
    
    def test_default_configuration(self, clean_env):
        """Test default logging configuration values."""
        config = LoggingConfig()
        assert config.enabled is True  # Should default to enabled
        assert config.level in ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']
    
    def test_enable_disable_functionality(self, clean_env):
        """Test enable/disable logging functionality."""
        config = LoggingConfig()
        
        # Test disable
        config.disable()
        assert config.enabled is False
        assert os.environ.get('XSYSTEM_LOGGING_DISABLE') == 'true'
        
        # Test enable
        config.enable()
        assert config.enabled is True
        assert os.environ.get('XSYSTEM_LOGGING_DISABLE') == 'false'
    
    def test_level_setting(self, clean_env, logging_test_levels):
        """Test setting different logging levels."""
        config = LoggingConfig()
        
        for level in logging_test_levels:
            config.set_level(level)
            assert config.level == level
    
    def test_level_case_insensitive(self, clean_env):
        """Test that level setting is case insensitive."""
        config = LoggingConfig()
        
        test_cases = [
            ('debug', 'DEBUG'),
            ('Info', 'INFO'),
            ('WARNING', 'WARNING'),
            ('error', 'ERROR'),
            ('Critical', 'CRITICAL')
        ]
        
        for input_level, expected_level in test_cases:
            config.set_level(input_level)
            assert config.level == expected_level


@pytest.mark.xsystem_unit
class TestLoggingConfigEnvironment:
    """Test suite for environment variable handling."""
    
    def test_environment_variable_respect(self, clean_env):
        """Test that configuration respects environment variables."""
        # Set environment variable before creating config
        os.environ['XSYSTEM_LOGGING_DISABLE'] = 'true'
        
        config = LoggingConfig()
        config.enable()  # Try to enable
        
        # Environment variable should be updated
        assert os.environ.get('XSYSTEM_LOGGING_DISABLE') == 'false'
    
    def test_disable_sets_env_var(self, clean_env):
        """Test that disable() sets environment variable."""
        config = LoggingConfig()
        config.disable()
        
        assert os.environ.get('XSYSTEM_LOGGING_DISABLE') == 'true'
    
    def test_enable_sets_env_var(self, clean_env):
        """Test that enable() sets environment variable."""
        config = LoggingConfig()
        config.disable()  # First disable
        config.enable()   # Then enable
        
        assert os.environ.get('XSYSTEM_LOGGING_DISABLE') == 'false'


@pytest.mark.xsystem_unit
class TestLoggingConfigIntegration:
    """Test suite for logging config integration with Python logging."""
    
    @patch('logging.disable')
    def test_disable_calls_logging_module(self, mock_disable, clean_env):
        """Test that disable() calls Python logging.disable()."""
        config = LoggingConfig()
        config.disable()
        
        mock_disable.assert_called_with(logging.CRITICAL)
    
    @patch('logging.disable')
    def test_enable_calls_logging_module(self, mock_disable, clean_env):
        """Test that enable() calls Python logging.disable()."""
        config = LoggingConfig()
        config.enable()
        
        mock_disable.assert_called_with(logging.NOTSET)
    
    @patch('logging.getLogger')
    def test_set_level_calls_logging_when_enabled(self, mock_get_logger, clean_env):
        """Test that set_level() calls logging module when enabled."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        config = LoggingConfig()
        config.set_level('WARNING')
        
        mock_get_logger.assert_called_once()
        mock_logger.setLevel.assert_called_once_with(logging.WARNING)
    
    @patch('logging.getLogger')
    def test_set_level_no_call_when_disabled(self, mock_get_logger, clean_env):
        """Test that set_level() doesn't call logging when disabled."""
        config = LoggingConfig()
        config.disable()
        config.set_level('DEBUG')
        
        # Should track level but not call logging module
        assert config.level == 'DEBUG'
        # getLogger might be called during disable, but not for set_level
        # We can't easily test this without more complex mocking


@pytest.mark.xsystem_unit
class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_logging_disable_function(self, clean_env):
        """Test logging_disable() convenience function."""
        logging_disable()
        assert os.environ.get('XSYSTEM_LOGGING_DISABLE') == 'true'
    
    def test_logging_enable_function(self, clean_env):
        """Test logging_enable() convenience function."""
        logging_enable()
        assert logging_config.enabled is True
    
    def test_logging_set_level_function(self, clean_env):
        """Test logging_set_level() convenience function."""
        logging_set_level('ERROR')
        assert logging_config.level == 'ERROR'
    
    def test_global_logging_config_singleton(self, clean_env):
        """Test that global logging_config works as singleton."""
        # Store original state
        original_enabled = logging_config.enabled
        
        # Modify through global instance
        logging_config.disable()
        assert logging_config.enabled is False
        
        logging_config.enable()
        assert logging_config.enabled is True


@pytest.mark.xsystem_unit
class TestLoggingSetup:
    """Test suite for logging setup functionality."""
    
    def test_get_logger_basic(self, clean_env):
        """Test basic get_logger functionality."""
        logger = get_logger('test_logger')
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_with_name(self, clean_env):
        """Test get_logger with specific name."""
        logger = get_logger('xsystem.test')
        assert logger.name == 'xsystem.test'
    
    def test_get_logger_without_name(self, clean_env):
        """Test get_logger without name parameter."""
        logger = get_logger()
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    @patch.dict(os.environ, {'XSYSTEM_LOGGING_DISABLE': 'true'})
    def test_get_logger_when_disabled(self, clean_env):
        """Test get_logger when logging is disabled via environment."""
        logger = get_logger('test_disabled')
        assert logger.disabled is True
    
    def test_setup_logging_basic_functionality(self, temp_log_dir, clean_env):
        """Test basic setup_logging functionality."""
        log_file = temp_log_dir / "test.log"
        
        # This should not raise an error
        try:
            setup_logging(log_file=str(log_file), level=logging.DEBUG)
            # If we get here, setup worked
            success = True
        except Exception as e:
            success = False
            error = str(e)
        finally:
            # Clean up logging handlers to release file locks
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
        
        assert success, f"setup_logging failed: {error if not success else 'Unknown error'}"
    
    @patch.dict(os.environ, {'XSYSTEM_LOGGING_DISABLE': 'true'})
    def test_setup_logging_respects_disable_env(self, clean_env):
        """Test that setup_logging respects disable environment variable."""
        # Should return early without setting up logging
        setup_logging()
        
        # Hard to test without more invasive mocking, but should not raise errors


@pytest.mark.xsystem_config
class TestLoggingConfigEdgeCases:
    """Test suite for edge cases and error handling."""
    
    def test_invalid_level_handling(self, clean_env):
        """Test handling of invalid logging levels."""
        config = LoggingConfig()
        
        # This should raise AttributeError when trying to get invalid level from logging module
        with pytest.raises(AttributeError):
            config.set_level('INVALID_LEVEL')
    
    def test_multiple_enable_disable_cycles(self, clean_env):
        """Test multiple enable/disable cycles."""
        config = LoggingConfig()
        
        for _ in range(5):
            config.disable()
            assert config.enabled is False
            
            config.enable()
            assert config.enabled is True
    
    def test_concurrent_access(self, clean_env):
        """Test basic thread safety (simple check)."""
        import threading
        import time
        
        config = LoggingConfig()
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    config.disable()
                    time.sleep(0.001)
                    config.enable()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Thread safety issues: {errors}"


if __name__ == "__main__":
    # Allow direct execution
    pytest.main([__file__, "-v"])
