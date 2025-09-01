import os

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap


class ImageFile:
    path: str
    stat: os.stat_result
    __is_valid: bool | None = None
    __size: QSize | None = None

    def __init__(self, path: str, stat: os.stat_result):
        self.path = path
        self.stat = stat

    @property
    def is_valid(self) -> bool:
        if self.__is_valid is None:
            pm = QPixmap(self.path)
            self.__is_valid = not pm.isNull() and pm.height() > 0 and pm.width() > 0
        return self.__is_valid

    @property
    def size(self) -> QSize:
        if self.__size is None:
            pm = QPixmap(self.path)
            self.__size = pm.size()
        return self.__size

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.path == self.path

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return f"<ImageFile path={self.path}>"

    def scaled_width(self, height: float) -> float:
        return self.size.width() * (height / self.size.height())
