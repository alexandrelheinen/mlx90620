"""Serial framing helpers matching the Arduino firmware contract."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from mlx90620 import FRAME_COLS, FRAME_ROWS, PIXEL_COUNT


@dataclass(frozen=True, slots=True)
class ScanMarker:
    """Decoded scan-mode pose marker (value <= -300 on the wire)."""

    row: int
    col: int
    raw: int

    @property
    def encoded(self) -> int:
        return -(self.raw + 300)


def is_scan_marker(value: float) -> bool:
    """Return True when a decoded numeric line is a scan frame marker."""
    return value <= -300.0 and math.isfinite(value)


def decode_scan_marker(value: float) -> ScanMarker:
    """Decode ``-(300 + 10 * row + col)`` into pose indices."""
    if not is_scan_marker(value):
        raise ValueError(f"not a scan marker: {value!r}")
    raw = int(round(value))
    encoded = -(raw + 300)
    col = encoded % 10
    row = encoded // 10
    return ScanMarker(row=row, col=col, raw=raw)


def encode_scan_marker(row: int, col: int) -> int:
    """Mirror of ``MLX90620::scanFrameMarker`` in firmware."""
    return -(300 + 10 * int(row) + int(col))


def reshape_frame(values: list[float] | np.ndarray) -> np.ndarray:
    """
    Build a (16, 4) frame from 64 wire values.

    Firmware streams row-major temperatures; MATLAB historically stored each
    incoming row flipped vertically (``image(rows-i+1, j)``). We keep that
    convention so visuals match the 2015 UIs.
    """
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    if arr.size != PIXEL_COUNT:
        raise ValueError(f"expected {PIXEL_COUNT} temperatures, got {arr.size}")
    frame = arr.reshape((FRAME_ROWS, FRAME_COLS))
    return np.flipud(frame)


def mosaic_shape(tile_rows: int = 1, tile_cols: int = 4) -> tuple[int, int]:
    return tile_rows * FRAME_ROWS, tile_cols * FRAME_COLS


def place_tile(
    mosaic: np.ndarray,
    tile: np.ndarray,
    row_index: int,
    col_index: int,
    *,
    tile_rows: int = 1,
    tile_cols: int = 4,
) -> None:
    """
    Insert a tile using the MATLAB indexing convention
    ``globalImage{numIm1 - r, numIm2 - c}``.
    """
    r = tile_rows - 1 - row_index
    c = tile_cols - 1 - col_index
    if not (0 <= r < tile_rows and 0 <= c < tile_cols):
        raise ValueError(f"tile index out of range: row={row_index} col={col_index}")
    r0 = r * FRAME_ROWS
    c0 = c * FRAME_COLS
    mosaic[r0 : r0 + FRAME_ROWS, c0 : c0 + FRAME_COLS] = tile
