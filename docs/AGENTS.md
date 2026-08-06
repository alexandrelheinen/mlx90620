# Instructions for AI coding agents

This repository is an **Arduino + Python** thermal-camera project for the Melexis **MLX90620**. Before changing code, read and follow **[CONTRIBUTING.md](../CONTRIBUTING.md)**.

## Required reading order

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** — standards and workflow.
2. **[README.md](../README.md)** / **[BUILD.md](BUILD.md)** — how to build and run.
3. **[MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md)** — phased roadmap.
4. **[python-migration-analysis.md](python-migration-analysis.md)** — host-stack design choices.
5. **[REPORT.md](REPORT.md)** — design context.

## Quick checklist

- [ ] Use English identifiers, comments, and UI strings.
- [ ] Put sensor logic in `firmware/lib/MLX90620`; keep examples thin.
- [ ] Put host logic in `python/src/mlx90620`; GUI under `app/`.
- [ ] Build with `make build` (or `pio run -d firmware/examples/realtime`).
- [ ] Run `make lint` and `make test-python` after Python changes.
- [ ] Acquisition must use `AcquisitionWorker` (no serial I/O on the UI thread).
- [ ] Do not invent hardware capture results or edit demo images to fake heatmaps.
- [ ] Preserve the serial framing contract documented in `BUILD.md` unless intentionally versioned.
- [ ] Do not commit `.pio/`, `__pycache__/`, or OS junk (`Thumbs.db`).
- [ ] Keep pull requests focused; separate docs, CI, and refactors when practical.
- [ ] Do not revive the archived MATLAB tree under `docs/archive/matlab-2015/` as the primary host.

## Entry points

| Component | Entry |
|-----------|--------|
| Realtime firmware | `firmware/examples/realtime/realtime.ino` |
| Scan firmware | `firmware/examples/scan/scan.ino` |
| Python CLI | `mlx90620` / `python -m mlx90620` |
| Python GUI | `mlx90620 gui` |

## When unsure

Prefer minimal diffs, preserve acquisition behaviour, and document non-obvious changes in commit messages. If a task conflicts with `CONTRIBUTING.md`, follow `CONTRIBUTING.md`.
