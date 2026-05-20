# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ThreatIntel Daily Windows GUI
Run: pyinstaller threatintel-daily.spec
"""

a = Analysis(
    ['threatintel_daily/gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('threatintel_daily', 'threatintel_daily'),
        ('config.example.yml', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'yaml',
        'requests',
        'sqlalchemy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['matplotlib', 'scipy', 'numpy'],
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
    name='ThreatIntel Daily',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Optional: add icon.ico file
)

# Optional: Create directory bundle
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ThreatIntel Daily',
)
