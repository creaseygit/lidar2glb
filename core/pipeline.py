"""Export pipeline orchestrator running in a background thread."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from core.extractor import apply_local_shift, extract_points
from core.inspector import TileInfo
from core.triangulator import triangulate_2d5
from exporters.glb_writer import write_glb


@dataclass
class ExportSettings:
    """Parameters controlling the export pipeline."""

    decimation: int = 1
    z_scale: float = 1.0
    output_path: str = ""


class WorkerSignals(QObject):
    """Signals emitted by :class:`ExportWorker`."""

    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


class ExportWorker(QRunnable):
    """Runs the full extract -> triangulate -> write pipeline.

    Designed to be submitted to a :class:`QThreadPool`.
    """

    def __init__(self, tile_info: TileInfo, settings: ExportSettings) -> None:
        super().__init__()
        self.tile_info = tile_info
        self.settings = settings
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self) -> None:
        try:
            self._run_pipeline()
        except Exception as exc:
            self.signals.error.emit(str(exc))

    def _run_pipeline(self) -> None:
        info = self.tile_info
        settings = self.settings

        # --- Step 1: Extract points ----------------------------------------
        self.signals.log.emit(
            f"Extracting points (decimation={settings.decimation})..."
        )
        self.signals.progress.emit(10)

        points = extract_points(
            info.path,
            nodata_value=info.nodata_value,
            decimation=settings.decimation,
        )
        self.signals.log.emit(f"Extracted {len(points):,} points.")
        self.signals.progress.emit(30)

        # --- Step 2: Apply local origin shift ------------------------------
        self.signals.log.emit("Applying local origin shift...")
        points, (shift_x, shift_y) = apply_local_shift(points)
        self.signals.progress.emit(35)

        # --- Step 3: Apply Z scale -----------------------------------------
        if settings.z_scale != 1.0:
            self.signals.log.emit(f"Applying Z scale: {settings.z_scale}x")
            points[:, 2] *= settings.z_scale

        # --- Step 4: Convert to GLTF coordinate system ----------------------
        #   Source X (easting)  -> GLTF X
        #   Source Z (elevation) -> GLTF Y
        #   Source Y (northing, negated) -> GLTF Z
        self.signals.log.emit("Converting to GLTF coordinate system...")
        gltf_points = points.copy()
        gltf_points[:, 0] = points[:, 0]   # X -> X
        gltf_points[:, 1] = points[:, 2]   # Z -> Y
        gltf_points[:, 2] = -points[:, 1]  # -Y -> Z
        self.signals.progress.emit(40)

        # --- Step 5: Triangulate -------------------------------------------
        self.signals.log.emit("Triangulating (this may take a while)...")
        vertices, faces = triangulate_2d5(gltf_points)
        self.signals.log.emit(
            f"Created mesh: {len(vertices):,} vertices, {len(faces):,} faces."
        )
        self.signals.progress.emit(80)

        # --- Step 6: Write GLB ---------------------------------------------
        output_path = settings.output_path
        self.signals.log.emit(f"Writing GLB to {output_path}...")

        extras = {
            "source_file": os.path.basename(info.path),
            "crs_epsg": info.crs_epsg,
            "origin_easting": shift_x,
            "origin_northing": shift_y,
            "pixel_size_m": info.pixel_size_m,
            "z_scale": settings.z_scale,
            "z_min": info.z_min,
            "z_max": info.z_max,
        }

        write_glb(vertices, faces, output_path, extras)
        self.signals.progress.emit(100)

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        self.signals.log.emit(
            f"Done. {os.path.basename(output_path)} ({file_size_mb:.1f} MB)"
        )
        self.signals.finished.emit(output_path)
