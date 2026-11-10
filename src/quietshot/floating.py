"""A small, movable screenshot button that stays above normal windows."""

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QMenu, QWidget


class FloatingButton(QWidget):
    capture_requested = Signal()
    quit_requested = Signal()

    def __init__(self) -> None:
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowStaysOnTopHint)
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(64, 64)
        self.setWindowTitle("QuietShot capture")
        self.setToolTip("Click to capture · Drag to move · Right-click for menu")
        self._press: QPoint | None = None
        self._origin: QPoint | None = None
        self._dragged = False
        self._hover = False

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(17, 24, 39, 220 if self._hover else 160))
        painter.setPen(QPen(QColor(251, 191, 36, 225), 1.5))
        painter.drawEllipse(5, 5, 54, 54)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#ffffff"), 2.5, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawRoundedRect(18, 24, 29, 20, 3, 3)
        painter.drawRect(25, 20, 14, 5)
        painter.drawEllipse(28, 28, 9, 9)
        painter.end()

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press = event.globalPosition().toPoint()
            self._origin = self.pos()
            self._dragged = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press is None or self._origin is None:
            return
        delta = event.globalPosition().toPoint() - self._press
        if delta.manhattanLength() > 5:
            self._dragged = True
        if self._dragged:
            self.move(self._origin + delta)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._press is not None:
            if not self._dragged:
                self.capture_requested.emit()
            self._press = self._origin = None

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        menu.addAction("Capture area", self.capture_requested.emit)
        menu.addSeparator()
        menu.addAction("Quit QuietShot", self.quit_requested.emit)
        menu.exec(event.globalPos())

