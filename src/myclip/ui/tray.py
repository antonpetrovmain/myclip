"""System tray icon and menu using rumps for macOS."""

from __future__ import annotations

from collections.abc import Callable

import rumps


class TrayIcon(rumps.App):
    """System tray icon with menu for clipboard manager."""

    def __init__(
        self,
        on_show_history: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        super().__init__("MyClip", "📋", quit_button=None)
        self._on_show_history = on_show_history
        self._on_quit = on_quit

        # Build menu
        self.menu = [
            rumps.MenuItem("Show History (Cmd+Ctrl+P)", callback=self._handle_show_history),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self._handle_quit),
        ]

    def _handle_show_history(self, _) -> None:
        """Handle show history menu item click."""
        self._on_show_history()

    def _handle_quit(self, _) -> None:
        """Handle quit menu item click."""
        self._on_quit()
        rumps.quit_application()
