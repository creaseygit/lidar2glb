# CLAUDE.md -- Project Index

LiDAR2GLB is a Windows desktop application that converts DEFRA LiDAR GeoTIFF tiles (EPSG:27700) into GLB 3D mesh files. It provides a PyQt6 drag-and-drop UI, runs the conversion pipeline in a background thread, and ships as a single .exe via PyInstaller. The output GLB has accurate metre-scale geometry suitable for Blender, game engines, or any glTF viewer.

## Project Structure

```
app/                  PyQt6 UI layer
  main.py             Entry point (QApplication setup)
  main_window.py      Main window layout and signal wiring
  drop_zone.py        Drag-and-drop file input widget
  tile_info_panel.py  Displays loaded tile metadata
  settings_panel.py   Resolution, Z scale, output path controls
  log_panel.py        Scrolling log output

core/                 Processing pipeline
  inspector.py        Read and validate GeoTIFF metadata (TileInfo dataclass)
  extractor.py        Raster to XYZ numpy array, local origin shift
  triangulator.py     Delaunay 2.5D triangulation via scipy
  pipeline.py         Orchestrator (ExportWorker QRunnable with signals)

exporters/            Output format writers
  glb_writer.py       numpy arrays to binary GLB via pygltflib

build/                Build tooling
  build.bat           Windows build script
  lidar2glb.spec      PyInstaller spec file

tests/                Unit tests (pytest)
  test_inspector.py   Tests for inspector and validation
```

## Documentation Index

| File | Description |
|---|---|
| [README.md](README.md) | Project overview, quick start, usage |
| [SPEC.md](SPEC.md) | Full technical specification |
| [docs/architecture.md](docs/architecture.md) | Pipeline architecture and data flow |
| [docs/glb-format.md](docs/glb-format.md) | GLB output format and metadata schema |
| [docs/development.md](docs/development.md) | Developer setup, testing, building |
| [docs/defra-lidar.md](docs/defra-lidar.md) | Guide to DEFRA LiDAR data sources |

## Key Commands

```bash
# Run the app
python -m app.main

# Run tests
pytest tests/

# Build the .exe
build\build.bat
```

## Tech Decisions

**rasterio over raw GDAL**: rasterio ships as a self-contained wheel on Windows with GDAL bundled inside. This avoids needing a separate GDAL installation and eliminates the complexity of finding `gdal_translate` binaries at runtime when packaging with PyInstaller.

**PyQt6**: Produces native-looking Windows applications, has strong drag-and-drop support, and bundles cleanly with PyInstaller. The QThreadPool/QRunnable model provides straightforward background processing with signal-based progress reporting.

**pygltflib**: Pure Python GLB writer with no native dependencies. Allows direct construction of the glTF JSON structure and binary blob without shelling out to external tools.

## Coordinate Transform

The source data is in EPSG:27700 (British National Grid) with X = easting, Y = northing, Z = elevation. glTF uses a right-handed Y-up coordinate system. The transform applied in `core/pipeline.py` is:

```
Source X (easting)           ->  glTF X
Source Z (elevation)         ->  glTF Y  (up)
Source Y (northing, negated) ->  glTF Z
```

A local origin shift is applied first (subtract min X and min Y) so the mesh is centred near the origin. The original easting/northing offsets are stored in the GLB metadata extras so the mesh can be repositioned to real-world coordinates if needed.
