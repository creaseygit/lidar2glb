from __future__ import annotations

import numpy as np
import pytest

from exporters.obj_writer import write_obj


def _simple_triangle():
    vertices = np.array(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]],
        dtype=np.float32,
    )
    faces = np.array([[0, 1, 2]], dtype=np.uint32)
    return vertices, faces


class TestWriteObj:
    def test_creates_file(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.obj")

        write_obj(vertices, faces, out, extras={"source": "test"})

        assert (tmp_path / "test.obj").exists()

    def test_correct_vertex_count(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.obj")

        write_obj(vertices, faces, out, extras={})

        lines = (tmp_path / "test.obj").read_text().splitlines()
        v_lines = [l for l in lines if l.startswith("v ")]
        assert len(v_lines) == 3

    def test_correct_face_count(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.obj")

        write_obj(vertices, faces, out, extras={})

        lines = (tmp_path / "test.obj").read_text().splitlines()
        f_lines = [l for l in lines if l.startswith("f ")]
        assert len(f_lines) == 1

    def test_faces_are_one_indexed(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.obj")

        write_obj(vertices, faces, out, extras={})

        lines = (tmp_path / "test.obj").read_text().splitlines()
        f_line = [l for l in lines if l.startswith("f ")][0]
        indices = [int(x) for x in f_line.split()[1:]]
        assert indices == [1, 2, 3]

    def test_extras_in_header_comments(self, tmp_path):
        vertices, faces = _simple_triangle()
        out = str(tmp_path / "test.obj")

        write_obj(vertices, faces, out, extras={"crs": "EPSG:27700"})

        text = (tmp_path / "test.obj").read_text()
        assert "# crs: EPSG:27700" in text

    def test_multi_triangle_mesh(self, tmp_path):
        vertices = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0]],
            dtype=np.float32,
        )
        faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)
        out = str(tmp_path / "test.obj")

        write_obj(vertices, faces, out, extras={})

        lines = (tmp_path / "test.obj").read_text().splitlines()
        v_lines = [l for l in lines if l.startswith("v ")]
        f_lines = [l for l in lines if l.startswith("f ")]
        assert len(v_lines) == 4
        assert len(f_lines) == 2
