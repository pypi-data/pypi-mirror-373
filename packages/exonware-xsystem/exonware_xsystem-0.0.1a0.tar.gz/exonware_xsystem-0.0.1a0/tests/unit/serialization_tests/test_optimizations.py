#!/usr/bin/env python3
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Comprehensive tests for serialization optimization features.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import optimized serializers
from exonware.xsystem.serialization.xml import XmlSerializer
from exonware.xsystem.serialization.json import JsonSerializer
from exonware.xsystem.serialization.bson import BsonSerializer


class TestOptimizationFeatures:
    """Test optimization features in serializers."""
    
    @pytest.fixture
    def test_data(self):
        """Standard test data for all serializers."""
        return {
            "name": "optimization_test",
            "values": [1, 2, 3],
            "nested": {"key": "value"},
            "number": 42.5,
            "boolean": True
        }
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        yield Path(path)
        if os.path.exists(path):
            os.unlink(path)
    
    def test_xml_inherited_file_operations(self, test_data, temp_file):
        """Test XML serializer uses inherited file operations."""
        serializer = XmlSerializer()
        
        # Verify it's a text format
        assert not serializer.is_binary_format
        assert serializer.format_name == "XML"
        
        # Test inherited save_file
        temp_xml = temp_file.with_suffix('.xml')
        serializer.save_file(test_data, temp_xml)
        assert temp_xml.exists()
        
        # Test inherited load_file
        loaded_data = serializer.load_file(temp_xml)
        assert isinstance(loaded_data, dict)
        
        # Clean up
        if temp_xml.exists():
            temp_xml.unlink()
    
    def test_json_inherited_file_operations(self, test_data, temp_file):
        """Test JSON serializer uses inherited file operations."""
        serializer = JsonSerializer()
        
        # Verify it's a text format
        assert not serializer.is_binary_format
        assert serializer.format_name == "JSON"
        
        # Test inherited save_file
        temp_json = temp_file.with_suffix('.json')
        serializer.save_file(test_data, temp_json)
        assert temp_json.exists()
        
        # Test inherited load_file
        loaded_data = serializer.load_file(temp_json)
        assert loaded_data == test_data  # JSON should preserve exact data
        
        # Clean up
        if temp_json.exists():
            temp_json.unlink()
    
    def test_bson_inherited_file_operations(self, test_data, temp_file):
        """Test BSON serializer uses inherited file operations."""
        serializer = BsonSerializer()
        
        # Verify it's a binary format
        assert serializer.is_binary_format
        assert serializer.format_name == "BSON"
        
        # Test inherited save_file (should handle binary automatically)
        temp_bson = temp_file.with_suffix('.bson')
        serializer.save_file(test_data, temp_bson)
        assert temp_bson.exists()
        
        # Test inherited load_file (should handle binary automatically)
        loaded_data = serializer.load_file(temp_bson)
        assert isinstance(loaded_data, dict)
        
        # Clean up
        if temp_bson.exists():
            temp_bson.unlink()
    
    def test_unified_error_handling(self):
        """Test unified error handling across serializers."""
        serializers = [
            XmlSerializer(),
            JsonSerializer(),
            BsonSerializer()
        ]
        
        for serializer in serializers:
            # Test that error handling method exists
            assert hasattr(serializer, '_handle_serialization_error')
            
            # Test error handling with invalid data
            with pytest.raises(Exception) as exc_info:
                # This should trigger unified error handling
                serializer.dumps(object())  # Unserializable object
            
            # Verify error contains format name
            error_str = str(exc_info.value)
            assert serializer.format_name.lower() in error_str.lower()
    
    def test_automatic_binary_text_detection(self, test_data):
        """Test automatic binary vs text file handling."""
        text_serializer = JsonSerializer()
        binary_serializer = BsonSerializer()
        
        # Text format should return string from dumps
        json_result = text_serializer.dumps(test_data)
        assert isinstance(json_result, str)
        
        # Binary format should return bytes/string (BSON returns base64 string)
        bson_result = binary_serializer.dumps(test_data)
        assert isinstance(bson_result, str)  # BSON returns base64 string
        
        # Test that binary serializer has bytes method
        bson_bytes = binary_serializer.dumps_bytes(test_data)
        assert isinstance(bson_bytes, bytes)
    
    def test_no_duplicate_file_methods(self):
        """Test that optimized serializers don't have duplicate file methods."""
        optimized_serializers = [
            XmlSerializer(),
            JsonSerializer(),
            BsonSerializer()
        ]
        
        for serializer in optimized_serializers:
            # These should be inherited from base, not redefined
            save_file_method = getattr(serializer.__class__, 'save_file', None)
            load_file_method = getattr(serializer.__class__, 'load_file', None)
            
            # If they exist in the class, they should be inherited or wrapped
            if save_file_method:
                # Check if it's defined in the serializer class or inherited (may be wrapped by decorators)
                method_str = str(save_file_method)
                assert ('aSerialization' in method_str or 'wrapper' in method_str), \
                    f"save_file method appears to be overridden: {method_str}"
            
            if load_file_method:
                method_str = str(load_file_method)
                assert ('aSerialization' in method_str or 'wrapper' in method_str), \
                    f"load_file method appears to be overridden: {method_str}"


