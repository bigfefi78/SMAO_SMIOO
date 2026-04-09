"""
Test valori fuori range
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from widgets import DisplacementIndicator

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Test Fuori Range")
window.resize(800, 400)
layout = QVBoxLayout(window)

# Widget con range -100/+100
indicator = DisplacementIndicator()
indicator.label = "TEST"
indicator.unit = "µm"
indicator.minRange = -100.0
indicator.maxRange = 100.0
indicator.minLimit = -80.0
indicator.maxLimit = 80.0
indicator.value = 0.0
layout.addWidget(indicator)

# Pulsanti test
layout.addWidget(QPushButton("Valore -150 (fuori range sx)", clicked=lambda: indicator.setValue(-150)))
layout.addWidget(QPushButton("Valore -85 (fuori limite)", clicked=lambda: indicator.setValue(-85)))
layout.addWidget(QPushButton("Valore 0 (OK)", clicked=lambda: indicator.setValue(0)))
layout.addWidget(QPushButton("Valore +85 (fuori limite)", clicked=lambda: indicator.setValue(85)))
layout.addWidget(QPushButton("Valore +150 (fuori range dx)", clicked=lambda: indicator.setValue(150)))

window.show()
sys.exit(app.exec_())