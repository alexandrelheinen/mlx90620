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

From the repository root:

```bash
pio run -e realtime
pio run -e scan
# or
make build
```

Upload (with the Uno connected):

```bash
pio run -e realtime -t upload
pio device monitor -b 9600
```

Build products land under `.pio/build/<env>/` (`firmware.hex`, `firmware.elf`). CI uploads those hex files plus a size report as workflow artifacts.

## MATLAB

```matlab
cd matlab
setupPaths
realtime.interface   % or: scan.interface — GUIDE entry is interface.m inside each folder
```

Or open `matlab/realtime/interface.m` / `matlab/scan/interface.m` after `setupPaths`.

Default serial port in scripts is `COM3` (Windows). Change the `com` variable for your OS (`/dev/ttyACM0` on many Linux Unos).

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
