"""Synthetic frames for hardware-free demos and CI."""

from __future__ import annotations

import time

import numpy as np

from mlx90620 import FRAME_COLS, FRAME_ROWS


def demo_frame(
    rows: int = FRAME_ROWS,
    cols: int = FRAME_COLS,
    t: float | None = None,
) -> np.ndarray:
    """
    Warm blob drifting over a ~20-35 C background (same idea as MATLAB demoFrame).
    """
    if t is None:
        t = time.time()
    ys = np.arange(1, rows + 1, dtype=np.float64)[:, None]
    xs = np.arange(1, cols + 1, dtype=np.float64)[None, :]
    cx = 1.5 + 1.5 * np.sin(0.4 * t)
    cy = 8.0 + 4.0 * np.cos(0.25 * t)
    return 22.0 + 10.0 * np.exp(-((xs - cx) ** 2 + ((ys - cy) / 3.0) ** 2) / 4.0)
