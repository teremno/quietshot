"""The editor stays open until a screenshot is actually saved."""

import os

import pytest
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog

from quietshot.editor import Editor


@pytest.fixture(scope="module")
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_successful_save_closes_editor(tmp_path, monkeypatch, app):
    image = QImage(120, 80, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ffffff"))
    chosen = tmp_path / "selected-folder" / "shot.png"
    chosen.parent.mkdir()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_args: (str(chosen), "PNG (*.png)"))
    editor = Editor(QPixmap.fromImage(image), tmp_path)
    finished = []
    editor.finished.connect(lambda: finished.append(True))
    editor.show()
    app.processEvents()

    editor.save_image()

    assert chosen.exists()
    saved = QImage(str(chosen))
    assert saved.size() == image.size()
    assert not editor.isVisible()
    assert finished == [True]


def test_cancelled_save_keeps_editor_open(tmp_path, monkeypatch, app):
    image = QImage(10, 10, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ffffff"))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_args: ("", ""))
    editor = Editor(QPixmap.fromImage(image), tmp_path)
    editor.show()
    app.processEvents()

    editor.save_image()

    assert editor.isVisible()
    editor.close()
