"""PySide6 + pyqtgraph dual-heatmap application."""

from __future__ import annotations

import sys
from queue import Empty
from typing import Any

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mlx90620 import TEMP_CLIM_C
from mlx90620.serial_io import serial_settings
from mlx90620.worker import AcquisitionWorker


class MainWindow(QMainWindow):
    def __init__(
        self,
        *,
        mode: str = "realtime",
        demo: bool = False,
        port: str | None = None,
        expansion: int = 4,
        median_radius: int = 4,
    ):
        super().__init__()
        self.setWindowTitle("MLX90620 Thermal Camera")
        self.resize(960, 560)

        self._settings = serial_settings(port)
        self._demo = demo
        self._worker: AcquisitionWorker | None = None

        self._mode = QComboBox()
        self._mode.addItems(["realtime", "scan"])
        self._mode.setCurrentText(mode)

        self._expansion = QSpinBox()
        self._expansion.setRange(1, 16)
        self._expansion.setValue(expansion)

        self._median = QSpinBox()
        self._median.setRange(1, 21)
        self._median.setSingleStep(2)
        self._median.setValue(median_radius)

        self._status = QLabel(self._status_text())
        self._tile = QLabel("tile: -")

        self._start = QPushButton("Start")
        self._stop = QPushButton("Stop")
        self._stop.setEnabled(False)
        self._start.clicked.connect(self.start_acquisition)
        self._stop.clicked.connect(self.stop_acquisition)

        controls = QFormLayout()
        controls.addRow("Mode", self._mode)
        controls.addRow("Expansion n", self._expansion)
        controls.addRow("Median radius", self._median)
        controls.addRow(self._status)
        controls.addRow(self._tile)

        buttons = QHBoxLayout()
        buttons.addWidget(self._start)
        buttons.addWidget(self._stop)

        pg.setConfigOptions(imageAxisOrder="row-major", antialias=True)
        self._raw_view = pg.ImageView(view=pg.PlotItem())
        self._filt_view = pg.ImageView(view=pg.PlotItem())
        self._raw_view.ui.roiBtn.hide()
        self._raw_view.ui.menuBtn.hide()
        self._filt_view.ui.roiBtn.hide()
        self._filt_view.ui.menuBtn.hide()
        for view in (self._raw_view, self._filt_view):
            view.setPredefinedGradient("thermal")
            view.setLevels(*TEMP_CLIM_C)

        plots = QHBoxLayout()
        plots.addWidget(self._raw_view, 1)
        plots.addWidget(self._filt_view, 1)

        root = QVBoxLayout()
        root.addLayout(controls)
        root.addLayout(buttons)
        root.addLayout(plots, 1)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._poll_queue)

        self._expansion.valueChanged.connect(self._push_filter_params)
        self._median.valueChanged.connect(self._push_filter_params)

    def _status_text(self) -> str:
        if self._demo:
            return "Demo mode (synthetic frames)"
        return f"Arduino Uno - {self._settings.port} @ {self._settings.baud} baud"

    def _push_filter_params(self) -> None:
        if self._worker is not None:
            self._worker.set_filter_params(self._expansion.value(), self._median.value())

    def start_acquisition(self) -> None:
        self.stop_acquisition()
        self._status.setText(self._status_text())
        self._worker = AcquisitionWorker(
            mode=self._mode.currentText(),
            demo=self._demo,
            settings=self._settings,
            expansion=self._expansion.value(),
            median_radius=self._median.value(),
            on_error=self._on_worker_error,
        )
        self._worker.start()
        self._timer.start()
        self._start.setEnabled(False)
        self._stop.setEnabled(True)
        self._mode.setEnabled(False)

    def stop_acquisition(self) -> None:
        self._timer.stop()
        if self._worker is not None:
            self._worker.stop()
            self._worker = None
        self._start.setEnabled(True)
        self._stop.setEnabled(False)
        self._mode.setEnabled(True)

    def _on_worker_error(self, exc: BaseException) -> None:
        # Qt slots must run on the GUI thread; use a single-shot timer trampoline.
        QTimer.singleShot(0, lambda: self._show_error(exc))

    def _show_error(self, exc: BaseException) -> None:
        self.stop_acquisition()
        QMessageBox.critical(self, "Acquisition error", str(exc))

    def _poll_queue(self) -> None:
        if self._worker is None:
            return
        latest: tuple[Any, Any] | None = None
        q = self._worker.queue
        while True:
            try:
                latest = q.get_nowait()
            except Empty:
                break
        if latest is None:
            return
        packet, filtered = latest
        raw = np.asarray(packet.raw, dtype=np.float64)
        filt = np.asarray(filtered, dtype=np.float64)
        self._raw_view.setImage(raw, autoLevels=False)
        self._filt_view.setImage(filt, autoLevels=False)
        if packet.row_index is not None and packet.col_index is not None:
            suffix = " (mosaic)" if packet.mosaic_complete else ""
            self._tile.setText(f"tile: {packet.row_index}x{packet.col_index}{suffix}")

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        self.stop_acquisition()
        super().closeEvent(event)


def run_app(
    *,
    mode: str = "realtime",
    demo: bool = False,
    port: str | None = None,
    expansion: int = 4,
    median_radius: int = 4,
) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(
        mode=mode,
        demo=demo,
        port=port,
        expansion=expansion,
        median_radius=median_radius,
    )
    window.show()
    return int(app.exec())
