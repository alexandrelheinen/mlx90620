#!/usr/bin/env bash
# Apply project formatters (C/C++ via clang-format; Python via black + ruff).
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

if command -v black >/dev/null 2>&1; then
  echo "Formatting Python with black..."
  (cd python && black src tests)
else
  echo "black not found; skipping (pip install -e 'python/[dev]')" >&2
fi

if command -v ruff >/dev/null 2>&1; then
  echo "Fixing Python imports/lint with ruff..."
  (cd python && ruff check --fix --unsafe-fixes src tests)
else
  echo "ruff not found; skipping" >&2
fi

echo "Done."
