#!/usr/bin/env python3
"""
Unit test runner for xSystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025
"""

import sys
import subprocess
from pathlib import Path


def run_unit_tests():
    """Run all unit tests with appropriate configuration."""
    
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    
    # Configure pytest arguments
    pytest_args = [
        str(test_dir),
        "-v",                    # Verbose output
        "--tb=short",           # Short traceback format
        "-x",                   # Stop on first failure
        "--strict-markers",     # Treat unknown markers as errors
        "-m", "xsystem_unit",   # Only run unit-marked tests
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


def run_specific_unit_tests(category: str):
    """Run specific unit test category."""
    
    test_dir = Path(__file__).parent / category
    
    if not test_dir.exists():
        print(f"Test category '{category}' not found")
        return 1
    
    pytest_args = [
        str(test_dir),
        "-v",
        "--tb=short",
        "-x",
        "--strict-markers",
        "-m", f"xsystem_{category}",
    ]
    
    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        category = sys.argv[1]
        exit_code = run_specific_unit_tests(category)
    else:
        exit_code = run_unit_tests()
    sys.exit(exit_code)
