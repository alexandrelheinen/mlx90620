from pathlib import Path

from mlx90620.cli import main


def test_capture_demo_png(tmp_path: Path):
    out = tmp_path / "frame.png"
    rc = main(
        [
            "capture",
            "--demo",
            "--mode",
            "realtime",
            "--frames",
            "1",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()
    assert out.stat().st_size > 0


def test_capture_demo_scan(tmp_path: Path):
    out = tmp_path / "mosaic.png"
    rc = main(
        [
            "capture",
            "--demo",
            "--mode",
            "scan",
            "--frames",
            "4",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()
