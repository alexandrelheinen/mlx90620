import numpy as np
import pytest

from mlx90620.protocol import (
    decode_scan_marker,
    encode_scan_marker,
    is_scan_marker,
    mosaic_shape,
    place_tile,
    reshape_frame,
)


def test_encode_decode_roundtrip():
    for row in range(3):
        for col in range(4):
            marker = encode_scan_marker(row, col)
            assert marker <= -300
            decoded = decode_scan_marker(float(marker))
            assert decoded.row == row
            assert decoded.col == col


def test_is_scan_marker():
    assert is_scan_marker(-300)
    assert is_scan_marker(-324.0)
    assert not is_scan_marker(-299)
    assert not is_scan_marker(25.5)


def test_reshape_flips_rows_like_matlab():
    values = list(range(64))
    frame = reshape_frame(values)
    assert frame.shape == (16, 4)
    # First four wire values are row 0 on the wire -> bottom row after flipud.
    assert np.allclose(frame[-1], [0, 1, 2, 3])
    assert np.allclose(frame[0], [60, 61, 62, 63])


def test_place_tile_matlab_indexing():
    mosaic = np.zeros(mosaic_shape(1, 4))
    tile = np.full((16, 4), 7.0)
    place_tile(mosaic, tile, row_index=0, col_index=0, tile_rows=1, tile_cols=4)
    # numIm2 - c = 4 - 0 = 4 -> last column slot index 3
    assert np.allclose(mosaic[:, 12:16], 7.0)
    with pytest.raises(ValueError):
        place_tile(mosaic, tile, row_index=9, col_index=0, tile_rows=1, tile_cols=4)
