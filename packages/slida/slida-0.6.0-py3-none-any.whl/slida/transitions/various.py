from PySide6.QtCore import QEasingCurve, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap

from slida.transitions.base import Transition


class HingeTransition(Transition):
    no_borders = True

    def on_progress(self, value: float):
        super().on_progress(value)
        self.parent().setRotation(value)


class ShrinkGrowTransition(Transition):
    property_name = "scale"

    def on_animation_group_start(self):
        super().on_animation_group_start()
        size = self.parent().size()
        self.parent().setTransformOriginPoint(size.width() / 2, size.height() / 2)


class FadeIn(Transition):
    property_name = "opacity"


class FadeOut(Transition):
    end_value = 0.0
    property_name = "opacity"
    start_value = 1.0

    def cleanup(self):
        super().cleanup()
        self.parent().setOpacity(1.0)


class FlashIn(Transition):
    easing = QEasingCurve.Type.OutSine
    parent_z = 1.0
    start_value = 1.0
    end_value = 0.0

    def on_progress(self, value: float):
        super().on_progress(value)
        self.parent().update(self.parent().rect())

    def paint(self, painter: QPainter, image: QImage, image_rect: QRectF):
        painter.drawImage(self.parent().rect(), image)

        if self._progress:
            overlay = QPixmap(self.parent().size().toSize())
            overlay.fill(QColor(255, 255, 255, int(self._progress * 255)))
            painter.drawPixmap(self.parent().rect().toRect(), overlay)


class Grow(ShrinkGrowTransition):
    easing = QEasingCurve.Type.OutExpo


class HingeIn(HingeTransition):
    easing = QEasingCurve.Type.OutBack
    end_value = 0.0
    parent_z = 1.0
    start_value = -90.0

    def on_animation_group_start(self):
        super().on_animation_group_start()
        self.parent().setTransformOriginPoint(0.0, self.parent().size().height())


class HingeOut(HingeTransition):
    end_value = -90.0
    start_value = 0.0

    def cleanup(self):
        super().cleanup()
        self.parent().setRotation(0.0)

    def on_animation_group_start(self):
        super().on_animation_group_start()
        size = self.parent().size()
        self.parent().setTransformOriginPoint(size.width(), size.height())


class Noop(Transition):
    end_value = 0.0


class Shrink(ShrinkGrowTransition):
    easing = QEasingCurve.Type.OutSine
    end_value = 0.0
    start_value = 1.0

    def cleanup(self):
        super().cleanup()
        self.parent().setScale(1.0)
