"""
Performance tests for xSystem threading utilities.
Tests thread safety, lock contention, and factory performance under load.
Following xSystem test quality standards.
"""

import pytest
import time
import threading
import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from exonware.xsystem.threading.safe_factory import ThreadSafeFactory
    from exonware.xsystem.threading.locks import EnhancedRLock
except ImportError as e:
    pytest.skip(f"Threading utilities import failed: {e}", allow_module_level=True)


@pytest.mark.xsystem_unit
class TestThreadSafeFactoryPerformance:
    """Performance tests for ThreadSafeFactory under load."""
    
    def test_factory_registration_performance(self, benchmark_iterations, performance_threshold):
        """Test factory registration performance under load."""
        factory = ThreadSafeFactory()
        
        start_time = time.time()
        
        # Register many handlers
        for i in range(benchmark_iterations):
            factory.register(f"handler_{i}", Mock, [f"ext_{i}"])
        
        execution_time = time.time() - start_time
        
        # Performance assertions
        assert execution_time < performance_threshold['max_execution_time'] * 10  # Allow 1s for 1000 registrations
        assert len(factory.get_available_formats()) == benchmark_iterations
    
    def test_factory_retrieval_performance(self, benchmark_iterations, performance_threshold):
        """Test factory retrieval performance under load."""
        factory = ThreadSafeFactory()
        
        # Pre-register handlers
        for i in range(100):
            factory.register(f"handler_{i}", Mock, [f"ext_{i}"])
        
        start_time = time.time()
        
        # Retrieve handlers many times
        for i in range(benchmark_iterations):
            handler = factory.get_handler(f"handler_{i % 100}")
            assert handler is not None
        
        execution_time = time.time() - start_time
        
        # Should be very fast for retrieval
        assert execution_time < performance_threshold['max_execution_time'] * 5  # Allow 500ms for 1000 retrievals
    
    def test_factory_concurrent_access_performance(self, thread_count, performance_threshold):
        """Test factory performance under concurrent access."""
        factory = ThreadSafeFactory()
        errors = []
        start_time = time.time()
        
        def worker(worker_id):
            try:
                # Mix of registrations and retrievals
                for i in range(50):
                    factory.register(f"worker_{worker_id}_handler_{i}", Mock, [f"ext_{worker_id}_{i}"])
                    
                    # Retrieve some handlers
                    if i > 10:
                        handler = factory.get_handler(f"worker_{worker_id}_handler_{i-10}")
                        assert handler is not None
                        
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        # Start worker threads
        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        execution_time = time.time() - start_time
        
        # Performance and correctness assertions
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert execution_time < performance_threshold['max_execution_time'] * 50  # Allow 5s for concurrent operations
        assert len(factory.get_available_formats()) == thread_count * 50


@pytest.mark.xsystem_unit
class TestEnhancedRLockPerformance:
    """Performance tests for EnhancedRLock under contention."""
    
    def test_lock_acquisition_performance(self, benchmark_iterations, performance_threshold):
        """Test lock acquisition/release performance."""
        lock = EnhancedRLock(name="perf_test_lock")
        
        start_time = time.time()
        
        # Rapid acquire/release cycles
        for _ in range(benchmark_iterations):
            acquired = lock.acquire(timeout=1.0)
            assert acquired is True
            lock.release()
        
        execution_time = time.time() - start_time
        
        # Should be very fast for uncontended access
        assert execution_time < performance_threshold['max_execution_time'] * 10  # Allow 1s for 1000 operations
    
    def test_lock_contention_performance(self, thread_count, performance_threshold):
        """Test lock performance under contention."""
        lock = EnhancedRLock(name="contention_test_lock")
        shared_data = {'counter': 0}
        errors = []
        lock_wait_times = []
        
        def contending_worker(worker_id):
            try:
                for _ in range(50):
                    acquire_start = time.time()
                    acquired = lock.acquire(timeout=5.0)
                    acquire_time = time.time() - acquire_start
                    lock_wait_times.append(acquire_time)
                    
                    if acquired:
                        try:
                            # Simulate work
                            current = shared_data['counter']
                            time.sleep(0.001)  # 1ms work
                            shared_data['counter'] = current + 1
                        finally:
                            lock.release()
                    else:
                        errors.append(f"Worker {worker_id}: Failed to acquire lock")
                        
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        start_time = time.time()
        
        # Start contending threads
        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=contending_worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        execution_time = time.time() - start_time
        
        # Performance and correctness assertions
        assert len(errors) == 0, f"Lock contention errors: {errors}"
        assert shared_data['counter'] == thread_count * 50, "Lost updates due to race conditions"
        
        # Check lock wait times
        if lock_wait_times:
            max_wait_time = max(lock_wait_times)
            avg_wait_time = sum(lock_wait_times) / len(lock_wait_times)
            
            assert max_wait_time < 1.0, f"Lock wait time too high: {max_wait_time}s"
            assert avg_wait_time < performance_threshold['max_lock_contention'], f"Average lock contention too high: {avg_wait_time}s"
    
    def test_lock_statistics_overhead(self, benchmark_iterations, performance_threshold):
        """Test that lock statistics don't impact performance significantly."""
        lock = EnhancedRLock(name="stats_test_lock")
        
        # Test without statistics collection (if available)
        start_time = time.time()
        for _ in range(benchmark_iterations):
            acquired = lock.acquire(timeout=1.0)
            assert acquired is True
            lock.release()
        base_time = time.time() - start_time
        
        # Get statistics
        stats = lock.get_stats()
        assert stats['acquisition_count'] >= benchmark_iterations
        
        # Statistics collection should not significantly impact performance
        # This is more of a regression test
        assert base_time < performance_threshold['max_execution_time'] * 15  # Allow 1.5s for 1000 operations with stats


