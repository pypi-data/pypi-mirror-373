"""
Pytest configuration for core tests

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: {GENERATION_DATE}
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture(scope="session")
def sample_data():
    """Sample data fixture for tests."""
    return {
        "test_data": "sample",
        "numbers": [1, 2, 3, 4, 5],
        "nested": {
            "key": "value",
            "items": ["a", "b", "c"]
        }
    }
