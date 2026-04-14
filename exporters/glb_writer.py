"""Binary GLB mesh writer using pygltflib."""

from __future__ import annotations

import struct

import numpy as np
from pygltflib import (
    FLOAT,
    SCALAR,
    TRIANGLES,
    UNSIGNED_INT,
    VEC3,
    Accessor,
    Asset,
    Buffer,
    BufferView,
    GLTF2,
    Mesh,
    Node,
    Primitive,
    Scene,
)


def write_glb(
    vertices: np.ndarray,
    faces: np.ndarray,
    output_path: str,
    extras: dict,
) -> None:
    """Write a triangle mesh to a binary GLB file.

    Args:
        vertices: (N, 3) float32 vertex positions.
        faces: (M, 3) uint32 triangle indices.
        output_path: Destination file path.
        extras: Metadata dict embedded under the root node's "lidar2mesh" key.
    """
    vertices = np.ascontiguousarray(vertices, dtype=np.float32)
    faces = np.ascontiguousarray(faces, dtype=np.uint32)

    vertex_blob = vertices.tobytes()
    index_blob = faces.flatten().tobytes()
    binary_blob = vertex_blob + index_blob

    vertex_byte_length = len(vertex_blob)
    index_byte_length = len(index_blob)
    index_byte_offset = vertex_byte_length

    v_min = vertices.min(axis=0).tolist()
    v_max = vertices.max(axis=0).tolist()

    gltf = GLTF2(
        asset=Asset(generator="LiDAR2Mesh", version="2.0"),
        scene=0,
        scenes=[Scene(nodes=[0])],
        nodes=[
            Node(
                mesh=0,
                extras={"lidar2mesh": extras},
            ),
        ],
        meshes=[
            Mesh(
                primitives=[
                    Primitive(
                        attributes={"POSITION": 0},
                        indices=1,
                        mode=TRIANGLES,
                    ),
                ],
            ),
        ],
        accessors=[
            Accessor(
                bufferView=0,
                byteOffset=0,
                componentType=FLOAT,
                count=len(vertices),
                type=VEC3,
                max=v_max,
                min=v_min,
            ),
            Accessor(
                bufferView=1,
                byteOffset=0,
                componentType=UNSIGNED_INT,
                count=faces.size,
                type=SCALAR,
                max=[int(faces.max())],
                min=[int(faces.min())],
            ),
        ],
        bufferViews=[
            BufferView(
                buffer=0,
                byteOffset=0,
                byteLength=vertex_byte_length,
                target=34962,  # ARRAY_BUFFER
            ),
            BufferView(
                buffer=0,
                byteOffset=index_byte_offset,
                byteLength=index_byte_length,
                target=34963,  # ELEMENT_ARRAY_BUFFER
            ),
        ],
        buffers=[
            Buffer(byteLength=len(binary_blob)),
        ],
    )

    gltf.set_binary_blob(binary_blob)
    gltf.save(output_path)
