# LiDAR2Mesh

Convert DEFRA LiDAR GeoTIFF tiles to 3D meshes (GLB and OBJ).

LiDAR2Mesh is a Windows desktop app that turns DEFRA LiDAR elevation data (.tif) into 3D mesh files (.glb or .obj) you can open in Blender, game engines, or any 3D viewer. No GIS software required.

*Screenshot coming soon.*

## Features

- **Single exe** -- download and run, no installation needed
- **Drag-and-drop** -- drop a .tif file onto the window to load it
- **GLB and OBJ export** -- choose your preferred mesh format
- **Accurate real-world metre scale** -- 1 unit = 1 metre
- **No GIS software needed** -- GDAL is bundled inside the app via rasterio
- **Open source** -- MIT licensed

## Quick Start

### Download

Grab the latest release from the [Releases](https://github.com/creaseygit/lidar2mesh/releases) page and run `lidar2mesh.exe`.

### Developer Setup

```bash
git clone https://github.com/creaseygit/lidar2mesh.git
cd lidar2mesh
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.main
```

Requires Python 3.11+.

## Usage

1. Drop a `.tif` file onto the drop zone (or click to browse)
2. Review the tile info (CRS, resolution, elevation range)
3. Choose export format (GLB or OBJ)
4. Adjust settings -- resolution (Full / Half / Quarter) and Z scale
5. Set the output path
6. Click **Export Mesh**

The log panel shows progress during export.

## Getting DEFRA LiDAR Data

DEFRA publishes free LiDAR survey data for England at:

**https://environment.data.gov.uk/DefraDataDownload/?Mode=survey**

Navigate the map, select a survey, and download DSM or DTM tiles as GeoTIFF. The tiles are in EPSG:27700 (British National Grid) at 0.25m, 0.5m, or 1.0m resolution.

See [docs/defra-lidar.md](docs/defra-lidar.md) for a detailed guide.

## Output Formats

### GLB

Binary glTF 2.0 file with a single triangle mesh. Coordinate system is Y-up (glTF standard), 1 unit = 1 metre. Metadata (source CRS, origin coordinates, pixel size, elevation range) is embedded in the root node's `extras.lidar2mesh` object.

See [docs/glb-format.md](docs/glb-format.md) for full format documentation.

### OBJ

Wavefront OBJ text file with vertices and triangular faces. Metadata is written as comments in the file header. Same coordinate transform as GLB.

## Building from Source

```bash
python -m PyInstaller build/lidar2mesh.spec --noconfirm
```

Outputs to `dist/lidar2mesh/`. See [docs/development.md](docs/development.md) for details.

## Running Tests

```bash
pytest tests/
```

## License

[MIT](LICENSE)

## Documentation

- [SPEC.md](SPEC.md) -- original technical specification
- [docs/architecture.md](docs/architecture.md) -- architecture overview
- [docs/glb-format.md](docs/glb-format.md) -- GLB output format
- [docs/development.md](docs/development.md) -- developer guide
- [docs/defra-lidar.md](docs/defra-lidar.md) -- guide to DEFRA LiDAR data
