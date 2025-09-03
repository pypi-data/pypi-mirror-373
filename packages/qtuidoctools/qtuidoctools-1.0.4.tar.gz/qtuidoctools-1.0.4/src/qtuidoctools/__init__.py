#!/usr/bin/env -S uv run -s
# /// script
# dependencies = [
#   "click>=7.0",
#   "lxml>=4.4.1",
#   "PyYAML>=5.1.1",
#   "Qt.py>=1.2.1",
#   "yaplon",
# ]
# ///
# this_file: src/qtuidoctools/__init__.py
"""qtuidoctools package initializer.

Provides package metadata and public exports for the qtuidoctools tools.
The inline uv script header declares runtime dependencies used by the
package modules (CLI in ``__main__`` and helpers in ``qtui``/``qtuibuild``).

Compatible with Python 3.11+.
"""

try:
    from ._version import __version__
except ImportError:
    # Fallback for development/editable installs without build
    __version__ = "dev"

# Public modules re-exported by the package for convenience
__all__: list[str] = ["__main__", "qtui", "textutils"]
