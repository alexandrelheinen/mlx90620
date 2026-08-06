# Build and run

## Requirements

| Component | Requirement |
|-----------|-------------|
| Firmware toolchain | [PlatformIO Core](https://platformio.org/) 6+ (pulls `atmelavr` / Arduino framework) |
| Board | Arduino Uno (ATmega328P) |
| Sensor | Melexis MLX90620 on I2C (SDA/SCL = A4/A5 on Uno) |
| Optional actuators | Two hobby servos on pins **9** (pan) and **11** (tilt) for *scan* mode |
| Host UI | MATLAB with Image Processing Toolbox (`medfilt2`) |

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

## MATLAB

Requires **R2019b+** (`serialport`). Image Processing Toolbox is needed for `medfilt2`.

```matlab
cd matlab
setupPaths
% open realtime/interface.m or scan/interface.m
```

### Serial port

| Setting | How |
|---------|-----|
| Default Windows | `COM3` |
| Default Linux/macOS | `/dev/ttyACM0` |
| Override | `setenv('MLX90620_PORT','…')` |

Helpers: `mlx90620.serialSettings`, `mlx90620.openSerial`, `mlx90620.readNumericLine`.

### Demo mode (no Arduino)

```matlab
setenv('MLX90620_DEMO','1')
```

Acquisition loops feed synthetic frames from `mlx90620.demoFrame` so the GUIDE UIs can be exercised without hardware.

## Serial protocol (stable contract)

Baud rate: **9600** for both examples.

### Realtime (`firmware/examples/realtime`)

Each frame is **64** lines. Each line is one object temperature in °C printed with `Serial.println` (pixel order as read from the sensor IR RAM).

### Scan (`firmware/examples/scan`)

1. One integer marker line: `(-(300 + 10 * rowIndex + colIndex))` with value **≤ −300**.
2. Then **64** temperature lines for that servo pose (same format as realtime).

MATLAB reconstructs the mosaic from the marker’s encoded row/column indices.

## Wiring notes

- Enable AVR internal pull-ups on SDA/SCL in firmware (`PORTC` bits for A4/A5) and use external 4.7 kΩ pull-ups if the bus is long or noisy.
- Servo power should not be drawn from the Uno 5 V rail under load; use a separate supply with common ground when possible.

## Continuous integration

GitHub Actions (`.github/workflows/ci.yml`) compiles both environments on every push/PR and uploads:

- `realtime.hex` / `scan.hex`
- `size-report.txt` (AVR memory usage)

Download the artifact from the Actions run for visual inspection of the build outputs.
