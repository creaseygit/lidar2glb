# DEFRA LiDAR Data Guide

## What Is It

DEFRA (Department for Environment, Food and Rural Affairs) publishes free airborne LiDAR survey data covering large parts of England. The data captures ground elevation using laser scanning from aircraft and is available as raster tiles in GeoTIFF format.

The data is released under the Open Government Licence and is free to download and use.

## Where to Download

**DEFRA Data Download portal:**
https://environment.data.gov.uk/DefraDataDownload/?Mode=survey

1. Navigate the map to your area of interest
2. Select a survey (each survey covers a region at a specific date)
3. Choose the product type (DSM or DTM) and resolution
4. Download the tile(s) as GeoTIFF (.tif)

Tiles are typically named like `DSM_D0155333_20120402_20120416.tif` where the numbers encode the grid reference, survey start date, and survey end date.

## DSM vs DTM

| Type | Full Name | Description |
|---|---|---|
| **DSM** | Digital Surface Model | Elevation including buildings, trees, and other structures |
| **DTM** | Digital Terrain Model | Bare-earth elevation with structures removed |

- Use **DSM** if you want buildings and vegetation in your 3D mesh
- Use **DTM** if you want just the ground surface

## Expected Tile Format

LiDAR2Mesh expects tiles with these characteristics:

| Property | Value |
|---|---|
| Format | GeoTIFF (.tif) |
| CRS | EPSG:27700 (British National Grid) |
| Units | Metres |
| Data type | Float32 |
| Pixel size | 0.25m, 0.5m, or 1.0m |
| Tile size | Typically 1km x 1km (e.g. 2000x2000 px at 0.5m) |
| NoData | `-3.4028235e+38` (may vary slightly) |
| Bands | 1 (elevation) |

The app validates these properties on load and warns if something does not match.

## Available Resolutions

| Resolution | Pixel Size | Points per 1km Tile | Typical Use |
|---|---|---|---|
| High | 0.25m | 16,000,000 | Detailed urban areas |
| Medium | 0.5m | 4,000,000 | General purpose (most common) |
| Low | 1.0m | 1,000,000 | Large area overview |

Not all resolutions are available for all areas. 0.5m is the most widely available.

## Tips for Choosing Tiles

- **Start with 1.0m or 0.5m resolution**. High-resolution 0.25m tiles produce very large meshes and need significant RAM during triangulation.
- **Check the survey date**. Newer surveys generally have better quality. Multiple surveys may cover the same area at different dates.
- **Coastal and river tiles** may have large NoData regions where the laser hit water. The resulting mesh will have holes or irregular edges at these boundaries.
- **Use the Half or Quarter resolution export setting** in LiDAR2Mesh if full resolution produces a mesh that is too large for your target application.
- **Full resolution 0.5m tiles** (4M points) need approximately 2GB of RAM during triangulation. Quarter resolution reduces this significantly.
