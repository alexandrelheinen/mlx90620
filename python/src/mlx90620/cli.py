"""Command-line entry points for capture and GUI launch."""

from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path

import numpy as np
from PIL import Image

from mlx90620 import TEMP_CLIM_C, __version__
from mlx90620.filter import image_process
from mlx90620.serial_io import serial_settings, use_demo_mode
from mlx90620.sources import build_source


def _frame_to_png(frame: np.ndarray, path: Path, clim: tuple[float, float] = TEMP_CLIM_C) -> None:
    lo, hi = clim
    norm = np.clip((frame - lo) / (hi - lo), 0.0, 1.0)
    # Simple magma-like grayscale export is enough for CLI smoke; GUI uses color maps.
    pixels = (norm * 255.0).astype(np.uint8)
    Image.fromarray(pixels, mode="L").save(path)


def cmd_capture(args: argparse.Namespace) -> int:
    demo = use_demo_mode(args.demo)
    settings = serial_settings(args.port)
    source = build_source(args.mode, demo=demo, settings=settings)
    stop = threading.Event()
    source.open()
    try:
        count = 0
        for packet in source.frames(stop):
            if args.mode == "scan" and not packet.mosaic_complete and not demo:
                continue
            filtered = image_process(packet.raw, args.expansion, args.median_radius)
            count += 1
            if args.output and (count >= args.frames or packet.mosaic_complete):
                out = Path(args.output)
                _frame_to_png(filtered, out)
                print(f"wrote {out} shape={filtered.shape}")
                break
            if count >= args.frames:
                print(
                    f"captured {count} frame(s); "
                    f"raw mean={float(np.mean(packet.raw)):.2f} C "
                    f"filtered mean={float(np.mean(filtered)):.2f} C"
                )
                break
            if demo:
                time.sleep(0.05)
    finally:
        stop.set()
        source.close()
    return 0


def cmd_gui(args: argparse.Namespace) -> int:
    try:
        from mlx90620.app.main_window import run_app
    except ImportError as exc:
        print(
            "GUI dependencies missing. Install with: pip install -e '.[gui]'\n"
            f"Import error: {exc}",
            file=sys.stderr,
        )
        return 1
    demo = use_demo_mode(args.demo)
    return run_app(
        mode=args.mode,
        demo=demo,
        port=args.port,
        expansion=args.expansion,
        median_radius=args.median_radius,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mlx90620",
        description="Python host tools for the MLX90620 thermal camera",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--mode",
            choices=("realtime", "scan"),
            default="realtime",
            help="acquisition mode (default: realtime)",
        )
        p.add_argument("--port", default=None, help="serial port (or MLX90620_PORT)")
        p.add_argument(
            "--demo",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="use synthetic frames (or MLX90620_DEMO=1)",
        )
        p.add_argument("--expansion", type=int, default=4, help="upscale factor n")
        p.add_argument("--median-radius", type=int, default=4, help="median filter window")

    capture = sub.add_parser("capture", help="acquire frames on the CLI")
    add_common(capture)
    capture.add_argument("--frames", type=int, default=1, help="frames to capture")
    capture.add_argument("--output", type=str, default=None, help="optional PNG path")
    capture.set_defaults(func=cmd_capture)

    gui = sub.add_parser("gui", help="launch the desktop UI")
    add_common(gui)
    gui.set_defaults(func=cmd_gui)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
