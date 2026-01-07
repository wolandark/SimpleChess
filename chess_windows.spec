# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Windows build
# Run with: pyinstaller chess_windows.spec

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include all game assets
        ('fonts', 'fonts'),
        ('img', 'img'),
        ('sfx', 'sfx'),
        # Include Stockfish engine for Windows
        ('engine/stockfish/win', 'engine/stockfish/win'),
    ],
    hiddenimports=[
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'chess',
        'chess.engine',
        'chess.pgn',
        'tkinter',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SimpleChess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for no console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SimpleChess',
)
