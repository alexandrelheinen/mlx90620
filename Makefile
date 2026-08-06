# Thin wrappers around PlatformIO and the Python host package.

REALTIME_DIR := firmware/examples/realtime
SCAN_DIR := firmware/examples/scan

.PHONY: build realtime scan clean size artifacts format lint format-check \
	test-host test-python test gui-demo

build: realtime scan

test-host:
	$(CXX) -std=c++17 -Wall -Wextra -Werror -o /tmp/test_scan_marker tests/test_scan_marker.cpp
	/tmp/test_scan_marker

test-python:
	cd python && pytest -q

test: test-host test-python

realtime:
	pio run -d $(REALTIME_DIR)

scan:
	pio run -d $(SCAN_DIR)

clean:
	pio run -d $(REALTIME_DIR) -t clean
	pio run -d $(SCAN_DIR) -t clean
	rm -rf artifacts/firmware artifacts/reports artifacts/python

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

gui-demo:
	mlx90620 gui --demo --mode realtime

format:
	@chmod +x scripts/format.sh
	./scripts/format.sh

lint format-check:
	@chmod +x scripts/lint.sh
	./scripts/lint.sh
