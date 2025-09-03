#!/usr/bin/env python3
""
Main test runner for xaction

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025

Usage:
    python tests/runner.py              # Run all tests
    python tests/runner.py --core       # Run only core tests
    python tests/runner.py --unit       # Run only unit tests
    python tests/runner.py --integration # Run only integration tests
""

import sys
import pytest
from pathlib import Path

def main():
    ""Main test runner function.""
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Parse arguments
    args = sys.argv[1:]
    
    if "--core" in args:
        # Run core tests only
        exit_code = pytest.main(["-v", "tests/core/"])
    elif "--unit" in args:
        # Run unit tests only
        exit_code = pytest.main(["-v", "tests/unit/"])
    elif "--integration" in args:
        # Run integration tests only
        exit_code = pytest.main(["-v", "tests/integration/"])
    else:
        # Run all tests
        exit_code = pytest.main(["-v", "tests/"])
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
