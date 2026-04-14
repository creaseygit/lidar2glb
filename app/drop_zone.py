"""Drag-and-drop widget for loading GeoTIFF files."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QLabel, QVBoxLayout, QWidget

_DROP_ZONE_STYLE = """
    QLabel {
        border: 2px dashed #888888;
        border-radius: 8px;
        padding: 24px;
        color: #666666;
        font-size: 14px;
        background-color: #f8f8f8;
    }
    QLabel:hover {
        border-color: #4a90d9;
        background-color: #eef4fb;
    }
"""

_DROP_ZONE_ACTIVE_STYLE = """
    QLabel {
        border: 2px dashed #4a90d9;
        border-radius: 8px;
        padding: 24px;
        color: #4a90d9;
        font-size: 14px;
        background-color: #dde8f5;
    }
"""


class DropZone(QWidget):
    """Widget that accepts drag-and-dropped .tif files or opens a file dialog."""

    fileSelected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)

        self._label = QLabel("Drop .tif file here\nor click to browse")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumHeight(80)
        self._label.setStyleSheet(_DROP_ZONE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

    # -- Drag events ---------------------------------------------------------

    def dragEnterEvent(self, event) -> None:  # type: ignore[override]
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".tif"):
                    event.acceptProposedAction()
                    self._label.setStyleSheet(_DROP_ZONE_ACTIVE_STYLE)
                    return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:  # type: ignore[override]
        self._label.setStyleSheet(_DROP_ZONE_STYLE)

    def dropEvent(self, event) -> None:  # type: ignore[override]
        self._label.setStyleSheet(_DROP_ZONE_STYLE)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".tif"):
                self._set_file(path)
                event.acceptProposedAction()
                return
        event.ignore()

    # -- Click to browse -----------------------------------------------------

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GeoTIFF file",
            "",
            "GeoTIFF files (*.tif *.tiff);;All files (*)",
        )
        if path:
            self._set_file(path)

    # -- Internals -----------------------------------------------------------

    def _set_file(self, path: str) -> None:
        name = Path(path).name
        self._label.setText(f"Loaded: {name}")
        self.fileSelected.emit(path)
