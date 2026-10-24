"""Pytest harness configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_fixture() -> str:
    """Sample fixture for test harness initialization."""
    return "harness_active"