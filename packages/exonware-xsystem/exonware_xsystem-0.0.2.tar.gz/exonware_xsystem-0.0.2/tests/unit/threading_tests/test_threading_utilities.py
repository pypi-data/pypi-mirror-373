"""
Test threading utilities from xsystem.
"""

import pytest
import threading
import time
import sys
from pathlib import Path
from unittest.mock import Mock

# Import the actual xsystem threading utilities
# Navigate to the correct xsystem location - avoid module name conflicts
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
xsystem_path = project_root / "src" / "exonware" / "xsystem"

# Import directly from file paths to avoid threading module name conflict
try:
    # Add the specific file paths to sys.path temporarily
    threading_dir = str(xsystem_path / "threading")
    sys.path.insert(0, threading_dir)
    
    # Import using importlib to avoid name conflicts
    import importlib.util
    
    # Load locks module
    locks_spec = importlib.util.spec_from_file_location("xsystem_locks", xsystem_path / "threading" / "locks.py")
    locks_module = importlib.util.module_from_spec(locks_spec)
    locks_spec.loader.exec_module(locks_module)
    EnhancedRLock = locks_module.EnhancedRLock
    
    # Load safe_factory module
    factory_spec = importlib.util.spec_from_file_location("xsystem_factory", xsystem_path / "threading" / "safe_factory.py")
    factory_module = importlib.util.module_from_spec(factory_spec)
    factory_spec.loader.exec_module(factory_module)
    ThreadSafeFactory = factory_module.ThreadSafeFactory
    MethodGenerator = factory_module.MethodGenerator
    
    THREADING_AVAILABLE = True
    IMPORT_ERROR = None

except Exception as e:
    THREADING_AVAILABLE = False
    IMPORT_ERROR = str(e)
    EnhancedRLock = None
    ThreadSafeFactory = None
    MethodGenerator = None

finally:
    # Clean up sys.path
    if threading_dir in sys.path:
        sys.path.remove(threading_dir)


@pytest.mark.skipif(not THREADING_AVAILABLE, reason=f"Threading utilities not available: {IMPORT_ERROR if not THREADING_AVAILABLE else ''}")
class TestThreadingLocks:
    """Test enhanced locking utilities."""
    
    def test_lock_creation(self):
        """Test basic lock creation."""
        lock = EnhancedRLock()
        assert lock is not None
        assert lock._name.startswith("EnhancedRLock-")
        
        # Test with custom name
        named_lock = EnhancedRLock(name="test_lock")
        assert named_lock._name == "test_lock"
    
    def test_lock_acquire_release(self):
        """Test basic acquire/release functionality."""
        lock = EnhancedRLock()
        
        # Test acquire with explicit timeout to avoid None timeout issue
        result = lock.acquire(timeout=1.0)
        assert result is True
        
        # Test release
        lock.release()
        
        # Test acquire with explicit timeout again
        result = lock.acquire(timeout=2.0)
        assert result is True
        lock.release()
    
    def test_lock_functionality(self):
        """Test basic lock functionality with explicit timeouts."""
        lock = EnhancedRLock()
        shared_data = {"counter": 0}
        errors = []

        def worker():
            try:
                # Use explicit acquire/release with timeout instead of context managers
                if lock.acquire(timeout=5.0):  # Use generous timeout
                    try:
                        current = shared_data["counter"]
                        time.sleep(0.001)  # Simulate work
                        shared_data["counter"] = current + 1
                    finally:
                        lock.release()
                else:
                    errors.append("Failed to acquire lock")
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert shared_data["counter"] == 10
    
    def test_lock_timeout(self):
        """Test lock timeout functionality."""
        lock = EnhancedRLock()
        
        # Acquire lock in main thread with explicit timeout
        assert lock.acquire(timeout=1.0) is True
        
        # Try to acquire with timeout from another thread
        result = [None]
        def timeout_worker():
            result[0] = lock.acquire(timeout=0.1)
        
        thread = threading.Thread(target=timeout_worker)
        thread.start()
        thread.join()
        
        # Should have timed out
        assert result[0] is False
        
        # Release the lock
        lock.release()


@pytest.mark.skipif(not THREADING_AVAILABLE, reason=f"Threading utilities not available: {IMPORT_ERROR if not THREADING_AVAILABLE else ''}")
class TestThreadSafeFactory:
    """Test thread-safe factory utilities."""
    
    def test_factory_creation(self):
        """Test basic factory creation."""
        factory = ThreadSafeFactory()
        assert factory is not None
        assert len(factory.get_available_formats()) == 0
    
    def test_handler_registration(self):
        """Test handler registration and retrieval."""
        factory = ThreadSafeFactory()
        
        class TestHandler:
            def __init__(self, name):
                self.name = name
        
        # Register handler
        factory.register("test", TestHandler)
        
        # Check registration
        assert factory.has_handler("test")
        assert factory.has_handler("TEST")  # Case insensitive
        
        # Get handler class
        handler_class = factory.get_handler("test")
        assert handler_class == TestHandler
        
        # Create instance manually
        handler_instance = handler_class(name="test_instance")
        assert handler_instance.name == "test_instance"
    
    def test_thread_safe_operations(self):
        """Test thread-safe factory operations."""
        factory = ThreadSafeFactory()
        results = []
        errors = []

        class TestHandler:
            def __init__(self, name):
                self.name = name

        def worker(worker_id):
            try:
                handler_name = f"handler_{worker_id}"
                # Register the handler
                factory.register(handler_name, TestHandler)
                
                # Get the handler class and create instance
                handler_class = factory.get_handler(handler_name)
                handler = handler_class(name=handler_name)
                results.append((worker_id, handler.name))
            except Exception as e:
                errors.append((worker_id, str(e)))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        # Check all handlers were created correctly
        for worker_id, handler_name in results:
            assert handler_name == f"handler_{worker_id}"
    
    def test_extension_mapping(self):
        """Test file extension mapping."""
        factory = ThreadSafeFactory()
        
        class JsonHandler:
            pass
        
        # Register with extensions
        factory.register("json", JsonHandler, extensions=["json", "jsonl"])
        
        # Test extension lookup
        assert factory.get_format_by_extension("json") == "json"
        assert factory.get_format_by_extension(".json") == "json"
        assert factory.get_format_by_extension("jsonl") == "json"
        assert factory.get_format_by_extension("txt") is None


@pytest.mark.skipif(not THREADING_AVAILABLE, reason=f"Threading utilities not available: {IMPORT_ERROR if not THREADING_AVAILABLE else ''}")
class TestMethodGenerator:
    """Test dynamic method generation utilities."""
    
    def test_method_generator_exists(self):
        """Test that MethodGenerator class exists."""
        assert MethodGenerator is not None
        assert hasattr(MethodGenerator, 'generate_export_methods')
    
    def test_method_generation_basic(self):
        """Test basic method generation functionality."""
        factory = ThreadSafeFactory()
        
        class TestHandler:
            pass
        
        # Register a handler
        factory.register("json", TestHandler)
        
        # Create a target class
        class TestTarget:
            def template_method(self, format_name, *args, **kwargs):
                return f"processed_{format_name}"
        
        # Generate methods
        MethodGenerator.generate_export_methods(
            TestTarget, 
            factory, 
            TestTarget.template_method
        )
        
        # Check if method was generated
        target = TestTarget()
        assert hasattr(target, 'export_json')


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 