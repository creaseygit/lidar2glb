# Architecture Overview

## Pipeline

```
Input .tif
    |
    v
1. Inspector (core/inspector.py)
   Read CRS, extent, pixel size, NoData, Z stats
   Validate against expected DEFRA format
   Return TileInfo dataclass
    |
    v
2. Extractor (core/extractor.py)
   Read raster band, apply decimation
   Convert pixel grid to XYZ point array
   Apply local origin shift (subtract min X/Y)
    |
    v
3. Triangulator (core/triangulator.py)
   Delaunay 2.5D triangulation over XY plane
   Output: vertices (N,3) + faces (M,3)
    |
    v
4. Mesh Writer (exporters/glb_writer.py or obj_writer.py)
   Pack vertices/faces into binary GLB
   Embed metadata in node extras
    |
    v
Output .glb
```

## Module Responsibilities

### `core/` -- Processing Pipeline

| Module | Responsibility | Input | Output |
|---|---|---|---|
| `inspector.py` | Read and validate GeoTIFF metadata | File path | `TileInfo` dataclass |
| `extractor.py` | Raster to point cloud with origin shift | File path, nodata, decimation | `np.ndarray (N,3)` + shift vector |
| `triangulator.py` | Delaunay triangulation | Points `(N,3)` | Vertices `(N,3)` + faces `(M,3)` |
| `pipeline.py` | Orchestrate full pipeline in worker thread | `TileInfo` + `ExportSettings` | `.glb` file on disk |

### `exporters/` -- Output Formats

| Module | Responsibility |
|---|---|
| `glb_writer.py` | Convert numpy arrays to binary GLB via pygltflib |
| `obj_writer.py` | Convert numpy arrays to Wavefront OBJ |

### `app/` -- User Interface

| Module | Responsibility |
|---|---|
| `main.py` | Application entry point, creates `QApplication` |
| `main_window.py` | Main window layout, signal wiring, export orchestration |
| `drop_zone.py` | Drag-and-drop / click-to-browse file input |
| `tile_info_panel.py` | Display loaded tile metadata |
| `settings_panel.py` | Resolution, Z scale, output path controls |
| `log_panel.py` | Scrolling text log |

## Data Flow

### Step 1: Inspect

`inspector.inspect(path)` opens the GeoTIFF with rasterio, reads metadata from the dataset header and computes Z statistics from the band data. Returns a `TileInfo` dataclass with all metadata needed for the UI and subsequent pipeline steps.

### Step 2: Extract

`extractor.extract_points(path, nodata, decimation)` reads the raster band, builds a coordinate grid from the affine transform, filters NoData pixels, and returns an `(N, 3)` numpy array of `[easting, northing, elevation]`.

`extractor.apply_local_shift(points)` subtracts the minimum X and Y values from all points so the mesh is near the origin. Returns the shifted points and the shift vector `(shift_x, shift_y)`.

### Step 3: Triangulate

`triangulator.triangulate_2d5(points)` runs `scipy.spatial.Delaunay` on the XY ground plane (easting and northing). This must happen **before** the coordinate transform — triangulating after the Y/Z swap would connect points by elevation similarity instead of spatial proximity. Returns float32 vertices and uint32 face indices.

### Step 4: Coordinate Transform

The pipeline (in `pipeline.py`) converts from source CRS coordinates to glTF Y-up:

- X stays as X
- Z (elevation) becomes Y (up)
- Y (northing) becomes -Z

Z scale is applied before triangulation.

### Step 5: Write GLB

The pipeline selects the writer based on the output file extension. `glb_writer.write_glb()` constructs a glTF 2.0 structure with one scene, one node, one mesh, one TRIANGLES primitive, and two buffer views (positions + indices). Metadata is embedded in the node's `extras` field. `obj_writer.write_obj()` writes a plain-text Wavefront OBJ with vertices, faces, and metadata as header comments.

## Threading Model

```
UI Thread                          Worker Thread (QThreadPool)
---------                          ----------------------------
MainWindow                         ExportWorker (QRunnable)
  |                                  |
  |-- click Export -->               |
  |   create ExportWorker            |
  |   submit to QThreadPool          |
  |                                  |-- extract_points()
  |  <-- signals.log ----            |
  |  <-- signals.progress --         |-- apply_local_shift()
  |                                  |-- coordinate transform
  |  <-- signals.log ----            |-- triangulate_2d5()
  |  <-- signals.progress --         |
  |                                  |-- write_glb()
  |  <-- signals.finished --         |
  |   re-enable export button        |
```

- **UI thread**: Handles all widget events, file loading (inspect), and signal reception. The inspect step runs on the UI thread because it is fast (reads metadata only, one band scan for Z stats).
- **Worker thread**: Runs the heavy pipeline (extract, triangulate, write). Communicates back to the UI via `pyqtSignal` emissions (`progress`, `log`, `finished`, `error`).
- **Thread pool**: Uses `QThreadPool.globalInstance()`. Only one export runs at a time (export button is disabled during processing).
