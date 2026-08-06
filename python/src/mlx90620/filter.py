"""Image processing helpers (MATLAB ``imageProcess`` replacement)."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter


def upscale_nearest(frame: np.ndarray, factor: int) -> np.ndarray:
    """Nearest-neighbor upscale via Kronecker product (MATLAB ``kron``)."""
    if factor < 1:
        raise ValueError("factor must be >= 1")
    if factor == 1:
        return np.asarray(frame, dtype=np.float64)
    kernel = np.ones((factor, factor), dtype=np.float64)
    return np.kron(np.asarray(frame, dtype=np.float64), kernel)


def image_process(frame: np.ndarray, expansion: int, median_radius: int) -> np.ndarray:
    """
    Upscale by ``expansion`` then apply a median filter of window
    ``[median_radius, median_radius]`` (MATLAB ``medfilt2`` analogue).
    """
    if median_radius < 1:
        raise ValueError("median_radius must be >= 1")
    scaled = upscale_nearest(frame, expansion)
    # SciPy uses size=; for odd radii this matches common medfilt2 usage.
    return median_filter(scaled, size=median_radius)
