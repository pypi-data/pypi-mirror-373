"""
Test suite for xSystem core functionality.
Tests basic xSystem imports, initialization, and general utilities.
Following Python/pytest best practices.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import components being tested
try:
    import exonware.xsystem as xsystem
    from exonware.xsystem import __version__
except ImportError as e:
    pytest.skip(f"xSystem import failed: {e}", allow_module_level=True)


class TestXSystemCore:
    """Test suite for core xSystem functionality."""
    
    def test_xsystem_import(self):
        """Test that xsystem can be imported successfully."""
        import exonware.xsystem
        assert exonware.xsystem is not None
    
    def test_xsystem_version(self):
        """Test that xsystem has a version string."""
        assert hasattr(xsystem, '__version__')
        assert isinstance(xsystem.__version__, str)
        assert len(xsystem.__version__) > 0
    
    def test_xsystem_module_structure(self):
        """Test that xsystem has expected module structure."""
        # Test that main components are accessible
        import exonware.xsystem.io
        import exonware.xsystem.security
        import exonware.xsystem.structures
        import exonware.xsystem.patterns
        import exonware.xsystem.threading
        
        assert exonware.xsystem.io is not None
        assert exonware.xsystem.security is not None
        assert exonware.xsystem.structures is not None
        assert exonware.xsystem.patterns is not None
        assert exonware.xsystem.threading is not None


class TestXSystemUtilities:
    """Test suite for general xSystem utilities."""
    
    def test_module_attributes(self):
        """Test that xsystem module has expected attributes."""
        assert hasattr(xsystem, '__version__')
        # Test that version is a valid string
        assert isinstance(xsystem.__version__, str)
        assert len(xsystem.__version__) > 0
        
    def test_examples_available(self):
        """Test that examples module is available."""
        try:
            from exonware.xsystem import examples
            assert examples is not None
        except ImportError:
            pytest.skip("Examples module not available")


if __name__ == "__main__":
    # Allow direct execution
    pytest.main([__file__, "-v"]) 