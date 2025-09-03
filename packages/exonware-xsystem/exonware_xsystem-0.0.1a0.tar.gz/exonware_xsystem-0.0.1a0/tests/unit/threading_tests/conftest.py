"""
Pytest configuration for xSystem threading tests.
"""

import pytest
import sys
import time
import threading as std_threading
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def locks_module():
    """Provide locks module for testing."""
    try:
        from exonware.xsystem.threading import locks
        return locks
    except ImportError as e:
        pytest.skip(f"Threading locks import failed: {e}")

@pytest.fixture
def safe_factory_module():
    """Provide safe_factory module for testing."""
    try:
        from exonware.xsystem.threading.safe_factory import SafeFactory
        return SafeFactory
    except ImportError as e:
        pytest.skip(f"SafeFactory import failed: {e}")

@pytest.fixture
def thread_test_data():
    """Provide data for thread testing."""
    return {
        "shared_counter": 0,
        "results": [],
        "errors": [],
        "thread_count": 5,
        "iterations": 100
    }

def sample_worker(data, delay=0.001):
    """Sample worker function for threading tests."""
    time.sleep(delay)
    data["shared_counter"] += 1
    data["results"].append(std_threading.current_thread().name)
    return data["shared_counter"] 