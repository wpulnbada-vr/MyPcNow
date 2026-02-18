# -*- mode: python ; coding: utf-8 -*-
# mypcnow PyInstaller spec file

import os
import customtkinter

a = Analysis(
    ['src/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/cleaners', 'cleaners'),
        (os.path.dirname(customtkinter.__file__), 'customtkinter'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
    ],
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
    name='mypcnow',
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
    icon='assets/icon.ico',
    uac_admin=True,
    version='version_info.txt',
)
