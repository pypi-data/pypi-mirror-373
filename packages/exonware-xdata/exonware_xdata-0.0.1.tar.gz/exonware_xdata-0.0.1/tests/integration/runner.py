#!/usr/bin/env python3
"""
Integration tests runner for LIBRARY_NAME

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: {GENERATION_DATE}
"""

import sys
import pytest
from pathlib import Path

def main():
    """Run integration tests."""
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Run integration tests
    exit_code = pytest.main(["-v", "tests/integration/"])
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
