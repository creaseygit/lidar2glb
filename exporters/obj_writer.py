"""Wavefront OBJ mesh writer."""

from __future__ import annotations

import numpy as np


def write_obj(
    vertices: np.ndarray,
    faces: np.ndarray,
    output_path: str,
    extras: dict,
) -> None:
    """Write a triangle mesh to a Wavefront OBJ file.

    Args:
        vertices: (N, 3) float32 vertex positions.
        faces: (M, 3) uint32 triangle indices (0-based).
        output_path: Destination file path.
        extras: Metadata dict written as comments in the file header.
    """
    with open(output_path, "w") as f:
        f.write("# LiDAR2Mesh OBJ export\n")
        for key, value in extras.items():
            f.write(f"# {key}: {value}\n")
        f.write(f"# vertices: {len(vertices)}\n")
        f.write(f"# faces: {len(faces)}\n")
        f.write("\n")

        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        f.write("\n")

        # OBJ uses 1-based indices
        for face in faces:
            f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")
