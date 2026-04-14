# Developer Guide

## Prerequisites

- **Python 3.11+** (tested with 3.12)
- **Windows** (the app targets Windows; the core pipeline may work on other platforms but is untested)

## Dev Environment Setup

```bash
git clone https://github.com/creaseygit/lidar2glb.git
cd lidar2glb
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
```

`requirements-dev.txt` includes everything in `requirements.txt` plus `pytest` and `pyinstaller`.

## Project Structure

```
app/                  PyQt6 UI
  main.py             Entry point
  main_window.py      Window layout and export orchestration
  drop_zone.py        Drag-and-drop file input
  tile_info_panel.py  Tile metadata display
  settings_panel.py   Export settings controls
  log_panel.py        Log output widget

core/                 Processing pipeline
  inspector.py        GeoTIFF metadata reader (TileInfo)
  extractor.py        Raster to numpy XYZ array
  triangulator.py     Delaunay 2.5D mesh generation
  pipeline.py         Pipeline orchestrator (ExportWorker)

exporters/            Output writers
  glb_writer.py       Binary GLB writer via pygltflib

build/                Build tooling
  build.bat           Build script
  lidar2glb.spec      PyInstaller spec

tests/                Unit tests
```

## Running the App

```bash
python -m app.main
```

## Running Tests

```bash
pytest tests/
```

Tests use mocked rasterio datasets so no real GeoTIFF files are needed.

## Building the .exe

```bash
build\build.bat
```

Or manually:

```bash
python -m PyInstaller build/lidar2glb.spec --noconfirm
```

This outputs a folder at `dist/lidar2glb/` containing `lidar2glb.exe` and an `_internal/` directory with all dependencies.

The spec file uses `collect_all('rasterio')` and `collect_all('PyQt6')` to bundle GDAL and Qt6. It strips conflicting ICU DLLs from rasterio and copies Qt6 DLLs next to PyQt6's `.pyd` files to fix DLL resolution. A runtime hook (`build/pyi_rth_qt6_dlls.py`) adds the Qt6 bin directory to the Windows DLL search path.

Logs from the packaged exe are written to `_internal/logs/`.

## Adding New Features

### New export format

1. Create a new writer module in `exporters/` (e.g. `exporters/obj_writer.py`)
2. Implement a `write_obj(vertices, faces, output_path, extras)` function matching the same signature as `glb_writer.write_glb`
3. Call it from `core/pipeline.py` in `ExportWorker._run_pipeline()` based on the output file extension
4. Update `app/settings_panel.py` to allow selecting the format (add a dropdown or radio buttons)

### New export setting

1. Add the UI control in `app/settings_panel.py`
2. Include it in `SettingsPanel.get_settings()` return dict
3. Add the field to `ExportSettings` dataclass in `core/pipeline.py`
4. Wire it into `MainWindow._on_export_clicked()` in `app/main_window.py`
5. Use it in the pipeline step where it applies

### New pipeline step

1. Create a new module in `core/` with a function that takes numpy arrays and returns numpy arrays
2. Call it from the appropriate point in `ExportWorker._run_pipeline()` in `core/pipeline.py`
3. Add progress and log signals around the step

### New input validation

Add checks to `validate_defra_format()` in `core/inspector.py`. The function returns a list of warning strings that are displayed in the log panel.

## Dependencies

| Package | Purpose |
|---|---|
| PyQt6 | Desktop UI framework |
| rasterio | GeoTIFF reading (bundles GDAL) |
| numpy | Array operations |
| scipy | Delaunay triangulation |
| pygltflib | GLB file writing |
| pytest | Testing |
| pyinstaller | .exe packaging |
