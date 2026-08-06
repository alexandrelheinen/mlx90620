# Build and run

## Requirements

| Component | Requirement |
|-----------|-------------|
| Firmware toolchain | [PlatformIO Core](https://platformio.org/) 6+ (pulls `atmelavr` / Arduino framework) |
| Board | Arduino Uno (ATmega328P) |
| Sensor | Melexis MLX90620 on I2C (SDA/SCL = A4/A5 on Uno) |
| Optional actuators | Two hobby servos on pins **9** (pan) and **11** (tilt) for *scan* mode |
| Host UI | Python 3.11+ with `python/[gui]` extras (PySide6 + pyqtgraph) |

Arduino IDE remains supported: copy `firmware/lib/MLX90620` into your libraries folder and add `firmware/external/I2Cmaster` the same way (or keep `lib_extra_dirs` via PlatformIO only).

## Firmware (PlatformIO)

Each example is its own PlatformIO project (so the `.ino` can sit at the source root):

```bash
pio run -d firmware/examples/realtime
pio run -d firmware/examples/scan
# or
make build
```

Upload (with the Uno connected):

```bash
pio run -d firmware/examples/realtime -t upload
pio device monitor -d firmware/examples/realtime -b 9600
```

Build products land under `firmware/examples/<name>/.pio/build/uno/` (`firmware.hex`, `firmware.elf`). CI collects them into `artifacts/` and uploads the hex files plus a size report.

## Python host

```bash
cd python
python -m pip install -e ".[dev]"   # includes GUI + pytest/black/ruff
```

### CLI

```bash
# Synthetic frame (no Arduino)
mlx90620 capture --demo --mode realtime --frames 1 --output /tmp/frame.png

# Live serial capture
export MLX90620_PORT=/dev/ttyACM0   # or COM3 on Windows
mlx90620 capture --mode realtime --frames 5
```

### GUI

```bash
mlx90620 gui --demo                 # hardware-free
mlx90620 gui --mode realtime
mlx90620 gui --mode scan --port /dev/ttyACM0
```

The GUI runs acquisition on a **background thread** and updates two pyqtgraph heatmaps (raw + filtered). Closing the window always stops the worker and releases the serial port.

### Serial port

| Setting | How |
|---------|-----|
| Default Windows | `COM3` |
| Default Linux/macOS | `/dev/ttyACM0` |
| Override | `MLX90620_PORT` env var or `--port` |

### Demo mode (no Arduino)

```bash
export MLX90620_DEMO=1
# or pass --demo to the CLI/GUI
```

## Serial protocol (stable contract)

Baud rate: **9600** for both examples.

### Realtime (`firmware/examples/realtime`)

Each frame is **64** lines. Each line is one object temperature in °C printed with `Serial.println` (pixel order as read from the sensor IR RAM). The host reshapes to 16×4 with the historical vertical flip used by the 2015 MATLAB UI.

### Scan (`firmware/examples/scan`)

1. One integer marker line: `(-(300 + 10 * rowIndex + colIndex))` with value **≤ −300**.
2. Then **64** temperature lines for that servo pose (same format as realtime).

The host reconstructs the mosaic from the marker’s encoded row/column indices.

## Wiring notes

- Enable AVR internal pull-ups on SDA/SCL in firmware (`PORTC` bits for A4/A5) and use external 4.7 kΩ pull-ups if the bus is long or noisy.
- Servo power should not be drawn from the Uno 5 V rail under load; use a separate supply with common ground when possible.

## Continuous integration

GitHub Actions (`.github/workflows/ci.yml`):

- compiles both firmware environments and uploads `.hex` / size reports
- runs Black, Ruff, pytest, demo PNG capture, and an offscreen GUI smoke test
- uploads `python-demo-frames` artifacts

## Archived MATLAB host

The 2015/2026 MATLAB GUIDE tree lives under [`docs/archive/matlab-2015/`](archive/matlab-2015/) for reference only.
