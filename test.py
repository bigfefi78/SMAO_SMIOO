"""
Test DisplacementIndicator
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

# Import dal package
from custom_widgets import DisplacementIndicator


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test DisplacementIndicator")
        self.resize(900, 300)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel("🎨 Test Indicatore Custom")
        info.setStyleSheet("background: #E3F2FD; padding: 10px;")
        layout.addWidget(info)
        
        # Indicatore
        self.indicator = DisplacementIndicator()
        self.indicator.label = "TEST"
        self.indicator.unit = "mm"
        layout.addWidget(self.indicator)
        
        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Valore:"))
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setValue(25)
        self.slider.valueChanged.connect(self.indicator.setValue)
        slider_layout.addWidget(self.slider)
        
        self.slider_label = QLabel("+025.00")
        # self.slider_label.setMinimumWidth(70)
        slider_layout.addWidget(self.slider_label)
        
        layout.addLayout(slider_layout)
        
        # Pulsanti
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("-100", clicked=lambda: self.set_value(-100)))
        btn_layout.addWidget(QPushButton("-85", clicked=lambda: self.set_value(-85)))
        btn_layout.addWidget(QPushButton("0", clicked=lambda: self.set_value(0)))
        btn_layout.addWidget(QPushButton("+85", clicked=lambda: self.set_value(85)))
        btn_layout.addWidget(QPushButton("+100", clicked=lambda: self.set_value(100)))
        layout.addLayout(btn_layout)
        
        # Status
        self.label_status = QLabel("Status: OK")
        self.label_status.setStyleSheet("background: #4CAF50; color: white; padding: 8px;")
        layout.addWidget(self.label_status)
        
        self.setLayout(layout)
        
        # Connetti segnali
        self.indicator.valueChanged.connect(self.on_value_changed)
        self.indicator.limitExceeded.connect(self.on_limit_exceeded)
    
    def set_value(self, value):
        self.indicator.setValue(value)
        self.slider.setValue(int(value))
    
    def on_value_changed(self, value):
        self.slider_label.setText(f"{value:+07.2f}")
    
    def on_limit_exceeded(self, exceeded):
        if exceeded:
            self.label_status.setText(f"⚠️  FUORI LIMITE: {self.indicator.value:+.2f}")
            self.label_status.setStyleSheet("background: #FF8A80; color: white; padding: 8px;")
        else:
            self.label_status.setText(f"✓ OK: {self.indicator.value:+.2f}")
            self.label_status.setStyleSheet("background: #4CAF50; color: white; padding: 8px;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("✅ Test avviato")
    
    sys.exit(app.exec_())