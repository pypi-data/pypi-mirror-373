"""
Pytest configuration for xSystem config tests.
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def config_module():
    """Provide config module for testing."""
    try:
        from exonware.xsystem.config import logging
        return logging
    except ImportError as e:
        pytest.skip(f"Config module import failed: {e}")

@pytest.fixture
def clean_env():
    """Clean environment fixture for isolated tests."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clean xsystem-related env vars
    xsystem_vars = [k for k in os.environ.keys() if k.startswith('XSYSTEM_')]
    for var in xsystem_vars:
        del os.environ[var]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def temp_log_dir():
    """Provide temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def logging_test_levels():
    """Provide standard logging levels for testing."""
    return ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
