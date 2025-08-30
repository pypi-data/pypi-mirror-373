from typing import TypeVar, cast

from klaatu_python.case import KebabCase, PascalCase, convert_case
from PySide6.QtCore import (
    QAbstractAnimation,
    QAnimationGroup,
    QObject,
    QParallelAnimationGroup,
    QSequentialAnimationGroup,
    Slot,
)
from PySide6.QtWidgets import QGraphicsWidget

from slida.debug import add_live_object, remove_live_object
from slida.transitions.base import Transition


_TP = TypeVar("_TP", bound="TransitionPair")


class TransitionPair(QObject):
    animation_group: QAnimationGroup
    enter_class: type[Transition]
    exit_class: type[Transition]
    name: str

    animation_group_type: type[QAnimationGroup] = QParallelAnimationGroup
    enter: Transition | None = None
    exit: Transition | None = None

    def __init__(
        self,
        parent: QObject,
        enter_parent: QGraphicsWidget | None,
        exit_parent: QGraphicsWidget | None,
        duration: int,
    ):
        super().__init__(parent)
        self.animation_group = self.animation_group_type(parent)

        add_live_object(id(self), self.__class__.__name__)

        if exit_parent:
            self.exit = self.exit_class(name=self.name, parent=exit_parent, duration=duration)
            self.animation_group.addAnimation(self.exit.animation)
        if enter_parent:
            self.enter = self.enter_class(name=self.name, parent=enter_parent, duration=duration)
            self.animation_group.addAnimation(self.enter.animation)

        self.animation_group.stateChanged.connect(self.on_animation_state_changed)

    def deleteLater(self):
        remove_live_object(id(self))
        self.animation_group.deleteLater()
        super().deleteLater()

    @Slot(QAbstractAnimation.State, QAbstractAnimation.State)
    def on_animation_state_changed(self, new_state: QAbstractAnimation.State, old_state: QAbstractAnimation.State):
        if new_state == QAbstractAnimation.State.Running and old_state != new_state:
            if self.enter:
                self.enter.on_animation_group_start()
            if self.exit:
                self.exit.on_animation_group_start()
        elif new_state == QAbstractAnimation.State.Stopped and old_state != new_state:
            try:
                if self.enter:
                    self.enter.on_animation_group_finish()
                if self.exit:
                    self.exit.on_animation_group_finish()
                self.animation_group.stateChanged.disconnect(self.on_animation_state_changed)
                self.deleteLater()
            except RuntimeError:
                pass


class SequentialTransitionPair(TransitionPair):
    animation_group_type = QSequentialAnimationGroup

    def __init__(self, parent, enter_parent, exit_parent, duration):
        super().__init__(parent, enter_parent, exit_parent, int(duration / 2))
        if self.exit:
            self.exit.finished.connect(self.on_exit_animation_finish)

    @Slot()
    def on_exit_animation_finish(self):
        if self.exit:
            self.exit.parent().hide()


def transition_pair_factory(
    name: str,
    enter_class: type[Transition],
    exit_class: type[Transition],
    pair_class: type[_TP] = TransitionPair,
) -> type[_TP]:
    return cast(type[_TP], type(
        convert_case(name, source=KebabCase, target=PascalCase),
        (pair_class,),
        {
            "name": name,
            "enter_class": enter_class,
            "exit_class": exit_class,
        }
    ))
