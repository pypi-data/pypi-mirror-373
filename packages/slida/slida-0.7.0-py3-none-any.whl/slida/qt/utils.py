from PySide6.QtCore import QRectF, QSize, QSizeF


def get_centered_content_rect(bounds: QSize | QSizeF, content: QSize | QSizeF) -> QRectF:
    """Assumes `content` fits inside of `bounds`."""
    top = 0.0
    left = 0.0
    if isinstance(bounds, QSize):
        bounds = bounds.toSizeF()
    if isinstance(content, QSize):
        content = content.toSizeF()
    if content.height() < bounds.height():
        top = (bounds.height() - content.height()) / 2
    if content.width() < bounds.width():
        left = (bounds.width() - content.width()) / 2
    return QRectF(left, top, content.width(), content.height())


def get_subsquare_count(bounds: QSize | QSizeF, min_width: int):
    columns = int(bounds.width() / min_width)
    sub_width = bounds.width() / columns
    rows = round(bounds.height() / sub_width)

    return rows, columns
