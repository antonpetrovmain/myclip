"""Clipboard monitoring with polling."""

from __future__ import annotations

import threading
import time

import pyperclip

from ..config import POLL_INTERVAL_SECONDS
from .history import ClipboardHistory


class ClipboardMonitor:
    """Background thread that polls clipboard for changes."""

    def __init__(self, history: ClipboardHistory):
        self._history = history
        self._last_value: str | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start monitoring the clipboard in a background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop monitoring the clipboard."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _monitor_loop(self) -> None:
        """Main monitoring loop that polls clipboard for changes."""
        # Initialize with current clipboard content
        try:
            self._last_value = pyperclip.paste()
        except Exception:
            self._last_value = None

        while self._running:
            try:
                current_value = pyperclip.paste()

                # Check if clipboard content has changed
                if current_value and current_value != self._last_value:
                    self._history.add(current_value)
                    self._last_value = current_value

            except Exception:
                # Ignore clipboard access errors
                pass

            time.sleep(POLL_INTERVAL_SECONDS)
