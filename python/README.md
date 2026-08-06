# MLX90620 Python host

Host-side tools that replace the legacy MATLAB GUIDE UIs: serial acquisition,
median filtering, demo frames, CLI, and an optional PySide6 + pyqtgraph GUI.

## Install

```bash
cd python
python -m pip install -e ".[dev]"   # core + GUI + pytest/black/ruff
# or runtime only:
python -m pip install -e ".[gui]"
```

## Quick start

```bash
# Demo mode (no Arduino) — save a filtered PNG
mlx90620 capture --demo --frames 1 --output /tmp/frame.png

# Live GUI (demo)
mlx90620 gui --demo

# Live GUI on a real port
export MLX90620_PORT=/dev/ttyACM0
mlx90620 gui --mode realtime
mlx90620 gui --mode scan
```

See the repository [`docs/BUILD.md`](../docs/BUILD.md) for the serial protocol.
