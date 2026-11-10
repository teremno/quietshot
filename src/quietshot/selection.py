"""Select an image region while preserving source pixel resolution."""

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from quietshot.capture import CapturedScreen


class SelectionOverlay(QWidget):
    selected = Signal(QPixmap)
    cancelled = Signal()

    def __init__(self, captured: CapturedScreen) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.image = captured.image
        self.setGeometry(captured.screen.geometry())
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.start: QPoint | None = None
        self.end: QPoint | None = None

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image, self.image.rect())
        painter.fillRect(self.rect(), QColor(0, 0, 0, 105))
        if self.start is not None and self.end is not None:
            area = QRect(self.start, self.end).normalized().intersected(self.rect())
            if area.isValid():
                painter.drawPixmap(area, self.image, self._source_rect(area))
                painter.setPen(QColor("#fbbf24"))
                painter.drawRect(area.adjusted(0, 0, -1, -1))
                label = f"{self._source_rect(area).width()} × {self._source_rect(area).height()} px"
                painter.fillRect(QRect(area.left(), max(0, area.top() - 27), 145, 24),
                                 QColor("#111827"))
                painter.setPen(QColor("#ffffff"))
                painter.drawText(area.left() + 8, max(17, area.top() - 10), label)
        painter.end()

    def _source_rect(self, area: QRect) -> QRect:
        sx = self.image.width() / max(1, self.width())
        sy = self.image.height() / max(1, self.height())
        left = round(area.left() * sx)
        top = round(area.top() * sy)
        right = round((area.right() + 1) * sx)
        bottom = round((area.bottom() + 1) * sy)
        return QRect(left, top, right - left, bottom - top).intersected(self.image.rect())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.start = event.position().toPoint()
            self.end = self.start
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.start is not None:
            self.end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self.start is None:
            return
        self.end = event.position().toPoint()
        area = QRect(self.start, self.end).normalized().intersected(self.rect())
        if area.width() < 5 or area.height() < 5:
            self.start = self.end = None
            self.update()
            return
        cropped = self.image.copy(self._source_rect(area))
        self.selected.emit(cropped)
        self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()
        else:
            super().keyPressEvent(event)

