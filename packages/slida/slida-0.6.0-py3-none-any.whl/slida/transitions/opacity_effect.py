import math
import random
from abc import abstractmethod

from klaatu_python.utils import coerce_between
from PySide6.QtCore import QEasingCurve, QPoint, QPointF, Qt
from PySide6.QtGui import (
    QConicalGradient,
    QGradient,
    QLinearGradient,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect

from slida.transitions.base import EffectTransition


class OpacityEffectTransition(EffectTransition[QGraphicsOpacityEffect]):
    @abstractmethod
    def create_brush(self, value: float) -> QGradient:
        ...

    def get_black_pos(self, progress: float) -> float:
        return progress

    def get_effect(self):
        parent = self.parent()
        effect = parent.graphicsEffect()

        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(parent)
            parent.setGraphicsEffect(effect)

        return effect

    def get_transparent_pos(self, progress: float) -> float:
        return progress

    def on_progress(self, value):
        super().on_progress(value)
        effect = self.get_effect()

        if value < 1.0:
            brush = self.create_brush(value)
            effect.setEnabled(True)
            effect.setOpacity(1.0)
            transparent_pos = coerce_between(self.get_transparent_pos(value), 0.0, 1.0)
            black_pos = coerce_between(self.get_black_pos(value), 0.0, 1.0)
            brush.setColorAt(transparent_pos, Qt.GlobalColor.transparent)
            brush.setColorAt(black_pos, Qt.GlobalColor.black)
            effect.setOpacityMask(brush)
        else:
            effect.setEnabled(False)


class ExplodeImplodeTransition(OpacityEffectTransition):
    def create_brush(self, value):
        rect = self.parent().rect()
        # - Vad är det som är vitt och kladdigt i matteboken?
        # - Pythagoras sats.
        corner_radius = math.sqrt(pow(rect.width() / 2, 2) + pow(rect.height() / 2, 2))

        return QRadialGradient(rect.center(), value * corner_radius)

    def get_transparent_pos(self, progress):
        return progress + 0.01


class BlindsOut(OpacityEffectTransition):
    easing = QEasingCurve.Type.OutSine

    def create_brush(self, value):
        brush = QLinearGradient(QPoint(0, 0), QPoint(50, 0))
        brush.setSpread(QGradient.Spread.RepeatSpread)

        return brush

    def get_black_pos(self, progress):
        return progress + 0.01


class ClockfaceOut(OpacityEffectTransition):
    easing = QEasingCurve.Type.InOutSine

    def create_brush(self, value):
        return QConicalGradient(self.parent().rect().center(), 0)

    def get_black_pos(self, progress):
        return progress + 0.02


class ExplodeIn(ExplodeImplodeTransition):
    easing = QEasingCurve.Type.OutExpo
    parent_z = 1.0


class ImplodeOut(ExplodeImplodeTransition):
    easing = QEasingCurve.Type.OutBounce
    end_value = 0.0
    start_value = 1.0


class RadialOut(OpacityEffectTransition):
    easing = QEasingCurve.Type.OutCirc
    offset: tuple[float, float] = 0.0, 0.0

    def __init__(self, name, parent, duration):
        self.offset = random.random(), random.random()
        super().__init__(name, parent, duration)

    def create_brush(self, value):
        rect = self.parent().rect()
        center = QPointF(rect.width() * self.offset[0], rect.height() * self.offset[1])
        brush = QRadialGradient(center, 25)
        brush.setSpread(QGradient.Spread.ReflectSpread)

        return brush

    def get_black_pos(self, progress):
        return progress + 0.1
