"""Regression checks for capture exits and an unreachable floating trigger."""

import os

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from quietshot.app import QuietShotApp
from quietshot.capture import CapturedScreen
from quietshot.config import Settings


@pytest.fixture(scope="module")
def qt_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


@pytest.fixture
def controller(qt_app, monkeypatch):
    monkeypatch.setattr("quietshot.app.load_settings", lambda: Settings())
    monkeypatch.setattr("quietshot.app.is_wayland", lambda: False)
    monkeypatch.setattr(QuietShotApp, "_setup_tray", lambda self: None)
    instance = QuietShotApp(qt_app)
    instance.floating.restore()
    yield instance
    instance.button_visibility.timer.stop()
    if instance.overlay is not None:
        instance.overlay.close()
    if instance.editor is not None:
        instance.editor.close()
    instance.floating.close()


def show_selection(controller, qt_app):
    image = QPixmap(200, 150)
    image.fill(Qt.GlobalColor.white)
    controller.floating.hide()
    controller._capture_pending = True
    controller._show_selection(CapturedScreen(image, qt_app.primaryScreen()))
    return controller.overlay


@pytest.mark.parametrize("escape", [False, True])
def test_selection_close_releases_capture_and_restores_button(controller, qt_app, escape):
    overlay = show_selection(controller, qt_app)
    if escape:
        QTest.keyClick(overlay, Qt.Key.Key_Escape)
    else:
        overlay.close()  # Same close event as Alt+F4/window-manager close.
    assert not controller._capture_busy()
    assert controller.floating.isVisible()


def test_successful_selection_keeps_button_hidden_until_editor_closes(controller, qt_app):
    overlay = show_selection(controller, qt_app)
    QTest.mousePress(overlay, Qt.MouseButton.LeftButton, pos=QPoint(20, 20))
    QTest.mouseRelease(overlay, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    assert controller.editor is not None
    controller.button_visibility.refresh()
    assert not controller.floating.isVisible()
    controller.editor.close()
    assert not controller._capture_busy()
    assert controller.floating.isVisible()


def test_idle_recovery_and_explicit_hide(controller, qt_app):
    controller.floating.move(-10000, -10000)
    controller.floating.hide()
    controller.button_visibility.refresh()
    assert controller.floating.isVisible()
    assert any(s.availableGeometry().contains(controller.floating.geometry())
               for s in qt_app.screens())
    controller.floating.showMinimized()
    controller.button_visibility.refresh()
    assert not controller.floating.isMinimized()
    controller.button_visibility.hide()
    controller.button_visibility.refresh()
    assert not controller.floating.isVisible()
    controller.button_visibility.show()
    assert controller.floating.isVisible()


def test_unexpected_capture_failure_does_not_strand_button(controller, qt_app, monkeypatch):
    def fail(_screen):
        raise RuntimeError("Capture backend stopped")

    monkeypatch.setattr(controller.capture_backend, "capture", fail)
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: None)
    controller._capture_pending = True
    controller.floating.hide()
    controller._capture_after_hide(qt_app.primaryScreen())
    assert not controller._capture_busy()
    assert controller.floating.isVisible()
