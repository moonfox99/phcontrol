# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['azymuth8.py'],
    pathex=[],
    binaries=[],
    datas=[('translations.py', '.'), ('documentation.py', '.'), ('help_dialogs.py', '.'), ('image_processor.py', '.'), ('widgets.py', '.')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PIL.Image', 'PIL.ImageDraw', 'docx', 'tempfile', 'json', 'webbrowser'],
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
    name='PhControl',
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
    icon=['netaz.ico'],
)
