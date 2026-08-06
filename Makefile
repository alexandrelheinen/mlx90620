# Thin wrappers around PlatformIO for local builds and CI helpers.

REALTIME_DIR := firmware/examples/realtime
SCAN_DIR := firmware/examples/scan

.PHONY: build realtime scan clean size artifacts format-check

build: realtime scan

realtime:
	pio run -d $(REALTIME_DIR)

scan:
	pio run -d $(SCAN_DIR)

clean:
	pio run -d $(REALTIME_DIR) -t clean
	pio run -d $(SCAN_DIR) -t clean
	rm -rf artifacts/firmware artifacts/reports

size: build
	@mkdir -p artifacts/reports
	@echo "=== realtime ===" > artifacts/reports/size-report.txt
	@pio run -d $(REALTIME_DIR) -t size >> artifacts/reports/size-report.txt
	@echo "" >> artifacts/reports/size-report.txt
	@echo "=== scan ===" >> artifacts/reports/size-report.txt
	@pio run -d $(SCAN_DIR) -t size >> artifacts/reports/size-report.txt
	@cat artifacts/reports/size-report.txt

artifacts: build
	@chmod +x scripts/collect-artifacts.sh
	./scripts/collect-artifacts.sh

format-check:
	@command -v clang-format >/dev/null || { echo "clang-format not installed"; exit 1; }
	clang-format --dry-run --Werror \
	  firmware/lib/MLX90620/MLX90620.cpp \
	  firmware/lib/MLX90620/MLX90620.h \
	  firmware/examples/realtime/realtime.ino \
	  firmware/examples/scan/scan.ino
