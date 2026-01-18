# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -e .                          # Install in development mode
myclip                                    # Run the app
python -m pytest tests/                   # Run tests
python -m myclip.ui.popup_runner          # Run popup directly (for UI testing)
pyinstaller MyClip.spec --noconfirm       # Build macOS app bundle
```

Requires macOS with Accessibility permissions (System Settings > Privacy & Security > Accessibility).

## Architecture

MyClip is a macOS menu bar clipboard manager with global hotkey support (`Cmd+Ctrl+P`).

### Component Structure

**App** (`src/myclip/app.py`) - Central orchestrator that:
- Starts ClipboardMonitor and HotkeyManager on background threads
- Runs TrayIcon on main thread (required for macOS)
- Spawns popup as subprocess to avoid GUI conflicts between rumps and customtkinter

**ClipboardMonitor** (`src/myclip/clipboard/monitor.py`) - Background thread polling clipboard every second via pyperclip

**ClipboardHistory** (`src/myclip/clipboard/history.py`) - Thread-safe storage with:
- Persistence to `~/.myclip_history.json`
- Fuzzy search via rapidfuzz
- Standalone functions (`load_history_readonly`, `delete_history_item`) for subprocess access

**HotkeyManager** (`src/myclip/hotkeys/manager.py`) - Uses `Quartz.CGEventTap` to intercept `Cmd+Ctrl+P` globally

**TrayIcon** (`src/myclip/ui/tray.py`) - Menu bar icon using rumps library

**PopupWindow** (`src/myclip/ui/popup_runner.py`) - CustomTkinter GUI that runs as subprocess (`python -m myclip.ui.popup_runner`), restores focus to previous app after selection

### Key Design Decisions

**Subprocess popup**: The popup runs as a separate subprocess rather than in the main process. This avoids GUI conflicts when CustomTkinter and rumps both try to manage the macOS event loop.

**Thread model**: Main thread runs the rumps event loop (TrayIcon). Background threads handle clipboard monitoring and hotkey detection via CGEventTap.

**Subprocess data access**: The popup subprocess reads history directly from `~/.myclip_history.json` using standalone functions (`load_history_readonly`, `delete_history_item`) rather than sharing state with the main process.

## Configuration

All settings in `src/myclip/config.py`: poll interval, max history items, fuzzy search threshold, popup dimensions.
