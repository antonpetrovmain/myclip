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

## Installation

### Option 1: Quick Install (Recommended)

Run this command in Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/antonpetrovmain/myclip/main/install.sh | bash
```

This downloads the latest release, installs it to `/Applications`, and bypasses Gatekeeper.

After installation, grant Accessibility permissions:
- Open **System Settings > Privacy & Security > Accessibility**
- Click **+** and add **MyClip** from Applications
- Quit and relaunch MyClip for permissions to take effect

### Option 2: Manual Download

1. Download `MyClip-vX.X.X-macos-arm64.zip` from the [Releases](https://github.com/antonpetrovmain/myclip/releases) page
2. Extract and move `MyClip.app` to your Applications folder
3. Open Terminal and run:
   ```bash
   xattr -cr /Applications/MyClip.app
   ```
4. Launch MyClip from Applications
5. Grant Accessibility permissions (see Option 1)

### Option 3: Build from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/antonpetrovmain/myclip.git
   cd myclip
   ```

2. Create a virtual environment and install:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   pip install pyinstaller pillow
   ```

3. Build the app:
   ```bash
   pyinstaller MyClip.spec --noconfirm
   cp -r dist/MyClip.app /Applications/
   ```

4. Grant Accessibility permissions:
   - Open **System Settings > Privacy & Security > Accessibility**
   - Add and enable **MyClip**

### Option 3: Run from Source (Development)

```bash
source venv/bin/activate
myclip
```

## Usage

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
| `Cmd+Delete` | Delete selected entry |

**Editing (search field):**
| Shortcut | Action |
|----------|--------|
| `Option+Backspace` | Delete word backward |
| `Ctrl+W` | Delete word backward |
| `Ctrl+U` | Delete to beginning |
| `Ctrl+K` | Delete to end |
| `Ctrl+A` | Move to beginning |
| `Ctrl+E` | Move to end |
| `Ctrl+D` | Delete character forward |

### Menu bar options

Click the clipboard icon in the menu bar to:
- **Show History**: Open the clipboard history popup
- **Quit**: Exit the application

## Auto-start on Login

To have MyClip start automatically when you log in:

1. Open **System Settings > General > Login Items**
2. Click **+** under "Open at Login"
3. Navigate to **Applications** and select **MyClip**

## Configuration

Settings are in `src/myclip/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `POLL_INTERVAL_SECONDS` | 1.0 | How often to check clipboard |
| `MAX_HISTORY_ITEMS` | 100 | Maximum items to store |
| `FUZZY_SCORE_THRESHOLD` | 60 | Minimum match score for search |

## Data Storage

Clipboard history is stored in `~/.myclip_history.json`.

## Requirements

- macOS 10.15+
- Accessibility permissions (for global hotkey)

## License

MIT
