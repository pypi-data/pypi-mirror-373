"""
Pytest configuration for xSystem patterns tests.
"""

import pytest
import sys
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def handler_factory_module():
    """Provide GenericHandlerFactory module for testing."""
    try:
        from exonware.xsystem.patterns.handler_factory import GenericHandlerFactory
        return GenericHandlerFactory
    except ImportError as e:
        pytest.skip(f"GenericHandlerFactory import failed: {e}")

# Sample handler classes for testing
class SampleHandler:
    """Sample handler for testing."""
    def __init__(self, config=None):
        self.config = config or {}
    
    def handle(self, data):
        return f"handled: {data}"

class AnotherHandler:
    """Another sample handler for testing."""
    def __init__(self, name="default"):
        self.name = name
    
    def process(self, data):
        return f"{self.name}: {data}"

@pytest.fixture
def sample_handlers():
    """Provide sample handler classes for testing."""
    return {
        "sample": SampleHandler,
        "another": AnotherHandler
    } 