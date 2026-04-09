"""
Pagina gestione misure (tab "Misure")
"""

from PyQt5.QtWidgets import (
    QWidget,
    QListWidgetItem,
    QMessageBox,
    QListWidget,
    QStyledItemDelegate,
    QStyle,
)
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QSize
from PyQt5.QtGui import QColor, QDrag, QPen, QBrush

from .measurements_page_ui import Ui_MeasurementsPage
from models import Measurement, MeasurementStatus, MeasurementType
from widgets.measurement_card import MeasurementCard
from core import MeasurementsManager  # ✅ NUOVO


# ✅ DELEGATE PERSONALIZZATO PER ITEM SENSORI
class SensorItemDelegate(QStyledItemDelegate):
    """Disegna item con colori persistenti"""

    def paint(self, painter, option, index):
        """Disegna item personalizzato"""
        painter.save()

        # Ottieni dati
        text = index.data(Qt.DisplayRole)
        bg_color = index.data(Qt.BackgroundRole)
        fg_color = index.data(Qt.ForegroundRole)

        # Rettangolo item
        rect = option.rect
        rect.adjust(4, 2, -4, -2)  # Margine

        # Disegna background arrotondato
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 5, 5)

        # Bordo se hover o selezionato
        if option.state & QStyle.State_MouseOver:
            painter.setPen(QPen(QColor("#3498DB"), 2))
            painter.drawRoundedRect(rect, 5, 5)
        elif option.state & QStyle.State_Selected:
            painter.setPen(QPen(QColor("#2980B9"), 3))
            painter.drawRoundedRect(rect, 5, 5)

        # Disegna testo centrato verticalmente
        painter.setPen(fg_color.color())
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft, f"  {text}")

        painter.restore()

    def sizeHint(self, option, index):
        """Altezza item"""
        return QSize(option.rect.width(), 45)


# ✅ LISTA CON DRAG & DROP ABILITATO
class DraggableSensorList(QListWidget):
    """Lista sensori con drag & drop abilitato"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.CopyAction)

        # Imposta delegate personalizzato
        self.setItemDelegate(SensorItemDelegate())

        # Stile lista
        self.setStyleSheet("""
