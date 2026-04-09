from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QAxContainer import QAxWidget

app = QApplication([])

win = QWidget()
layout = QVBoxLayout(win)

bar = QAxWidget()
bar.setControl("BarMeasure.Bar")   # 👉 ProgID corretto

layout.addWidget(bar)

win.setGeometry(200, 200, 600, 120)
win.setWindowTitle("MeasureBar ActiveX in PyQt5")
win.show()

app.exec_()

# """
# Esempio completo: ToggleButton con SMIOO Output
# """
# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
# from PyQt5.QtCore import pyqtSlot

# from custom_widgets.toggle_button import ToggleButton
# from managers import SMIOOManager


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Controllo Output SMIOO con ToggleButton")
        
#         # Inizializza SMIOO
#         self.smioo = SMIOOManager()
#         self.output = None
        
#         if self.smioo.initialize_smioo():
#             self.smioo.get_info()
#             self.output = self.smioo.new_output_bit(11)
#         else:
#             print("⚠️ SMIOO non disponibile - modalità simulazione")
        
#         self.setup_ui()
    
#     def setup_ui(self):
#         """Crea l'interfaccia"""
#         central = QWidget()
#         layout = QVBoxLayout()
        
#         # Status label
#         if self.smioo.status:
#             status_text = "✓ SMIOO connesso"
#             status_color = "#4CAF50"
#         else:
#             status_text = "✗ SMIOO non disponibile"
#             status_color = "#F44336"
        
#         self.status_label = QLabel(status_text)
#         self.status_label.setStyleSheet(f"""
#             background-color: {status_color};
#             color: white;
#             font-weight: bold;
#             padding: 10px;
#             border-radius: 4px;
#         """)
#         layout.addWidget(self.status_label)
        
#         # Toggle Button
#         self.toggle_btn = ToggleButton()
#         self.toggle_btn.textOn = "OUTPUT 11 ON"
#         self.toggle_btn.textOff = "OUTPUT 11 OFF"
#         self.toggle_btn.colorOn = "#FF5722"
#         self.toggle_btn.colorOff = "#9E9E9E"
#         self.toggle_btn.stateChanged.connect(self.on_toggle_changed)
        
#         if not self.smioo.status:
#             self.toggle_btn.setEnabled(False)
        
#         layout.addWidget(self.toggle_btn)
        
#         central.setLayout(layout)
#         self.setCentralWidget(central)
#         self.resize(300, 200)
    
#     @pyqtSlot(bool)
#     def on_toggle_changed(self, is_on):
#         """Gestisce cambio stato toggle"""
#         print(f"\n{'='*40}")
#         print(f"Toggle Button: {'ON' if is_on else 'OFF'}")
        
#         if self.output:
#             try:
#                 self.output.WriteBitValue(is_on)
#                 print(f"✓ Output 11 scritto: {is_on}")
#             except Exception as e:
#                 print(f"✗ Errore scrittura output: {e}")
#         else:
#             print("⚠️ Modalità simulazione")
        
#         print(f"{'='*40}\n")
    
#     def closeEvent(self, event):
#         """Cleanup alla chiusura"""
#         if self.output:
#             try:
#                 self.output.WriteBitValue(False)
#                 print("✓ Output spento")
#             except:
#                 pass
        
#         if self.smioo:
#             self.smioo.shutdown()
        
#         event.accept()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())