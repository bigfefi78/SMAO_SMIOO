"""
TEST STEP 4: Verifica widget riorganizzato
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

# ✅ Import dalla nuova posizione
from widgets import DisplacementIndicator

print("="*60)
print("TEST STEP 4: WIDGET RIORGANIZZATO")
print("="*60)

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test DisplacementIndicator - Step 4")
        self.resize(900, 300)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel("🎨 Test Widget Riorganizzato")
        info.setStyleSheet("background: #E3F2FD; padding: 10px; font-weight: bold;")
        layout.addWidget(info)
        
        # ===== TEST 1: Widget base =====
        print("\n📋 TEST 1: Creazione widget base")
        self.indicator1 = DisplacementIndicator()
        self.indicator1.label = "T-01"
        self.indicator1.unit = "µm"
        self.indicator1.value = 25.0
        layout.addWidget(self.indicator1)
        print("  ✓ Widget 1 creato")
        
        # ===== TEST 2: Widget con configurazione custom =====
        print("\n📋 TEST 2: Widget con configurazione custom")
        self.indicator2 = DisplacementIndicator()
        self.indicator2.label = "T-02"
        self.indicator2.unit = "mm"
        self.indicator2.value = -45.5
        self.indicator2.minRange = -50.0
        self.indicator2.maxRange = 50.0
        self.indicator2.minLimit = -40.0
        self.indicator2.maxLimit = 40.0
        layout.addWidget(self.indicator2)
        print("  ✓ Widget 2 creato")
        
        # Slider per controllare valore
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Controllo valore:"))
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setValue(25)
        self.slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.slider)
        
        self.slider_label = QLabel("+025.00")
        self.slider_label.setMinimumWidth(70)
        slider_layout.addWidget(self.slider_label)
        
        layout.addLayout(slider_layout)
        
        # Pulsanti test
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("-100", clicked=lambda: self.set_value(-100)))
        btn_layout.addWidget(QPushButton("-85", clicked=lambda: self.set_value(-85)))
        btn_layout.addWidget(QPushButton("0", clicked=lambda: self.set_value(0)))
        btn_layout.addWidget(QPushButton("+85", clicked=lambda: self.set_value(85)))
        btn_layout.addWidget(QPushButton("+100", clicked=lambda: self.set_value(100)))
        layout.addLayout(btn_layout)
        
        # Status
        self.label_status = QLabel("✓ Widgets caricati correttamente")
        self.label_status.setStyleSheet("background: #4CAF50; color: white; padding: 8px;")
        layout.addWidget(self.label_status)
        
        self.setLayout(layout)
        
        # Connetti segnali
        self.indicator1.valueChanged.connect(self.on_value_changed)
        self.indicator1.limitExceeded.connect(self.on_limit_exceeded)
        
        print("\n✅ Setup completato")
    
    def set_value(self, value):
        self.indicator1.setValue(value)
        self.indicator2.setValue(value)
        self.slider.setValue(int(value))
    
    def on_slider_changed(self, value):
        self.indicator1.setValue(value)
        self.indicator2.setValue(value)
        self.slider_label.setText(f"{value:+07.2f}")
    
    def on_value_changed(self, value):
        pass
    
    def on_limit_exceeded(self, exceeded):
        if exceeded:
            self.label_status.setText(f"⚠️  FUORI LIMITE: {self.indicator1.value:+.2f}")
            self.label_status.setStyleSheet("background: #FF8A80; color: white; padding: 8px;")
        else:
            self.label_status.setText(f"✓ OK: {self.indicator1.value:+.2f}")
            self.label_status.setStyleSheet("background: #4CAF50; color: white; padding: 8px;")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Avvio applicazione Qt...")
    print("="*60 + "\n")
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())