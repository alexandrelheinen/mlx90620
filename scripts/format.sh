#!/usr/bin/env bash
# Apply project formatters (C/C++ via clang-format; MATLAB via MISS_HIT).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v clang-format >/dev/null 2>&1; then
  echo "Formatting C/C++ with clang-format..."
  clang-format -i \
    firmware/lib/MLX90620/MLX90620.cpp \
    firmware/lib/MLX90620/MLX90620.h \
    firmware/examples/realtime/realtime.ino \
    firmware/examples/scan/scan.ino
else
  echo "clang-format not found; skipping C/C++ format" >&2
fi

if command -v mh_style >/dev/null 2>&1; then
  echo "Formatting MATLAB with mh_style --fix..."
  mh_style --fix matlab/+mlx90620 matlab/realtime/cameraProcess.m \
    matlab/realtime/cameraSave.m matlab/scan/cameraProcess.m matlab/setupPaths.m
else
  echo "mh_style not found; skipping MATLAB format (pip install miss_hit)" >&2
fi

echo "Done."
