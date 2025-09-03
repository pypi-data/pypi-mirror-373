#!/usr/bin/env python3
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Simple optimization test for quick validation.
"""

import pytest
import tempfile
import os
from pathlib import Path


def test_optimized_serializers_basic():
    """Basic test that optimized serializers work."""
    # Test data
    test_data = {
        "name": "test",
        "values": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    # Test XML (text format)
    try:
        from exonware.xsystem.serialization.xml import XmlSerializer
        xml_serializer = XmlSerializer()
        
        # Basic serialization
        xml_str = xml_serializer.dumps(test_data)
        xml_loaded = xml_serializer.loads(xml_str)
        
        assert isinstance(xml_str, str)
        assert isinstance(xml_loaded, dict)
        assert not xml_serializer.is_binary_format
        
        print("✅ XML optimized serializer working")
        
    except ImportError:
        print("⚠️  XML serializer not available")
    
    # Test JSON (text format)
    try:
        from exonware.xsystem.serialization.json import JsonSerializer
        json_serializer = JsonSerializer()
        
        # Basic serialization
        json_str = json_serializer.dumps(test_data)
        json_loaded = json_serializer.loads(json_str)
        
        assert isinstance(json_str, str)
        assert json_loaded == test_data
        assert not json_serializer.is_binary_format
        
        print("✅ JSON optimized serializer working")
        
    except ImportError:
        print("⚠️  JSON serializer not available")
    
    # Test BSON (binary format)
    try:
        from exonware.xsystem.serialization.bson import BsonSerializer
        bson_serializer = BsonSerializer()
        
        # Basic serialization
        bson_str = bson_serializer.dumps(test_data)
        bson_loaded = bson_serializer.loads(bson_str)
        
        assert isinstance(bson_str, str)  # BSON returns base64 string
        assert isinstance(bson_loaded, dict)
        assert bson_serializer.is_binary_format
        
        print("✅ BSON optimized serializer working")
        
    except ImportError:
        print("⚠️  BSON serializer not available")


def test_inherited_file_operations():
    """Test that file operations are properly inherited."""
    test_data = {"test": "data"}
    
    # Test with available serializers
    serializers = []
    
    try:
        from exonware.xsystem.serialization.json import JsonSerializer
        serializers.append(("JSON", JsonSerializer(), ".json"))
    except ImportError:
        pass
    
    try:
        from exonware.xsystem.serialization.xml import XmlSerializer
        serializers.append(("XML", XmlSerializer(), ".xml"))
    except ImportError:
        pass
    
    for name, serializer, ext in serializers:
        # Create temp file
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        temp_path = Path(temp_path)
        
        try:
            # Test inherited save_file
            serializer.save_file(test_data, temp_path)
            assert temp_path.exists()
            
            # Test inherited load_file
            loaded = serializer.load_file(temp_path)
            assert isinstance(loaded, dict)
            
            print(f"✅ {name} inherited file operations working")
            
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    print("🧪 Running Simple Optimization Tests")
    print("=" * 40)
    
    test_optimized_serializers_basic()
    test_inherited_file_operations()
    
    print("\n🎉 Simple optimization tests completed!")
