from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt5.QtCore import Qt
from widgets import MeasurementIndicator
from core import MeasurementsEngine


class MeasurementsMonitorPage(QWidget):
    def __init__(self, measurements_engine: MeasurementsEngine, parent=None):
        super().__init__(parent)
        self.measurements_engine = measurements_engine
        self.measurement_widgets = {}
        self._setup_ui()
        print("[MeasurementsMonitorPage] Inizializzata")

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        header = QLabel("📏 VISUALIZZAZIONE MISURE")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.measurements_container = QWidget()
        self.measurements_layout = QVBoxLayout(self.measurements_container)
        self.measurements_layout.setSpacing(5)
        self.measurements_layout.setContentsMargins(5, 5, 5, 5)
        self.measurements_layout.addStretch()
        scroll_area.setWidget(self.measurements_container)
        main_layout.addWidget(scroll_area)

    def refresh_measurements(self):
        print("[MeasurementsMonitorPage] Refresh misure...")
        self._clear_widgets()
        enabled_measurements = self.measurements_engine.load_enabled_measurements()
        print(
            f"[MeasurementsMonitorPage] Trovate {len(enabled_measurements)} misure abilitate"
        )
        for measurement in enabled_measurements:
            widget = MeasurementIndicator(measurement, self)
            self.measurement_widgets[measurement.id] = widget
            self.measurements_layout.insertWidget(
                self.measurements_layout.count() - 1, widget
            )
        if not enabled_measurements:
            label = QLabel(
                "⚠️ Nessuna misura abilitata\n\nVai al tab 'Gestione Misure' per creare e abilitare misure"
            )
            label.setAlignment(Qt.AlignCenter)
            self.measurements_layout.insertWidget(0, label)

    def update_measurements_values(self):
        # Calcola tutto
        results = self.measurements_engine.calculate_all()

        for measurement_id, widget in self.measurement_widgets.items():
            measurement = widget.measurement
            success = results.get(measurement_id, False)

            # Se successo E il valore è numerico -> Passa il numero
            # Altrimenti (successo False o valore None) -> Passa None

            val_to_display = None

            if success and measurement.current_value is not None:
                # Gestione caso tupla se arriva da sensore (val, status)
                raw_val = measurement.current_value
                if isinstance(raw_val, tuple):
                    val_to_display = raw_val[1]
                else:
                    val_to_display = raw_val

                # Ulteriore controllo di sicurezza
                if not isinstance(val_to_display, (int, float)):
                    val_to_display = None

            # Passa il valore (float o None) al widget
            widget.setValue(val_to_display)

    def _clear_widgets(self):
        for widget in self.measurement_widgets.values():
            self.measurements_layout.removeWidget(widget)
            widget.deleteLater()
        self.measurement_widgets.clear()
        for i in reversed(range(self.measurements_layout.count())):
            item = self.measurements_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, QLabel):
                    self.measurements_layout.removeWidget(w)
                    w.deleteLater()
