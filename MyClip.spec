# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for MyClip macOS application."""

import sys
from pathlib import Path

block_cipher = None

# Get the customtkinter path for data files
import customtkinter
ctk_path = Path(customtkinter.__file__).parent

a = Analysis(
    ['scripts/myclip_app.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        (str(ctk_path), 'customtkinter'),  # Include customtkinter assets
    ],
    hiddenimports=[
        'rumps',
        'pyperclip',
        'rapidfuzz',
        'rapidfuzz.fuzz',
        'rapidfuzz.process',
        'customtkinter',
        'tkinter',
        'AppKit',
        'Quartz',
        'Foundation',
        'objc',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyClip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyClip',
)

app = BUNDLE(
    coll,
    name='MyClip.app',
    icon='resources/MyClip.icns',
    bundle_identifier='com.myclip.app',
    info_plist={
        'CFBundleName': 'MyClip',
        'CFBundleDisplayName': 'MyClip',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.15',
        'LSUIElement': True,  # Menu bar app (no dock icon)
        'NSHighResolutionCapable': True,
        'NSAppleEventsUsageDescription': 'MyClip needs accessibility access for global hotkeys.',
        'NSAccessibilityUsageDescription': 'MyClip needs accessibility access to register global hotkeys.',
    },
)
