"""Platform boundary for obtaining a full-resolution screen image."""

import os
import sys
from dataclasses import dataclass

from PySide6.QtGui import QPixmap, QScreen


class CaptureError(RuntimeError):
    """A screenshot could not be captured on this desktop session."""


@dataclass(frozen=True)
class CapturedScreen:
    image: QPixmap
    screen: QScreen


class QtScreenCapture:
    """Capture one monitor via Qt; replaceable for other platform backends."""

    def capture(self, screen: QScreen) -> CapturedScreen:
        if sys.platform.startswith("linux") and os.environ.get("XDG_SESSION_TYPE") == "wayland":
            raise CaptureError(
                "Wayland needs a desktop portal capture backend. "
                "QuietShot 0.1 currently supports Linux X11."
            )
        image = screen.grabWindow(0)
        if image.isNull():
            raise CaptureError("Screen capture failed. Check system screen-recording permissions.")
        return CapturedScreen(image=image, screen=screen)

