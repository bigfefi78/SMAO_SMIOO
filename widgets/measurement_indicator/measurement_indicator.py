"""
Widget indicatore misura (visualizzazione) - Subclass di DisplacementIndicator
Persistenza runtime solo in sessione: codice/matricola/descrizione
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from widgets import DisplacementIndicator
from core.session_state_manager import SessionStateManager


class MeasurementIndicator(QWidget):
    """
    Widget per visualizzare una misura calcolata, con inserimento e
    validazione di codice prodotto, matricola, descrizione.
    Tutto è solo a livello sessione!
    """

    def __init__(self, measurement, parent=None):
        super().__init__(parent)
        self.measurement = measurement
        self.current_product = None

        # Layout principale
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # DisplacementIndicator
        self.displacement_widget = DisplacementIndicator(self)
        from models import ChannelInfo

        temp_channel = ChannelInfo(
            driver_name="MEASUREMENT", channel_number=0, user_channel_number=0
        )
        temp_channel.label = measurement.name
        temp_channel.unit = measurement.unit
        temp_channel.decimals = measurement.decimals
        temp_channel.rb = 1.0
        if measurement.min_limit is not None:
            temp_channel.min_limit = measurement.min_limit
        if measurement.max_limit is not None:
            temp_channel.max_limit = measurement.max_limit
        if measurement.min_limit is not None and measurement.max_limit is not None:
            range_size = measurement.max_limit - measurement.min_limit
            margin = range_size * 0.1
            temp_channel.min_range = measurement.min_limit - margin
            temp_channel.max_range = measurement.max_limit + margin
        else:
            temp_channel.min_range = -100.0
            temp_channel.max_range = 100.0
        self.displacement_widget.set_channel_info(temp_channel)
        main_layout.addWidget(self.displacement_widget)

        # RIGA: cod. prodotto, matricola, descrizione
        inputs_widget = QWidget()
        inputs_layout = QHBoxLayout(inputs_widget)
        inputs_layout.setSpacing(10)
        inputs_layout.setContentsMargins(5, 5, 5, 5)

        # --- CODICE ---
        inputs_layout.addWidget(QLabel("Codice:"))
        self.input_code = QLineEdit()
        self.input_code.setMaximumWidth(200)
        self.input_code.setPlaceholderText("Doppio click per cerca prodotto")
        self.input_code.textChanged.connect(self._on_code_changed)
        self.input_code.editingFinished.connect(self._validate_code)
        self.input_code.mouseDoubleClickEvent = self._on_code_double_click
        inputs_layout.addWidget(self.input_code)
        inputs_layout.addSpacing(5)

        # --- MATRICOLA ---
        inputs_layout.addWidget(QLabel("Matricola:"))
        self.input_serial = QLineEdit()
        self.input_serial.setMaximumWidth(150)
        self.input_serial.textChanged.connect(self._on_serial_changed)
        self.input_serial.setPlaceholderText("Matricola esemplare")
        inputs_layout.addWidget(self.input_serial)
        inputs_layout.addSpacing(5)

        # --- DESCRIZIONE ---
        inputs_layout.addWidget(QLabel("Descrizione:"))
        self.label_description = QLabel("-")
        self.label_description.setMinimumWidth(200)
        inputs_layout.addWidget(self.label_description)
        inputs_layout.addStretch()

        main_layout.addWidget(inputs_widget)

        # Restore stato sessione se già presente
        self._restore_from_session()

    # ====== SESSIONE PERSISTENTE SOLO IN RAM (SessionStateManager) ======
    def _save_to_session(self):
        SessionStateManager.instance().save(
            self.measurement.id,
            self.input_code.text().strip(),
            self.input_serial.text().strip(),
            self.label_description.text().strip(),
        )
        self.sync_to_measurement()

    def _restore_from_session(self):
        session = SessionStateManager.instance().get(self.measurement.id)
        if session:
            self.input_code.setText(session.get("product_code", ""))
            self.input_serial.setText(session.get("serial_number", ""))
            self.label_description.setText(session.get("description", "-"))

    # ====== LOGICA INFO PRODOTTO ======
    def _on_code_changed(self, text):
        self._save_to_session()
        # Reset stile su edit
        self.input_code.setStyleSheet("")
        self.label_description.setText("-")
        self.current_product = None

    def _on_serial_changed(self, text):
        self._save_to_session()

    def _validate_code(self):
        code = self.input_code.text().strip()
        if not code:
            self.label_description.setText("-")
            self.current_product = None
            return
        products_db = self._get_products_db()
        if not products_db:
            self.label_description.setText("DB non disponibile")
            return
        product = products_db.get_product(code)
        if product:
            self._set_code_valid(product)
        else:
            self._set_code_invalid("Codice non trovato nel database")

    def _set_code_valid(self, product):
        self.current_product = product
        self.label_description.setText(product.description)
        # Evidenzia verde
        self.input_code.setStyleSheet(
            "background-color: #d4edda; border: 2px solid #28a745; color: #155724;"
        )
        self._save_to_session()

    def _set_code_invalid(self, reason=""):
        self.current_product = None
        self.label_description.setText("-")
        # Evidenzia rosso
        self.input_code.setStyleSheet(
            "background-color: #f8d7da; border: 2px solid #dc3545; color: #721c24;"
        )
        if reason:
            self.input_code.setToolTip(reason)
        else:
            self.input_code.setToolTip("")

    def _on_code_double_click(self, event):
        """Doppio click: apri dialog selezione prodotto"""
        from widgets import ProductSelectionDialog

        products_db = self._get_products_db()
        if not products_db:
            return
        dialog = ProductSelectionDialog(products_db, parent=None)
        if dialog.exec_():
            prod = dialog.get_selected_product()
            if prod:
                self.input_code.setText(prod.code)
                self._validate_code()

    def _get_products_db(self):
        # Cerca in parent chain
        parent = self.parent()
        while parent:
            if hasattr(parent, "products_db"):
                return parent.products_db
            parent = parent.parent()
        from core import ProductsDB

        return ProductsDB("products.db")

    # ====== API PUBBLICA (usata dalla page) ======

    def setValue(self, value):
        """
        Imposta il valore.
        Accetta float, int o None.
        Se None, il widget DisplacementIndicator mostrerà ERR in rosso automaticamente.
        """
        # Passiamo il valore direttamente, senza logica "strana" qui
        self.displacement_widget.setValue(value)
        self.measurement.current_value = value

    def get_code(self) -> str:
        return self.input_code.text().strip()

    def get_serial_number(self) -> str:
        return self.input_serial.text().strip()

    def get_description(self) -> str:
        return self.label_description.text().strip()

    def set_code(self, code: str):
        self.input_code.setText(code)

    def set_serial_number(self, serial: str):
        self.input_serial.setText(serial)

    def clear_product_info(self):
        self.input_code.clear()
        self.input_serial.clear()
        self.label_description.setText("-")
        self.current_product = None
        # Cancella anche da sessione
        SessionStateManager.instance().clear(self.measurement.id)

    def sync_to_measurement(self):
        """Aggiorna i dati codice/matricola/descrizione dall’UI all’istanza Measurement associata."""
        if self.measurement:
            self.measurement.product_code = self.get_code()
            self.measurement.product_serial_number = self.get_serial_number()
            self.measurement.product_description = self.get_description()
