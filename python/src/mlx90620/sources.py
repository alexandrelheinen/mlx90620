"""Frame sources: realtime serial, scan serial, and demo generators."""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
import serial

from mlx90620 import PIXEL_COUNT
from mlx90620.demo import demo_frame
from mlx90620.protocol import (
    decode_scan_marker,
    is_scan_marker,
    mosaic_shape,
    place_tile,
    reshape_frame,
)
from mlx90620.serial_io import SerialSettings, open_serial, read_numeric_line


@dataclass(frozen=True, slots=True)
class FramePacket:
    """One displayable frame plus optional scan metadata."""

    raw: np.ndarray
    row_index: int | None = None
    col_index: int | None = None
    mosaic_complete: bool = False


def _read_temperatures(ser: serial.Serial) -> list[float]:
    values: list[float] = []
    while len(values) < PIXEL_COUNT:
        value = read_numeric_line(ser)
        if np.isnan(value):
            continue
        if is_scan_marker(value):
            # Unexpected marker mid-frame: restart collection after decode path.
            raise RuntimeError("scan marker received while filling a temperature frame")
        values.append(value)
    return values


class RealtimeSerialSource:
    def __init__(self, settings: SerialSettings):
        self._settings = settings
        self._ser: serial.Serial | None = None

    def open(self) -> None:
        self._ser = open_serial(self._settings)

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def frames(self, stop_flag) -> Iterator[FramePacket]:
        assert self._ser is not None
        while not stop_flag.is_set():
            values = _read_temperatures(self._ser)
            yield FramePacket(raw=reshape_frame(values))


class ScanSerialSource:
    def __init__(
        self,
        settings: SerialSettings,
        *,
        tile_rows: int = 1,
        tile_cols: int = 4,
    ):
        self._settings = settings
        self._tile_rows = tile_rows
        self._tile_cols = tile_cols
        self._ser: serial.Serial | None = None
        self._mosaic = np.zeros(mosaic_shape(tile_rows, tile_cols), dtype=np.float64)

    def open(self) -> None:
        self._ser = open_serial(self._settings)
        self._mosaic[:] = 0.0

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def frames(self, stop_flag) -> Iterator[FramePacket]:
        assert self._ser is not None
        while not stop_flag.is_set():
            marker_value = float("nan")
            while not stop_flag.is_set() and not is_scan_marker(marker_value):
                marker_value = read_numeric_line(self._ser)
            if stop_flag.is_set():
                return
            marker = decode_scan_marker(marker_value)
            values = _read_temperatures(self._ser)
            tile = reshape_frame(values)
            place_tile(
                self._mosaic,
                tile,
                marker.row,
                marker.col,
                tile_rows=self._tile_rows,
                tile_cols=self._tile_cols,
            )
            complete = marker.row == (self._tile_rows - 1) and marker.col == (self._tile_cols - 1)
            display = self._mosaic.copy() if complete else tile
            yield FramePacket(
                raw=display,
                row_index=marker.row,
                col_index=marker.col,
                mosaic_complete=complete,
            )


class DemoRealtimeSource:
    def open(self) -> None:
        return None

    def close(self) -> None:
        return None

    def frames(self, stop_flag) -> Iterator[FramePacket]:
        while not stop_flag.is_set():
            yield FramePacket(raw=demo_frame())
            time.sleep(0.1)


class DemoScanSource:
    def __init__(self, *, tile_rows: int = 1, tile_cols: int = 4):
        self._tile_rows = tile_rows
        self._tile_cols = tile_cols
        self._mosaic = np.zeros(mosaic_shape(tile_rows, tile_cols), dtype=np.float64)

    def open(self) -> None:
        self._mosaic[:] = 0.0

    def close(self) -> None:
        return None

    def frames(self, stop_flag) -> Iterator[FramePacket]:
        col = 0
        while not stop_flag.is_set():
            row = 0
            tile = demo_frame() + float(col)
            place_tile(
                self._mosaic,
                tile,
                row,
                col,
                tile_rows=self._tile_rows,
                tile_cols=self._tile_cols,
            )
            complete = col == (self._tile_cols - 1)
            display = self._mosaic.copy() if complete else tile
            yield FramePacket(
                raw=display,
                row_index=row,
                col_index=col,
                mosaic_complete=complete,
            )
            col = (col + 1) % self._tile_cols
            time.sleep(0.1)


def build_source(mode: str, *, demo: bool, settings: SerialSettings):
    mode = mode.lower()
    if mode not in {"realtime", "scan"}:
        raise ValueError(f"unknown mode: {mode}")
    if demo:
        return DemoRealtimeSource() if mode == "realtime" else DemoScanSource()
    if mode == "realtime":
        return RealtimeSerialSource(settings)
    return ScanSerialSource(settings)
