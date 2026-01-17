"""Clipboard history storage and search functionality."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from rapidfuzz import fuzz, process

from ..config import MAX_HISTORY_ITEMS, FUZZY_SCORE_THRESHOLD

# Storage location
HISTORY_FILE = Path(os.path.expanduser("~/.myclip_history.json"))


class ClipboardHistory:
    """Thread-safe clipboard history storage with fuzzy search and persistence."""

    def __init__(self, max_items: int = MAX_HISTORY_ITEMS):
        self._items: list[str] = []
        self._max_items = max_items
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Load history from disk."""
        try:
            if HISTORY_FILE.exists():
                data = json.loads(HISTORY_FILE.read_text())
                if isinstance(data, list):
                    self._items = data[: self._max_items]
        except Exception:
            self._items = []

    def _save(self) -> None:
        """Save history to disk."""
        try:
            HISTORY_FILE.write_text(json.dumps(self._items))
        except Exception:
            pass

    def add(self, text: str) -> None:
        """Add an item to history. Moves duplicates to top, trims to max size."""
        if not text or not text.strip():
            return

        with self._lock:
            # Remove duplicate if exists
            if text in self._items:
                self._items.remove(text)

            # Add to front (newest first)
            self._items.insert(0, text)

            # Trim to max size
            if len(self._items) > self._max_items:
                self._items = self._items[: self._max_items]

            self._save()

    def get_all(self) -> list[str]:
        """Get all items in history (newest first)."""
        with self._lock:
            return self._items.copy()

    def search(self, query: str) -> list[str]:
        """Search items using fuzzy matching. Returns matching items sorted by score."""
        if not query or not query.strip():
            return self.get_all()

        with self._lock:
            if not self._items:
                return []

            # Use RapidFuzz for fuzzy matching
            results = process.extract(
                query,
                self._items,
                scorer=fuzz.partial_ratio,
                limit=None,
                score_cutoff=FUZZY_SCORE_THRESHOLD,
            )

            # Return items sorted by score (highest first)
            return [item for item, score, _ in results]

    def clear(self) -> None:
        """Clear all history."""
        with self._lock:
            self._items.clear()
            self._save()

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)


def load_history_readonly() -> list[str]:
    """Load history from disk (for use in subprocess)."""
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text())
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def delete_history_item(item: str) -> bool:
    """Delete an item from history file (for use in subprocess)."""
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text())
            if isinstance(data, list) and item in data:
                data.remove(item)
                HISTORY_FILE.write_text(json.dumps(data))
                return True
    except Exception:
        pass
    return False
