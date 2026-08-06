# Contributing

Thank you for improving this project. This document defines the code standards and workflow expected from human and automated contributors.

## Project overview

MLX90620 is a Supélec *Projet de Conception* (2015) that pairs Arduino Uno firmware with a host application to acquire and display frames from a Melexis MLX90620 16×4 IR array. Optional dual-servo scanning builds a larger mosaic (*scan* mode). The host stack is **Python** (the original MATLAB GUIDE UIs are archived).

| Area | Role |
|------|------|
| `firmware/lib/MLX90620` | First-party sensor library |
| `firmware/external/I2Cmaster` | Vendored GPL-3 TWI library |
| `firmware/examples/` | `realtime` and `scan` sketches |
| `python/` | Host package (CLI + PySide6 GUI) |
| `docs/` | Markdown documentation |
| `docs/archive/matlab-2015/` | Historical MATLAB host (reference only) |

See [docs/MODERNIZATION_PLAN.md](docs/MODERNIZATION_PLAN.md) and [docs/python-migration-analysis.md](docs/python-migration-analysis.md).

## General principles

1. **English everywhere in source code** — identifiers, comments, user-facing strings, and commit messages.
2. **Minimal, focused changes** — match surrounding style; avoid unrelated refactors in the same commit.
3. **Keep CI green** — firmware (`make build`) and Python (`make test-python`, `make lint`).
4. **Preserve sensor maths and serial framing** unless a datasheet bug is proven. Document protocol changes in `docs/BUILD.md`.
5. **Never block the UI thread** on serial I/O — use `AcquisitionWorker`.

## C / C++ (Arduino)

- Target the **Arduino Uno** (`atmelavr` / ATmega328P) via PlatformIO.
- Prefer **C++17** features only when they remain AVR-safe (no exceptions/RTTI reliance).
- Naming: `PascalCase` types, `camelCase` methods/variables, `kConstant` / `UPPER_SNAKE` constants.
- Use `uint8_t` / `int16_t` from `<stdint.h>`; do not `#define byte`.
- Sketches own a file-scope `MLX90620` instance; call `begin()` from `setup()`.
- Format with the committed `.clang-format` (LLVM-based, 2-space indent, 100 columns).

## Python

- Target **Python 3.11+**; package under `python/src/mlx90620`.
- Format with **Black** (line length 100); lint/import-sort with **Ruff**.
- Core deps: `numpy`, `scipy`, `pyserial`, `Pillow`. GUI extras: `PySide6`, `pyqtgraph`.
- Prefer type hints on new public functions.
- Tests with **pytest** (`python/tests`).
- Port / demo flags: `MLX90620_PORT`, `MLX90620_DEMO` (see `docs/BUILD.md`).

## Formatting

```bash
make format    # clang-format + black + ruff --fix
make lint      # check-only (CI)
```

Do not format vendored `firmware/external/I2Cmaster` unless intentionally updating that dependency.

## Git workflow

1. Branch from `master` (`cursor/…` for automated agent work).
2. Commit messages in English, imperative mood (`Add Python capture CLI`).
3. Keep commits logically separated (docs, firmware, Python, CI).
4. Open a pull request against `master` and ensure CI is green.

## Testing expectations

- Firmware: `make build`
- C++ marker test: `make test-host`
- Python: `make test-python`
- Style: `make lint`
- Demo GUI: `mlx90620 gui --demo` (or CI offscreen smoke)
- Hardware-in-the-loop validation is encouraged when an MLX90620 is available but is not required for CI.
