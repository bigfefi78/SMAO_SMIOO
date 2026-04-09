"""
Widget card per visualizzare una misura
"""

from PyQt5.QtWidgets import QFrame, QLabel, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent

from .measurement_card_ui import Ui_MeasurementCard
from widgets.flow_layout import FlowLayout


class SensorChip(QLabel):
    """Chip per visualizzare un sensore con X per rimuoverlo"""

    removeRequested = pyqtSignal(str)  # Emette channel_label

    def __init__(self, channel_label: str, parent=None):
        super().__init__(parent)

        self.channel_label = channel_label

        # Testo: "T-01 ×"
        self.setText(f"{channel_label} ×")

        # Stile chip
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid white;
                border-radius: 8px;
                padding: 3px 6px;
                color: white;
                font-size: 8pt;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: rgba(255, 100, 100, 0.6);
            }
        """)

        # Dimensioni fisse per evitare shrink
        self.setFixedHeight(20)
        self.setMinimumWidth(40)

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        """Click per rimuovere"""
        if event.button() == Qt.LeftButton:
            print(f"[SensorChip] Richiesta rimozione: {self.channel_label}")
            self.removeRequested.emit(self.channel_label)


class MeasurementCard(QFrame):
    """
    Card che rappresenta una misura

    Supporta Drag & Drop di sensori
    """

    clicked = pyqtSignal(str)
    doubleClicked = pyqtSignal(str)
    sensorDropped = pyqtSignal(str, str)
    sensorRemoved = pyqtSignal(str, str)
    enabledToggled = pyqtSignal(str, bool)
    nameChanged = pyqtSignal(str)

    def __init__(self, measurement, parent=None):
        super().__init__(parent)

        self.measurement = measurement
        self.sensor_chips = {}

        # Carica UI
        self.ui = Ui_MeasurementCard()
        self.ui.setupUi(self)

        # Imposta dati iniziali
        self.ui.labelName.setText(measurement.name)
        self._update_formula_display()

        # ✅ SETUP FLOW LAYOUT per area sensori
        old_layout = self.ui.widgetSensors.layout()
        if old_layout:
            QWidget().setLayout(old_layout)

        self.sensors_layout = FlowLayout(self.ui.widgetSensors, margin=3, spacing=3)
        self._update_sensors_display()

        # Connetti pulsante
        self.ui.btnToggleEnabled.clicked.connect(self._on_toggle_enabled)
        self._update_enabled_button()

        # Stile
        self._update_style()
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptDrops(True)

        # Nome cliccabile
        self.ui.labelName.setCursor(Qt.PointingHandCursor)
        self.ui.labelName.mouseDoubleClickEvent = self._on_name_double_click

        print(f"[MeasurementCard] Inizializzata card per '{measurement.name}'")

    def _update_style(self):
        """Aggiorna colore card in base allo stato"""
        from models import MeasurementStatus

        status_colors = {
            MeasurementStatus.READY: "#4CAF50",
            MeasurementStatus.PARTIAL: "#FFC107",
            MeasurementStatus.ERROR: "#F44336",
            MeasurementStatus.DISABLED: "#9E9E9E",
        }

        color = status_colors.get(self.measurement.status, "#4CAF50")

        self.setStyleSheet(f"""
            MeasurementCard {{
                background-color: {color};
                border: 2px solid #555;
                border-radius: 8px;
            }}
            MeasurementCard:hover {{
                border: 3px solid #000;
            }}
            QLabel {{
                color: white;
                background: transparent;
                border: none;
            }}
        """)

    def _update_sensors_display(self):
        """Aggiorna visualizzazione sensori come chip"""
        for chip in self.sensor_chips.values():
            self.sensors_layout.removeWidget(chip)
            chip.deleteLater()

        self.sensor_chips.clear()

        if not self.measurement.channels:
            label = QLabel("Trascina sensori qui")
            label.setStyleSheet(
                "color: rgba(255,255,255,0.5); font-size: 8pt; font-style: italic;"
            )
            self.sensors_layout.addWidget(label)
        else:
            for channel_label in self.measurement.channels:
                chip = SensorChip(channel_label, self)
                chip.removeRequested.connect(self._on_sensor_remove_requested)

                self.sensor_chips[channel_label] = chip
                self.sensors_layout.addWidget(chip)

        self.ui.widgetSensors.updateGeometry()
        self.updateGeometry()

    def _update_formula_display(self):
        """Aggiorna display formula"""
        if self.measurement.formula:
            self.ui.labelFormula.setText(self.measurement.formula)
        else:
            self.ui.labelFormula.setText("Doppio click per formula")

    def _update_enabled_button(self):
        """Aggiorna icona pulsante abilita/disabilita"""
        if self.measurement.enabled:
            self.ui.btnToggleEnabled.setText("✓")
            self.ui.btnToggleEnabled.setToolTip("Disabilita misura")
        else:
            self.ui.btnToggleEnabled.setText("✗")
            self.ui.btnToggleEnabled.setToolTip("Abilita misura")

    def update_value(self, value: float):
        """Aggiorna valore visualizzato"""
        self.measurement.current_value = value
        text = f"{value:.{self.measurement.decimals}f} {self.measurement.unit}"
        self.ui.labelValue.setText(text)

    def update_status(self, status):
        """Aggiorna stato e colore"""
        self.measurement.status = status
        self._update_style()

    def _on_toggle_enabled(self):
        """Toggle abilita/disabilita misura"""
        self.measurement.enabled = not self.measurement.enabled
        self._update_enabled_button()

        print(
            f"[MeasurementCard] Misura '{self.measurement.name}' → {'ABILITATA' if self.measurement.enabled else 'DISABILITATA'}"
        )

        self.enabledToggled.emit(self.measurement.id, self.measurement.enabled)

    def _on_sensor_remove_requested(self, channel_label: str):
        """Richiesta rimozione sensore (click su X)"""
        if channel_label in self.measurement.channels:
            self.measurement.channels.remove(channel_label)
            self._update_sensors_display()

            print(
                f"[MeasurementCard] Sensore '{channel_label}' rimosso da '{self.measurement.name}'"
            )

            self.sensorRemoved.emit(self.measurement.id, channel_label)

    def _on_name_double_click(self, event):
        """Doppio click sul nome per modificarlo"""
        from PyQt5.QtWidgets import QInputDialog

        new_name, ok = QInputDialog.getText(
            self, "Rinomina Misura", "Nuovo nome:", text=self.measurement.name
        )

        if ok and new_name.strip():
            self.measurement.name = new_name.strip()
            self.ui.labelName.setText(self.measurement.name)
            print(f"[MeasurementCard] Misura rinominata: {self.measurement.name}")
        
        self.nameChanged.emit(self.measurement.id)            

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accetta drag di sensori"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet(
                self.styleSheet() + "\nMeasurementCard { border: 4px dashed yellow; }"
            )

    def dragLeaveEvent(self, event):
        """Ripristina bordo normale"""
        self._update_style()

    def dropEvent(self, event: QDropEvent):
        """Gestisce drop di un sensore"""
        channel_label = event.mimeData().text()

        if channel_label not in self.measurement.channels:
            self.measurement.channels.append(channel_label)
            self._update_sensors_display()
            print(
                f"[MeasurementCard] Sensore '{channel_label}' aggiunto a '{self.measurement.name}'"
            )

        self.sensorDropped.emit(self.measurement.id, channel_label)
        self._update_style()

        event.acceptProposedAction()

    def mousePressEvent(self, event):
        """Click singolo"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.measurement.id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Doppio click → Modifica formula"""
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit(self.measurement.id)
        super().mouseDoubleClickEvent(event)