class TestOptimizationPerformance:
    """Test performance aspects of optimizations."""
    
    @pytest.fixture
    def large_test_data(self):
        """Large test data for performance testing."""
        return {
            "users": [
                {"id": i, "name": f"user_{i}", "data": list(range(10))}
                for i in range(100)
            ],
            "metadata": {
                "count": 100,
                "generated": "test",
                "nested": {"deep": {"structure": True}}
            }
        }
    
    def test_direct_type_detection_performance(self, large_test_data):
        """Test that direct type detection doesn't add overhead."""
        import time
        
        serializers = [
            ('JSON', JsonSerializer()),
            ('BSON', BsonSerializer()),
            ('XML', XmlSerializer())
        ]
        
        for name, serializer in serializers:
            # Time the serialization (should be fast)
            start_time = time.time()
            
            # Multiple operations to measure overhead
            for _ in range(10):
                serialized = serializer.dumps(large_test_data)
                deserialized = serializer.loads(serialized)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time (not strict timing test)
            assert duration < 5.0, f"{name} serialization took too long: {duration}s"
    
    def test_error_handling_overhead(self):
        """Test that unified error handling doesn't add significant overhead."""
        serializer = JsonSerializer()
        test_data = {"simple": "data"}
        
        import time
        start_time = time.time()
        
        # Many successful operations
        for _ in range(1000):
            serialized = serializer.dumps(test_data)
            deserialized = serializer.loads(serialized)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be very fast for simple operations
        assert duration < 2.0, f"Error handling overhead too high: {duration}s"


class TestOptimizationCompatibility:
    """Test that optimizations maintain compatibility."""
    
    def test_all_original_methods_present(self):
        """Test that all original serializer methods are still present."""
        serializers = [
            XmlSerializer(),
            JsonSerializer(),
            BsonSerializer()
        ]
        
        required_methods = [
            'dumps', 'loads', 'save_file', 'load_file',
            'get_config', 'get_schema_info'
        ]
        
        for serializer in serializers:
            for method_name in required_methods:
                assert hasattr(serializer, method_name), \
                    f"{serializer.format_name} missing {method_name}"
                
                method = getattr(serializer, method_name)
                assert callable(method), \
                    f"{serializer.format_name}.{method_name} is not callable"
    
    def test_properties_preserved(self):
        """Test that all format properties are preserved."""
        serializers = [
            ('XML', XmlSerializer()),
            ('JSON', JsonSerializer()),  
            ('BSON', BsonSerializer())
        ]
        
        required_properties = [
            'format_name', 'file_extensions', 'mime_type',
            'is_binary_format', 'supports_streaming'
        ]
        
        for name, serializer in serializers:
            for prop_name in required_properties:
                assert hasattr(serializer, prop_name), \
                    f"{name} missing property {prop_name}"
                
                prop_value = getattr(serializer, prop_name)
                assert prop_value is not None, \
                    f"{name}.{prop_name} is None"
    
    def test_format_specific_features_preserved(self):
        """Test that format-specific features are preserved."""
        # Test BSON-specific methods
        bson_serializer = BsonSerializer()
        assert hasattr(bson_serializer, 'dumps_bytes')
        assert hasattr(bson_serializer, 'loads_bytes')
        
        # Test JSON-specific configuration
        json_serializer = JsonSerializer(indent=2, sort_keys=True)
        test_data = {"b": 2, "a": 1}
        result = json_serializer.dumps(test_data)
        assert isinstance(result, str)
        # Should be indented and sorted
        assert "\n" in result and '"a"' in result
        
        # Test XML-specific features
        xml_serializer = XmlSerializer()
        result = xml_serializer.dumps({"test": "value"})
        assert "<root>" in result and "</root>" in result


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
