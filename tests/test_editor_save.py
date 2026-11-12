"""The editor stays open until a screenshot is actually saved."""

import os
from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QColorDialog, QFileDialog

from quietshot.editor import Editor
from quietshot.save_location import SaveLocationStore


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
    locations = SaveLocationStore(tmp_path / "state.json")
    editor.saved.connect(lambda path: locations.remember(path.parent))
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
    assert SaveLocationStore(tmp_path / "state.json").preferred_dir(tmp_path) == chosen.parent

    proposed_paths = []

    def cancel_next_dialog(_parent, _title, proposed, _filter):
        proposed_paths.append(Path(proposed))
        return "", ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", cancel_next_dialog)
    next_editor = Editor(
        QPixmap.fromImage(image),
        SaveLocationStore(tmp_path / "state.json").preferred_dir(tmp_path),
    )
    next_editor.save_image()
    assert proposed_paths[0].parent == chosen.parent
    next_editor.close()


def test_cancelled_save_keeps_editor_open(tmp_path, monkeypatch, app):
    image = QImage(10, 10, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ffffff"))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_args: ("", ""))
    editor = Editor(QPixmap.fromImage(image), tmp_path)
    locations = SaveLocationStore(tmp_path / "state.json")
    editor.saved.connect(lambda path: locations.remember(path.parent))
    editor.show()
    app.processEvents()

    editor.save_image()

    assert editor.isVisible()
    assert locations.preferred_dir(tmp_path) == tmp_path
    editor.close()


def test_style_controls_change_new_annotation_settings(tmp_path, monkeypatch, app):
    image = QImage(120, 80, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ffffff"))
    editor = Editor(QPixmap.fromImage(image), tmp_path)
    editor._colors["#3b82f6"].click()
    editor.thickness.setValue(12)
    assert editor.canvas.stroke_color == "#3b82f6"
    assert editor.canvas.stroke_width == 12

    monkeypatch.setattr(QColorDialog, "getColor", lambda *_args: QColor("#a855f7"))
    editor._choose_color()
    assert editor.canvas.stroke_color == "#a855f7"

    editor._tools["redact"].click()
    assert not editor.style_controls.isEnabled()
    editor._tools["arrow"].click()
    assert editor.style_controls.isEnabled()
    editor.close()
