"""
Setup script for building MyClip as a macOS application.

Usage:
    python setup_app.py py2app
"""

from setuptools import setup

APP = ["src/myclip/__main__.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "resources/MyClip.icns",
    "plist": {
        "CFBundleName": "MyClip",
        "CFBundleDisplayName": "MyClip",
        "CFBundleIdentifier": "com.myclip.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSMinimumSystemVersion": "10.15",
        "LSUIElement": True,  # Menu bar app (no dock icon)
        "NSHighResolutionCapable": True,
        "NSAppleEventsUsageDescription": "MyClip needs accessibility access for global hotkeys.",
        "NSAccessibilityUsageDescription": "MyClip needs accessibility access to register global hotkeys.",
    },
    "packages": ["myclip", "customtkinter", "rumps", "pyperclip", "rapidfuzz"],
    "includes": [
        "tkinter",
        "AppKit",
        "Quartz",
        "Foundation",
        "objc",
    ],
    "excludes": ["test", "tests", "unittest"],
    "resources": [],
}

setup(
    name="MyClip",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
