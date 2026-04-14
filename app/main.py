"""Application entry point."""

from __future__ import annotations

import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def _setup_logging() -> Path:
    """Configure file logging next to the executable."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent

    log_dir = base / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"lidar2mesh_{datetime.now():%Y%m%d_%H%M%S}.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return log_file


def main() -> None:
    log_file = _setup_logging()
    logging.info("LiDAR2Mesh starting")
    logging.info("Python %s", sys.version)

    try:
        from PyQt6.QtWidgets import QApplication

        from app.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("LiDAR2Mesh")
        window = MainWindow()
        window.show()
        logging.info("UI launched successfully")
        sys.exit(app.exec())
    except Exception:
        logging.critical("Fatal error:\n%s", traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
