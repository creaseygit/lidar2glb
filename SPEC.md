# LiDAR2GLB — Technical Specification

> A self-contained Windows desktop application that converts DEFRA LiDAR GeoTIFF tiles into GLB meshes with accurate real-world scale.

---

## Overview

LiDAR2GLB takes DEFRA LiDAR DSM/DTM GeoTIFF tiles as input and produces a `.glb` 3D mesh file suitable for use in Blender, game engines, or any GLB-compatible tool. It runs entirely offline, requires no GIS software installation, and ships as a single Windows `.exe` with all dependencies bundled.

The target user is a developer, architect, or designer who has downloaded LiDAR tiles from DEFRA and wants a 3D mesh without learning GIS tooling.

---

## Goals

- Single `.exe` — no Python, GDAL, or QGIS installation required
- Accurate scale — output mesh is in real-world metres, no reprojection
- Simple UI — drag a `.tif` in, click export, get a `.glb` out
- Open source — MIT licensed, hosted on GitHub

---

## Non-Goals (v1.0)

- Aerial/texture image draping
- Point cloud classification or filtering
- Reprojection to CRS other than the source
- Mac or Linux builds
- Web-based viewer
- Real-time 3D preview inside the app

---

## Target Input Format

DEFRA LiDAR tiles have the following known characteristics. The app should validate against these on load:

| Property | Expected value |
|---|---|
| Format | GeoTIFF (.tif) |
| CRS | EPSG:27700 (British National Grid) |
| Units | Metres |
| Data type | Float32 |
| Compression | LZW |
| Pixel size | 0.25m, 0.5m, or 1.0m |
| Tile size | Typically 2000×2000 px (1km × 1km at 0.5m) |
| NoData value | `-3.4028235e+38` |
| Band count | 1 (elevation) |
| Z range | Typically -5m to ~300m depending on region |

The app must also handle DTM variants and tiles with slightly different NoData values gracefully.

---

## Core Pipeline

```
Input .tif
    │
    ▼
1. Inspect (gdalinfo equivalent)
   - Read CRS, extent, pixel size, NoData, Z min/max
   - Validate expected format
   - Display metadata to user
    │
    ▼
2. Export point cloud (gdal_translate → XYZ)
   - Strip NoData pixels
   - Apply optional decimation (full / half / quarter resolution)
   - Output: X (easting), Y (northing), Z (elevation) in source CRS units
    │
    ▼
3. Local origin shift
   - Subtract tile min X and min Y from all coordinates
   - Keeps Z values unchanged (real elevation above sea level)
   - Record shift vector for embedding in GLB metadata
    │
    ▼
4. Triangulate (Delaunay 2.5D)
   - Triangle mesh over XY plane
   - Each vertex Z = elevation value
    │
    ▼
5. Export GLB
   - Binary GLB (not GLTF+bin)
   - Vertex positions as Float32
   - Face indices as Uint32
   - Embed metadata in GLB extras:
       origin_easting, origin_northing, crs_epsg,
       pixel_size_m, z_min, z_max, source_file
```

---

## UI Framework

Use **PyQt6** for the UI. It produces native-looking Windows applications, supports drag-and-drop well, and bundles cleanly with PyInstaller.

### Layout

Single-window application. No tabs. Sections stacked vertically:

```
┌─────────────────────────────────────────┐
│  LiDAR2GLB                    [v1.0.0]  │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Drop .tif file here            │    │
│  │  or click to browse             │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ── Tile Info ───────────────────────   │
│  File:        DSM_D0155333_...tif       │
│  CRS:         EPSG:27700 (BNG)          │
│  Resolution:  0.5m                      │
│  Tile size:   1000m × 1000m             │
│  Elevation:   -1.12m → 49.43m          │
│  Points:      4,000,000                 │
│                                         │
│  ── Export Settings ─────────────────   │
│  Resolution:  ● Full  ○ Half  ○ Quarter │
│  Z scale:     [1.0  ▲▼]                 │
│                                         │
│  Output:      [output.glb        ] [..] │
│                                         │
│  [        Export GLB        ]           │
│                                         │
│  ── Log ─────────────────────────────   │
│  > Loaded tile: DSM_D0155333...         │
│  > Exporting 4,000,000 points...        │
│  > Triangulating...                     │
│  > Writing GLB...                       │
│  > Done. output.glb (142 MB)            │
└─────────────────────────────────────────┘
```

