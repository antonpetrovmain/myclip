"""Global hotkey registration and management using CGEventTap for macOS."""

from __future__ import annotations

import threading
from collections.abc import Callable

import Quartz


class HotkeyManager:
    """Manages global hotkey registration using CGEventTap to capture and consume events."""

    # Key codes (macOS virtual key codes)
    KEY_P = 15

    # Modifier flags
    MOD_CMD = Quartz.kCGEventFlagMaskCommand
    MOD_CTRL = Quartz.kCGEventFlagMaskControl

    def __init__(self, on_hotkey: Callable[[], None]):
        self._on_hotkey = on_hotkey
        self._tap = None
        self._run_loop_source = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._hotkey_held = False  # Track if hotkey is currently held down

    def start(self) -> None:
        """Start listening for global hotkeys."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_event_tap, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop listening for global hotkeys."""
        self._running = False
        if self._tap:
            Quartz.CGEventTapEnable(self._tap, False)
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run_event_tap(self) -> None:
        """Run the event tap in a background thread."""
        # Create callback
        def callback(proxy, event_type, event, refcon):
            keycode = Quartz.CGEventGetIntegerValueField(
                event, Quartz.kCGKeyboardEventKeycode
            )
            flags = Quartz.CGEventGetFlags(event)

            # Check for Cmd+Ctrl+P
            has_cmd = bool(flags & self.MOD_CMD)
            has_ctrl = bool(flags & self.MOD_CTRL)
            is_hotkey = keycode == self.KEY_P and has_cmd and has_ctrl

            if event_type == Quartz.kCGEventKeyDown and is_hotkey:
                if not self._hotkey_held:
                    # First press - trigger callback
                    self._hotkey_held = True
                    self._on_hotkey()
                # Consume event (both initial and repeats)
                return None

            if event_type == Quartz.kCGEventKeyUp and keycode == self.KEY_P:
                # Reset held state when P is released
                self._hotkey_held = False

            return event

        # Create event tap for both keyDown and keyUp
        event_mask = (
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)
        )
        self._tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            event_mask,
            callback,
            None,
        )

        if self._tap is None:
            print("ERROR: Failed to create event tap!")
            print("Please grant Accessibility permissions:")
            print("  System Settings > Privacy & Security > Accessibility")
            print("  Add and enable your terminal app or Python")
            return

        # Create run loop source
        self._run_loop_source = Quartz.CFMachPortCreateRunLoopSource(
            None, self._tap, 0
        )

        # Add to run loop
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            self._run_loop_source,
            Quartz.kCFRunLoopCommonModes,
        )

        # Enable the tap
        Quartz.CGEventTapEnable(self._tap, True)

        # Run the loop
        while self._running:
            Quartz.CFRunLoopRunInMode(Quartz.kCFRunLoopDefaultMode, 0.5, False)
