"""Standalone popup runner for subprocess execution."""

from __future__ import annotations

import time

import customtkinter as ctk
import pyperclip
from AppKit import NSApplicationActivateIgnoringOtherApps, NSWorkspace

from ..clipboard.history import delete_history_item, load_history_readonly, search_items
from ..config import ITEM_PREVIEW_LENGTH, POPUP_HEIGHT, POPUP_WIDTH

# UI Constants
FONT_FAMILY = "Menlo"
ITEM_ROW_HEIGHT = 20
SEARCH_HEIGHT = 28
PREVIEW_MAX_CHARS = 500
PREVIEW_MAX_LINES = 15

# Color palette for cycling through entries (light mode, dark mode)
COLOR_PALETTE = [
    ("#e8f4f8", "#1a3a4a"),  # soft blue
    ("#f0e8f8", "#2d1a4a"),  # soft purple
    ("#e8f8e8", "#1a4a2d"),  # soft green
    ("#f8f0e8", "#4a3a1a"),  # soft orange
    ("#f8e8f0", "#4a1a3a"),  # soft pink
]
SELECTED_COLOR = ("gray70", "gray30")


def truncate_text(text: str, max_len: int) -> str:
    """Truncate text for display, collapsing whitespace."""
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def format_preview(text: str) -> str:
    """Format text for preview panel, limiting length and lines."""
    preview = text[:PREVIEW_MAX_CHARS]
    if len(text) > PREVIEW_MAX_CHARS:
        preview += "..."

    lines = preview.split("\n")[:PREVIEW_MAX_LINES]
    if len(text.split("\n")) > PREVIEW_MAX_LINES:
        lines.append("...")

    return "\n".join(lines)


