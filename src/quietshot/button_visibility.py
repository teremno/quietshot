"""Maintain the floating trigger while respecting capture and explicit hiding."""

from collections.abc import Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from quietshot.floating import FloatingButton


class ButtonVisibility:
    def __init__(self, button: FloatingButton, busy: Callable[[], bool]) -> None:
        self.button = button
        self.busy = busy
        self.wanted = True
        self.timer = QTimer(button)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.refresh)

    def refresh(self) -> None:
        """Repair hidden/minimized/off-screen windows and refresh their stacking."""
        if (self.wanted and not self.busy() and not self.button.interacting
                and QApplication.activePopupWidget() is None
                and QApplication.activeModalWidget() is None):
            self.button.restore()

    def show(self) -> None:
        self.wanted = True
        self.refresh()

    def hide(self) -> None:
        self.wanted = False
        self.button.hide()
