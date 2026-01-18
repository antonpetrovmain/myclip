#!/usr/bin/env python3
"""Standalone entry point for MyClip macOS application."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from myclip.app import App


def main() -> None:
    """Main entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
