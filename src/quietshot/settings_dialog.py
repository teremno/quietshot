"""Small settings dialog for shortcut and screenshot destination."""

from pathlib import Path

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from quietshot.config import Settings
from quietshot.shortcuts import to_pynput, to_qt


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.setWindowTitle("QuietShot settings")
        self.setMinimumWidth(480)
        self._saved: Settings | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)
        form = QFormLayout()
        form.setSpacing(12)
        self.hotkey = QKeySequenceEdit(QKeySequence(to_qt(settings.hotkey)))
        self.hotkey.setMaximumSequenceLength(1)
        self.hotkey.setToolTip("Press a modifier plus a letter, digit, or F1–F12")
        form.addRow("Capture shortcut", self.hotkey)

        destination = QHBoxLayout()
        self.folder = QLineEdit(settings.output_dir or str(Path.home() / "Pictures" / "QuietShot"))
        self.folder.setPlaceholderText("Choose a folder for PNG files")
        destination.addWidget(self.folder)
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        destination.addWidget(browse)
        form.addRow("Default folder", destination)
        layout.addLayout(form)

        note = QLabel(
            "After the first save, QuietShot suggests the last folder you used. "
            "The shortcut changes immediately. On Wayland, global shortcuts may be unavailable."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #94a3b8;")
        layout.addWidget(note)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setStyleSheet(
            "QDialog { background: #1e293b; color: #f8fafc; font-size: 14px; }"
            "QLabel { color: #f8fafc; }"
            "QLineEdit, QKeySequenceEdit { background: #0f172a; color: #f8fafc;"
            " border: 1px solid #64748b; border-radius: 6px; padding: 8px; }"
            "QLineEdit:focus, QKeySequenceEdit:focus { border: 2px solid #fbbf24; }"
            "QPushButton { background: #334155; color: #f8fafc; border: 1px solid #64748b;"
            " border-radius: 6px; padding: 8px 14px; }"
            "QPushButton:hover { background: #475569; }"
        )

    def _browse(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Screenshot folder", self.folder.text())
        if chosen:
            self.folder.setText(chosen)

    def _validate_and_accept(self) -> None:
        try:
            portable = self.hotkey.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
            hotkey = to_pynput(portable)
            folder = self.folder.text().strip()
            if not folder:
                raise ValueError("Choose a folder for screenshots.")
            path = Path(folder).expanduser()
            if path.exists() and not path.is_dir():
                raise ValueError("The selected path is a file, not a folder.")
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise ValueError(f"Cannot create the screenshot folder: {exc}") from exc
            self._saved = Settings(hotkey=hotkey, output_dir=str(path))
        except ValueError as exc:
            QMessageBox.warning(self, "Check settings", str(exc))
            return
        self.accept()

    def result_settings(self) -> Settings:
        if self._saved is None:
            raise RuntimeError("Settings dialog was not saved")
        return self._saved
