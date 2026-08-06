import numpy as np

from mlx90620.demo import demo_frame
from mlx90620.filter import image_process, upscale_nearest


def test_upscale_nearest():
    frame = np.arange(8, dtype=float).reshape(2, 4)
    out = upscale_nearest(frame, 2)
    assert out.shape == (4, 8)
    assert out[0, 0] == frame[0, 0]
    assert out[1, 1] == frame[0, 0]


def test_image_process_shape():
    frame = demo_frame()
    out = image_process(frame, expansion=4, median_radius=3)
    assert out.shape == (frame.shape[0] * 4, frame.shape[1] * 4)
    assert np.isfinite(out).all()


def test_demo_frame_range():
    frame = demo_frame(t=0.0)
    assert frame.shape == (16, 4)
    assert frame.min() > 15
    assert frame.max() < 40
