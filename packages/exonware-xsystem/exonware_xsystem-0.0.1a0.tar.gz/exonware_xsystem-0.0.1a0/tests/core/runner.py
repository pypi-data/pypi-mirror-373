#!/usr/bin/env python3
"""
Core test runner for xSystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025
"""

import sys
import subprocess
from pathlib import Path


def run_core_tests():
    """Run all core tests with appropriate configuration."""
    
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    
    # Configure pytest arguments
    pytest_args = [
        str(test_dir),
        "-v",                    # Verbose output
        "--tb=short",           # Short traceback format
        "-x",                   # Stop on first failure
        "--strict-markers",     # Treat unknown markers as errors
        "-m", "xsystem_core",   # Only run core-marked tests
    ]
    
    # Add coverage if available
    try:
        import coverage
        pytest_args.extend([
            "--cov=exonware.xsystem",
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
    exit_code = run_core_tests()
    sys.exit(exit_code) 