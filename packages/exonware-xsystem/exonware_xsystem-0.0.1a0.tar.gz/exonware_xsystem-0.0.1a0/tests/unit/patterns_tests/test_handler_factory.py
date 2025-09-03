"""
Test suite for xSystem HandlerFactory functionality.
Tests handler registration, creation, and thread safety.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports - navigate to project root then to src
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from exonware.xsystem.patterns.handler_factory import GenericHandlerFactory
except ImportError as e:
    pytest.skip(f"GenericHandlerFactory import failed: {e}", allow_module_level=True)


@pytest.mark.xsystem_patterns
class TestHandlerFactoryBasic:
    """Test suite for basic HandlerFactory functionality."""
    
    def test_handler_factory_creation(self):
        """Test creating GenericHandlerFactory instance."""
        factory = GenericHandlerFactory()
        assert factory is not None
    
    def test_handler_registration(self, sample_handlers):
        """Test handler registration."""
        factory = GenericHandlerFactory()
        
        for name, handler_class in sample_handlers.items():
            factory.register(name, handler_class)
            assert factory.has_handler(name)
    
    def test_handler_creation(self, sample_handlers):
        """Test handler creation."""
        factory = GenericHandlerFactory()
        
        # Register handlers
        for name, handler_class in sample_handlers.items():
            factory.register(name, handler_class)
        
        # Get handlers
        for name in sample_handlers.keys():
            handler_class = factory.get_handler(name)
            assert handler_class is not None
            assert hasattr(handler_class, '__name__')
            
            # Create instance
            handler_instance = handler_class()
            assert handler_instance is not None


@pytest.mark.xsystem_patterns
class TestHandlerFactoryThreadSafety:
    """Test suite for thread safety."""
    
    def test_concurrent_registration(self, sample_handlers):
        """Test concurrent handler registration."""
        import threading
        factory = GenericHandlerFactory()
        errors = []
        
        def register_worker(name, handler_class):
            try:
                factory.register(name, handler_class)
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for name, handler_class in sample_handlers.items():
            thread = threading.Thread(target=register_worker, args=(name, handler_class))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0
        for name in sample_handlers.keys():
            assert factory.has_handler(name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 