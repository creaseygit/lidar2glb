"""Panel displaying GeoTIFF tile metadata."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.inspector import TileInfo, validate_defra_format


class TileInfoPanel(QGroupBox):
    """Displays metadata from a loaded GeoTIFF tile."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Tile Info", parent)

        self._file_label = QLabel("—")
        self._crs_label = QLabel("—")
        self._resolution_label = QLabel("—")
        self._tile_size_label = QLabel("—")
        self._elevation_label = QLabel("—")
        self._points_label = QLabel("—")
        self._warnings_label = QLabel("")
        self._warnings_label.setWordWrap(True)

        form = QFormLayout()
        form.addRow("File:", self._file_label)
        form.addRow("CRS:", self._crs_label)
        form.addRow("Resolution:", self._resolution_label)
        form.addRow("Tile size:", self._tile_size_label)
        form.addRow("Elevation:", self._elevation_label)
        form.addRow("Points:", self._points_label)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._warnings_label)

    def update_info(self, info: TileInfo) -> None:
        """Populate the panel with tile metadata."""
        from pathlib import Path

        self._file_label.setText(Path(info.path).name)
        self._crs_label.setText(f"EPSG:{info.crs_epsg} ({info.crs_name})")
        self._resolution_label.setText(f"{info.pixel_size_m}m")
        self._tile_size_label.setText(
            f"{info.width_m:.0f}m x {info.height_m:.0f}m "
            f"({info.width_px} x {info.height_px} px)"
        )
        self._elevation_label.setText(
            f"{info.z_min:.2f}m \u2192 {info.z_max:.2f}m "
            f"(mean {info.z_mean:.2f}m)"
        )
        self._points_label.setText(f"{info.point_count:,}")

        warnings = validate_defra_format(info)
        if warnings:
            text = "\n".join(f"\u26a0 {w}" for w in warnings)
            self._warnings_label.setText(text)
            self._warnings_label.setStyleSheet("color: #cc6600; font-weight: bold;")
        else:
            self._warnings_label.setText("")
            self._warnings_label.setStyleSheet("")

    def clear(self) -> None:
        """Reset all fields to their default state."""
        for label in (
            self._file_label,
            self._crs_label,
            self._resolution_label,
            self._tile_size_label,
            self._elevation_label,
            self._points_label,
        ):
            label.setText("\u2014")
        self._warnings_label.setText("")
        self._warnings_label.setStyleSheet("")
