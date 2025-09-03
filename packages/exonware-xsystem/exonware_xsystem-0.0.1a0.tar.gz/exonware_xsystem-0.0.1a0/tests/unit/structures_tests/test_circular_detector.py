"""
Test suite for xSystem CircularDetector functionality.
Tests circular reference detection, depth limits, and complex data structures.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from exonware.xsystem.structures.circular_detector import CircularReferenceDetector
except ImportError as e:
    pytest.skip(f"CircularReferenceDetector import failed: {e}", allow_module_level=True)


@pytest.mark.xsystem_structures
class TestCircularDetectorBasic:
    """Test suite for basic CircularDetector functionality."""
    
    def test_circular_detector_creation(self):
        """Test creating CircularReferenceDetector instance."""
        detector = CircularReferenceDetector()
        assert detector is not None
    
    def test_safe_data_detection(self, safe_data):
        """Test detection of safe (non-circular) data."""
        detector = CircularReferenceDetector()
        result = detector.is_circular(safe_data)
        assert result is False
    
    def test_simple_circular_detection(self, circular_data):
        """Test detection of simple circular references."""
        detector = CircularReferenceDetector()
        result = detector.is_circular(circular_data)
        assert result is True


@pytest.mark.xsystem_structures
class TestCircularDetectorComplex:
    """Test suite for complex scenarios."""
    
    def test_complex_circular_detection(self, complex_circular_data):
        """Test detection of complex circular references."""
        detector = CircularReferenceDetector()
        result = detector.is_circular(complex_circular_data)
        assert result is True
    
    def test_list_circular_references(self):
        """Test detection of circular references in lists."""
        list_a = [1, 2, 3]
        list_b = [4, 5, list_a]
        list_a.append(list_b)
        
        detector = CircularReferenceDetector()
        result = detector.is_circular(list_a)
        assert result is True


@pytest.mark.xsystem_structures
class TestCircularDetectorEdgeCases:
    """Test suite for edge cases."""
    
    def test_empty_structures(self):
        """Test handling of empty structures."""
        detector = CircularReferenceDetector()
        
        empty_cases = [{}, [], None, "", 0, False]
        for empty_case in empty_cases:
            result = detector.is_circular(empty_case)
            assert result is False
    
    def test_primitive_types(self):
        """Test handling of primitive types."""
        detector = CircularReferenceDetector()
        
        primitives = ["string", 123, 45.67, True, False, None]
        for primitive in primitives:
            result = detector.is_circular(primitive)
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 