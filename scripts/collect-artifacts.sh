#!/usr/bin/env bash
# Collect PlatformIO build products into artifacts/ for CI upload or local review.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REALTIME_DIR="firmware/examples/realtime"
SCAN_DIR="firmware/examples/scan"

mkdir -p artifacts/firmware artifacts/reports

copy_env() {
  local name="$1"
  local project_dir="$2"
  local hex="${project_dir}/.pio/build/uno/firmware.hex"
  local elf="${project_dir}/.pio/build/uno/firmware.elf"
  if [[ ! -f "$hex" || ! -f "$elf" ]]; then
    echo "Missing build outputs for ${name}. Run: pio run -d ${project_dir}" >&2
    exit 1
  fi
  cp "$hex" "artifacts/firmware/${name}.hex"
  cp "$elf" "artifacts/firmware/${name}.elf"
}

copy_env realtime "$REALTIME_DIR"
copy_env scan "$SCAN_DIR"

{
  echo "MLX90620 firmware size report"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "=== realtime ==="
  pio run -d "$REALTIME_DIR" -t size
  echo
  echo "hex sha256: $(sha256sum artifacts/firmware/realtime.hex | awk '{print $1}')"
  echo "elf sha256: $(sha256sum artifacts/firmware/realtime.elf | awk '{print $1}')"
  echo
  echo "=== scan ==="
  pio run -d "$SCAN_DIR" -t size
  echo
  echo "hex sha256: $(sha256sum artifacts/firmware/scan.hex | awk '{print $1}')"
  echo "elf sha256: $(sha256sum artifacts/firmware/scan.elf | awk '{print $1}')"
  echo
} | tee artifacts/reports/size-report.txt

{
  echo "First 40 lines of each Intel HEX (visual smoke check)"
  echo
  for env in realtime scan; do
    echo "===== ${env}.hex ====="
    head -n 40 "artifacts/firmware/${env}.hex"
    echo
  done
} | tee artifacts/reports/hex-preview.txt

ls -la artifacts/firmware artifacts/reports
