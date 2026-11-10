"""Annotation canvas and a compact save/copy editor."""

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QImage, QKeySequence, QMouseEvent, QPainter, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from quietshot.annotations import Annotation, paint_annotations, render_annotations
from quietshot.filenames import next_screenshot_path


class Canvas(QWidget):
    changed = Signal()

    def __init__(self, source: QImage) -> None:
        super().__init__()
        self.source = source
        self.source.setDevicePixelRatio(1.0)
        self.annotations: list[Annotation] = []
        self.active: Annotation | None = None
        self.tool = "arrow"
        self.setMouseTracking(True)
        self.setMinimumSize(400, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _image_rect(self) -> QRectF:
        scale = min((self.width() - 32) / self.source.width(),
                    (self.height() - 32) / self.source.height(), 1.0)
        width, height = self.source.width() * scale, self.source.height() * scale
        return QRectF((self.width() - width) / 2, (self.height() - height) / 2, width, height)

    def _image_point(self, position: QPointF) -> QPointF:
        target = self._image_rect()
        x = (position.x() - target.left()) * self.source.width() / target.width()
        y = (position.y() - target.top()) * self.source.height() / target.height()
        return QPointF(max(0, min(self.source.width() - 1, x)),
                       max(0, min(self.source.height() - 1, y)))

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#111827"))
        target = self._image_rect()
        painter.drawImage(target, self.source)
        painter.save()
        painter.translate(target.left(), target.top())
        painter.scale(target.width() / self.source.width(),
                      target.height() / self.source.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        items = self.annotations + ([self.active] if self.active else [])
        paint_annotations(painter, items)
        painter.restore()
        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._image_rect().contains(event.position()):
            point = self._image_point(event.position())
            self.active = Annotation(self.tool, [point, point])
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.active is None:
            return
        point = self._image_point(event.position())
        if self.tool == "pen":
            self.active.points.append(point)
        else:
            self.active.points[-1] = point
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.active is not None and event.button() == Qt.MouseButton.LeftButton:
            self.active.points[-1] = self._image_point(event.position())
            self.annotations.append(self.active)
            self.active = None
            self.changed.emit()
            self.update()

    def undo(self) -> None:
        if self.annotations:
            self.annotations.pop()
            self.changed.emit()
            self.update()

    def final_image(self) -> QImage:
        return render_annotations(self.source, self.annotations)


class Editor(QMainWindow):
    finished = Signal()

    def __init__(self, image: QPixmap, output_dir: Path) -> None:
        super().__init__()
        self.canvas = Canvas(image.toImage())
        self.output_dir = output_dir
        self.setWindowTitle("QuietShot · Edit screenshot")
        self.resize(1000, 720)
        self.setMinimumSize(540, 400)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self._tools: dict[str, QPushButton] = {}
        for kind, label in (("arrow", "Arrow"), ("rectangle", "Rectangle"),
                            ("pen", "Pen"), ("redact", "Cover")):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setMinimumHeight(38)
            button.clicked.connect(lambda checked=False, k=kind: self._set_tool(k))
            toolbar.addWidget(button)
            self._tools[kind] = button
        self._set_tool("arrow")
        toolbar.addStretch()
        for label, callback in (("Undo", self.canvas.undo), ("Copy", self.copy_image),
                                ("Save PNG", self.save_image)):
            button = QPushButton(label)
            button.setMinimumHeight(38)
            button.clicked.connect(callback)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)
        hint = QLabel("Full-size PNG · Esc closes · Ctrl+Z undoes · Ctrl+S saves")
        hint.setStyleSheet("color: #94a3b8; padding: 2px;")
        layout.addWidget(hint)
        container.setStyleSheet(
            "QWidget { background: #1e293b; color: #f8fafc; font-size: 14px; }"
            "QPushButton { background: #334155; border: 1px solid #475569;"
            " border-radius: 7px; padding: 6px 12px; }"
            "QPushButton:hover { background: #475569; }"
            "QPushButton:checked { background: #92400e; border-color: #fbbf24; }"
            "QPushButton:focus { border: 2px solid #fbbf24; }"
        )
        self.setCentralWidget(container)
        QShortcut(QKeySequence.StandardKey.Undo, self, self.canvas.undo)
        QShortcut(QKeySequence.StandardKey.Save, self, self.save_image)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

    def _set_tool(self, kind: str) -> None:
        self.canvas.tool = kind
        for name, button in self._tools.items():
            button.setChecked(name == kind)

    def copy_image(self) -> None:
        QApplication.clipboard().setImage(self.canvas.final_image())
        self.statusBar().showMessage("Copied full-resolution image to clipboard", 3000)

    def save_image(self) -> None:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", f"Could not create screenshot folder: {exc}")
            return
        proposed = next_screenshot_path(self.output_dir)
        chosen, _ = QFileDialog.getSaveFileName(self, "Save screenshot", str(proposed), "PNG (*.png)")
        if not chosen:
            return
        path = Path(chosen)
        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")
        if not self.canvas.final_image().save(str(path), "PNG", 100):
            QMessageBox.critical(self, "Save failed", f"Could not write {path}")
            return
        self.statusBar().showMessage(f"Saved {path}", 5000)

    def closeEvent(self, event) -> None:
        self.finished.emit()
        super().closeEvent(event)
