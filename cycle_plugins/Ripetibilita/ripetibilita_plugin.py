from core.cycle_plugin_base import CyclePluginBase
from cycle_plugins.Ripetibilita.ripetibilita_ui import Ui_CicloRipetibilitaForm
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import datetime


class RipetibilitaPlugin(CyclePluginBase):
    LABEL = "Ciclo Ripetibilità STANDARD"
    DESCRIPTION = (
        "Ripetizione ciclo pneumatico con parametri modificabili e controllo live."
    )

    step_data_ready = pyqtSignal(object)  # signal: dict {step, timestamp, measurements}
    reset_visualization = pyqtSignal()  # nuovo segnale

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.ui = Ui_CicloRipetibilitaForm()
        self.ui.setupUi(self)
        self.api = api

        self.ui.frame_io.setEnabled(False)
        self.ui.frame_cycle.setEnabled(False)
        self.ui.checkEnableMod.setChecked(False)

        self.ui.checkEnableMod.stateChanged.connect(self.toggle_frames)
        self.ui.btnStart.clicked.connect(self.toggle_start_pause)
        self.ui.btnStop.clicked.connect(self.stop_cycle)

        self.is_running = False
        self.is_paused = False
        self.is_first_cycle = True  # flag per avvio (NO reset su ripresa!)
        self.step_state = 0
        self.cycle_count = 0
        self.num_cycles = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_step)
        self.progressBar = self.ui.progressBar
        self.wait_start_time = None

    def toggle_frames(self, state):
        enabled = state == Qt.Checked
        self.ui.frame_io.setEnabled(enabled)
        self.ui.frame_cycle.setEnabled(enabled)

    def toggle_start_pause(self):
        if not self.is_running:
            self.start_cycle()
        else:
            self.pause_cycle()

    def start_cycle(self):
        self.in_meas = self.ui.in_meas_switch.value()
        self.in_home = self.ui.in_home_switch.value()
        self.out_ev = self.ui.out_EV.value()
        self.num_cycles = self.ui.numCycles.value()
        self.meas_wait = self.ui.MeasWaitTime_ms.value()
        self.home_wait = self.ui.HomeMeasWait.value()
        self.step_wait = self.ui.StepWait.value()

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
        self.timer.start(50)

        self.api.logger.info(
            f"Avvio ciclo ripetibilità: {self.num_cycles} cicli, EV={self.out_ev}, MeasWait={self.meas_wait}ms, HomeWait={self.home_wait}ms, StepWait={self.step_wait}ms"
        )
        # Solo all'avvio ciclo, NON dopo pause!
        if self.is_first_cycle:
            self.reset_visualization.emit()
            self.is_first_cycle = False

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
        self.api.set_output(self.out_ev, 0)
        if self.cycle_count < self.num_cycles:
            self.api.logger.warning("Ciclo interrotto da utente")
        self.is_first_cycle = True  # reset per prossimo avvio ciclo

    def _now_ms(self):
        import time

        return int(time.time() * 1000)

    def cycle_step(self):
        if not self.is_running or self.is_paused:
            return

        if self.step_state == 0:
            self.api.set_output(self.out_ev, 1)
            self.api.logger.info("EV aperta")
            self.step_state = 1
        elif self.step_state == 1:
            if self.api.read_input(self.in_meas):
                self.wait_start_time = self._now_ms()
                self.step_state = 2
        elif self.step_state == 2:
            if self._now_ms() - self.wait_start_time >= self.meas_wait:
                self.step_state = 3
        elif self.step_state == 3:
            measures = self.api.get_enabled_measurements()
            measurements_dict = {}
            for m in measures:
                success = self.api.calculate_measurement(m)
                if success and m.current_value is not None:
                    self.api.logger.info(
                        f"Misura '{m.name}': Valore={m.current_value}, Codice={m.product_code}, Matricola={m.product_serial_number}, Desc={m.product_description}"
                    )
                    measurements_dict[m.name] = m.current_value
                else:
                    self.api.logger.error(f"Errore acquisizione misura '{m.name}'")
            step_dict = {
                "step": self.cycle_count + 1,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "measurements": measurements_dict,
            }
            self.step_data_ready.emit(step_dict)

            self.wait_start_time = self._now_ms()
            self.step_state = 4
        elif self.step_state == 4:
            if self._now_ms() - self.wait_start_time >= self.step_wait:
                self.step_state = 5
        elif self.step_state == 5:
            self.api.set_output(self.out_ev, 0)
            self.api.logger.info("EV chiusa")
            self.step_state = 6
        elif self.step_state == 6:
            if self.api.read_input(self.in_home):
                self.wait_start_time = self._now_ms()
                self.step_state = 7
        elif self.step_state == 7:
            if self._now_ms() - self.wait_start_time >= self.home_wait:
                self.step_state = 8
        elif self.step_state == 8:
            self.cycle_count += 1
            self.progressBar.setValue(self.cycle_count)
            self.api.logger.info(
                f"Ciclo {self.cycle_count}/{self.num_cycles} completato."
            )
            if self.cycle_count >= self.num_cycles:
                self.stop_cycle()
                self.api.logger.info("Ciclo ripetibilità completato.")
                return
            else:
                self.step_state = 0


