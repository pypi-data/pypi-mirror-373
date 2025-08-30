from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QSizeF, Qt
from PySide6.QtGui import QImage, QPainter

from slida.utils import get_centered_content_rect


if TYPE_CHECKING:
    from slida.ImageFile import ImageFile


class ImageScreen:
    __inner_qimage: QImage | None = None
    __outer_qimage: QImage | None = None

    def __init__(self, bounds: QSizeF, *images: "ImageFile"):
        self.bounds = bounds
        self.images = images
        self.size = self.__get_size()
        self.area = self.size.width() * self.size.height()
        self.bounds_ratio = self.bounds.width() / self.bounds.height() if self.bounds.height() > 0 else 0.0
        self.images_ratio = self.size.width() / self.size.height() if self.size.height() > 0 else 0.0
        self.can_fit_more = self.bounds_ratio - self.images_ratio >= 0.4
        self.inner_rect = get_centered_content_rect(bounds, self.size)

    def get_inner_qimage(self):
        if self.__inner_qimage is None:
            self.__inner_qimage = QImage(self.size.toSize(), QImage.Format.Format_RGB32)
            qpainter = QPainter(self.__inner_qimage)
            left = 0

            for image in self.images:
                qpixmap = image.get_scaled_qpixmap(self.size.height())
                qpainter.drawPixmap(QPointF(left, 0), qpixmap)
                left += qpixmap.width()

            qpainter.end()

        return self.__inner_qimage

    def get_outer_qimage(self):
        if self.__outer_qimage is None:
            self.__outer_qimage = QImage(self.bounds.toSize(), QImage.Format.Format_RGB32)
            self.__outer_qimage.fill(Qt.GlobalColor.black)
            if not self.size.isEmpty():
                qpainter = QPainter(self.__outer_qimage)
                content = self.get_inner_qimage()
                qpainter.drawImage(self.inner_rect.topLeft(), content)
                qpainter.end()
        return self.__outer_qimage

    def __get_size(self) -> QSizeF:
        height = self.bounds.height()
        width = sum((f.scaled_size(self.bounds.height()).width() for f in self.images), 0.0)

        if width > self.bounds.width():
            height = self.bounds.height() * (self.bounds.width() / width)
            width = self.bounds.width()

        return QSizeF(width, height)
