from typing import TYPE_CHECKING

from PySide6.QtCore import QSizeF
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import (
    QGraphicsSceneResizeEvent,
    QGraphicsWidget,
    QStyleOptionGraphicsItem,
    QWidget,
)

from slida.debug import add_live_object, remove_live_object


if TYPE_CHECKING:
    from slida.files.manager import ImageFileManager
    from slida.qt.image_screen import ImageScreen
    from slida.transitions import Transition


class ImageScreenWidget(QGraphicsWidget):
    __image_file_manager: "ImageFileManager"
    __image_screen: "ImageScreen"
    __qimage: QImage
    __screen_idx: int
    __transition: "Transition | None" = None

    def __init__(self, image_file_manager: "ImageFileManager", screen_idx: int, size: QSizeF):
        self.__screen_idx = screen_idx
        self.__image_file_manager = image_file_manager
        self.__image_screen = image_file_manager.get_image_screen(screen_idx, size)
        self.__qimage = self.__image_screen.get_outer_qimage()
        super().__init__(size=size)
        add_live_object(id(self), self.__class__.__name__)

    def deleteLater(self):
        if self.__transition:
            self.__transition.deleteLater()
        remove_live_object(id(self))
        super().deleteLater()

    def get_current_filenames(self):
        return [i.path for i in self.__image_screen.images]

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None):
        if self.__transition:
            self.__transition.paint(painter, self.__qimage, self.__image_screen.inner_rect)
        else:
            painter.drawImage(self.rect(), self.__qimage)

    def resizeEvent(self, event: QGraphicsSceneResizeEvent):
        super().resizeEvent(event)
        if self.size() != self.__image_screen.bounds:
            self.__image_screen = self.__image_file_manager.get_image_screen(self.__screen_idx, self.size())
            self.__qimage = self.__image_screen.get_outer_qimage()

    def set_transition(self, transition: "Transition | None"):
        if self.__transition:
            self.__transition.deleteLater()
        if transition:
            transition.setParent(self)
        self.__transition = transition
