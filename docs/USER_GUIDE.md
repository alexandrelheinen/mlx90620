# User guide (English)

> Updated for the Python host (2026). The 2015 French operator note is preserved at
> [`docs/archive/mode_demploi.pdf`](archive/mode_demploi.pdf).

## Prerequisites

1. Build and upload firmware with PlatformIO (see [`BUILD.md`](BUILD.md)):
   - Realtime: `pio run -d firmware/examples/realtime -t upload`
   - Scan: `pio run -d firmware/examples/scan -t upload`
2. Install the Python host:

```bash
cd python
python -m pip install -e ".[gui]"
```

## Realtime mode

1. Upload the **realtime** sketch to the Uno.  
2. Launch the GUI:

```bash
export MLX90620_PORT=/dev/ttyACM0   # or COM3 on Windows
mlx90620 gui --mode realtime
```

3. Set **Expansion n** and **Median radius** for filtering.  
4. Press **Start** to open the serial link. Left = raw temperatures, right = filtered.  
5. Press **Stop** (or close the window) to end acquisition — the port is released cleanly.

## Scan mode (balayage)

1. Upload the **scan** sketch.  
2. Run:

```bash
mlx90620 gui --mode scan
```

3. The tile label shows the current mosaic coordinates (`row x col`). The dual heatmaps
   update with the latest tile; when a full mosaic is assembled, the raw view shows the
   stitched image.

## Serial port

| OS | Default |
|----|---------|
| Windows | `COM3` |
| Linux / macOS | `/dev/ttyACM0` |

Override:

```bash
export MLX90620_PORT=COM5
# or
mlx90620 gui --port /dev/ttyUSB0
```

## Demo mode (no hardware)

```bash
mlx90620 gui --demo
mlx90620 capture --demo --frames 1 --output /tmp/frame.png
```

## CLI capture

```bash
mlx90620 capture --mode realtime --frames 10
mlx90620 capture --mode scan --demo --frames 4 --output mosaic.png
```

## Filter parameters

Typical values from the 2015 evaluation: expansion \(n = 4\) and median radius \(m = 4\)
(sometimes \(m = 6\) for demo figures). Adjust live from the GUI spin boxes.

## Important notes

1. Always **Stop** or close the window to release the serial port (the Python worker is
   designed for this; the old MATLAB GUIDE failure mode no longer applies).  
2. Historical MATLAB sources are archived under [`docs/archive/matlab-2015/`](archive/matlab-2015/).