### Behaviour

- Drag-and-drop a `.tif` onto the drop zone to load
- On load: run inspect, populate tile info panel, enable export button
- Export runs in a background thread with a progress bar
- Log panel streams messages during export
- Error states shown inline (red text in log, tile info shows warning)
- Window is resizable; log panel expands with window

---

## Settings

| Setting | Type | Default | Notes |
|---|---|---|---|
| Resolution | Radio (Full / Half / Quarter) | Full | Decimates point count 1×, 4×, or 16× |
| Z scale | Float spinner | 1.0 | Multiplies elevation values (useful for exaggeration) |
| Output path | File path | Same dir as input, `.glb` extension | User-editable |

---

## GLB Output Specification

- Format: binary GLB (single `.glb` file, no external `.bin`)
- Mesh: single `TRIANGLES` primitive
- Attributes: `POSITION` only (no normals, no UVs, no colour in v1.0)
- Position type: `VEC3`, component type `FLOAT` (32-bit)
- Index type: `SCALAR`, component type `UNSIGNED_INT` (32-bit)
- Coordinate system: right-handed, Y-up (GLTF standard)
  - Source X (easting) → GLTF X
  - Source Z (elevation) → GLTF Y
  - Source Y (northing, negated) → GLTF Z
- Scale: 1 GLTF unit = 1 metre
- Extras on the root node:

```json
{
  "lidar2glb": {
    "source_file": "DSM_D0155333_20120402_20120416.tif",
    "crs_epsg": 27700,
    "origin_easting": 527000.0,
    "origin_northing": 178000.0,
    "pixel_size_m": 0.5,
    "z_scale": 1.0,
    "z_min": -1.12,
    "z_max": 49.43
  }
}
```

---

## Tech Stack

| Component | Library | Notes |
|---|---|---|
| UI | PyQt6 | Native Windows look |
| Raster I/O | GDAL (via rasterio or direct gdal bindings) | Read GeoTIFF, inspect metadata |
| Point cloud export | gdal_translate (subprocess) or rasterio | XYZ extraction |
| Triangulation | scipy.spatial.Delaunay | 2.5D Delaunay over XY |
| GLB write | pygltflib | Binary GLB output |
| Bundling | PyInstaller | Single .exe with all deps |
| GDAL bundling | Use rasterio wheels which include GDAL | Avoids separate GDAL install |

### Why rasterio over raw GDAL subprocess?

`rasterio` ships as a self-contained wheel on Windows with GDAL bundled. This is significantly easier to bundle with PyInstaller than calling `gdal_translate` as a subprocess, which requires finding the binary at runtime.

---

## Repo Structure

```
lidar2glb/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point, QApplication setup
│   ├── main_window.py       # Main window, layout
│   ├── drop_zone.py         # Drag-and-drop widget
│   ├── tile_info_panel.py   # Metadata display
│   ├── settings_panel.py    # Resolution, Z scale, output path
│   └── log_panel.py         # Scrolling log output
├── core/
│   ├── __init__.py
│   ├── inspector.py         # Read and validate GeoTIFF metadata
│   ├── extractor.py         # Raster → XYZ point array (numpy)
│   ├── triangulator.py      # Delaunay 2.5D mesh
│   └── pipeline.py          # Orchestrates inspect → extract → triangulate
├── exporters/
│   ├── __init__.py
│   └── glb_writer.py        # numpy arrays → GLB via pygltflib
├── tests/
│   ├── test_inspector.py
│   ├── test_extractor.py
│   ├── test_triangulator.py
│   └── test_glb_writer.py
├── build/
│   ├── lidar2glb.spec       # PyInstaller spec
│   └── build.bat            # Windows build script
├── assets/
│   └── icon.ico
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── SPEC.md                  # This file
```

---

## Module Responsibilities

### `core/inspector.py`

