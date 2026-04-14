# CLAUDE.md -- Project Index

LiDAR2Mesh is a Windows desktop application that converts DEFRA LiDAR GeoTIFF tiles (EPSG:27700) into 3D mesh files (GLB or OBJ). It provides a PyQt6 drag-and-drop UI, runs the conversion pipeline in a background thread, and ships as a distributable exe via PyInstaller. The output meshes have accurate metre-scale geometry suitable for Blender, game engines, or any 3D viewer.

## Project Structure

```
app/                  PyQt6 UI layer
  main.py             Entry point, file logging, error handling
  main_window.py      Main window layout and signal wiring
  drop_zone.py        Drag-and-drop file input widget
  tile_info_panel.py  Displays loaded tile metadata
  settings_panel.py   Format, resolution, Z scale, output path controls
  log_panel.py        Scrolling log output

core/                 Processing pipeline
  inspector.py        Read and validate GeoTIFF metadata (TileInfo dataclass)
  extractor.py        Raster to XYZ numpy array, local origin shift
  triangulator.py     Delaunay 2.5D triangulation via scipy
  pipeline.py         Orchestrator (ExportWorker QRunnable with signals)

exporters/            Output format writers
  glb_writer.py       numpy arrays to binary GLB via pygltflib
  obj_writer.py       numpy arrays to Wavefront OBJ

build/                Build tooling
  build.bat           Windows build script
  lidar2mesh.spec     PyInstaller spec (onedir, ICU exclusion, Qt6 DLL fix)
  pyi_rth_qt6_dlls.py Runtime hook: adds Qt6 DLL dir to search path

tests/                Unit tests (pytest)
```

## Documentation Index

| File | Description |
|---|---|
| [README.md](README.md) | Project overview, quick start, usage |
| [SPEC.md](SPEC.md) | Original technical specification |
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

# Build the exe (outputs to dist/lidar2mesh/)
python -m PyInstaller build/lidar2mesh.spec --noconfirm
```

## Tech Decisions

**rasterio over raw GDAL**: rasterio ships as a self-contained wheel on Windows with GDAL bundled inside. This avoids needing a separate GDAL installation and eliminates the complexity of finding `gdal_translate` binaries at runtime when packaging with PyInstaller.

**PyQt6**: Produces native-looking Windows applications, has strong drag-and-drop support, and bundles cleanly with PyInstaller. The QThreadPool/QRunnable model provides straightforward background processing with signal-based progress reporting.

**pygltflib**: Pure Python GLB writer with no native dependencies. Allows direct construction of the glTF JSON structure and binary blob without shelling out to external tools.

**OBJ writer**: Pure Python, no dependencies. Wavefront OBJ is a simple text format widely supported by 3D tools. Metadata is stored as comments in the header.

## Coordinate Transform

The source data is in EPSG:27700 (British National Grid) with X = easting, Y = northing, Z = elevation. glTF uses a right-handed Y-up coordinate system. The pipeline triangulates on the XY ground plane first, then converts to glTF/OBJ coordinates:

```
Source X (easting)           ->  X
Source Z (elevation)         ->  Y  (up)
Source Y (northing, negated) ->  Z
```

A local origin shift is applied first (subtract min X and min Y) so the mesh is centred near the origin. The original easting/northing offsets are stored in the GLB metadata extras (or OBJ header comments) so the mesh can be repositioned to real-world coordinates if needed.

## Build Gotchas

- **ICU DLL conflict**: rasterio/GDAL bundles `icuuc.dll` (ICU 67, versioned symbols) which poisons Qt6Core.dll's ICU resolution. The spec strips these — nothing in the bundle actually needs them.
- **Qt6 DLL path**: PyQt6's `.pyd` files need Qt6 DLLs next to them. The spec copies `Qt6/bin/*.dll` into `PyQt6/` alongside the `.pyd` files, and a runtime hook (`pyi_rth_qt6_dlls.py`) adds the path to the DLL search order.
- **Onedir not onefile**: The build uses `--onedir` (COLLECT) because `--onefile` has Qt DLL resolution issues in the temp extraction folder.
- **CRS detection**: DEFRA tiles use ESRI WKT instead of EPSG codes. The inspector falls back to fuzzy matching and WKT string inspection to detect EPSG:27700.
