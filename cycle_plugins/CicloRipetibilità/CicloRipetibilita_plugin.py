from core.cycle_plugin_base import CyclePluginBase
from cycle_plugins.CicloRipetibilità.CicloRipetibilita_ui import Ui_CicloRipetibilitaForm
from PyQt5.QtCore import QTimer

class CicloRipetibilita(CyclePluginBase):
    LABEL = "TEST SEMPLICE ON/OFF"
    DESCRIPTION = "Esegue attivazione ripetuta."

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.ui = Ui_CicloRipetibilitaForm()
        self.ui.setupUi(self)
        self.api = api
        self.ui.btnStart.clicked.connect(self.start_cycle)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_step)
        self.is_on = False
        self.current = 0
        self.total = 0

    def start_cycle(self):
        self.api.logger.clear()
        self.current = 0
        self.total = self.ui.spinRipetizioni.value()
        self.ui.progressBar.maximum = self.total
        self.ui.labelStatus.setText("Esecuzione in corso...")
        self.is_on = False
        self.timer.start(1000)  # Timer ogni 1 secondo

    def next_step(self):
        self.ui.progressBar.setValue(self.current)
        if self.current < self.total:
            if not self.is_on:
                self.api.set_output(10, 1)
                self.is_on = True
            else:
                self.api.set_output(10, 0)
                self.api.logger.warning(f"Ciclo {self.current+1}/{self.total} completato")
                self.current += 1
                self.is_on = False
        else:
            self.timer.stop()
            self.api.logger.info("Ciclo completato")