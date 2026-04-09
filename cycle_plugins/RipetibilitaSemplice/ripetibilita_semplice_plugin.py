import time
from core.cycle_plugin_base import CyclePluginBase
from cycle_plugins.RipetibilitaSemplice.ripetibilita_semplice_ui import (
    Ui_CicloRipetibilitaForm,
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import datetime


class RipetibilitaPlugin(CyclePluginBase):
    """
    Ciclo di ripetibilità semplice:
    - acquisizione misure in loop.
    - Nessun controllo IO, solo timing.
    """

    LABEL = "Ciclo Ripetibilità SEMPLICE"
    DESCRIPTION = "Ripetizione semplice di N acquisizioni."

    # Segnale che invia il dato step
    step_data_ready = pyqtSignal(object)  # signal: dict {step, timestamp, measurements}
    reset_visualization = pyqtSignal()  # nuovo segnale

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.ui = Ui_CicloRipetibilitaForm()
        self.ui.setupUi(self)
        self.api = api

        # All'avvio: frame disabilitati, checkbox non selezionata
        self.ui.frame_cycle.setEnabled(False)
        self.ui.checkEnableMod.setChecked(False)

        self.ui.checkEnableMod.stateChanged.connect(self.toggle_frames)
        self.ui.btnStart.clicked.connect(self.toggle_start_pause)
        self.ui.btnStop.clicked.connect(self.stop_cycle)

        self.is_running = False
        self.is_paused = False
        self.step_state = 0
        self.cycle_count = 0
        self.num_cycles = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_step)
        self.progressBar = self.ui.progressBar
        self.progLabel = self.ui.progLabel

        # Parametri per step machine
        self.wait_start_time = None

    def toggle_frames(self, state):
        enabled = state == Qt.Checked
        self.ui.frame_cycle.setEnabled(enabled)

    def toggle_start_pause(self):
        if not self.is_running:
            self.start_cycle()
        else:
            self.pause_cycle()

    def start_cycle(self):
        if not self.is_running:
            self.reset_visualization.emit()  # SOLO all'avvio vero!

        self.num_cycles = self.ui.numCycles.value()
        self.meas_wait = self.ui.MeasWaitTime_ms.value()

        self.cycle_count = 0
        self.step_state = 0
        self.is_running = True
        self.is_paused = False
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(self.num_cycles)
        self.ui.btnStart.setText("PAUSA")
        self.ui.btnStart.setStyleSheet("background-color: orange; color: black;")
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(True)
        self.api.logger.clear()
        self.timer.start(25)

        self.api.logger.info(
            f"Avvio ciclo ripetibilità s emplice: {self.num_cycles} cicli,  MeasWait={self.meas_wait}ms."
        )
        # Reset per visualizzazione
        self.data_steps = []

    def pause_cycle(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop()
            self.ui.btnStart.setText("START")
            self.ui.btnStart.setStyleSheet("background-color: green; color:white;")
            self.api.logger.info("Ciclo in pausa.")
        else:
            self.timer.start(50)
            self.ui.btnStart.setText("PAUSA")
            self.ui.btnStart.setStyleSheet("background-color: orange; color: black;")
            self.api.logger.info("Ciclo ripreso.")

    def stop_cycle(self):
        self.is_running = False
        self.is_paused = False
        self.timer.stop()
        self.progressBar.setValue(0)
        self.ui.btnStart.setText("START")
        self.ui.btnStart.setStyleSheet("background-color: green; color:white;")
        if self.cycle_count < self.num_cycles:
            self.api.logger.warning("Ciclo interrotto da utente")

    def _now_ms(self):
        return int(time.time() * 1000)

    def cycle_step(self):
        if not self.is_running or self.is_paused:
            return

        if self.step_state == 0:
            measures = self.api.get_enabled_measurements()
            measurements_dict = {}
            for m in measures:
                success = self.api.calculate_measurement(m)
                if success and m.current_value[1] is not None:
                    # self.api.logger.info(
                    #     f"Misura '{m.name}': Valore={m.current_value}, Codice={m.product_code}, Matricola={m.product_serial_number}, Desc={m.product_description}"
                    # )
                    measurements_dict[m.name] = m.current_value
                else:
                    self.api.logger.error(f"Errore acquisizione misura '{m.name}'")
                    measurements_dict[m.name] = (
                        999999  # valore di errore per visualizzazione
                    )

            step_dict = {
                "step": self.cycle_count + 1,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "measurements": measurements_dict,
            }
            # Segnale dati/aggiornamento verso CyclePage
            self.step_data_ready.emit(step_dict)
            self.step_state = 1  # aggiorno lo stato per il prossimo step
            self.api.logger.info(
                f"Ciclo {self.cycle_count}/{self.num_cycles} completato."
            )
            self.cycle_count += 1  # incremento il contatore cicli (sto contando le acquisizioni effettuate)
            self.wait_start_time = (
                self._now_ms()
            )  # memorizzo il tempo di inizio step successivo
        elif self.step_state == 1:
            self.progressBar.setValue(self.cycle_count)
            if self.cycle_count >= self.num_cycles:
                self.stop_cycle()
                self.api.logger.info(
                    "Ciclo di ripetibilità semplice completato.",
                    {self.__class__.__name__},
                )
                return
            else:
                if self._now_ms() - self.wait_start_time >= self.meas_wait:
                    self.step_state = 0  # mi riporto allo step 0 per acquisire nuovamente le misure (ciclo semplice)
                    self.progLabel.setText(f"{self.cycle_count}/{self.num_cycles}")
