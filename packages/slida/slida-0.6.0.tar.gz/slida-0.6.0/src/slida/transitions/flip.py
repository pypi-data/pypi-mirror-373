from PySide6.QtCore import QEasingCurve, Qt
from PySide6.QtGui import QTransform

from slida.transitions.base import Transition


class FadeIn(Transition):
    property_name = "opacity"


class FadeOut(Transition):
    end_value = 0.0
    property_name = "opacity"
    start_value = 1.0

    def cleanup(self):
        super().cleanup()
        self.parent().setOpacity(1.0)


class FlipTransition(Transition):
    axis: Qt.Axis

    def on_progress(self, value: float):
        super().on_progress(value)
        size = self.parent().size()
        t = QTransform()
        # 1. Translate so (0, 0) is in the view's center:
        t.translate(size.width() / 2, size.height() / 2)
        # 2. Do the transformation:
        t.rotate(value * 90.0, self.axis, 2000.0)
        # 3. Translate back so stuff renders where it should:
        t.translate(-size.width() / 2, -size.height() / 2)
        self.parent().setTransform(t)
        self.parent().setVisible(True)


class FlipInTransition(FlipTransition):
    easing = QEasingCurve.Type.OutBack
    end_value = 0.0
    start_value = -1.0

    def on_animation_group_start(self):
        super().on_animation_group_start()
        self.parent().setVisible(False)

    def on_animation_start(self):
        super().on_animation_start()
        self.parent().setVisible(True)


class FlipOutTransition(FlipTransition):
    easing = QEasingCurve.Type.InSine

    def cleanup(self):
        super().cleanup()
        self.parent().setTransform(QTransform())


class FlipXIn(FlipInTransition):
    axis = Qt.Axis.XAxis


class FlipXOut(FlipOutTransition):
    axis = Qt.Axis.XAxis


class FlipYIn(FlipInTransition):
    axis = Qt.Axis.YAxis


class FlipYOut(FlipOutTransition):
    axis = Qt.Axis.YAxis
