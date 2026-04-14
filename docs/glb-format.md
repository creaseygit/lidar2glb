# GLB Output Format

## Overview

LiDAR2Mesh produces binary GLB files (glTF 2.0). Each file contains a single triangle mesh representing the terrain surface.

## Binary GLB Structure

A GLB file has three sections:

| Section | Bytes | Content |
|---|---|---|
| Header | 12 | Magic `glTF`, version `2`, total length |
| JSON chunk | Variable | glTF JSON with scene/node/mesh/accessor definitions |
| Binary chunk | Variable | Vertex positions + triangle indices |

The binary chunk contains two buffer views packed sequentially:

```
[  vertex positions (float32 x N x 3)  |  face indices (uint32 x M x 3)  ]
```

## Coordinate System

Source GeoTIFF data (EPSG:27700, British National Grid) is transformed to glTF's right-handed Y-up system:

| Source | Direction | glTF Axis |
|---|---|---|
| X (easting) | East | X |
| Z (elevation) | Up | Y |
| Y (northing) | North | -Z (negated) |

A local origin shift is applied before the transform: the minimum easting and northing are subtracted so the mesh sits near the origin. The original offsets are recorded in the metadata.

Scale: **1 glTF unit = 1 metre**.

## Vertex Format

| Attribute | Accessor type | Component type | Description |
|---|---|---|---|
| `POSITION` | `VEC3` | `FLOAT` (5126) | X, Y, Z in metres |

No normals, UVs, or vertex colours are included. Normals can be recomputed in the target application.

## Index Format

| Accessor type | Component type | Description |
|---|---|---|
| `SCALAR` | `UNSIGNED_INT` (5125) | Triangle vertex indices |

Faces are `TRIANGLES` mode (mode 4). Each group of three indices defines one triangle.

## Buffer Views

| Index | Target | Content |
|---|---|---|
| 0 | `ARRAY_BUFFER` (34962) | Vertex positions |
| 1 | `ELEMENT_ARRAY_BUFFER` (34963) | Face indices |

## glTF Scene Structure

```
Scene 0
  Node 0 (extras: lidar2mesh metadata)
    Mesh 0
      Primitive 0 (mode: TRIANGLES)
        POSITION -> Accessor 0 -> BufferView 0
        indices  -> Accessor 1 -> BufferView 1
```

## Metadata Extras Schema

Metadata is stored on the root node under `extras.lidar2mesh`:

```json
{
  "lidar2mesh": {
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

| Field | Type | Description |
|---|---|---|
| `source_file` | string | Original .tif filename |
| `crs_epsg` | int | Source coordinate reference system (27700 = BNG) |
| `origin_easting` | float | Easting subtracted during local shift (metres) |
| `origin_northing` | float | Northing subtracted during local shift (metres) |
| `pixel_size_m` | float | Source raster pixel size in metres |
| `z_scale` | float | Elevation multiplier applied during export |
| `z_min` | float | Minimum elevation in the source tile (before Z scale) |
| `z_max` | float | Maximum elevation in the source tile (before Z scale) |

To recover real-world coordinates from vertex positions:

```
real_easting  = vertex.x + origin_easting
real_northing = -vertex.z + origin_northing
real_elevation = vertex.y / z_scale
```

## Reading Metadata in Blender

After importing the GLB in Blender, use this Python snippet in the scripting workspace to read the embedded metadata:

```python
import bpy
import json

obj = bpy.context.active_object
if obj and "lidar2mesh" in obj:
    meta = obj["lidar2mesh"]
    # meta is a dict-like IDPropertyGroup
    print(f"Source: {meta['source_file']}")
    print(f"CRS: EPSG:{meta['crs_epsg']}")
    print(f"Origin: {meta['origin_easting']}E, {meta['origin_northing']}N")
    print(f"Pixel size: {meta['pixel_size_m']}m")
    print(f"Z range: {meta['z_min']} to {meta['z_max']}")
    print(f"Z scale: {meta['z_scale']}")
else:
    print("Select an imported LiDAR2Mesh object first.")
```

You can also view the extras in the Object Properties panel under Custom Properties.
