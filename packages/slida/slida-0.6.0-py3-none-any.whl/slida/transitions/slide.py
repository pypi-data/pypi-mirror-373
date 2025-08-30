from PySide6.QtCore import QEasingCurve

from slida.transitions.base import Transition


class HorizontalSlideTransition(Transition):
    easing = QEasingCurve.Type.OutBack
    end_value = 0.0
    property_name = "x"

    def cleanup(self):
        super().cleanup()
        self.parent().setX(0.0)


class VerticalSlideTransition(Transition):
    easing = QEasingCurve.Type.OutBack
    end_value = 0.0
    property_name = "y"

    def cleanup(self):
        super().cleanup()
        self.parent().setY(0.0)


class SlideInFromBottom(VerticalSlideTransition):
    def get_start_value(self):
        return self.parent().size().height()


class SlideInFromLeft(HorizontalSlideTransition):
    def get_start_value(self):
        return self.parent().size().width() * -1


class SlideInFromRight(HorizontalSlideTransition):
    def get_start_value(self):
        return self.parent().size().width()


class SlideInFromTop(VerticalSlideTransition):
    def get_start_value(self):
        return self.parent().size().height() * -1


class SlideOutToBottom(VerticalSlideTransition):
    def get_end_value(self):
        return self.parent().size().height()


class SlideOutToLeft(HorizontalSlideTransition):
    def get_end_value(self):
        return self.parent().size().width() * -1


class SlideOutToRight(HorizontalSlideTransition):
    def get_end_value(self):
        return self.parent().size().width()


class SlideOutToTop(VerticalSlideTransition):
    def get_end_value(self):
        return self.parent().size().height() * -1
