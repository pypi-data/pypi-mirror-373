"""
Pytest configuration for xSystem performance tests.
"""

import pytest
import sys
import time
import threading
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def performance_data():
    """Provide test data for performance benchmarks."""
    return {
        'small_dict': {f'key_{i}': f'value_{i}' for i in range(100)},
        'medium_dict': {f'key_{i}': f'value_{i}' for i in range(1000)},
        'large_dict': {f'key_{i}': f'value_{i}' for i in range(10000)},
        'nested_dict': {
            'level1': {
                'level2': {
                    'level3': {f'key_{i}': f'value_{i}' for i in range(100)}
                }
            }
        }
    }

@pytest.fixture
def circular_data():
    """Create data with circular references for testing."""
    data = {'root': {}}
    data['root']['parent'] = data
    return data

@pytest.fixture
def thread_count():
    """Provide thread count for concurrency tests."""
    return min(10, (threading.active_count() + 5))

@pytest.fixture
def benchmark_iterations():
    """Provide iteration count for benchmarks."""
    return 1000

@pytest.fixture
def performance_threshold():
    """Provide performance thresholds for validation."""
    return {
        'max_execution_time': 0.1,  # 100ms max for most operations
        'max_memory_mb': 50,        # 50MB max memory usage
        'max_lock_contention': 0.01  # 10ms max lock wait time
    }
