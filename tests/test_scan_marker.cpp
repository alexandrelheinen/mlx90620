// Host-side unit test for the scan-mode serial marker encoding.
// Mirrors MLX90620::scanFrameMarker without requiring the Arduino toolchain.
//
// Build & run: make test-host

#include <cassert>
#include <cstdint>
#include <cstdio>

static int scanFrameMarker(uint8_t rowIndex, uint8_t colIndex) {
  return -(300 + 10 * static_cast<int>(rowIndex) + static_cast<int>(colIndex));
}

int main() {
  assert(scanFrameMarker(0, 0) == -300);
  assert(scanFrameMarker(0, 3) == -303);
  assert(scanFrameMarker(1, 0) == -310);
  assert(scanFrameMarker(2, 4) == -324);

  // MATLAB recovery: C = -(c + 300); col = C % 10; row = floor(C / 10)
  const int marker = scanFrameMarker(1, 2);
  assert(marker <= -300);
  const int encoded = -(marker + 300);
  assert(encoded % 10 == 2);
  assert(encoded / 10 == 1);

  std::puts("test_scan_marker: OK");
  return 0;
}
