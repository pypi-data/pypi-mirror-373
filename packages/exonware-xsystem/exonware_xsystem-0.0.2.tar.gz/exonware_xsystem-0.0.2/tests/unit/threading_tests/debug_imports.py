"""
Debug script to test imports for xsystem threading utilities.
"""

import sys
from pathlib import Path

print("DEBUG: xSystem Threading Utilities Import Test")
print("=" * 50)

# Show current paths
print(f"Current working directory: {Path.cwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print()

# Navigate to the correct xsystem location - need to go to project root first
# From tests/packages/xsystem/unit/threading_tests -> project root
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
xsystem_path = project_root / "src" / "exonware" / "xsystem"
print(f"Project root: {project_root}")
print(f"xSystem path: {xsystem_path}")
print(f"xSystem path exists: {xsystem_path.exists()}")
print(f"xSystem path resolved: {xsystem_path.resolve()}")
print()

# Check threading directory
threading_path = xsystem_path / "threading"
print(f"Threading path: {threading_path}")
print(f"Threading path exists: {threading_path.exists()}")
if threading_path.exists():
    print(f"Threading directory contents: {list(threading_path.iterdir())}")
print()

# Add to sys.path
sys.path.insert(0, str(xsystem_path))
print(f"Added to sys.path: {xsystem_path}")
print(f"Current sys.path (first 3): {sys.path[:3]}")
print()

# Test individual imports
components = [
    ("threading.locks", "EnhancedRLock"),
    ("threading.safe_factory", "ThreadSafeFactory"),
    ("threading.safe_factory", "MethodGenerator"),
]

import_results = {}

for module_name, class_name in components:
    try:
        print(f"Trying to import {class_name} from {module_name}...")
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"  ✅ Successfully imported {class_name}")
        print(f"     Module: {module}")
        print(f"     Class: {cls}")
        import_results[f"{module_name}.{class_name}"] = True
    except Exception as e:
        print(f"  ❌ Failed to import {class_name}: {e}")
        import_results[f"{module_name}.{class_name}"] = False
    print()

# Summary
print("IMPORT SUMMARY:")
print("=" * 20)
for component, success in import_results.items():
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{component}: {status}")

all_success = all(import_results.values())
print(f"\nOverall status: {'✅ ALL COMPONENTS AVAILABLE' if all_success else '❌ SOME COMPONENTS MISSING'}") 