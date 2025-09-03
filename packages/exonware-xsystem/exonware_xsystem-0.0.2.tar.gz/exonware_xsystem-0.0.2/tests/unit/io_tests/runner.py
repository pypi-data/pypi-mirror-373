#!/usr/bin/env python3
"""
Runner script for xSystem IO tests.
"""

import sys
import subprocess
from pathlib import Path

def run_tests(verbose=True, coverage=False):
    """Run the xSystem IO tests."""
    cmd = [sys.executable, "-m", "pytest", str(Path(__file__).parent)]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov=exonware.xsystem.io", "--cov-report=term-missing"])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run xSystem IO tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    args = parser.parse_args()
    
    sys.exit(run_tests(verbose=args.verbose, coverage=args.coverage)) 