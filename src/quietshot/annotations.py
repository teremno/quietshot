"""Image-space annotation model and lossless-size renderer."""

from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen, QPolygonF


@dataclass
class Annotation:
    kind: str
    points: list[QPointF]


def render_annotations(base: QImage, annotations: list[Annotation]) -> QImage:
    """Paint at the image's original pixel dimensions, without resampling."""
    result = base.copy()
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    paint_annotations(painter, annotations)
    painter.end()
    return result


def paint_annotations(painter: QPainter, annotations: list[Annotation]) -> None:
    """Draw annotations in source-image coordinates."""
    for item in annotations:
        if len(item.points) < 2:
            continue
        start, end = item.points[0], item.points[-1]
        if item.kind == "redact":
            painter.fillRect(QRectF(start, end).normalized(), QColor("#111111"))
            continue
        painter.setPen(QPen(QColor("#ef4444"), 4, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        if item.kind == "arrow":
            painter.drawLine(start, end)
            delta = end - start
            length = (delta.x() ** 2 + delta.y() ** 2) ** 0.5
            if length > 1:
                ux, uy = delta.x() / length, delta.y() / length
                left = QPointF(end.x() - 15 * ux - 8 * uy, end.y() - 15 * uy + 8 * ux)
                right = QPointF(end.x() - 15 * ux + 8 * uy, end.y() - 15 * uy - 8 * ux)
                painter.setBrush(QColor("#ef4444"))
                painter.drawPolygon(QPolygonF([end, left, right]))
                painter.setBrush(Qt.BrushStyle.NoBrush)
        elif item.kind == "rectangle":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(start, end).normalized())
        elif item.kind == "pen":
            path = QPainterPath(start)
            for point in item.points[1:]:
                path.lineTo(point)
            painter.drawPath(path)
