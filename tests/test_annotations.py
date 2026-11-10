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

