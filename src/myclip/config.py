"""Configuration constants for MyClip.

Values are loaded from ~/.config/myclip/config.toml with fallback defaults.
"""

from . import user_config

# Clipboard monitoring
POLL_INTERVAL_SECONDS = user_config.get("clipboard", "poll_interval", 1.0)
MAX_HISTORY_ITEMS = user_config.get("clipboard", "max_history_items", 100)

# UI settings
POPUP_WIDTH = user_config.get("popup", "width", 650)
POPUP_HEIGHT = user_config.get("popup", "height", 400)
ITEM_PREVIEW_LENGTH = user_config.get("popup", "item_preview_length", 80)

# Search settings
FUZZY_SCORE_THRESHOLD = user_config.get("search", "fuzzy_score_threshold", 60)

# Hotkey settings
HOTKEY_MODIFIERS = user_config.get("hotkey", "modifiers", "cmd+ctrl")
HOTKEY_KEY = user_config.get("hotkey", "key", "p")
