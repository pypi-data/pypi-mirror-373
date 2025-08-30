from PySide6.QtCore import QEasingCurve
from PySide6.QtWidgets import QGraphicsBlurEffect

from slida.transitions.base import EffectTransition


class BlurTransition(EffectTransition[QGraphicsBlurEffect]):
    def cleanup(self):
        super().cleanup()
        self.parent().setOpacity(1.0)

    def get_effect(self):
        parent = self.parent()
        effect = parent.graphicsEffect()

        if not isinstance(effect, QGraphicsBlurEffect):
            effect = QGraphicsBlurEffect(parent, blurHints=QGraphicsBlurEffect.BlurHint.AnimationHint)
            parent.setGraphicsEffect(effect)

        return effect

    def on_progress(self, value: float):
        super().on_progress(value)
        self.parent().setOpacity(1 - (value / 100))
        effect = self.get_effect()

        if value > 0.0:
            effect.setEnabled(True)
            effect.setBlurRadius(value)
        else:
            effect.setEnabled(False)


class BlurDecrease(BlurTransition):
    easing = QEasingCurve.Type.InBounce
    end_value = 0.0
    start_value = 100.0


class BlurIncrease(BlurTransition):
    easing = QEasingCurve.Type.InCubic
    end_value = 100.0
