"""Export settings panel with resolution, Z-scale, and output path controls."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class SettingsPanel(QGroupBox):
    """Controls for export resolution, Z scale, and output file path."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Export Settings", parent)

        # -- Resolution radio buttons ----------------------------------------
        self._full_radio = QRadioButton("Full")
        self._half_radio = QRadioButton("Half")
        self._quarter_radio = QRadioButton("Quarter")
        self._full_radio.setChecked(True)

        self._resolution_group = QButtonGroup(self)
        self._resolution_group.addButton(self._full_radio, 1)
        self._resolution_group.addButton(self._half_radio, 2)
        self._resolution_group.addButton(self._quarter_radio, 4)

        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        resolution_layout.addWidget(self._full_radio)
        resolution_layout.addWidget(self._half_radio)
        resolution_layout.addWidget(self._quarter_radio)
        resolution_layout.addStretch()

        # -- Format selector --------------------------------------------------
        self._format_combo = QComboBox()
        self._format_combo.addItem("GLB (.glb)", ".glb")
        self._format_combo.addItem("OBJ (.obj)", ".obj")
        self._format_combo.currentIndexChanged.connect(self._on_format_changed)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self._format_combo)
        format_layout.addStretch()

        # -- Z scale spinner --------------------------------------------------
        self._z_scale_spin = QDoubleSpinBox()
        self._z_scale_spin.setRange(0.1, 100.0)
        self._z_scale_spin.setValue(1.0)
        self._z_scale_spin.setSingleStep(0.1)
        self._z_scale_spin.setDecimals(1)

        z_scale_layout = QHBoxLayout()
        z_scale_layout.addWidget(QLabel("Z scale:"))
        z_scale_layout.addWidget(self._z_scale_spin)
        z_scale_layout.addStretch()

        # -- Output path ------------------------------------------------------
        self._output_edit = QLineEdit()
        self._output_edit.setPlaceholderText("output.glb")
        self._browse_button = QPushButton("Browse...")
        self._browse_button.clicked.connect(self._browse_output)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        output_layout.addWidget(self._output_edit, stretch=1)
        output_layout.addWidget(self._browse_button)

        # -- Assemble ---------------------------------------------------------
        layout = QVBoxLayout(self)
        layout.addLayout(resolution_layout)
        layout.addLayout(format_layout)
        layout.addLayout(z_scale_layout)
        layout.addLayout(output_layout)

    def get_settings(self) -> dict[str, int | float | str]:
        """Return current settings as a dictionary.

        Keys:
            decimation (int): 1, 2, or 4
            z_scale (float): elevation multiplier
            output_path (str): destination file path
        """
        return {
            "decimation": self._resolution_group.checkedId(),
            "z_scale": self._z_scale_spin.value(),
            "output_path": self._output_edit.text(),
        }

    def set_output_path(self, path: str) -> None:
        """Pre-fill the output path (typically derived from the input file)."""
        self._output_edit.setText(path)

    def _on_format_changed(self) -> None:
        """Update the output path extension when the format changes."""
        current = self._output_edit.text()
        if not current:
            return
        ext = self._format_combo.currentData()
        new_path = str(Path(current).with_suffix(ext))
        self._output_edit.setText(new_path)

    def _browse_output(self) -> None:
        current = self._output_edit.text()
        start_dir = str(Path(current).parent) if current else ""
        ext = self._format_combo.currentData()
        if ext == ".obj":
            filter_str = "OBJ files (*.obj);;All files (*)"
        else:
            filter_str = "GLB files (*.glb);;All files (*)"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save mesh file",
            start_dir,
            filter_str,
        )
        if path:
            if not path.lower().endswith(ext):
                path += ext
            self._output_edit.setText(path)
