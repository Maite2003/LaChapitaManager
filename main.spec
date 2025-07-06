# -*- mode: python ; coding: utf-8 -*-

import os

project_root = os.path.abspath(os.getcwd())
a = Analysis(
    ['desktop/main.py'],        # main script path relative to project root
    pathex=[project_root],      # tell PyInstaller where to look for imports
    binaries=[],
    datas=[
        ('db/schema.sql', 'db'),
        ('assets/logo.png', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LCManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo_icon.ico',  # specify the icon for the executable
)
