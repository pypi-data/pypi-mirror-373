"""
Pytest configuration and fixtures for disk-backed list tests.
"""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"test": "data"}
