"""Serial port helpers for the Arduino Uno link."""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

import serial

from mlx90620 import DEFAULT_BAUD


@dataclass(frozen=True, slots=True)
class SerialSettings:
    port: str
    baud: int = DEFAULT_BAUD


def default_port() -> str:
    env = os.environ.get("MLX90620_PORT", "").strip()
    if env:
        return env
    if sys.platform.startswith("win"):
        return "COM3"
    return "/dev/ttyACM0"


def serial_settings(port: str | None = None, baud: int = DEFAULT_BAUD) -> SerialSettings:
    return SerialSettings(port=port or default_port(), baud=baud)


def use_demo_mode(explicit: bool | None = None) -> bool:
    """Honor ``MLX90620_DEMO`` unless an explicit flag is provided."""
    if explicit is not None:
        return explicit
    flag = os.environ.get("MLX90620_DEMO", "").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def open_serial(settings: SerialSettings | None = None, *, reset_delay_s: float = 1.5):
    """Open the port with LF terminators semantics (line reads)."""
    cfg = settings or serial_settings()
    ser = serial.Serial(cfg.port, cfg.baud, timeout=1.0)
    # USB-CDC open usually resets the Uno; wait before reading frames.
    time.sleep(reset_delay_s)
    ser.reset_input_buffer()
    return ser


def read_numeric_line(ser: serial.Serial) -> float:
    """Read one LF-terminated line and parse as float (NaN if blank/invalid)."""
    raw = ser.readline()
    if not raw:
        return float("nan")
    text = raw.decode("ascii", errors="ignore").strip()
    if not text:
        return float("nan")
    return float(text)
