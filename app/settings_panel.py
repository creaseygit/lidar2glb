"""Export settings panel with resolution, Z-scale, and output path controls."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QButtonGroup,
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

    def _browse_output(self) -> None:
        current = self._output_edit.text()
        start_dir = str(Path(current).parent) if current else ""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save GLB file",
            start_dir,
            "GLB files (*.glb);;All files (*)",
        )
        if path:
            if not path.lower().endswith(".glb"):
                path += ".glb"
            self._output_edit.setText(path)
