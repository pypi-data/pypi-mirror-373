#!/usr/bin/env python3
""
Core tests runner for xentity

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025
""

import sys
import pytest
from pathlib import Path

def main():
    ""Run core tests.""
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Run core tests
    exit_code = pytest.main(["-v", "tests/core/"])
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
