"""Standalone popup runner for subprocess execution."""

from __future__ import annotations

import time

import customtkinter as ctk
import pyperclip
from AppKit import NSApplicationActivateIgnoringOtherApps, NSWorkspace
from rapidfuzz import fuzz, process

from ..clipboard.history import delete_history_item, load_history_readonly
from ..config import FUZZY_SCORE_THRESHOLD, ITEM_PREVIEW_LENGTH, POPUP_HEIGHT, POPUP_WIDTH


def search_items(query: str, items: list[str]) -> list[str]:
    """Search items using fuzzy matching."""
    if not query or not query.strip():
        return items

    if not items:
        return []

    results = process.extract(
        query,
        items,
        scorer=fuzz.partial_ratio,
        limit=None,
        score_cutoff=FUZZY_SCORE_THRESHOLD,
    )
    return [item for item, score, _ in results]


def truncate_text(text: str, max_len: int) -> str:
    """Truncate text for display, handling newlines."""
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def run_popup() -> None:
    """Run the popup window."""
    # Save the currently active application to restore focus later
    workspace = NSWorkspace.sharedWorkspace()
    previous_app = workspace.frontmostApplication()

    # Load history from disk
    all_items = load_history_readonly()

    # Set up CustomTkinter appearance (do this once)
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    # Create root window (hidden initially to avoid position glitch)
    root = ctk.CTk()
    root.withdraw()
    root.title("MyClip - Clipboard History")

    # Calculate center position
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - POPUP_WIDTH) // 2
    y = (screen_height - POPUP_HEIGHT) // 3
    root.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}+{x}+{y}")

    # Make it float on top
    root.attributes("-topmost", True)

    # Configure grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    # Create fonts once (reuse for all buttons)
    mono_font = ctk.CTkFont(family="monospace", size=12)
    search_font = ctk.CTkFont(size=14)
    delete_font = ctk.CTkFont(size=11)

    # State
    selected_index = [0]
    item_buttons: list[ctk.CTkButton] = []
    delete_buttons: list[ctk.CTkButton] = []
    current_items: list[str] = all_items.copy()

    # Search entry
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(
        root,
        textvariable=search_var,
        placeholder_text="Search clipboard history...",
        height=40,
        font=search_font,
    )
    search_entry.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

    # Scrollable frame for items
    items_frame = ctk.CTkScrollableFrame(root)
    items_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
    items_frame.grid_columnconfigure(0, weight=1)
    items_frame.grid_columnconfigure(1, weight=0)

    def restore_previous_app() -> None:
        """Restore focus to the previously active application."""
        if previous_app:
            time.sleep(0.1)
            previous_app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)

    def update_selection_highlight() -> None:
        """Update which item is highlighted."""
        for i, button in enumerate(item_buttons):
            if i == selected_index[0]:
                button.configure(fg_color=("gray70", "gray30"))
            else:
                button.configure(fg_color="transparent")

    def select_item(index: int) -> None:
        """Select and copy an item to clipboard."""
        if 0 <= index < len(current_items):
            pyperclip.copy(current_items[index])
            root.quit()

    def delete_item(index: int) -> None:
        """Delete an item from history."""
        nonlocal all_items
        if 0 <= index < len(current_items):
            item_to_delete = current_items[index]
            delete_history_item(item_to_delete)
            if item_to_delete in all_items:
                all_items.remove(item_to_delete)
            query = search_var.get()
            items = search_items(query, all_items)
            selected_index[0] = min(selected_index[0], max(0, len(items) - 1))
            update_items_list(items)
            search_entry.focus_set()

    def update_items_list(items: list[str]) -> None:
        """Update the displayed list of items."""
        nonlocal current_items
        current_items = items

        # Clear existing buttons
        for btn in item_buttons:
            btn.destroy()
        for btn in delete_buttons:
            btn.destroy()
        item_buttons.clear()
        delete_buttons.clear()

        # Create new buttons
        for i, item in enumerate(items):
            display_text = truncate_text(item, ITEM_PREVIEW_LENGTH)

            button = ctk.CTkButton(
                items_frame,
                text=display_text,
                anchor="w",
                font=mono_font,
                height=36,
                fg_color="transparent" if i != selected_index[0] else ("gray70", "gray30"),
                hover_color=("gray75", "gray25"),
                command=lambda idx=i: select_item(idx),
            )
            button.grid(row=i, column=0, padx=(2, 0), pady=1, sticky="ew")
            item_buttons.append(button)

            del_btn = ctk.CTkButton(
                items_frame,
                text="X",
                width=30,
                height=36,
                font=delete_font,
                fg_color="transparent",
                hover_color=("red", "darkred"),
                text_color=("gray50", "gray50"),
                command=lambda idx=i: delete_item(idx),
            )
            del_btn.grid(row=i, column=1, padx=(2, 2), pady=1)
            delete_buttons.append(del_btn)

    def on_search_changed(*args) -> None:
        """Handle search text changes."""
        query = search_var.get()
        items = search_items(query, all_items)
        selected_index[0] = 0
        update_items_list(items)

    def on_enter(event) -> None:
        select_item(selected_index[0])

    def on_escape(event) -> None:
        root.quit()

    def on_arrow_up(event) -> str:
        if selected_index[0] > 0:
            selected_index[0] -= 1
            update_selection_highlight()
        return "break"

    def on_arrow_down(event) -> str:
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

    # Show window first, then populate (feels more responsive)
    root.deiconify()
    root.lift()
    root.focus_force()
    search_entry.focus_set()

    # Populate items after window is visible
    root.after(10, lambda: update_items_list(all_items))

    # Run event loop
    root.mainloop()
    root.destroy()

    # Restore focus to the previous application
    restore_previous_app()


if __name__ == "__main__":
    run_popup()