# from core.cycle_plugin_base import CyclePluginBase
# from cycle_plugins.Ripetibilita.ripetibilita_ui import Ui_CicloRipetibilitaForm
# from PyQt5.QtCore import QTimer, Qt


# class RipetibilitaPlugin(CyclePluginBase):
#     LABEL = "Ciclo Ripetibilità STANDARD"
#     DESCRIPTION = (
#         "Ripetizione ciclo pneumatico con parametri modificabili e controllo live."
#     )

#     def __init__(self, api, parent=None):
#         super().__init__(parent)
#         self.ui = Ui_CicloRipetibilitaForm()
#         self.ui.setupUi(self)
#         self.api = api

#         # All'avvio: frame disabilitati, checkbox non selezionata
#         self.ui.frame_io.setEnabled(False)
#         self.ui.frame_cycle.setEnabled(False)
#         self.ui.checkEnableMod.setChecked(False)

#         # Gestione modifica parametri: una sola checkbox!
#         self.ui.checkEnableMod.stateChanged.connect(self.toggle_frames)

#         # Pulsanti controllo ciclo
#         self.ui.btnStart.clicked.connect(self.toggle_start_pause)
#         self.ui.btnStop.clicked.connect(self.stop_cycle)

#         self.is_running = False
#         self.is_paused = False
#         self.step_state = 0
#         self.cycle_count = 0
#         self.num_cycles = 0
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.cycle_step)
#         self.progressBar = self.ui.progressBar

#         # Parametri per step machine
#         self.wait_start_time = None

#     def toggle_frames(self, state):
#         enabled = state == Qt.Checked
#         self.ui.frame_io.setEnabled(enabled)
#         self.ui.frame_cycle.setEnabled(enabled)

#     def toggle_start_pause(self):
#         if not self.is_running:
#             self.start_cycle()
#         else:
#             self.pause_cycle()

#     def start_cycle(self):
#         if not self.is_running:
#             self.reset_visualization.emit()  # SOLO al primo avvio vero pulisco la grafica

#         # Leggi parametri (sempre dagli spinbox, indipendentemente dallo stato enabled)
#         self.in_meas = self.ui.in_meas_switch.value()
#         self.in_home = self.ui.in_home_switch.value()
#         self.out_ev = self.ui.out_EV.value()
#         self.num_cycles = self.ui.numCycles.value()
#         self.meas_wait = self.ui.MeasWaitTime_ms.value()
#         self.home_wait = self.ui.HomeMeasWait.value()
#         self.step_wait = self.ui.StepWait.value()

#         self.cycle_count = 0
#         self.step_state = 0
#         self.is_running = True
#         self.is_paused = False
#         self.progressBar.setValue(0)
#         self.progressBar.setMaximum(self.num_cycles)
#         self.ui.btnStart.setText("PAUSA")
#         self.ui.btnStart.setStyleSheet("background-color: orange; color: black;")
#         self.ui.btnStart.setEnabled(True)
#         self.ui.btnStop.setEnabled(True)
#         self.api.logger.clear()
#         self.timer.start(50)

#         self.api.logger.info(
#             f"Avvio ciclo ripetibilità: {self.num_cycles} cicli, EV={self.out_ev}, MeasWait={self.meas_wait}ms, HomeWait={self.home_wait}ms, StepWait={self.step_wait}ms"
#         )

