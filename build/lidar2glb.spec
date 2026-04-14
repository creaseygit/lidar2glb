# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for LiDAR2GLB
# Build with: pyinstaller build/lidar2glb.spec --noconfirm
#

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all rasterio data files, binaries, and hidden imports (bundles GDAL)
rasterio_datas, rasterio_binaries, rasterio_hiddenimports = collect_all('rasterio')

# Determine icon path (use icon.ico if it exists, otherwise no icon)
icon_path = os.path.join(SPECPATH, '..', 'assets', 'icon.ico')
icon_file = icon_path if os.path.isfile(icon_path) else None

a = Analysis(
    [os.path.join(SPECPATH, '..', 'app', 'main.py')],
    pathex=[],
    binaries=rasterio_binaries,
    datas=rasterio_datas,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'numpy',
        'scipy',
        'pygltflib',
    ] + rasterio_hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lidar2glb',
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
    icon=icon_file,
)
