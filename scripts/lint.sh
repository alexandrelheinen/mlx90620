#!/usr/bin/env bash
# Run formatters/linters in check-only mode (non-zero exit on violations).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
status=0

if command -v clang-format >/dev/null 2>&1; then
  echo "== clang-format (dry-run) =="
  clang-format --dry-run --Werror \
    firmware/lib/MLX90620/MLX90620.cpp \
    firmware/lib/MLX90620/MLX90620.h \
    firmware/examples/realtime/realtime.ino \
    firmware/examples/scan/scan.ino || status=1
else
  echo "clang-format not found" >&2
  status=1
fi

if command -v mh_style >/dev/null 2>&1; then
  echo "== mh_style =="
  # Lint first-party helpers/scripts; GUIDE-generated interface.m stays excluded.
  mh_style matlab/+mlx90620 matlab/realtime/cameraProcess.m \
    matlab/realtime/cameraSave.m matlab/scan/cameraProcess.m matlab/setupPaths.m \
    || status=1
  if command -v mh_lint >/dev/null 2>&1; then
    echo "== mh_lint =="
    mh_lint matlab/+mlx90620 matlab/realtime/cameraProcess.m \
      matlab/realtime/cameraSave.m matlab/scan/cameraProcess.m matlab/setupPaths.m \
      || status=1
  fi
else
  echo "mh_style not found (pip install miss_hit)" >&2
  status=1
fi

exit "$status"
