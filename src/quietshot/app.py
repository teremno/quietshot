"""Application orchestration; platform I/O remains behind small adapters."""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QTimer
from PySide6.QtGui import QCursor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from quietshot.capture import CaptureError, QtScreenCapture
from quietshot.config import load_settings
from quietshot.editor import Editor
from quietshot.floating import FloatingButton
from quietshot.hotkeys import GlobalHotkey
from quietshot.selection import SelectionOverlay

LOG = logging.getLogger(__name__)


class QuietShotApp:
    def __init__(self, qt_app: QApplication) -> None:
        self.qt_app = qt_app
        self.settings = load_settings()
        self.capture_backend = QtScreenCapture()
        self.floating = FloatingButton()
        self.floating.capture_requested.connect(self.start_capture)
        self.floating.quit_requested.connect(qt_app.quit)
        self.overlay: SelectionOverlay | None = None
        self.editor: Editor | None = None
        self.hotkey = GlobalHotkey(self.settings.hotkey)
        self.hotkey.activated.connect(self.start_capture)
        self.hotkey.failed.connect(self._hotkey_failed)
        self.tray: QSystemTrayIcon | None = None
        self._setup_tray()
        qt_app.aboutToQuit.connect(self.hotkey.stop)

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon = QPixmap(32, 32)
        icon.fill("#1e293b")
        painter = QPainter(icon)
        painter.setPen("#fbbf24")
        painter.drawRect(7, 10, 18, 13)
        painter.drawEllipse(13, 13, 6, 6)
        painter.end()
        self.tray = QSystemTrayIcon(QIcon(icon))
        menu = QMenu()
        menu.addAction("Capture area", self.start_capture)
        menu.addAction("Show floating button", self.floating.show)
        menu.addAction("Hide floating button", self.floating.hide)
        menu.addSeparator()
        menu.addAction("Quit", self.qt_app.quit)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip("QuietShot")
        self.tray.show()

    def run(self) -> int:
        screen = self.qt_app.primaryScreen()
        if screen is None:
            raise RuntimeError("No display found")
        bounds = screen.availableGeometry()
        self.floating.move(QPoint(bounds.right() - 80, bounds.center().y()))
        self.floating.show()
        self.hotkey.start()
        return self.qt_app.exec()

    def start_capture(self) -> None:
        if self.overlay is not None or self.editor is not None:
            return
        screen = self.qt_app.screenAt(QCursor.pos()) or self.qt_app.primaryScreen()
        if screen is None:
            return
        self.floating.hide()
        QTimer.singleShot(250, lambda: self._capture_after_hide(screen))

    def _capture_after_hide(self, screen) -> None:
        try:
            captured = self.capture_backend.capture(screen)
        except CaptureError as exc:
            LOG.warning("Capture unavailable: %s", exc)
            self.floating.show()
            QMessageBox.warning(None, "QuietShot", str(exc))
            return
        self.overlay = SelectionOverlay(captured)
        self.overlay.selected.connect(self._open_editor)
        self.overlay.cancelled.connect(self._finish_capture)
        self.overlay.show()
        self.overlay.activateWindow()

    def _open_editor(self, image: QPixmap) -> None:
        self.overlay = None
        output = Path(self.settings.output_dir).expanduser() if self.settings.output_dir else Path.home() / "Pictures" / "QuietShot"
        self.editor = Editor(image, output)
        self.editor.finished.connect(self._finish_capture)
        self.editor.show()
        self.editor.activateWindow()

    def _finish_capture(self) -> None:
        self.overlay = None
        self.editor = None
        self.floating.show()

    def _hotkey_failed(self, message: str) -> None:
        LOG.warning("Global hotkey did not start: %s", message)
        if self.tray is not None:
            self.tray.showMessage("QuietShot hotkey unavailable", message,
                                  QSystemTrayIcon.MessageIcon.Warning, 5000)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("QuietShot")
    qt_app.setOrganizationName("QuietShot")
    qt_app.setQuitOnLastWindowClosed(False)
    return QuietShotApp(qt_app).run()
