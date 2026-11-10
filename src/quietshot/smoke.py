"""Small runtime check for frozen packages on CI runners."""

from pathlib import Path

from PySide6.QtGui import QColor, QImage, QPixmap

from quietshot.config import Settings
from quietshot.editor import Editor
from quietshot.floating import FloatingButton
from quietshot.settings_dialog import SettingsDialog


def run_smoke() -> int:
    image = QImage(40, 30, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ffffff"))
    button = FloatingButton()
    dialog = SettingsDialog(Settings())
    editor = Editor(QPixmap.fromImage(image), Path("."))
    assert editor.canvas.final_image().size() == image.size()
    assert dialog.hotkey.keySequence().toString()
    button.close()
    dialog.close()
    editor.close()
    return 0
