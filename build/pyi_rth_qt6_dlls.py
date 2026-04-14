"""PyInstaller runtime hook: add Qt6 DLL directory to search path.

This runs before the main script, ensuring Qt6 DLLs are discoverable
when PyQt6 .pyd files try to load them.
"""

import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(sys._MEIPASS)

    qt_bin = base / "PyQt6" / "Qt6" / "bin"
    if qt_bin.is_dir():
        os.add_dll_directory(str(qt_bin))
        os.environ["PATH"] = str(qt_bin) + os.pathsep + os.environ.get("PATH", "")

    # Also ensure _internal root is searchable (VC runtime, etc.)
    os.add_dll_directory(str(base))
