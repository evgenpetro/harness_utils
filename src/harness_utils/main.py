"""Main entry point for harness_utils package."""

import sys

from harness_utils.cli import main


def run() -> int:
    """Execute the application main entry point."""
    return main()


if __name__ == "__main__":
    sys.exit(run())
