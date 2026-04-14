from __future__ import annotations

import numpy as np
import pytest
from pygltflib import GLTF2

from exporters.glb_writer import write_glb


def _simple_triangle():
    """Return a single-triangle mesh: 3 vertices, 1 face."""
    vertices = np.array(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]],
        dtype=np.float32,
    )
    faces = np.array([[0, 1, 2]], dtype=np.uint32)
    return vertices, faces


class TestWriteGlb:
    def test_creates_valid_glb_file(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.glb")

        write_glb(vertices, faces, out, extras={"source": "test"})

        gltf = GLTF2.load(out)
        assert gltf.asset.version == "2.0"

    def test_correct_accessor_count(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.glb")

        write_glb(vertices, faces, out, extras={})

        gltf = GLTF2.load(out)
        # 2 accessors: one for positions, one for indices
        assert len(gltf.accessors) == 2

    def test_correct_buffer_view_count(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.glb")

        write_glb(vertices, faces, out, extras={})

        gltf = GLTF2.load(out)
        # 2 buffer views: vertices and indices
        assert len(gltf.bufferViews) == 2

    def test_vertex_accessor_count_matches_input(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.glb")

        write_glb(vertices, faces, out, extras={})

        gltf = GLTF2.load(out)
        position_accessor = gltf.accessors[0]
        assert position_accessor.count == len(vertices)

    def test_index_accessor_count_matches_input(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.glb")

        write_glb(vertices, faces, out, extras={})

        gltf = GLTF2.load(out)
        index_accessor = gltf.accessors[1]
        assert index_accessor.count == faces.size  # 3 indices

    def test_extras_contain_lidar2glb_key(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.glb")
        metadata = {"crs": "EPSG:27700", "pixel_size": 1.0}

        write_glb(vertices, faces, out, extras=metadata)

        gltf = GLTF2.load(out)
        node_extras = gltf.nodes[0].extras
        assert "lidar2glb" in node_extras
        assert node_extras["lidar2glb"]["crs"] == "EPSG:27700"
        assert node_extras["lidar2glb"]["pixel_size"] == 1.0

    def test_multi_triangle_mesh(self, tmp_path):
        vertices = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0]],
            dtype=np.float32,
        )
        faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)
        out = str(tmp_path / "test.glb")

        write_glb(vertices, faces, out, extras={})

        gltf = GLTF2.load(out)
        assert gltf.accessors[0].count == 4
        assert gltf.accessors[1].count == 6  # 2 triangles * 3 indices