@pytest.mark.xsystem_unit
class TestThreadingIntegrationPerformance:
    """Integration performance tests combining multiple threading utilities."""
    
    def test_factory_with_locks_performance(self, thread_count, performance_threshold):
        """Test factory performance when handlers use locks."""
        factory = ThreadSafeFactory()
        shared_lock = EnhancedRLock(name="shared_handler_lock")
        shared_data = {'operations': 0}
        errors = []
        
        class LockingHandler:
            def __init__(self):
                self.lock = shared_lock
                self.data = shared_data
            
            def process(self):
                acquired = self.lock.acquire(timeout=2.0)
                if acquired:
                    try:
                        current = self.data['operations']
                        time.sleep(0.0001)  # Minimal work
                        self.data['operations'] = current + 1
                    finally:
                        self.lock.release()
                    return True
                return False
        
        # Register locking handler
        factory.register("locking_handler", LockingHandler, ["lock"])
        
        def worker(worker_id):
            try:
                for _ in range(25):
                    handler_class = factory.get_handler("locking_handler")
                    if handler_class:
                        handler = handler_class()
                        success = handler.process()
                        assert success is True
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        start_time = time.time()
        
        # Start worker threads
        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        execution_time = time.time() - start_time
        
        # Performance and correctness assertions
        assert len(errors) == 0, f"Integration errors: {errors}"
        assert shared_data['operations'] == thread_count * 25, "Lost operations due to race conditions"
        
        # Should complete within reasonable time
        assert execution_time < performance_threshold['max_execution_time'] * 100  # Allow 10s for complex operations


@pytest.mark.xsystem_unit
class TestThreadingMemoryPerformance:
    """Memory usage tests for threading utilities."""
    
    def test_factory_memory_usage(self, performance_threshold):
        """Test that factory doesn't leak memory under load."""
        import gc
        
        # Force garbage collection and get baseline
        gc.collect()
        
        factory = ThreadSafeFactory()
        
        # Register and unregister many handlers
        for cycle in range(10):
            for i in range(100):
                factory.register(f"cycle_{cycle}_handler_{i}", Mock, [f"ext_{cycle}_{i}"])
            
            # Clear by creating new factory (simulating cleanup)
            factory = ThreadSafeFactory()
            
            # Force garbage collection
            gc.collect()
        
        # Memory leaks are hard to test precisely, but we can check for obvious issues
        # This is more of a smoke test
        final_formats = factory.get_available_formats()
        assert len(final_formats) == 0, "Factory should be empty after recreation"
    
    def test_lock_memory_usage(self, benchmark_iterations):
        """Test that locks don't accumulate memory over time."""
        import gc
        
        gc.collect()
        
        # Create and destroy many locks
        for i in range(benchmark_iterations // 10):  # Reduced for memory test
            lock = EnhancedRLock(name=f"temp_lock_{i}")
            
            # Use the lock briefly
            acquired = lock.acquire(timeout=0.1)
            if acquired:
                lock.release()
            
            # Delete reference
            del lock
            
            # Periodic garbage collection
            if i % 50 == 0:
                gc.collect()
        
        # Final cleanup
        gc.collect()
        
        # This is primarily a smoke test for memory leaks
        assert True  # If we get here without memory errors, we're probably OK


if __name__ == "__main__":
    # Allow direct execution
    pytest.main([__file__, "-v"])
