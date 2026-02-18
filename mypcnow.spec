# -*- mode: python ; coding: utf-8 -*-
# MyPcNow v1.1.0 PyInstaller spec file
# Builds a single-file Windows exe with admin privileges

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
    excludes=[
        'unittest', 'test', 'tests',
        'numpy', 'pandas', 'scipy', 'matplotlib',
        'email', 'html', 'http', 'xmlrpc', 'pydoc',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MyPcNow',
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
