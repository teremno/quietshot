from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QImage

from quietshot.annotations import Annotation, render_annotations


def test_redaction_keeps_dimensions_and_covers_pixels():
    base = QImage(120, 80, QImage.Format.Format_ARGB32)
    base.fill(QColor("#ffffff"))
    result = render_annotations(
        base, [Annotation("redact", [QPointF(10, 10), QPointF(60, 40)])]
    )
    assert result.size() == base.size()
    assert result.pixelColor(30, 20) == QColor("#111111")
    assert result.pixelColor(90, 60) == QColor("#ffffff")


def test_arrow_uses_its_own_color_and_thickness():
    base = QImage(120, 80, QImage.Format.Format_ARGB32)
    base.fill(QColor("#ffffff"))
    thin = render_annotations(
        base,
        [Annotation("arrow", [QPointF(10, 40), QPointF(100, 40)], "#3b82f6", 1)],
    )
    thick = render_annotations(
        base,
        [Annotation("arrow", [QPointF(10, 40), QPointF(100, 40)], "#22c55e", 12)],
    )
    thin_pixel = thin.pixelColor(50, 40)
    assert thin_pixel.blue() > thin_pixel.red()
    assert thin_pixel != QColor("#ffffff")
    assert thin.pixelColor(50, 44) == QColor("#ffffff")
    assert thick.pixelColor(50, 40) == QColor("#22c55e")
    assert thick.pixelColor(50, 44) == QColor("#22c55e")

