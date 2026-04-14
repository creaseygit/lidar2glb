from __future__ import annotations

import numpy as np
from scipy.spatial import Delaunay


def triangulate_2d5(
    points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    tri = Delaunay(points[:, :2])
    vertices = points.astype(np.float32)
    faces = tri.simplices.astype(np.uint32)
    return vertices, faces