```python
@dataclass
class TileInfo:
    path: str
    crs_epsg: int
    crs_name: str
    pixel_size_m: float
    width_px: int
    height_px: int
    width_m: float
    height_m: float
    origin_easting: float
    origin_northing: float
    z_min: float
    z_max: float
    z_mean: float
    nodata_value: float
    point_count: int          # width_px * height_px (excluding nodata)
    data_type: str

def inspect(path: str) -> TileInfo: ...
def validate_defra_format(info: TileInfo) -> list[str]: ...  # returns list of warnings
```

### `core/extractor.py`

```python
def extract_points(
    path: str,
    nodata_value: float,
    decimation: int = 1       # 1=full, 2=half, 4=quarter
) -> np.ndarray:              # shape (N, 3), columns: X, Y, Z
    ...

def apply_local_shift(
    points: np.ndarray
) -> tuple[np.ndarray, tuple[float, float]]:  # shifted points, (shift_x, shift_y)
    ...
```

### `core/triangulator.py`

```python
def triangulate_2d5(
    points: np.ndarray        # (N, 3) array
) -> tuple[np.ndarray, np.ndarray]:  # vertices (N,3), faces (M,3)
    ...
```

### `exporters/glb_writer.py`

```python
def write_glb(
    vertices: np.ndarray,     # (N, 3) float32
    faces: np.ndarray,        # (M, 3) uint32
    output_path: str,
    extras: dict              # metadata to embed
) -> None: ...
```

### `core/pipeline.py`

Runs the full pipeline in a thread, emitting Qt signals for progress and log messages.

```python
class ExportWorker(QRunnable):
    def __init__(self, path: str, settings: ExportSettings): ...
    def run(self): ...

    # Signals:
    # progress(int)         # 0-100
    # log(str)              # log message
    # finished(str)         # output path on success
    # error(str)            # error message on failure
```

---

## Error Handling

| Error condition | User-facing message |
|---|---|
| File not a GeoTIFF | "Not a valid GeoTIFF file." |
| CRS not EPSG:27700 | "Warning: CRS is {crs}, expected EPSG:27700. Output scale may be incorrect." |
| All pixels are NoData | "Tile contains no valid elevation data." |
| Triangulation fails | "Triangulation failed — tile may be too large. Try half resolution." |
| Output path not writable | "Cannot write to output path. Choose a different location." |
| Out of memory | "Not enough memory. Try half or quarter resolution." |

---

## Build & Distribution

### Development setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.main
```

### Running tests

```bash
pytest tests/
```

### Building the .exe

```bash
build\build.bat
```

This runs PyInstaller with `build/lidar2glb.spec` and produces `dist/lidar2glb.exe`.

### PyInstaller notes

- Use `--onefile` for a single exe
- rasterio requires explicit `--collect-all rasterio` and `--collect-all fiona` hooks
- Include `assets/icon.ico` via `--icon`
- Set `--name lidar2glb`
- UPX compression optional but reduces size ~30%

---

## Python & Dependency Versions

| Package | Version | Notes |
|---|---|---|
| Python | 3.11 | 3.12 has PyInstaller compatibility issues with some wheels |
| PyQt6 | >=6.6 | |
| rasterio | >=1.3 | Includes GDAL binaries |
| numpy | >=1.26 | |
| scipy | >=1.12 | For Delaunay |
| pygltflib | >=1.16 | |
| PyInstaller | >=6.0 | |

---

## Known Limitations (v1.0)

- Full resolution 0.5m tiles (4M points) require ~2GB RAM during triangulation
- No progress reporting during scipy Delaunay step (can take 30–60s for full res)
- Output GLB has no normals — shading in Blender will require recalculating normals after import
- Tiles with large NoData regions (e.g. coastal tiles) may produce a non-manifold mesh at boundaries

---

## Future Work (Post v1.0)

- Batch processing of multiple tiles with optional merge
- Normal generation in the GLB writer
- Texture draping from aerial imagery
- Preview pane (simple 2D heightmap visualisation)
- Mac/Linux builds via GitHub Actions
- DTM/DSM diff mode (subtract one from the other)
- Export to STL, OBJ in addition to GLB
