# LiDAR2GLB

Convert DEFRA LiDAR GeoTIFF tiles to GLB 3D meshes.

LiDAR2GLB is a Windows desktop app that turns DEFRA LiDAR elevation data (.tif) into 3D mesh files (.glb) you can open in Blender, game engines, or any glTF viewer. No GIS software required.

*Screenshot coming soon.*

## Features

- **Single .exe** -- download and run, no installation needed
- **Drag-and-drop** -- drop a .tif file onto the window to load it
- **Accurate real-world metre scale** -- 1 glTF unit = 1 metre
- **No GIS software needed** -- GDAL is bundled inside the app via rasterio
- **Open source** -- MIT licensed

## Quick Start

### Download

Grab `lidar2glb.exe` from the [Releases](https://github.com/creaseygit/lidar2glb/releases) page and run it.

### Developer Setup

```bash
git clone https://github.com/creaseygit/lidar2glb.git
cd lidar2glb
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.main
```

Requires Python 3.11.

## Usage

1. Drop a `.tif` file onto the drop zone (or click to browse)
2. Review the tile info (CRS, resolution, elevation range)
3. Adjust export settings -- resolution (Full / Half / Quarter) and Z scale
4. Set the output path
5. Click **Export GLB**

The log panel shows progress during export.

## Getting DEFRA LiDAR Data

DEFRA publishes free LiDAR survey data for England at:

**https://environment.data.gov.uk/DefraDataDownload/?Mode=survey**

Navigate the map, select a survey, and download DSM or DTM tiles as GeoTIFF. The tiles are in EPSG:27700 (British National Grid) at 0.25m, 0.5m, or 1.0m resolution.

See [docs/defra-lidar.md](docs/defra-lidar.md) for a detailed guide.

## GLB Output

The output is a binary GLB file containing a single triangle mesh:

- **Coordinate system**: Y-up (glTF standard). Source easting maps to X, elevation to Y, negated northing to Z.
- **Scale**: 1 unit = 1 metre
- **Metadata**: embedded in the root node's `extras.lidar2glb` object, including source CRS, origin coordinates, pixel size, and elevation range

See [docs/glb-format.md](docs/glb-format.md) for full format documentation.

## Building from Source

```bash
build\build.bat
```

This runs PyInstaller and produces `dist\lidar2glb.exe`. See [docs/development.md](docs/development.md) for details.

## Running Tests

```bash
pytest tests/
```

## License

[MIT](LICENSE)

## Documentation

- [SPEC.md](SPEC.md) -- full technical specification
- [docs/architecture.md](docs/architecture.md) -- architecture overview
- [docs/glb-format.md](docs/glb-format.md) -- GLB output format
- [docs/development.md](docs/development.md) -- developer guide
- [docs/defra-lidar.md](docs/defra-lidar.md) -- guide to DEFRA LiDAR data
