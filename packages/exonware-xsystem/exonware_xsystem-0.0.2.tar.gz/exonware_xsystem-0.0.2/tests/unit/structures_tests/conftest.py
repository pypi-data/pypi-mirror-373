"""
Pytest configuration for xSystem structures tests.
"""

import pytest
import sys
from pathlib import Path

# Path setup - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def circular_detector_module():
    """Provide CircularReferenceDetector module for testing."""
    try:
        from exonware.xsystem.structures.circular_detector import CircularReferenceDetector
        return CircularReferenceDetector
    except ImportError as e:
        pytest.skip(f"CircularReferenceDetector import failed: {e}")

@pytest.fixture
def complex_circular_data():
    """Provide complex circular reference data for testing."""
    # Create deeply nested circular structure
    root = {"name": "root", "children": []}
    
    # Level 1
    child1 = {"name": "child1", "parent": root, "siblings": []}
    child2 = {"name": "child2", "parent": root, "siblings": []}
    
    # Level 2 
    grandchild = {"name": "grandchild", "parent": child1, "grandparent": root}
    
    # Create circular references
    root["children"] = [child1, child2]
    child1["siblings"] = [child2]
    child2["siblings"] = [child1]
    child1["children"] = [grandchild]
    
    return root

@pytest.fixture
def safe_deep_data():
    """Provide safe deeply nested data for testing."""
    return {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "data": "deep_value",
                        "numbers": [1, 2, 3, 4, 5]
                    }
                }
            }
        },
        "array": [
            {"item1": "value1"},
            {"item2": "value2"},
            {"item3": {"nested": "value3"}}
        ]
    } 