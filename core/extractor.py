from __future__ import annotations

import numpy as np
import rasterio


def extract_points(
    path: str,
    nodata_value: float,
    decimation: int = 1,
) -> np.ndarray:
    with rasterio.open(path) as ds:
        band = ds.read(1)
        transform = ds.transform

    rows, cols = np.mgrid[0:band.shape[0], 0:band.shape[1]]

    if decimation > 1:
        rows = rows[::decimation, ::decimation]
        cols = cols[::decimation, ::decimation]
        band = band[::decimation, ::decimation]

    xs = transform.c + (cols + 0.5) * transform.a
    ys = transform.f + (rows + 0.5) * transform.e

    valid = band != nodata_value
    x = xs[valid].astype(np.float64)
    y = ys[valid].astype(np.float64)
    z = band[valid].astype(np.float64)

    return np.column_stack((x, y, z))


def apply_local_shift(
    points: np.ndarray,
) -> tuple[np.ndarray, tuple[float, float]]:
    shift_x = float(points[:, 0].min())
    shift_y = float(points[:, 1].min())

    shifted = points.copy()
    shifted[:, 0] -= shift_x
    shifted[:, 1] -= shift_y

    return shifted, (shift_x, shift_y)
