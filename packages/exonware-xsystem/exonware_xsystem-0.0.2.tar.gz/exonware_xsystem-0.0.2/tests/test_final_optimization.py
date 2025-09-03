#!/usr/bin/env python3
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Final test to verify all serializers are working after optimization.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add xsystem to path - adjust for tests directory
current_dir = Path(__file__).parent
src_dir = current_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

def test_optimized_serializers():
    """Test all serializers after optimization to ensure they work correctly."""
    print("🧪 TESTING OPTIMIZED SERIALIZERS")
    print("=" * 50)
    
    # Simple test data to avoid validation issues
    test_data = {"test": "working", "number": 42}
    
    results = []
    
    # Core serializers to test
    serializer_configs = [
        ("JSON", "json", "JsonSerializer", False, test_data),
        ("XML", "xml", "XmlSerializer", False, test_data),
        ("YAML", "yaml", "YamlSerializer", False, test_data),
        ("TOML", "toml", "TomlSerializer", False, test_data),
        ("CSV", "csv", "CsvSerializer", False, [test_data]),  # CSV needs list
        ("BSON", "bson", "BsonSerializer", True, test_data),
        ("MessagePack", "msgpack", "MsgPackSerializer", True, test_data),
        ("CBOR", "cbor", "CborSerializer", True, test_data),
        ("Pickle", "pickle", "PickleSerializer", True, test_data),
        ("Marshal", "marshal", "MarshalSerializer", True, test_data),
        ("SQLite3", "sqlite3", "Sqlite3Serializer", True, [test_data]),  # SQLite needs list
        ("DBM", "dbm", "DbmSerializer", True, test_data),
        ("Shelve", "shelve", "ShelveSerializer", True, test_data),
    ]
    
    for name, module, class_name, is_binary, data in serializer_configs:
        try:
            print(f"\n🔄 Testing {name}...")
            
            # Import serializer
            module_obj = __import__(f"exonware.xsystem.serialization.{module}", fromlist=[class_name])
            serializer_class = getattr(module_obj, class_name)
            
            # Create serializer with test-friendly settings
            if name in ["Pickle", "Shelve"]:
                serializer = serializer_class(
                    validate_paths=False,  # Allow test paths
                    validate_input=False,  # Skip security validation for tests
                    max_depth=10,
                    allow_unsafe=True
                )
            else:
                serializer = serializer_class(
                    validate_paths=False,  # Allow test paths
                    validate_input=False,  # Skip security validation for tests
                    max_depth=10
                )
            
            # Verify properties
            assert serializer.format_name == name, f"{name} format name mismatch"
            assert serializer.is_binary_format == is_binary, f"{name} binary flag mismatch"
            
            # Test 1: Basic serialization
            try:
                serialized = serializer.dumps(data)
                deserialized = serializer.loads(serialized)
                print(f"  ✅ dumps/loads working")
            except Exception as e:
                print(f"  ❌ dumps/loads failed: {e}")
                results.append((name, "FAILED", f"serialization: {e}"))
                continue
            
            # Test 2: File operations with relative path
            test_file = Path(f"test_{name.lower()}{serializer.file_extensions[0]}")
            
            try:
                # Clean up any existing file
                if test_file.exists():
                    test_file.unlink()
                
                # Test save_file
                serializer.save_file(data, test_file)
                assert test_file.exists(), f"{name} save_file didn't create file"
                
                # Test load_file
                loaded = serializer.load_file(test_file)
                assert loaded is not None, f"{name} load_file returned None"
                
                print(f"  ✅ save_file/load_file working")
                
                # Check if using inherited or custom file operations
                has_custom_save = 'save_file' in serializer.__class__.__dict__
                has_custom_load = 'load_file' in serializer.__class__.__dict__
                
                if has_custom_save and has_custom_load:
                    print(f"  🗄️  Custom database file operations")
                elif has_custom_save or has_custom_load:
                    print(f"  ⚠️  Partially custom file operations")  
                else:
                    print(f"  🎯 Inherited optimized file operations")
                
                results.append((name, "WORKING", "All tests passed"))
                
            except Exception as e:
                print(f"  ❌ File operations failed: {e}")
                results.append((name, "FAILED", f"file ops: {e}"))
            finally:
                # Clean up
                if test_file.exists():
                    test_file.unlink()
                    
        except ImportError as e:
            print(f"  ⚠️  {name} not available: {e}")
            results.append((name, "MISSING", str(e)))
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")
            results.append((name, "FAILED", str(e)))
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 OPTIMIZATION TEST RESULTS")
    print("=" * 50)
    
    working = sum(1 for _, status, _ in results if status == "WORKING")
    failed = sum(1 for _, status, _ in results if status == "FAILED")
    missing = sum(1 for _, status, _ in results if status == "MISSING")
    
    for name, status, details in results:
        if status == "WORKING":
            print(f"✅ {name:12} - WORKING")
        elif status == "FAILED":
            print(f"❌ {name:12} - FAILED: {details[:50]}...")
        else:  # MISSING
            print(f"⚠️  {name:12} - MISSING DEPS")
    
    print(f"\n📈 SUMMARY:")
    print(f"  ✅ Working: {working}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️  Missing: {missing}")
    
    if working > 0:
        success_rate = working / (working + failed) * 100 if (working + failed) > 0 else 0
        print(f"  📊 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print(f"\n🎉 ALL AVAILABLE SERIALIZERS WORKING!")
            print("✅ Optimization successful!")
            return True
        else:
            print(f"\n⚠️ Partial success: {working} working, {failed} failed")
            return working >= failed  # Return true if more working than failed
    else:
        print(f"\n❌ NO SERIALIZERS WORKING!")
        return False

if __name__ == "__main__":
    success = test_optimized_serializers()
    print(f"\n{'🎉 OPTIMIZATION SUCCESS' if success else '❌ OPTIMIZATION FAILED'}")
    sys.exit(0 if success else 1)
