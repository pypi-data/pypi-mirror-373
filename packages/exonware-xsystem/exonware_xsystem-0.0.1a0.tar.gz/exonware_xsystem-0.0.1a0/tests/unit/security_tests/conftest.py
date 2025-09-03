"""
Pytest configuration for xSystem security tests.
"""

import pytest
import sys
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def path_validator_module():
    """Provide PathValidator module for testing."""
    try:
        from exonware.xsystem.security.path_validator import PathValidator
        return PathValidator
    except ImportError as e:
        pytest.skip(f"PathValidator import failed: {e}")

@pytest.fixture
def malicious_paths():
    """Provide malicious path examples for testing."""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow",
        "C:\\Windows\\System32\\config\\SAM",
        "\\\\unc\\path\\to\\file",
        "path\x00injection",
        "$(malicious command)",
        "`malicious command`",
        "path; rm -rf /",
    ]

@pytest.fixture
def safe_paths():
    """Provide safe path examples for testing."""
    return [
        "data/users.json",
        "files/documents/report.pdf",
        "temp/output.txt",
        "uploads/images/photo.jpg",
        "logs/application.log"
    ] 