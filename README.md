# MyClip

A lightweight clipboard manager for macOS that runs in the menu bar with global hotkey access to clipboard history.

## Features

- **Menu Bar App**: Runs quietly in the menu bar with a clipboard icon
- **Global Hotkey**: Press `Cmd+Ctrl+P` to instantly open clipboard history
- **Fuzzy Search**: Quickly find items with real-time fuzzy matching
- **Preview Panel**: See full content of selected item alongside the list
- **Color-Coded Entries**: Visual distinction between clipboard items
- **Keyboard Navigation**: Full support for arrow keys, Emacs bindings, and macOS shortcuts
- **Persistent History**: Saves up to 100 clipboard items across restarts
- **Focus Restoration**: Returns focus to your previous app after selection

## Requirements

- macOS
- Python 3.14+
- Accessibility permissions (for global hotkey)

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd myclip
   ```

2. Create a virtual environment and install:
   ```bash
   python3.14 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

3. Grant Accessibility permissions:
   - Open **System Settings > Privacy & Security > Accessibility**
   - Add and enable your terminal app (e.g., Terminal, iTerm2)

## Usage

### Start the app

```bash
source venv/bin/activate
myclip
```

Or use the launch script:
```bash
./run_myclip.sh
```

### Using the clipboard manager

1. Copy text as usual (`Cmd+C`)
2. Press `Cmd+Ctrl+P` to open the history popup
3. Type to search or use arrow keys to navigate
4. Press `Enter` or click to select an item
5. The selected text is copied to your clipboard and the popup closes

### Keyboard shortcuts

**Navigation:**
| Shortcut | Action |
|----------|--------|
| `↑` / `Ctrl+P` | Move up in list |
| `↓` / `Ctrl+N` | Move down in list |
| `Enter` | Select item |
| `Escape` | Close popup |

**Editing (search field):**
| Shortcut | Action |
|----------|--------|
| `Cmd+Backspace` | Clear all text |
| `Option+Backspace` | Delete word backward |
| `Ctrl+W` | Delete word backward |
| `Ctrl+U` | Delete to beginning |
| `Ctrl+K` | Delete to end |
| `Ctrl+A` | Move to beginning |
| `Ctrl+E` | Move to end |
| `Ctrl+D` | Delete character forward |

### Menu bar options

Click the clipboard icon (📋) in the menu bar to:
- **Show History**: Open the clipboard history popup
- **Quit**: Exit the application

## Auto-start on Login

To have MyClip start automatically when you log in:

1. Open **System Settings > General > Login Items**
2. Click **+** under "Open at Login"
3. Press `Cmd+Shift+G` and enter the path to `run_myclip.sh`
4. Add it

## Configuration

Settings are in `src/myclip/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `POLL_INTERVAL_SECONDS` | 1.0 | How often to check clipboard |
| `MAX_HISTORY_ITEMS` | 100 | Maximum items to store |
| `FUZZY_SCORE_THRESHOLD` | 60 | Minimum match score for search |

## Data Storage

Clipboard history is stored in `~/.myclip_history.json`.

## License

MIT
