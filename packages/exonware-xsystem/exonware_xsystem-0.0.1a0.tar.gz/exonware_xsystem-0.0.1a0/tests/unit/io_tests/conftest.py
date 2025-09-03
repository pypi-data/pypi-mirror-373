"""
Pytest configuration for xSystem IO tests.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def atomic_file_module():
    """Provide atomic_file module for testing."""
    try:
        from exonware.xsystem.io.atomic_file import AtomicFileWriter
        return AtomicFileWriter
    except ImportError as e:
        pytest.skip(f"AtomicFileWriter import failed: {e}")

@pytest.fixture
def safe_temp_dir():
    """Provide a safe temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_content():
    """Provide sample content for file testing."""
    return {
        "text": "Hello, World!\nThis is test content.",
        "json": {"name": "test", "value": 123},
        "binary": b"Binary content for testing"
    } 