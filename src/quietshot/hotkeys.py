"""Cross-platform best-effort global shortcut adapter."""

import logging

from PySide6.QtCore import QObject, Signal

LOG = logging.getLogger(__name__)


class GlobalHotkey(QObject):
    activated = Signal()
    failed = Signal(str)

    def __init__(self, combination: str) -> None:
        super().__init__()
        self.combination = combination
        self._listener = None

    def start(self) -> None:
        try:
            from pynput import keyboard

            self._listener = keyboard.GlobalHotKeys({self.combination: self.activated.emit})
            self._listener.start()
        except Exception as exc:
            LOG.exception("Global hotkey unavailable")
            self.failed.emit(str(exc))

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