def run_popup() -> None:
    """Run the popup window."""
    workspace = NSWorkspace.sharedWorkspace()
    previous_app = workspace.frontmostApplication()

    recent_items = load_history_readonly()[:10]

    # Set up CustomTkinter
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()
    root.title("MyClip - Clipboard History")

    # Calculate dynamic height based on number of entries
    row_height = ITEM_ROW_HEIGHT + 2  # button height + padding
    base_height = SEARCH_HEIGHT + 35  # search + margins
    dynamic_height = min(POPUP_HEIGHT, base_height + len(recent_items) * row_height)

    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - POPUP_WIDTH) // 2
    y = (screen_height - dynamic_height) // 3
    root.geometry(f"{POPUP_WIDTH}x{dynamic_height}+{x}+{y}")
    root.attributes("-topmost", True)

    # Configure grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    # Fonts
    mono_font = ctk.CTkFont(family=FONT_FAMILY, size=12)
    search_font = ctk.CTkFont(family=FONT_FAMILY, size=14)
    delete_font = ctk.CTkFont(size=11)
    preview_font = ctk.CTkFont(family=FONT_FAMILY, size=13)

    # State
    selected_index = [0]
    item_buttons: list[ctk.CTkButton] = []
    delete_buttons: list[ctk.CTkButton] = []
    current_items: list[str] = recent_items.copy()
    preview_window: ctk.CTkToplevel | None = None
    preview_label: ctk.CTkLabel | None = None
    search_after_id: str | None = None  # For debouncing search

    # --- Preview panel functions ---

    def show_preview(text: str, button: ctk.CTkButton | None = None) -> None:
        nonlocal preview_window, preview_label

        # Create window once, reuse it
        if preview_window is None or not preview_window.winfo_exists() or preview_label is None:
            if preview_window and preview_window.winfo_exists():
                preview_window.destroy()
            preview_window = ctk.CTkToplevel(root)
            preview_window.withdraw()
            preview_window.wm_overrideredirect(True)
            preview_window.attributes("-topmost", True)

            preview_label = ctk.CTkLabel(
                preview_window,
                text="",
                font=preview_font,
                justify="left",
                anchor="nw",
                wraplength=350,
                padx=8,
                pady=6,
            )
            preview_label.pack()

        # Update content
        preview_label.configure(text=format_preview(text))

        # Position to the right of popup, aligned with selected item
        root.update_idletasks()
        popup_x = root.winfo_x()
        popup_width = root.winfo_width()
        button_y = button.winfo_rooty() if button else root.winfo_y()

        preview_window.geometry(f"+{popup_x + popup_width + 10}+{button_y}")
        preview_window.deiconify()
        preview_window.lift()

    def hide_preview() -> None:
        nonlocal preview_window, preview_label
        if preview_window:
            try:
                preview_window.destroy()
            except Exception:
                pass
            preview_window = None
            preview_label = None

    # --- UI Components ---

    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(
        root,
        textvariable=search_var,
        placeholder_text="Search clipboard history...",
        height=SEARCH_HEIGHT,
        font=search_font,
    )
    search_entry.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
    search_entry._entry.configure(insertwidth=2, insertofftime=0)  # Visible cursor

    items_frame = ctk.CTkScrollableFrame(root, corner_radius=0)
    items_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
    items_frame.grid_columnconfigure(0, weight=1)
    items_frame.grid_columnconfigure(1, weight=0)

    # --- Item management functions ---

    def update_selection_highlight() -> None:
        for i, button in enumerate(item_buttons):
            color = SELECTED_COLOR if i == selected_index[0] else COLOR_PALETTE[i % len(COLOR_PALETTE)]
            button.configure(fg_color=color)
        if 0 <= selected_index[0] < len(current_items):
            show_preview(current_items[selected_index[0]], item_buttons[selected_index[0]])

    def select_item(index: int) -> None:
        if 0 <= index < len(current_items):
            pyperclip.copy(current_items[index])
            hide_preview()
            root.quit()

    def delete_item(index: int) -> None:
        nonlocal recent_items
        if 0 <= index < len(current_items):
            item = current_items[index]
            delete_history_item(item)
            if item in recent_items:
                recent_items.remove(item)
            query = search_var.get()
            items = search_items(query, recent_items) if query.strip() else recent_items
            selected_index[0] = min(selected_index[0], max(0, len(items) - 1))
            update_items_list(items)
            search_entry.focus_set()

    def update_items_list(items: list[str]) -> None:
        nonlocal current_items
        current_items = items

        for btn in item_buttons:
            btn.destroy()
        for btn in delete_buttons:
            btn.destroy()
        item_buttons.clear()
        delete_buttons.clear()

        for i, item in enumerate(items):
            color = SELECTED_COLOR if i == selected_index[0] else COLOR_PALETTE[i % len(COLOR_PALETTE)]

            button = ctk.CTkButton(
                items_frame,
                text=truncate_text(item, ITEM_PREVIEW_LENGTH),
                anchor="w",
                font=mono_font,
                height=ITEM_ROW_HEIGHT,
                corner_radius=0,
                fg_color=color,
                hover_color=("gray75", "gray25"),
                text_color=("gray10", "gray90"),
                command=lambda idx=i: select_item(idx),
            )
            button.grid(row=i, column=0, padx=(4, 0), pady=1, sticky="ew")
            item_buttons.append(button)

            del_btn = ctk.CTkButton(
                items_frame,
                text="X",
                width=30,
                height=ITEM_ROW_HEIGHT,
                font=delete_font,
                fg_color="transparent",
                hover_color=("red", "darkred"),
                text_color=("gray50", "gray50"),
                command=lambda idx=i: delete_item(idx),
            )
            del_btn.grid(row=i, column=1, padx=2, pady=1)
            delete_buttons.append(del_btn)

        if 0 <= selected_index[0] < len(current_items):
            show_preview(current_items[selected_index[0]], item_buttons[selected_index[0]])

    # --- Event handlers ---

    def on_search_changed(*args) -> None:
        nonlocal search_after_id
        # Cancel any pending search
        if search_after_id is not None:
            root.after_cancel(search_after_id)
        # Schedule new search with small delay (debounce)
        def do_search():
            nonlocal search_after_id
            search_after_id = None
            query = search_var.get()
            items = search_items(query, recent_items) if query.strip() else recent_items
            selected_index[0] = 0
            update_items_list(items)
        search_after_id = root.after(10, do_search)

    def on_enter(event) -> None:
        select_item(selected_index[0])

    def on_escape(event) -> None:
        hide_preview()
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

    def restore_previous_app() -> None:
        if previous_app:
            time.sleep(0.1)
            previous_app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)

    def on_clear_all(event) -> str:
        search_var.set("")
        return "break"

    def on_delete_word(event) -> str:
        # Delete from cursor to previous word boundary (Emacs: backward-kill-word)
        entry = search_entry._entry
        cursor = entry.index("insert")
        text = search_var.get()
        pos = cursor
        while pos > 0 and text[pos - 1] == " ":
            pos -= 1
        while pos > 0 and text[pos - 1] != " ":
            pos -= 1
        entry.delete(pos, cursor)
        return "break"

    def on_kill_line(event) -> str:
        # Delete from cursor to end of line (Emacs: kill-line)
        entry = search_entry._entry
        entry.delete("insert", "end")
        return "break"

    def on_kill_line_backward(event) -> str:
        # Delete from cursor to beginning of line (Emacs: backward-kill-line)
        entry = search_entry._entry
        entry.delete(0, "insert")
        return "break"

    def on_move_beginning(event) -> str:
        # Move to beginning of line (Emacs: move-beginning-of-line)
        search_entry._entry.icursor(0)
        return "break"

    def on_move_end(event) -> str:
        # Move to end of line (Emacs: move-end-of-line)
        search_entry._entry.icursor("end")
        return "break"

    def on_delete_char(event) -> str:
        # Delete character forward (Emacs: delete-char)
        search_entry._entry.delete("insert")
        return "break"

    # Bind events
    search_var.trace_add("write", on_search_changed)
    search_entry.bind("<Return>", on_enter)
    search_entry.bind("<Escape>", on_escape)
    search_entry.bind("<Up>", on_arrow_up)
    search_entry.bind("<Down>", on_arrow_down)
    # macOS shortcuts
    search_entry.bind("<Command-BackSpace>", on_clear_all)
    search_entry.bind("<Option-BackSpace>", on_delete_word)
    # Emacs bindings
    search_entry.bind("<Control-w>", on_delete_word)
    search_entry.bind("<Control-u>", on_kill_line_backward)
    search_entry.bind("<Control-k>", on_kill_line)
    search_entry.bind("<Control-a>", on_move_beginning)
    search_entry.bind("<Control-e>", on_move_end)
    search_entry.bind("<Control-d>", on_delete_char)
    search_entry.bind("<Control-p>", on_arrow_up)
    search_entry.bind("<Control-n>", on_arrow_down)
    root.bind("<Escape>", on_escape)
    root.protocol("WM_DELETE_WINDOW", root.quit)

    # Populate items before showing window
    update_items_list(recent_items)
    root.update_idletasks()

    # Show window and preview together
    root.deiconify()
    root.lift()
    root.focus_force()
    search_entry.focus_set()

    # Run event loop
    root.mainloop()
    root.destroy()
    restore_previous_app()


if __name__ == "__main__":
    run_popup()
