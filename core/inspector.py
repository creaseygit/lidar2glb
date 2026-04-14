from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import rasterio


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
    point_count: int
    data_type: str


def _resolve_epsg(crs: rasterio.crs.CRS) -> tuple[int, str]:
    """Resolve CRS to an EPSG code, handling ESRI WKT variants.

    DEFRA LiDAR tiles often use ESRI WKT for OSGB 1936 / British National
    Grid instead of embedding an EPSG code directly.
    """
    epsg = crs.to_epsg()
    if epsg:
        return epsg, crs.to_string()

    # Try with a confidence threshold — rasterio/PROJ can sometimes match
    # when the default exact match fails
    epsg = crs.to_epsg(confidence_threshold=70)
    if epsg:
        return epsg, crs.to_string()

    # Fall back to WKT string matching for known DEFRA CRS variants
    wkt = crs.to_wkt().upper()
    if "OSGB" in wkt and "BRITISH_NATIONAL_GRID" in wkt:
        return 27700, "OSGB 1936 / British National Grid"

    return 0, crs.to_string() if crs else "Unknown"


def inspect(path: str) -> TileInfo:
    with rasterio.open(path) as ds:
        crs = ds.crs
        crs_epsg, crs_name = _resolve_epsg(crs)
        transform = ds.transform
        pixel_size_m = abs(transform.a)
        width_px = ds.width
        height_px = ds.height
        width_m = width_px * pixel_size_m
        height_m = height_px * pixel_size_m
        origin_easting = transform.c
        origin_northing = transform.f
        nodata = ds.nodata
        data_type = ds.dtypes[0]

        band = ds.read(1)
        if nodata is not None:
            valid = band[band != nodata]
        else:
            valid = band[~np.isnan(band)]

        if valid.size == 0:
            raise ValueError("Tile contains no valid elevation data.")

        return TileInfo(
            path=path,
            crs_epsg=crs_epsg,
            crs_name=crs_name,
            pixel_size_m=pixel_size_m,
            width_px=width_px,
            height_px=height_px,
            width_m=width_m,
            height_m=height_m,
            origin_easting=origin_easting,
            origin_northing=origin_northing,
            z_min=float(valid.min()),
            z_max=float(valid.max()),
            z_mean=float(valid.mean()),
            nodata_value=float(nodata) if nodata is not None else float("nan"),
            point_count=int(valid.size),
            data_type=data_type,
        )


def validate_defra_format(info: TileInfo) -> list[str]:
    warnings: list[str] = []

    if info.crs_epsg != 27700:
        warnings.append(
            f"CRS is EPSG:{info.crs_epsg}, expected EPSG:27700. "
            "Output scale may be incorrect."
        )

    if info.pixel_size_m not in (0.25, 0.5, 1.0):
        warnings.append(
            f"Pixel size is {info.pixel_size_m}m, expected 0.25, 0.5, or 1.0m."
        )

    if info.data_type != "float32":
        warnings.append(
            f"Data type is {info.data_type}, expected float32."
        )

    if info.point_count == 0:
        warnings.append("Tile contains no valid elevation data.")

    return warnings
