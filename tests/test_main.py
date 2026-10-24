"""Tests for main entrypoint."""

from harness_utils.main import run


def test_run(sample_fixture: str) -> None:
    """Verify application entry point returns 0."""
    assert sample_fixture == "harness_active"
    assert run() == 0