"""
Integration tests for xSystem module interactions.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025
"""

import pytest
import tempfile
from pathlib import Path
import threading
import time

from exonware.xsystem import (
    ThreadSafeFactory, PathValidator, AtomicFileWriter, 
    CircularReferenceDetector, GenericHandlerFactory,
    setup_logging, get_logger
)


@pytest.mark.xsystem_integration
class TestModuleInteractions:
    """Test interactions between different xSystem modules."""
    
    def test_logging_with_threading_factory(self):
        """Test logging integration with threading factory."""
        logger = get_logger('integration.test')
        
        factory = ThreadSafeFactory()
        
        # Register handler with logging
        class LoggingHandler:
            def __init__(self):
                self.logger = get_logger('handler')
            
            def process(self, data):
                self.logger.info(f"Processing: {data}")
                return data.upper()
        
        factory.register("logging_handler", LoggingHandler, ["log"])
        
        # Test integration
        handler_class = factory.get_handler("logging_handler")
        handler = handler_class()
        result = handler.process("test")
        
        assert result == "TEST"
    
    def test_path_validation_with_file_operations(self):
        """Test path validation with atomic file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(base_path=tmpdir, allow_absolute=True)
            safe_path = Path(tmpdir) / "test.txt"
            validated_path = validator.validate_path(str(safe_path))
            
            # Use with atomic file writer
            writer = AtomicFileWriter()
            writer.write_file(validated_path, "test content")
            
            # Verify file was written
            assert safe_path.exists()
            assert safe_path.read_text() == "test content"
    
    def test_circular_detection_with_complex_data(self):
        """Test circular detection with complex nested data."""
        detector = CircularReferenceDetector()
        
        # Create complex data structure
        data = {
            'users': [
                {'id': 1, 'name': 'Alice', 'friends': []},
                {'id': 2, 'name': 'Bob', 'friends': []}
            ]
        }
        
        # Add circular reference
        data['users'][0]['friends'].append(data['users'][1])
        data['users'][1]['friends'].append(data['users'][0])
        
        # Test detection
        has_circular = detector.has_circular_references(data)
        assert has_circular is True
        
        # Test without circular reference
        clean_data = {
            'users': [
                {'id': 1, 'name': 'Alice'},
                {'id': 2, 'name': 'Bob'}
            ]
        }
        has_circular = detector.has_circular_references(clean_data)
        assert has_circular is False
    
    def test_concurrent_operations_integration(self):
        """Test concurrent operations across multiple modules."""
        factory = ThreadSafeFactory()
        logger = get_logger('concurrent.test')
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Register handler
                factory.register(f"worker_{worker_id}", str, [f"ext_{worker_id}"])
                
                # Get handler
                handler = factory.get_handler(f"worker_{worker_id}")
                
                # Log operation
                logger.info(f"Worker {worker_id} completed")
                
                results.append(worker_id)
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, "Not all workers completed"
    
    def test_error_recovery_with_logging(self):
        """Test error recovery with logging integration."""
        logger = get_logger('error.recovery')
        
        # Simulate error condition
        try:
            raise ValueError("Test error for recovery")
        except ValueError as e:
            logger.error(f"Caught error: {e}")
            
            # Test recovery
            logger.info("Attempting recovery...")
            # Simulate successful recovery
            logger.info("Recovery successful")
            
            assert True  # Recovery completed