QListWidget {
    background-color: #F5F5F5;
    border: 2px solid #34495E;
    border-radius: 5px;
    padding: 5px;
}""")

        # Spacing tra item
        self.setSpacing(4)

    def startDrag(self, supportedActions):
        """Avvia drag con il label del sensore"""
        item = self.currentItem()
        if not item:
            return

        channel_label = item.data(Qt.UserRole)

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(channel_label)
        drag.setMimeData(mime_data)

        print(f"[DraggableSensorList] Drag iniziato per: {channel_label}")

        drag.exec_(Qt.CopyAction)


class MeasurementsPage(QWidget):
    """
    Pagina per gestire le misure

    Layout a 3 colonne:
    - SX: Lista sensori (verde/rosso)
    - CENTRO: Pulsanti azioni
    - DX: Grid di card misure
    """

    measurementSelected = pyqtSignal(str)  # ID misura selezionata

    def __init__(self, sensor_manager, parent=None):
        super().__init__(parent)

        self.sensor_manager = sensor_manager
        self.measurements = []  # Lista di Measurement
        self.measurement_cards = {}  # {id: MeasurementCard}
        self.selected_measurement_id = None

        # Flag per disabilitare auto-save durante il caricamento iniziale
        self._loading = False

        # Manager per persistenza
        self.measurements_manager = MeasurementsManager("measurements.json")

        # Carica UI
        self.ui = Ui_MeasurementsPage()
        self.ui.setupUi(self)

        # ✅ SOSTITUISCI lista sensori con versione draggable
        old_list = self.ui.listSensors
        parent_widget = old_list.parent()
        parent_layout = parent_widget.layout()

        index = parent_layout.indexOf(old_list)

        parent_layout.removeWidget(old_list)
        old_list.deleteLater()

        # Crea nuova lista
        self.ui.listSensors = DraggableSensorList(parent_widget)
        self.ui.listSensors.setObjectName("listSensors")

        parent_layout.insertWidget(index, self.ui.listSensors)

        # Connetti pulsanti
        self.ui.btnNew.clicked.connect(self._on_new_measurement)
        self.ui.btnEdit.clicked.connect(self._on_edit_measurement)
        self.ui.btnDelete.clicked.connect(self._on_delete_measurement)
        self.ui.btnDuplicate.clicked.connect(self._on_duplicate_measurement)

        self.ui.btnEdit.setEnabled(False)
        self.ui.btnDelete.setEnabled(False)
        self.ui.btnDuplicate.setEnabled(False)

        # Carica misure salvate
        self._load_saved_measurements()

        print("[MeasurementsPage] Inizializzata con drag & drop")

    def update_sensors_list(self):
        """Aggiorna lista sensori da SensorManager"""
        self.ui.listSensors.clear()

        all_channels = self.sensor_manager.get_all_channels()

        for channel in all_channels:
            # Colori in base allo stato
            if channel.is_active:
                icon_text = "🟢"
                bg_color = "#27AE60"  # Verde
            else:
                icon_text = "🔴"
                bg_color = "#E74C3C"  # Rosso

            item = QListWidgetItem(f"{icon_text}  {channel.label}")

            # Imposta colori
            item.setBackground(QColor(bg_color))
            item.setForeground(QColor("#FFFFFF"))

            # Salva label nel UserRole
            item.setData(Qt.UserRole, channel.label)

            self.ui.listSensors.addItem(item)

        # ✅ Aggiorna stato di TUTTE le misure quando cambiano i sensori
        self._update_all_measurements_status()

        print(
            f"[MeasurementsPage] Lista sensori aggiornata: {len(all_channels)} sensori"
        )

    def _calculate_measurement_status(
        self, measurement: Measurement
    ) -> MeasurementStatus:
        """
        Calcola lo stato di una misura in base a sensori e formula

        Logica:
        - ROSSO: Nessun sensore OPPURE formula vuota
        - VERDE: Formula OK + Tutti i sensori attivi
        - GIALLO: Formula OK + Almeno un sensore NON attivo
        - GRIGIO: Misura disabilitata manualmente

        Returns:
            MeasurementStatus appropriato
        """
        # 1. Se disabilitata manualmente
        if not measurement.enabled:
            return MeasurementStatus.DISABLED

        # 2. Se non ha sensori O formula vuota → ROSSO
        if not measurement.channels or not measurement.formula.strip():
            return MeasurementStatus.ERROR

        # 3. Controlla se tutti i sensori sono attivi
        all_channels = self.sensor_manager.get_all_channels()

        # Crea mappa label → is_active
        channel_status_map = {ch.label: ch.is_active for ch in all_channels}

        # Conta sensori attivi/non attivi
        active_count = 0
        inactive_count = 0

        for sensor_label in measurement.channels:
            is_active = channel_status_map.get(sensor_label, False)
            if is_active:
                active_count += 1
            else:
                inactive_count += 1

        # 4. Se tutti attivi → VERDE
        if inactive_count == 0:
            return MeasurementStatus.READY

        # 5. Se alcuni non attivi → GIALLO
        return MeasurementStatus.PARTIAL

    def _update_all_measurements_status(self):
        """
        Aggiorna lo stato di tutte le misure
        (da chiamare quando cambiano i sensori attivi)
        """
        for measurement in self.measurements:
            new_status = self._calculate_measurement_status(measurement)

            # Aggiorna stato nel modello
            measurement.status = new_status

            # Aggiorna card
            card = self.measurement_cards.get(measurement.id)
            if card:
                card.update_status(new_status)

        if self.measurements:
            print(
                f"[MeasurementsPage] Aggiornati stati di {len(self.measurements)} misure"
            )

    def add_measurement(self, measurement: Measurement):
        """Aggiunge una nuova misura"""
        self.measurements.append(measurement)

        # Crea card
        card = MeasurementCard(measurement, self)
        card.clicked.connect(self._on_card_clicked)
        card.doubleClicked.connect(self._on_card_double_clicked)
        card.sensorDropped.connect(self._on_sensor_dropped)
        card.sensorRemoved.connect(self._on_sensor_removed)
        card.enabledToggled.connect(self._on_enabled_toggled)

        self.measurement_cards[measurement.id] = card

        # Aggiungi al grid (3 colonne)
        index = len(self.measurements) - 1
        row = index // 3
        col = index % 3

        self.ui.gridLayoutMeasurements.addWidget(card, row, col)

        # AUTO-SAVE
        self._save_measurements()

        print(f"[MeasurementsPage] Misura aggiunta: {measurement.name}")

    def remove_measurement(self, measurement_id: str):
        """Rimuove una misura"""
        measurement = next(
            (m for m in self.measurements if m.id == measurement_id), None
        )
        if not measurement:
            return

        # Rimuovi card
        card = self.measurement_cards.pop(measurement_id, None)
        if card:
            self.ui.gridLayoutMeasurements.removeWidget(card)
            card.deleteLater()

        # Rimuovi da lista
        self.measurements.remove(measurement)

        # Riorganizza grid
        self._reorganize_grid()

        # ✅ AUTO-SAVE
        self._save_measurements()

        print(f"[MeasurementsPage] Misura rimossa: {measurement.name}")

    def _reorganize_grid(self):
        """Riorganizza le card nel grid dopo una cancellazione"""
        # Rimuovi tutte le card dal layout
        for card in self.measurement_cards.values():
            self.ui.gridLayoutMeasurements.removeWidget(card)

        # Reinserisci in ordine
        for index, measurement in enumerate(self.measurements):
            card = self.measurement_cards[measurement.id]
            row = index // 3
            col = index % 3
            self.ui.gridLayoutMeasurements.addWidget(card, row, col)

    def _on_new_measurement(self):
        """Crea nuova misura"""
        print("[MeasurementsPage] Crea nuova misura")

        # Crea misura vuota (inizialmente ROSSA)
        measurement = Measurement(
            name=f"Misura {len(self.measurements) + 1}",
            type=MeasurementType.CUSTOM,
            channels=[],  # Vuoto
            formula="",  # Vuoto
            status=MeasurementStatus.ERROR,  # Rosso
        )

        self.add_measurement(measurement)

    def _on_edit_measurement(self):
        """Modifica misura selezionata"""
        if not self.selected_measurement_id:
            return

        print(f"[MeasurementsPage] Modifica misura: {self.selected_measurement_id}")

        # Apri dialog formula (stesso del doppio click)
        self._on_card_double_clicked(self.selected_measurement_id)

    def _on_delete_measurement(self):
        """Cancella misura selezionata"""
        if not self.selected_measurement_id:
            return

        # Trova misura
        measurement = next(
            (m for m in self.measurements if m.id == self.selected_measurement_id), None
        )

        if not measurement:
            return

        # Conferma
        reply = QMessageBox.question(
            self,
            "Conferma Cancellazione",
            f"Vuoi davvero cancellare la misura '{measurement.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.remove_measurement(self.selected_measurement_id)
            self.selected_measurement_id = None
            self.ui.btnEdit.setEnabled(False)
            self.ui.btnDelete.setEnabled(False)
            self.ui.btnDuplicate.setEnabled(False)

    def _on_duplicate_measurement(self):
        """Duplica misura selezionata"""
        if not self.selected_measurement_id:
            return

        # Trova misura
        measurement = next(
            (m for m in self.measurements if m.id == self.selected_measurement_id), None
        )

        if not measurement:
            return

        # Crea copia
        import copy
        import uuid
        from dataclasses import replace

        duplicated = copy.deepcopy(measurement)
        duplicated = replace(duplicated, id=str(uuid.uuid4()))
        duplicated.name = f"{measurement.name} (copia)"

        self.add_measurement(duplicated)

        print(f"[MeasurementsPage] Misura duplicata: {duplicated.name}")

    def _on_card_clicked(self, measurement_id: str):
        """Selezione card"""
        print(f"[MeasurementsPage] Card selezionata: {measurement_id}")

        self.selected_measurement_id = measurement_id

        self.ui.btnEdit.setEnabled(True)
        self.ui.btnDelete.setEnabled(True)
        self.ui.btnDuplicate.setEnabled(True)

        self.measurementSelected.emit(measurement_id)

    def _on_card_double_clicked(self, measurement_id: str):
        """Doppio click → Dialog formula CON VALIDAZIONE"""
        measurement = next(
            (m for m in self.measurements if m.id == measurement_id), None
        )

        if not measurement:
            return

        print(f"[MeasurementsPage] Apertura dialog formula per '{measurement.name}'")

        # Costruisci messaggio con sensori disponibili
        if measurement.channels:
            channels_hint = f"Sensori disponibili: {', '.join(measurement.channels)}\n"
            example_hint = f"Esempio: {{{measurement.channels[0]}}}"
            if len(measurement.channels) > 1:
                example_hint = f"Esempio: {{{measurement.channels[0]}}} - {{{measurement.channels[1]}}}"
        else:
            channels_hint = (
                "⚠️ Nessun sensore aggiunto!\nTrascina sensori dalla lista a sinistra.\n"
            )
            example_hint = "Esempio: {T-01} - {T-02}"

        # Loop finché formula valida o annulla
        while True:
            from PyQt5.QtWidgets import QInputDialog

            formula, ok = QInputDialog.getText(
                self,
                "Formula Misura",
                f"Inserisci formula per '{measurement.name}':\n\n"
                f"{channels_hint}"
                f"Usa {{Nome-Sensore}} per riferimento\n\n"
                f"{example_hint}",
                text=measurement.formula,
            )

            if not ok:
                # Utente ha annullato
                break

            formula = formula.strip()

            # VALIDA FORMULA
            from core import FormulaEvaluator
            evaluator = FormulaEvaluator()
            
            is_valid, error_msg = evaluator.validate_formula(formula)
            
            if not is_valid:
                # MOSTRA ERRORE e riapri dialog
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.critical(
                    self,
                    "Formula Non Valida",
                    f"❌ Errore nella formula:\n\n{error_msg}\n\nVuoi riprovare?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.No:
                    break
                
                continue
            
            # Formula valida! Controlla sensori richiesti
            required_sensors = evaluator.get_required_sensors(formula)
            missing_sensors = [s for s in required_sensors if s not in measurement.channels]
            
            if missing_sensors:
                # AVVISO sensori mancanti
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.warning(
                    self,
                    "Sensori Mancanti",
                    f"⚠️ La formula richiede sensori non aggiunti:\n\n"
                    f"{', '.join(missing_sensors)}\n\n"
                    f"Vuoi salvare comunque?\n(La misura sarà in errore finché non aggiungi i sensori)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    continue
            
            # SALVA FORMULA
            measurement.formula = formula

            # Ricalcola stato
            new_status = self._calculate_measurement_status(measurement)
            measurement.status = new_status

            # Aggiorna card
            card = self.measurement_cards.get(measurement_id)
            if card:
                card._update_formula_display()
                card.update_status(new_status)
                print(f"[MeasurementsPage] Formula aggiornata → Stato: {new_status.name}")
            
            # AUTO-SAVE
            self._save_measurements()
            
            break

    def _on_sensor_dropped(self, measurement_id: str, channel_label: str):
        """Callback quando un sensore viene droppato su una card"""
        print(
            f"[MeasurementsPage] Sensore '{channel_label}' → Misura '{measurement_id}'"
        )

        # Trova misura
        measurement = next(
            (m for m in self.measurements if m.id == measurement_id), None
        )

        if not measurement:
            return

        # ✅ Ricalcola stato dopo drop
        new_status = self._calculate_measurement_status(measurement)
        measurement.status = new_status

        # Aggiorna card
        card = self.measurement_cards.get(measurement_id)
        if card:
            card.update_status(new_status)
            print(f"[MeasurementsPage] Stato misura → {new_status.name}")
        # ✅ AUTO-SAVE
        self._save_measurements()

    def _on_sensor_removed(self, measurement_id: str, channel_label: str):
        """Callback quando un sensore viene rimosso"""
        print(
            f"[MeasurementsPage] Sensore '{channel_label}' rimosso da misura '{measurement_id}'"
        )

        # Trova misura
        measurement = next(
            (m for m in self.measurements if m.id == measurement_id), None
        )

        if not measurement:
            return

        # Ricalcola stato
        new_status = self._calculate_measurement_status(measurement)
        measurement.status = new_status

        # Aggiorna card
        card = self.measurement_cards.get(measurement_id)
        if card:
            card.update_status(new_status)
            print(f"[MeasurementsPage] Stato misura → {new_status.name}")

        # ✅ AUTO-SAVE
        self._save_measurements()

    def _on_enabled_toggled(self, measurement_id: str, enabled: bool):
        """Callback quando viene abilitata/disabilitata una misura"""
        print(
            f"[MeasurementsPage] Misura '{measurement_id}' → {'ABILITATA' if enabled else 'DISABILITATA'}"
        )

        # Trova misura
        measurement = next(
            (m for m in self.measurements if m.id == measurement_id), None
        )

        if not measurement:
            return

        # Ricalcola stato
        new_status = self._calculate_measurement_status(measurement)
        measurement.status = new_status

        # Aggiorna card
        card = self.measurement_cards.get(measurement_id)
        if card:
            card.update_status(new_status)
            print(f"[MeasurementsPage] Stato misura → {new_status.name}")

        # ✅ AUTO-SAVE
        self._save_measurements()

    def _load_saved_measurements(self):
        """Carica misure salvate dal file JSON"""
        print("[MeasurementsPage] Tentativo caricamento misure...")

        # Disabilita auto-save durante caricamento
        self._loading = True

        saved_measurements = self.measurements_manager.load_measurements()

        print(f"[MeasurementsPage] Trovate {len(saved_measurements)} misure salvate")

        for measurement in saved_measurements:
            print(f"[MeasurementsPage] Caricamento: {measurement.name}")
            self.add_measurement(measurement)

        # Riabilita auto-save
        self._loading = False

        if saved_measurements:
            print(f"[MeasurementsPage] ✓ Caricate {len(saved_measurements)} misure")
            # ✅ Ricalcola stati dopo caricamento
            self._update_all_measurements_status()
        else:
            print("[MeasurementsPage] ⚠ Nessuna misura trovata")

    def _save_measurements(self):
        # Non salvare se stiamo caricando
        if self._loading:
            print("[MeasurementsPage] Salvataggio saltato (caricamento in corso)")
            return
        """Salva tutte le misure su file JSON"""
        success = self.measurements_manager.save_measurements(self.measurements)
        if success:
            print(f"[MeasurementsPage] Salvate {len(self.measurements)} misure")
