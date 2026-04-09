from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from .container_ui import Ui_ContainerWidget
from widgets.led_indicator.led_indicator_widget import LedIndicatorWidget
from PyQt5.QtCore import Qt


class ContainerWidget(QWidget):
    def __init__(self, label, is_input=True, parent=None):
        super().__init__(parent)
        self.ui = Ui_ContainerWidget()
        self.ui.setupUi(self)
        self.ui.labelType.setText(label)
        self.rows = []
        self.labels = []
        self.leds = []
        self.buttons = []

        self.is_input = is_input
        # signalContainer è QVBoxLayout
        self.signalLayout = self.ui.signalContainer

    def add_row(self, name, btn_label="Read", btn_checkable=False):
        row_layout = QHBoxLayout()
        lbl = QLabel(name)
        lbl.setMinimumWidth(45)
        lbl.setAlignment(Qt.AlignCenter)
        led = LedIndicatorWidget(self)
        led.setMinimumSize(32, 20)
        led.setMaximumSize(32, 20)
        btn = QPushButton(btn_label, self)
        btn.setEnabled(False)
        btn.setCheckable(btn_checkable)
        btn.setMinimumWidth(60)
        row_layout.addWidget(lbl)
        row_layout.addWidget(led)
        row_layout.addWidget(btn)
        self.signalLayout.addLayout(row_layout)
        self.rows.append((lbl, led, btn))
        self.labels.append(lbl)
        self.leds.append(led)
        self.buttons.append(btn)
        return lbl, led, btn
