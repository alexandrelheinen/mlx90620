# Instructions for AI coding agents

This repository is an **Arduino + MATLAB** thermal-camera project for the Melexis **MLX90620**. Before changing code, read and follow **[CONTRIBUTING.md](../CONTRIBUTING.md)** — it is the source of truth for naming, layout, and review expectations.

## Required reading order

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** — standards and workflow.
2. **[README.md](../README.md)** / **[BUILD.md](BUILD.md)** — how to build and run.
3. **[MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md)** — phased roadmap and known pitfalls.
4. **[REPORT.md](REPORT.md)** — design context (when present).

## Quick checklist

- [ ] Use English identifiers, comments, and UI strings.
- [ ] Put sensor logic in `firmware/lib/MLX90620`; keep examples thin.
- [ ] Build with `make build` (or `pio run -d firmware/examples/realtime`).
- [ ] Do not invent hardware capture results or edit demo images to fake heatmaps.
- [ ] Preserve the serial framing contract documented in `BUILD.md` unless intentionally versioned.
- [ ] Do not commit `.pio/`, MATLAB `*.asv`, or OS junk (`Thumbs.db`).
- [ ] Keep pull requests focused; separate docs, CI, and refactors when practical.

## Entry points

| Component | Entry |
|-----------|--------|
| Realtime firmware | `firmware/examples/realtime/realtime.ino` |
| Scan firmware | `firmware/examples/scan/scan.ino` |
| MATLAB realtime UI | `matlab/realtime/interface.m` (after `setupPaths`) |
| MATLAB scan UI | `matlab/scan/interface.m` |

## When unsure

Prefer minimal diffs, preserve acquisition behaviour, and document non-obvious changes in commit messages. If a task conflicts with `CONTRIBUTING.md`, follow `CONTRIBUTING.md`.
