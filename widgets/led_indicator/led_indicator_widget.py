from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


class LedIndicatorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = False
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(32, 20)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.set_on(False)

    def set_on(self, value: bool):
        self._state = bool(value)
        color = "#43c852" if self._state else "#b42928"
        self.label.setStyleSheet(
            f"border-radius: 3px; background: {color}; border: 1px solid #333;"
        )
