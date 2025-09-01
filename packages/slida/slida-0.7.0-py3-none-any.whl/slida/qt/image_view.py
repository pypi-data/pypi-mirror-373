from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget

from slida.config import Config
from slida.debug import add_live_object, print_live_objects, remove_live_object
from slida.qt.image_screen_widget import ImageScreenWidget
from slida.transitions import NOOP


if TYPE_CHECKING:
    from slida.files.manager import ImageFileManager
    from slida.transitions import TransitionPair


class ImageView(QGraphicsView):
    __current_widget: ImageScreenWidget | None = None
    __image_file_manager: "ImageFileManager"
    __is_transitioning: bool = False
    __next_widget: ImageScreenWidget | None = None

    transition_finished = Signal()

    def __init__(self, image_file_manager: "ImageFileManager", parent: QWidget | None = None):
        super().__init__(parent)

        self.__image_file_manager = image_file_manager
        scene = QGraphicsScene(self)

        self.setScene(scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor.fromString(Config.current().background.value))

        add_live_object(id(self), self.__class__.__name__)

    @property
    def is_transitioning(self):
        return self.__is_transitioning

    def deleteLater(self):
        super().deleteLater()
        remove_live_object(id(self))

    def get_current_filenames(self):
        if self.__current_widget:
            return self.__current_widget.get_current_filenames()
        return []

    @Slot()
    def on_transition_finished(self):
        old_current = self.__current_widget
        self.__current_widget = self.__next_widget
        self.__is_transitioning = False

        if old_current:
            self.scene().removeItem(old_current)
            old_current.deleteLater()
            self.__next_widget = None

        self.transition_finished.emit()

    def resizeEvent(self, event):
        viewport_rect = self.viewport().rect()
        geometry = self.geometry()

        self.scene().setSceneRect(viewport_rect)
        if self.__current_widget:
            self.__current_widget.setGeometry(geometry)
        if self.__next_widget:
            self.__next_widget.setGeometry(geometry)
        super().resizeEvent(event)

    def transition_to(
        self,
        screen_idx: int,
        transition_pair_type: "type[TransitionPair] | None" = None,
        transition_duration: float = 0.0,
    ):
        if self.__is_transitioning:
            return

        if transition_pair_type is None:
            transition_pair_type = NOOP
            transition_duration = 0.0

        self.__next_widget = ImageScreenWidget(
            image_file_manager=self.__image_file_manager,
            screen_idx=screen_idx,
            size=self.size().toSizeF(),
        )
        self.scene().addItem(self.__next_widget)

        if self.__current_widget and self.__current_widget.isActive():
            self.__next_widget.stackBefore(self.__current_widget)

        transition_pair = transition_pair_type(
            parent=self,
            enter_parent=self.__next_widget,
            exit_parent=self.__current_widget,
            duration=int(transition_duration * 1000),
        )

        if Config.current().debug.value:
            print(
                f"enter_class={transition_pair.enter_class.__name__}, "
                f"exit_class={transition_pair.exit_class.__name__}"
            )
            if screen_idx % 10 == 0:
                print_live_objects()

        self.__next_widget.set_transition(transition_pair.enter)
        if self.__current_widget:
            self.__current_widget.set_transition(transition_pair.exit)

        self.__is_transitioning = True

        transition_pair.animation_group.finished.connect(self.on_transition_finished)
        transition_pair.animation_group.start()
