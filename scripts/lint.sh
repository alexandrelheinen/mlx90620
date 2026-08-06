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

if command -v black >/dev/null 2>&1; then
  echo "== black --check =="
  (cd python && black --check src tests) || status=1
else
  echo "black not found (pip install -e 'python/[dev]')" >&2
  status=1
fi

if command -v ruff >/dev/null 2>&1; then
  echo "== ruff check =="
  (cd python && ruff check src tests) || status=1
else
  echo "ruff not found" >&2
  status=1
fi

exit "$status"
