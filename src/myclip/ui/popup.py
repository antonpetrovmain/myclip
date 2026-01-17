"""Popup window for clipboard history search and selection."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import customtkinter as ctk
import pyperclip

if TYPE_CHECKING:
    from ..clipboard.history import ClipboardHistory

from ..config import ITEM_PREVIEW_LENGTH, POPUP_HEIGHT, POPUP_WIDTH


class PopupWindow:
    """Popup window for searching and selecting clipboard history items."""

    def __init__(self, history: ClipboardHistory):
        self._history = history
        self._lock = threading.Lock()
        self._is_showing = False

    def show_and_wait(self) -> None:
        """Show the popup window and wait for it to close. Creates its own event loop."""
        with self._lock:
            if self._is_showing:
                return
            self._is_showing = True

        try:
            self._run_popup()
        finally:
            with self._lock:
                self._is_showing = False

    def _run_popup(self) -> None:
        """Create and run the popup window with its own root."""
        # Set up CustomTkinter appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Create root window
        root = ctk.CTk()
        root.title("MyClip - Clipboard History")
        root.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}")

        # Center on screen
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - POPUP_WIDTH) // 2
        y = (screen_height - POPUP_HEIGHT) // 3  # Slightly above center
        root.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}+{x}+{y}")

        # Make it float on top
        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()

        # Configure grid
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        # State
        selected_index = [0]  # Use list for mutability in closures
        item_buttons: list[ctk.CTkButton] = []

        # Search entry
        search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            root,
            textvariable=search_var,
            placeholder_text="Search clipboard history...",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        search_entry.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        search_entry.focus_set()

        # Scrollable frame for items
        items_frame = ctk.CTkScrollableFrame(root)
        items_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        items_frame.grid_columnconfigure(0, weight=1)

        def truncate_text(text: str) -> str:
            """Truncate text for display, handling newlines."""
            text = text.replace("\n", " ").replace("\r", " ")
            text = " ".join(text.split())
            if len(text) > ITEM_PREVIEW_LENGTH:
                return text[: ITEM_PREVIEW_LENGTH - 3] + "..."
            return text

        def update_selection_highlight() -> None:
            """Update which item is highlighted."""
            for i, button in enumerate(item_buttons):
                if i == selected_index[0]:
                    button.configure(fg_color=("gray70", "gray30"))
                else:
                    button.configure(fg_color="transparent")

        def select_item(index: int) -> None:
            """Select and copy an item to clipboard."""
            query = search_var.get()
            items = self._history.search(query)
            if 0 <= index < len(items):
                pyperclip.copy(items[index])
                root.quit()

        def update_items_list(items: list[str]) -> None:
            """Update the displayed list of items."""
            # Clear existing buttons
            for button in item_buttons:
                button.destroy()
            item_buttons.clear()

            # Create new buttons
            for i, item in enumerate(items):
                display_text = truncate_text(item)
                button = ctk.CTkButton(
                    items_frame,
                    text=display_text,
                    anchor="w",
                    font=ctk.CTkFont(family="monospace", size=12),
                    height=36,
                    fg_color="transparent" if i != selected_index[0] else ("gray70", "gray30"),
                    hover_color=("gray75", "gray25"),
                    command=lambda idx=i: select_item(idx),
                )
                button.grid(row=i, column=0, padx=2, pady=1, sticky="ew")
                item_buttons.append(button)

        def on_search_changed(*args) -> None:
            """Handle search text changes."""
            query = search_var.get()
            items = self._history.search(query)
            selected_index[0] = 0
            update_items_list(items)

        def on_enter(event) -> None:
            """Handle Enter key."""
            select_item(selected_index[0])

        def on_escape(event) -> None:
            """Handle Escape key."""
            root.quit()

        def on_arrow_up(event) -> str:
            """Handle Up arrow."""
            if selected_index[0] > 0:
                selected_index[0] -= 1
                update_selection_highlight()
            return "break"

        def on_arrow_down(event) -> str:
            """Handle Down arrow."""
            if selected_index[0] < len(item_buttons) - 1:
                selected_index[0] += 1
                update_selection_highlight()
            return "break"

        # Bind events
        search_var.trace_add("write", on_search_changed)
        search_entry.bind("<Return>", on_enter)
        search_entry.bind("<Escape>", on_escape)
        search_entry.bind("<Up>", on_arrow_up)
        search_entry.bind("<Down>", on_arrow_down)
        root.bind("<Escape>", on_escape)
        root.protocol("WM_DELETE_WINDOW", root.quit)

        # Initial population
        update_items_list(self._history.get_all())

        # Run event loop
        root.mainloop()
        root.destroy()
