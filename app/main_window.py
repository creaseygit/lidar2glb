"""Main application window."""

from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.drop_zone import DropZone
from app.log_panel import LogPanel
from app.settings_panel import SettingsPanel
from app.tile_info_panel import TileInfoPanel
from core.inspector import TileInfo, inspect, validate_defra_format
from core.pipeline import ExportSettings, ExportWorker

_VERSION = "v1.0.0"


class MainWindow(QMainWindow):
    """Single-window UI for the LiDAR2Mesh application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"LiDAR2Mesh  {_VERSION}")
        self.setMinimumSize(500, 700)

        self._tile_info: TileInfo | None = None
        self._thread_pool = QThreadPool.globalInstance()

        self._build_ui()
        self._connect_signals()
        self._set_export_enabled(False)

    # -- UI construction -----------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Title bar
        header = QHBoxLayout()
        title = QLabel("LiDAR2Mesh")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        version = QLabel(_VERSION)
        version.setStyleSheet("color: #888888;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(version)
        root.addLayout(header)

        # Drop zone
        self._drop_zone = DropZone()
        root.addWidget(self._drop_zone)

        # Tile info
        self._tile_info_panel = TileInfoPanel()
        root.addWidget(self._tile_info_panel)

        # Settings
        self._settings_panel = SettingsPanel()
        root.addWidget(self._settings_panel)

        # Export button + progress
        self._export_button = QPushButton("Export Mesh")
        self._export_button.setMinimumHeight(36)
        self._export_button.setStyleSheet(
            "QPushButton { font-size: 14px; font-weight: bold; }"
        )
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(False)

        root.addWidget(self._export_button)
        root.addWidget(self._progress_bar)

        # Log panel (expands)
        self._log_panel = LogPanel()
        root.addWidget(self._log_panel, stretch=1)

    # -- Signal wiring -------------------------------------------------------

    def _connect_signals(self) -> None:
        self._drop_zone.fileSelected.connect(self._on_file_selected)
        self._export_button.clicked.connect(self._on_export_clicked)

    # -- Slot: file loaded ---------------------------------------------------

    def _on_file_selected(self, path: str) -> None:
        self._log_panel.clear()
        self._tile_info_panel.clear()
        self._set_export_enabled(False)
        self._log_panel.append(f"Loading {Path(path).name}...")

        try:
            info = inspect(path)
        except Exception as exc:  # noqa: BLE001
            self._log_panel.append(f"Error: {exc}")
            QMessageBox.critical(self, "Load Error", str(exc))
            return

        self._tile_info = info
        self._tile_info_panel.update_info(info)

        warnings = validate_defra_format(info)
        for w in warnings:
            self._log_panel.append(f"Warning: {w}")

        # Default output path: same directory, .glb extension
        default_output = str(Path(path).with_suffix(".glb"))
        self._settings_panel.set_output_path(default_output)

        self._log_panel.append("Tile loaded successfully.")
        self._set_export_enabled(True)

    # -- Slot: export --------------------------------------------------------

    def _on_export_clicked(self) -> None:
        if self._tile_info is None:
            return

        raw_settings = self._settings_panel.get_settings()
        output_path = str(raw_settings["output_path"])

        if not output_path:
            QMessageBox.warning(
                self, "Missing Output Path", "Please set an output file path."
            )
            return

        settings = ExportSettings(
            decimation=int(raw_settings["decimation"]),
            z_scale=float(raw_settings["z_scale"]),
            output_path=output_path,
        )

        self._set_export_enabled(False)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)

        worker = ExportWorker(self._tile_info, settings)
        worker.signals.progress.connect(self._on_progress)
        worker.signals.log.connect(self._log_panel.append)
        worker.signals.finished.connect(self._on_export_finished)
        worker.signals.error.connect(self._on_export_error)

        self._thread_pool.start(worker)

    # -- Worker callbacks ----------------------------------------------------

    def _on_progress(self, value: int) -> None:
        self._progress_bar.setValue(value)

    def _on_export_finished(self, output_path: str) -> None:
        self._progress_bar.setVisible(False)
        self._set_export_enabled(True)
        self._log_panel.append(f"Export complete: {output_path}")

    def _on_export_error(self, message: str) -> None:
        self._progress_bar.setVisible(False)
        self._set_export_enabled(True)
        self._log_panel.append(f"Error: {message}")
        QMessageBox.critical(self, "Export Error", message)

    # -- Helpers -------------------------------------------------------------

    def _set_export_enabled(self, enabled: bool) -> None:
        self._export_button.setEnabled(enabled)
