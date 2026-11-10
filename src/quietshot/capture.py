"""Platform boundary for obtaining a full-resolution screen image."""

import os
import sys
from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QPixmap, QScreen
from PySide6.QtMultimedia import QMediaCaptureSession, QScreenCapture, QVideoFrame, QVideoSink


class CaptureError(RuntimeError):
    """A screenshot could not be captured on this desktop session."""


@dataclass(frozen=True)
class CapturedScreen:
    image: QPixmap
    screen: QScreen


class QtScreenCapture:
    """Capture one monitor via Qt; replaceable for other platform backends."""

    def capture(self, screen: QScreen) -> CapturedScreen:
        image = screen.grabWindow(0)
        if image.isNull():
            raise CaptureError("Screen capture failed. Check system screen-recording permissions.")
        return CapturedScreen(image=image, screen=screen)


def is_wayland() -> bool:
    return sys.platform.startswith("linux") and os.environ.get("XDG_SESSION_TYPE") == "wayland"


class WaylandPortalCapture(QObject):
    """Acquire one frame through Qt's PipeWire/desktop-portal screen picker."""

    captured = Signal(object)
    failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._screen: QScreen | None = None
        self._capture = QScreenCapture(self)
        self._sink = QVideoSink(self)
        self._session = QMediaCaptureSession(self)
        self._session.setScreenCapture(self._capture)
        self._session.setVideoSink(self._sink)
        self._sink.videoFrameChanged.connect(self._on_frame)
        self._capture.errorOccurred.connect(self._on_error)
        self._timeout = QTimer(self)
        self._timeout.setSingleShot(True)
        self._timeout.timeout.connect(self._on_timeout)

    def start(self, screen: QScreen) -> None:
        self._screen = screen
        self._timeout.start(120_000)
        # Wayland shows the desktop's own screen chooser when capture starts.
        self._capture.start()

    def _on_frame(self, frame: QVideoFrame) -> None:
        if self._screen is None or not frame.isValid():
            return
        image = frame.toImage()
        if image.isNull():
            return
        screen = self._screen
        self._stop()
        self.captured.emit(CapturedScreen(QPixmap.fromImage(image), screen))

    def _on_error(self, _error: QScreenCapture.Error, message: str) -> None:
        if self._screen is None:
            return
        self._stop()
        self.failed.emit(message or "Screen capture was cancelled or unavailable.")

    def _on_timeout(self) -> None:
        self._stop()
        self.failed.emit("Timed out waiting for the desktop screen picker.")

    def _stop(self) -> None:
        self._timeout.stop()
        self._capture.stop()
        self._screen = None

