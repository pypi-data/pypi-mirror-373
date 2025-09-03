"""
Test runner for xSystem config tests.
Follows xSystem testing patterns.
"""

import sys
import subprocess
from pathlib import Path

def run_config_tests():
    """Run all config tests with appropriate configuration."""
    
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    
    # Configure pytest arguments
    pytest_args = [
        str(test_dir),
        "-v",                    # Verbose output
        "--tb=short",           # Short traceback format
        "-x",                   # Stop on first failure
        "--strict-markers",     # Treat unknown markers as errors
        "-m", "xsystem_config", # Only run config-marked tests
    ]
    
    # Add coverage if available
    try:
        import coverage
        pytest_args.extend([
            "--cov=exonware.xsystem.config",
            "--cov-report=term-missing"
        ])
    except ImportError:
        pass
    
    # Run tests using subprocess to avoid import issues
    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        # pytest not installed, try to install it
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

if __name__ == "__main__":
    """Direct execution of config tests."""
    sys.exit(run_config_tests())
