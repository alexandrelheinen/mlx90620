"""Background acquisition worker that never blocks the UI thread."""

from __future__ import annotations

import contextlib
import logging
import threading
from collections.abc import Callable
from queue import Empty, Full, Queue

from mlx90620.filter import image_process
from mlx90620.serial_io import SerialSettings
from mlx90620.sources import FramePacket, build_source

logger = logging.getLogger(__name__)


class AcquisitionWorker:
    """
    Runs a frame source on a daemon thread and pushes processed packets to a queue.

    Filter parameters can be updated live via ``set_filter_params``.
    """

    def __init__(
        self,
        *,
        mode: str,
        demo: bool,
        settings: SerialSettings,
        expansion: int = 4,
        median_radius: int = 4,
        queue_size: int = 2,
        on_error: Callable[[BaseException], None] | None = None,
    ):
        self._mode = mode
        self._demo = demo
        self._settings = settings
        self._expansion = expansion
        self._median_radius = median_radius
        self._queue: Queue[tuple[FramePacket, object]] = Queue(maxsize=queue_size)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._on_error = on_error
        self._lock = threading.Lock()

    @property
    def queue(self) -> Queue:
        return self._queue

    def set_filter_params(self, expansion: int, median_radius: int) -> None:
        with self._lock:
            self._expansion = max(1, int(expansion))
            self._median_radius = max(1, int(median_radius))

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="mlx90620-acq", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
        # Drain leftover frames so a restart starts clean.
        while True:
            try:
                self._queue.get_nowait()
            except Empty:
                break

    def _run(self) -> None:
        source = build_source(self._mode, demo=self._demo, settings=self._settings)
        try:
            source.open()
            for packet in source.frames(self._stop):
                with self._lock:
                    expansion = self._expansion
                    radius = self._median_radius
                filtered = image_process(packet.raw, expansion, radius)
                item = (packet, filtered)
                try:
                    self._queue.put_nowait(item)
                except Full:
                    with contextlib.suppress(Empty):
                        self._queue.get_nowait()
                    with contextlib.suppress(Full):
                        self._queue.put_nowait(item)
        except Exception as exc:  # noqa: BLE001 - surface to UI callback
            logger.exception("acquisition worker failed")
            if self._on_error is not None:
                self._on_error(exc)
        finally:
            source.close()
