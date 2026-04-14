"""Scrolling log panel for pipeline messages."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import QGroupBox, QTextEdit, QVBoxLayout, QWidget


class LogPanel(QGroupBox):
    """Read-only, timestamped, auto-scrolling log display."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Log", parent)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setStyleSheet(
            "QTextEdit { font-family: Consolas, monospace; font-size: 12px; }"
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self._text_edit)

    def append(self, message: str) -> None:
        """Add a timestamped message and scroll to the bottom."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._text_edit.append(f"[{timestamp}] {message}")
        scrollbar = self._text_edit.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.maximum())

    def clear(self) -> None:
        """Remove all log entries."""
        self._text_edit.clear()
