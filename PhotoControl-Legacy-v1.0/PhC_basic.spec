# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['azymuth10.9.py'],  # Головний файл програми
    pathex=[],
    binaries=[],
    datas=[('netaz.ico', '.')],  # Додаткові файли
    hiddenimports=[
        'sip', 
        'PIL._tkinter_finder',
        'PyQt5.QtPrintSupport',
        # Додаємо всі модулі python-docx
        'docx',
        'docx.shared',
        'docx.enum.text',
        'docx.enum.table', 
        'docx.enum.section',
        'docx.enum.style',
        'docx.oxml.shared',
        'docx.oxml.ns',
        'docx.oxml',
        'docx.oxml.parser',
        'docx.document',
        'docx.parts.document',
        'docx.parts.numbering',
        'docx.parts.settings',
        'docx.parts.styles',
        'docx.text.paragraph',
        'docx.text.run',
        'docx.table',
        'docx.section',
        'docx.styles.style',
        'docx.styles.styles',
        # Залежності docx
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'typing_extensions'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],  # Виключаємо tkinter для зменшення розміру
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PhControl 1.10.9',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консолі
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='netaz.ico'  # Іконка
)