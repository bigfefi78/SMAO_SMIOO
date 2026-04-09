"""
TEST STEP 5: Integrazione completa SensorManager + Widget
"""

import sys
from PyQt5.QtWidgets import QApplication

from ui import MainWindow

# print("=" * 60)
# print("TEST STEP 5: INTEGRAZIONE COMPLETA")
# print("=" * 60)

if __name__ == "__main__":
    print("\n[TEST] Avvio applicazione...")

    app = QApplication(sys.argv)

    # Crea finestra principale
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
