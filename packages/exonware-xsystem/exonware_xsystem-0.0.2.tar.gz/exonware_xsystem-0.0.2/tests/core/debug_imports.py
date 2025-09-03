#!/usr/bin/env python3
"""
Debug script for xSystem imports and setup.
Helps troubleshoot import issues and verify component availability.
"""

import sys
import traceback
from pathlib import Path

def test_path_setup():
    """Test Python path setup."""
    print("=== Python Path Setup ===")
    # Navigate to project root and then to src
    src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "src")
    print(f"Source path: {src_path}")
    print(f"Path exists: {Path(src_path).exists()}")
    
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print("✅ Added src to Python path")
    else:
        print("✅ src already in Python path")
    
    return True

def test_xsystem_imports():
    """Test importing xsystem components."""
    print("\n=== xSystem Import Tests ===")
    
    try:
        # Test main xsystem import
        import exonware.xsystem
        print("✅ Main xsystem import successful")
        
        # Test version
        print(f"✅ xSystem version: {exonware.xsystem.__version__}")
        
        # Test submodule imports
        components = [
            ("exonware.xsystem.io", "IO utilities"),
            ("exonware.xsystem.security", "Security utilities"),
            ("exonware.xsystem.structures", "Structure utilities"),
            ("exonware.xsystem.patterns", "Pattern utilities"),
            ("exonware.xsystem.threading", "Threading utilities")
        ]
        
        for module_name, description in components:
            try:
                __import__(module_name)
                print(f"✅ {description}: {module_name}")
            except ImportError as e:
                print(f"❌ {description}: {module_name} - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ xSystem import failed: {e}")
        traceback.print_exc()
        return False

def test_specific_components():
    """Test specific xsystem components."""
    print("\n=== Component-Specific Tests ===")
    
    tests = [
        ("atomic_file", "exonware.xsystem.io.atomic_file", "AtomicFileWriter"),
        ("path_validator", "exonware.xsystem.security.path_validator", "PathValidator"),
        ("circular_detector", "exonware.xsystem.structures.circular_detector", "CircularReferenceDetector"),
        ("handler_factory", "exonware.xsystem.patterns.handler_factory", "GenericHandlerFactory")
    ]
    
    success_count = 0
    for name, module_path, class_name in tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {name}: {class_name} class available")
            success_count += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\n✅ {success_count}/{len(tests)} components available")
    return success_count == len(tests)

def test_examples():
    """Test examples module."""
    print("\n=== Examples Test ===")
    
    try:
        from exonware.xsystem import examples
        print("✅ Examples module available")
        
        # Test if examples has demo functions
        if hasattr(examples, 'run_atomic_file_demo'):
            print("✅ Atomic file demo available")
        if hasattr(examples, 'run_security_demo'):
            print("✅ Security demo available")
        if hasattr(examples, 'run_circular_demo'):
            print("✅ Circular detection demo available")
            
        return True
    except Exception as e:
        print(f"❌ Examples test failed: {e}")
        return False

def main():
    """Main debug function."""
    print("xSystem Import Debug Tool")
    print("=" * 50)
    
    success = True
    
    # Run all tests
    success &= test_path_setup()
    success &= test_xsystem_imports()
    success &= test_specific_components()
    success &= test_examples()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All debug checks passed!")
    else:
        print("❌ Some debug checks failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 