"""Python host stack for the MLX90620 thermal camera project."""

from __future__ import annotations

__version__ = "1.0.0"

FRAME_ROWS = 16
FRAME_COLS = 4
PIXEL_COUNT = FRAME_ROWS * FRAME_COLS
DEFAULT_BAUD = 9600
TEMP_CLIM_C = (15.0, 40.0)

__all__ = [
    "FRAME_ROWS",
    "FRAME_COLS",
    "PIXEL_COUNT",
    "DEFAULT_BAUD",
    "TEMP_CLIM_C",
    "__version__",
]
