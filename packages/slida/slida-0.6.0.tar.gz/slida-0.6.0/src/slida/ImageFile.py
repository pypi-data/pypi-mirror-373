from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, QSizeF
from PySide6.QtGui import QPixmap


if TYPE_CHECKING:
    from slida.DirScanner import File


class ImageFile:
    file: "File"
    __is_valid: bool | None = None
    __size: QSize | None = None

    @property
    def is_valid(self) -> bool:
        if self.__is_valid is None:
            pm = QPixmap(self.file.path)
            self.__is_valid = not pm.isNull() and pm.height() > 0 and pm.width() > 0
        return self.__is_valid

    @property
    def size(self) -> QSize:
        if self.__size is None:
            pm = QPixmap(self.file.path)
            self.__size = pm.size()
        return self.__size

    def __init__(self, file: "File"):
        self.file = file

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.file.path == self.file.path

    def __hash__(self):
        return hash(self.file.path)

    def __repr__(self):
        return f"<ImageFile path={self.file.path}>"

    def get_scaled_qpixmap(self, height: float) -> QPixmap:
        return QPixmap(self.file.path).scaled(self.scaled_size(height).toSize())

    def scaled_size(self, height: float) -> QSizeF:
        return QSizeF(self.size.width() * (height / self.size.height()), height)
