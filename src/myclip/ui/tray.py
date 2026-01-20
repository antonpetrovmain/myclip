"""System tray icon and menu using rumps for macOS."""

from __future__ import annotations

import subprocess
from collections.abc import Callable

import rumps

from .. import user_config


class TrayIcon(rumps.App):
    """System tray icon with menu for clipboard manager."""

    def __init__(
        self,
        on_show_history: Callable[[], None],
        on_quit: Callable[[], None],
        version: str = "dev",
    ):
        super().__init__("MyClip", "📋", quit_button=None)
        self._on_show_history = on_show_history
        self._on_quit = on_quit

        # Build menu
        version_item = rumps.MenuItem(f"MyClip v{version}")
        version_item.set_callback(None)
        self.menu = [
            version_item,
            None,  # Separator
            rumps.MenuItem("Show History (Cmd+Ctrl+P)", callback=self._handle_show_history),
            rumps.MenuItem("Edit Settings...", callback=self._handle_edit_settings),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self._handle_quit),
        ]

    def _handle_show_history(self, _) -> None:
        """Handle show history menu item click."""
        self._on_show_history()

    def _handle_edit_settings(self, _) -> None:
        """Handle edit settings menu item click."""
        subprocess.run(["open", str(user_config.CONFIG_FILE)], check=False)

    def _handle_quit(self, _) -> None:
        """Handle quit menu item click."""
        self._on_quit()
        rumps.quit_application()
