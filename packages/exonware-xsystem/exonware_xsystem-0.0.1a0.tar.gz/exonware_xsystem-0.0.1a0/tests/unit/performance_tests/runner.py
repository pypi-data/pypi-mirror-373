"""
Test runner for xSystem performance tests.
Follows xSystem testing patterns.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025
"""

import sys
import pytest
from pathlib import Path

def run_performance_tests():
    """Run all performance tests with appropriate configuration."""
    
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    
    # Configure pytest arguments
    pytest_args = [
        str(test_dir),
        "-v",                        # Verbose output
        "--tb=short",               # Short traceback format
        "-x",                       # Stop on first failure
        "--strict-markers",         # Treat unknown markers as errors
        "-m", "xsystem_performance", # Only run performance-marked tests
    ]
    
    # Add coverage if available
    try:
        import coverage
        pytest_args.extend([
            "--cov=exonware.xsystem.threading",
            "--cov=exonware.xsystem.performance",
            "--cov-report=term-missing"
        ])
    except ImportError:
        pass
    
    # Run tests
    exit_code = pytest.main(pytest_args)
    
    return exit_code

if __name__ == "__main__":
    """Direct execution of performance tests."""
    sys.exit(run_performance_tests())