#     def pause_cycle(self):
#         self.is_paused = not self.is_paused
#         if self.is_paused:
#             self.timer.stop()
#             self.ui.btnStart.setText("START")
#             self.ui.btnStart.setStyleSheet("background-color: green; color:white;")
#             self.api.logger.info("Ciclo in pausa.")
#         else:
#             self.timer.start(50)
#             self.ui.btnStart.setText("PAUSA")
#             self.ui.btnStart.setStyleSheet("background-color: orange; color: black;")
#             self.api.logger.info("Ciclo ripreso.")

#     def stop_cycle(self):
#         self.is_running = False
#         self.is_paused = False
#         self.timer.stop()
#         self.progressBar.setValue(0)
#         self.ui.btnStart.setText("START")
#         self.ui.btnStart.setStyleSheet("background-color: green; color:white;")
#         self.api.set_output(self.out_ev, 0)  # Assicurariamoci che l'EV chiusa.
#         if self.cycle_count < self.num_cycles:
#             self.api.logger.warning("Ciclo interrotto da utente")

#     def _now_ms(self):
#         # Usa l'orologio del motore, oppure time.time()
#         import time

#         return int(time.time() * 1000)

#     def cycle_step(self):
#         if not self.is_running or self.is_paused:
#             return

#         # Step machine per la sequenza del ciclo
#         if self.step_state == 0:  # Step 0: Apre EV
#             self.api.set_output(self.out_ev, 1)
#             self.api.logger.info("EV aperta")
#             self.step_state = 1
#         elif self.step_state == 1:  # Step 1: aspetta switch misura
#             if self.api.read_input(self.in_meas):
#                 self.wait_start_time = self._now_ms()
#                 self.step_state = 2
#         elif self.step_state == 2:  # Step 2: aspetta MeasWaitTime_ms
#             if self._now_ms() - self.wait_start_time >= self.meas_wait:
#                 self.step_state = 3
#         elif self.step_state == 3:  # Step 3: acquisizioni misure
#             measures = self.api.get_enabled_measurements()
#             for m in measures:
#                 success = self.api.calculate_measurement(m)
#                 if success and m.current_value is not None:
#                     self.api.logger.info(
#                         f"Misura '{m.name}': Valore={m.current_value}, Codice={m.product_code}, Matricola={m.product_serial_number}, Desc={m.product_description}"
#                     )
#                     # self.api.logger.info(f"Misura '{m.name}': {m.current_value}")
#                 else:
#                     self.api.logger.error(f"Errore acquisizione misura '{m.name}'")

#             # results = {m.name: self.api.calculate_measurement(m) for m in measures}
#             # self.api.logger.info(f"Misure acquisite: {results}")

#             self.wait_start_time = self._now_ms()
#             self.step_state = 4
#         elif self.step_state == 4:  # Step 4: aspetta StepWait
#             if self._now_ms() - self.wait_start_time >= self.step_wait:
#                 self.step_state = 5
#         elif self.step_state == 5:  # Step 5: chiude EV
#             self.api.set_output(self.out_ev, 0)
#             self.api.logger.info("EV chiusa")
#             self.step_state = 6
#         elif self.step_state == 6:  # Step 6: aspetta switch home
#             if self.api.read_input(self.in_home):
#                 self.wait_start_time = self._now_ms()
#                 self.step_state = 7
#         elif self.step_state == 7:  # Step 7: aspetta HomeMeasWait
#             if self._now_ms() - self.wait_start_time >= self.home_wait:
#                 self.step_state = 8
#         elif self.step_state == 8:  # Step 8: fine ciclo/successivo
#             self.cycle_count += 1
#             self.progressBar.setValue(self.cycle_count)
#             self.api.logger.info(
#                 f"Ciclo {self.cycle_count}/{self.num_cycles} completato."
#             )
#             if self.cycle_count >= self.num_cycles:
#                 self.stop_cycle()
#                 self.api.logger.info("Ciclo ripetibilità completato.")
#                 # self.ui.labelTitle.setText("Ciclo completato.")
#                 return
#             else:
#                 self.step_state = 0  # Nuovo ciclo
