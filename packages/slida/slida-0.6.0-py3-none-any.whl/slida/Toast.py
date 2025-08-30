from PySide6.QtCore import QSize, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QDockWidget, QLabel

from slida.debug import add_live_object, remove_live_object


class Toast(QDockWidget):
    hidden = Signal()
    resized = Signal(QSize)
    shown = Signal()

    def __init__(self, parent, timeout: int | None = 3000, background: QPalette.ColorRole = QPalette.ColorRole.Accent):
        super().__init__(parent)
        self.setMinimumHeight(30)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setBackgroundRole(background)
        self.label.setAutoFillBackground(True)
        self.label.setMinimumHeight(30)
        self.timeout = timeout
        super().hide()

        add_live_object(id(self), self.__class__.__name__)

        if self.timeout:
            self.timer = QTimer(self, singleShot=True, interval=self.timeout)
            self.timer.timeout.connect(self.on_timeout)

    def deleteLater(self):
        remove_live_object(id(self))
        super().deleteLater()

    def hide(self):
        super().hide()
        self.hidden.emit()

    @Slot()
    def on_timeout(self):
        self.hide()

    def resizeEvent(self, event):
        self.label.setFixedWidth(self.width())
        self.resized.emit(self.size())
        return super().resizeEvent(event)

    def set_text(self, text: str):
        rows = text.split("\n")
        self.setMinimumHeight(20 + (10 * len(rows)))
        self.label.setMinimumHeight(20 + (10 * len(rows)))
        self.label.setText(text)

    def show(self):
        super().show()
        if self.timeout:
            self.timer.start()
        self.shown.emit()
