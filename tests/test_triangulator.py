from __future__ import annotations

import numpy as np
import pytest

from core.triangulator import triangulate_2d5


def _make_grid(rows: int = 3, cols: int = 3) -> np.ndarray:
    """Create a regular grid of 3D points with z = row + col."""
    xs, ys = np.meshgrid(np.arange(cols, dtype=np.float64),
                         np.arange(rows, dtype=np.float64))
    zs = xs + ys
    return np.column_stack((xs.ravel(), ys.ravel(), zs.ravel()))


class TestTriangulate2d5:
    def test_output_dtypes(self):
        pts = _make_grid(3, 3)
        vertices, faces = triangulate_2d5(pts)

        assert vertices.dtype == np.float32
        assert faces.dtype == np.uint32

    def test_face_indices_in_range(self):
        pts = _make_grid(3, 3)
        vertices, faces = triangulate_2d5(pts)

        assert faces.min() >= 0
        assert faces.max() < len(vertices)

    def test_expected_triangle_count_for_grid(self):
        # A regular MxN grid triangulated by Delaunay produces
        # 2*(M-1)*(N-1) triangles.
        rows, cols = 3, 3
        pts = _make_grid(rows, cols)
        _, faces = triangulate_2d5(pts)

        expected = 2 * (rows - 1) * (cols - 1)
        assert len(faces) == expected

    def test_vertices_match_input_values(self):
        pts = _make_grid(3, 3)
        vertices, _ = triangulate_2d5(pts)

        np.testing.assert_array_almost_equal(
            vertices, pts.astype(np.float32)
        )

    def test_larger_grid(self):
        pts = _make_grid(5, 4)
        vertices, faces = triangulate_2d5(pts)

        assert len(vertices) == 20
        expected_tris = 2 * 4 * 3  # 2*(rows-1)*(cols-1)
        assert len(faces) == expected_tris
