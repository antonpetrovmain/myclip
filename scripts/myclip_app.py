#!/usr/bin/env python3
"""Standalone entry point for MyClip macOS application."""

import os
import sys
from pathlib import Path

# Add src to path for imports (development mode)
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def main() -> None:
    """Main entry point."""
    # Check if we should run the popup (called with --popup flag or env var)
    if "--popup" in sys.argv or os.environ.get("MYCLIP_POPUP") == "1":
        from myclip.ui.popup_runner import run_popup
        run_popup()
    else:
        from myclip.app import App
        app = App()
        app.run()


if __name__ == "__main__":
    main()
