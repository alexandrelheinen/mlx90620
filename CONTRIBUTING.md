# Contributing

Thank you for improving this project. This document defines the code standards and workflow expected from human and automated contributors.

## Project overview

MLX90620 is a Supélec *Projet de Conception* (2015) that pairs Arduino Uno firmware with MATLAB GUIs to acquire and display frames from a Melexis MLX90620 16×4 IR array. Optional dual-servo scanning builds a larger mosaic (*scan* mode).

| Area | Role |
|------|------|
| `firmware/lib/MLX90620` | First-party sensor library |
| `firmware/external/I2Cmaster` | Vendored GPL-3 TWI library |
| `firmware/examples/` | `realtime` and `scan` sketches |
| `matlab/` | GUIDE UIs + shared `+mlx90620` helpers |
| `docs/` | Markdown documentation |

See [docs/MODERNIZATION_PLAN.md](docs/MODERNIZATION_PLAN.md) for the full modernization roadmap.

## General principles

1. **English everywhere in source code** — identifiers, comments, user-facing strings, and commit messages. Do not introduce new French identifiers.
2. **Minimal, focused changes** — match surrounding style; avoid unrelated refactors in the same commit.
3. **Keep CI green** — firmware must compile with PlatformIO (`make build` or `pio run -d firmware/examples/realtime`).
4. **Preserve sensor maths and serial framing** unless a datasheet bug is proven. Document protocol changes in `docs/BUILD.md`.

## C / C++ (Arduino)

- Target the **Arduino Uno** (`atmelavr` / ATmega328P) via PlatformIO.
- Prefer **C++17** features only when they remain AVR-safe (no exceptions/RTTI reliance).
- Naming: `PascalCase` types, `camelCase` methods/variables, `kConstant` / `UPPER_SNAKE` constants.
- Use `uint8_t` / `int16_t` from `<stdint.h>`; do not `#define byte`.
- Sketches own a file-scope `MLX90620` instance; call `begin()` from `setup()`.
- Format with the committed `.clang-format` (LLVM-based, 2-space indent, 100 columns) when touching C/C++.

## MATLAB

- Keep GUIDE `.fig` files working; put shared helpers in `matlab/+mlx90620/`.
- Use **`serialport`** via `mlx90620.openSerial` (R2019b+). Do not reintroduce `serial`/`fopen`.
- Port and demo flags: `MLX90620_PORT`, `MLX90620_DEMO` (see `docs/BUILD.md`).
- Run `matlab/setupPaths.m` (or rely on UI openers that add the package root) before launching interfaces.
- Image Processing Toolbox is required for `medfilt2`.
- Style-check helpers/scripts with MISS_HIT (`make lint`); GUIDE-generated `interface.m` is excluded.

## Git workflow

1. Branch from `master` (`cursor/…` for automated agent work).
2. Commit messages in English, imperative mood (`Fix MLX90620 EEPROM buffer size`).
3. Keep commits logically separated (docs, firmware fix, layout, CI).
4. Open a pull request against `master` and ensure CI is green.

## Formatting

```bash
make format    # clang-format + mh_style --fix
make lint      # check-only (CI)
```

Do not format vendored `firmware/external/I2Cmaster` unless intentionally updating that dependency.

## Testing expectations

- Firmware: `make build` (PlatformIO per-example projects under `firmware/examples/`).
- Style: `make lint`.
- Optional: inspect uploaded CI artifacts (`.hex` + size report) on the workflow run.
- MATLAB demo mode: `setenv('MLX90620_DEMO','1')` then open a GUIDE UI.
- Hardware-in-the-loop validation is encouraged when an MLX90620 is available but is not required for CI.
