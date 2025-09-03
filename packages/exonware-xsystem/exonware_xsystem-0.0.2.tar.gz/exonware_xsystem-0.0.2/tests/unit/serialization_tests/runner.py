#!/usr/bin/env python3
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Runner script for xSystem serialization tests.
"""

import sys
import subprocess
from pathlib import Path

def run_tests(verbose=True, coverage=False):
    """Run the xSystem serialization tests."""
    cmd = [sys.executable, "-m", "pytest", str(Path(__file__).parent)]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov=exonware.xsystem.serialization", "--cov-report=term-missing"])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run xSystem serialization tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    args = parser.parse_args()
    
    sys.exit(run_tests(verbose=args.verbose, coverage=args.coverage))
