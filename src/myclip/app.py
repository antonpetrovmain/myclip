"""Main application orchestrator."""

from __future__ import annotations

import subprocess
import sys
import threading

from .clipboard import ClipboardHistory, ClipboardMonitor
from .hotkeys import HotkeyManager
from .ui import TrayIcon


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
        # Start background services
        self._monitor.start()
        self._hotkey_manager.start()

        # Create and run tray icon on main thread (required for macOS)
        self._tray = TrayIcon(
            on_show_history=self._show_popup,
            on_quit=self._quit,
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
            self._popup_process = subprocess.Popen(
                [sys.executable, "-m", "myclip.ui.popup_runner"]
            )
        self._popup_process.wait()

    def _quit(self) -> None:
        """Quit the application."""
        self._hotkey_manager.stop()
        self._monitor.stop()
