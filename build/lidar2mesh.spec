# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for LiDAR2Mesh
# Build with: python -m PyInstaller build/lidar2mesh.spec --noconfirm
#

import os
import glob
from PyInstaller.utils.hooks import collect_all

# Collect rasterio (bundles GDAL)
rasterio_datas, rasterio_binaries, rasterio_hiddenimports = collect_all('rasterio')

# Collect PyQt6 fully — ensures Qt6 DLLs, platform plugins, etc. are bundled
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')

# Fix: also place key Qt6 DLLs directly next to the .pyd files (PyQt6/ dir)
# so Windows DLL search finds them when loading QtWidgets.pyd etc.
qt6_bin = os.path.join(
    os.sys.prefix, 'Lib', 'site-packages', 'PyQt6', 'Qt6', 'bin'
)
qt6_flat_binaries = []
for dll in glob.glob(os.path.join(qt6_bin, '*.dll')):
    qt6_flat_binaries.append((dll, 'PyQt6'))

# Remove conflicting ICU DLLs from rasterio/GDAL.
# rasterio bundles ICU 67 (versioned symbols like ucnv_open_67) which
# poisons Qt6Core.dll's ICU resolution (it expects unversioned symbols).
# Nothing in the rasterio bundle actually imports these DLLs.
_icu_blocklist = {'icuuc.dll', 'icudt67.dll', 'icuuc67.dll', 'icudt.dll'}
rasterio_binaries = [
    (src, dest) for src, dest in rasterio_binaries
    if os.path.basename(src).lower() not in _icu_blocklist
]

icon_path = os.path.join(SPECPATH, '..', 'assets', 'icon.ico')
icon_file = icon_path if os.path.isfile(icon_path) else None

a = Analysis(
    [os.path.join(SPECPATH, '..', 'app', 'main.py')],
    pathex=[os.path.join(SPECPATH, '..')],
    binaries=rasterio_binaries + pyqt6_binaries + qt6_flat_binaries,
    datas=rasterio_datas + pyqt6_datas,
    hiddenimports=[
        'numpy',
        'scipy',
        'scipy.spatial',
        'pygltflib',
        'core',
        'core.inspector',
        'core.extractor',
        'core.triangulator',
        'core.pipeline',
        'exporters',
        'exporters.glb_writer',
        'exporters.obj_writer',
    ] + rasterio_hiddenimports + pyqt6_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(SPECPATH, 'pyi_rth_qt6_dlls.py')],
    excludes=[],
    noarchive=False,
)

# Also strip ICU DLLs that PyInstaller's dependency scanner may have added
a.binaries = [b for b in a.binaries if os.path.basename(b[0]).lower() not in _icu_blocklist]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='lidar2mesh',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lidar2mesh',
)
