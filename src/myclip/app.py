"""Main application orchestrator."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from pathlib import Path

from .clipboard import ClipboardHistory, ClipboardMonitor
from .hotkeys import HotkeyManager
from .ui import TrayIcon

LOG_PATH = Path.home() / "Library/Logs/MyClip.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def is_frozen() -> bool:
    """Check if running as a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_version() -> str:
    """Get the app version from Info.plist (bundled) or package metadata."""
    if is_frozen():
        try:
            app_path = Path(sys.executable).parent.parent
            plist_path = app_path / "Info.plist"
            if plist_path.exists():
                result = subprocess.run(
                    ["defaults", "read", str(plist_path), "CFBundleShortVersionString"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception:
            pass
    # Fallback to version module
    try:
        from .version import __version__
        return __version__
    except Exception:
        return "dev"


class App:
    """Main application class that wires all components together."""

    def __init__(self):
        self._history = ClipboardHistory()
        self._monitor = ClipboardMonitor(self._history)
        self._hotkey_manager = HotkeyManager(self._show_popup)
        self._tray: TrayIcon | None = None
        self._popup_process: subprocess.Popen | None = None
        self._popup_lock = threading.Lock()

    def run(self) -> None:
        """Run the application."""
        log.info(f"MyClip v{get_version()} starting...")

        # Start background services
        self._monitor.start()
        self._hotkey_manager.start()

        # Create and run tray icon on main thread (required for macOS)
        self._tray = TrayIcon(
            on_show_history=self._show_popup,
            on_quit=self._quit,
            version=get_version(),
        )

        # This blocks - runs the macOS event loop
        self._tray.run()

    def _show_popup(self) -> None:
        """Show the popup window in a subprocess to avoid GUI conflicts."""
        with self._popup_lock:
            # Skip if popup is already running
            if self._popup_process is not None and self._popup_process.poll() is None:
                return
            # Launch popup in background thread
            thread = threading.Thread(target=self._launch_popup_process, daemon=True)
            thread.start()

    def _launch_popup_process(self) -> None:
        """Launch the popup window as a subprocess."""
        with self._popup_lock:
            if is_frozen():
                # Running as PyInstaller bundle - call self with --popup flag
                self._popup_process = subprocess.Popen(
                    [sys.executable, "--popup"],
                    env={**os.environ, "MYCLIP_POPUP": "1"},
                )
            else:
                # Running in development - use python -m
                self._popup_process = subprocess.Popen(
                    [sys.executable, "-m", "myclip.ui.popup_runner"]
                )
        self._popup_process.wait()

    def _quit(self) -> None:
        """Quit the application."""
        self._hotkey_manager.stop()
        self._monitor.stop()
