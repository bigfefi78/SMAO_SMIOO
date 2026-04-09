"""
Pagina gestione database prodotti
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
    QFileDialog,
    QHeaderView,
    QComboBox,
    QTextEdit,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt5.QtCore import Qt

from core import ProductsDB
from models import Product
import json


class ProductEditDialog(QDialog):
    """Dialog per modifica/creazione prodotto"""

    def __init__(self, product: Product = None, parent=None):
        super().__init__(parent)

        self.product = product or Product(code="", type="", description="")
        self.is_new = product is None

        self.setWindowTitle(
            "Nuovo Prodotto" if self.is_new else f"Modifica: {self.product.code}"
        )
        self.setMinimumWidth(500)

        self._setup_ui()

        if not self.is_new:
            self._load_data()

    def _setup_ui(self):
        layout = QFormLayout(self)

        # Codice
        self.input_code = QLineEdit()
        self.input_code.setEnabled(self.is_new)  # Solo per nuovi
        layout.addRow("Codice:", self.input_code)

        # Tipo
        self.input_type = QLineEdit()
        layout.addRow("Tipo:", self.input_type)

        # Descrizione
        self.input_description = QTextEdit()
        self.input_description.setMaximumHeight(80)
        layout.addRow("Descrizione:", self.input_description)

        # Connettore
        self.input_connector = QLineEdit()
        layout.addRow("Connettore:", self.input_connector)

        # Note
        self.input_notes = QTextEdit()
        self.input_notes.setMaximumHeight(80)
        layout.addRow("Note:", self.input_notes)

        # Pulsanti
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _load_data(self):
        """Carica dati prodotto esistente"""
        self.input_code.setText(self.product.code)
        self.input_type.setText(self.product.type)
        self.input_description.setPlainText(self.product.description)
        self.input_connector.setText(self.product.connector or "")
        self.input_notes.setPlainText(self.product.notes or "")

    def get_product(self) -> Product:
        """Ottieni prodotto con dati modificati"""
        self.product.code = self.input_code.text().strip()
        self.product.type = self.input_type.text().strip()
        self.product.description = self.input_description.toPlainText().strip()
        self.product.connector = self.input_connector.text().strip() or None
        self.product.notes = self.input_notes.toPlainText().strip() or None

        return self.product


class ProductsManagementPage(QWidget):
    """Pagina gestione database prodotti"""

    def __init__(self, products_db: ProductsDB, parent=None):
        super().__init__(parent)

        self.products_db = products_db
        self.current_products = []

        self._setup_ui()
        self._load_products()

        print("[ProductsManagementPage] Inizializzata")

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ===== HEADER =====
        header = QLabel("🗄️ GESTIONE DATABASE PRODOTTI")
        header.setStyleSheet(
            "background-color: #34495E; color: white; "
            "padding: 10px; font-size: 16pt; font-weight: bold;"
        )
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # ===== TOOLBAR =====
        toolbar_layout = QHBoxLayout()

        # Ricerca
        lbl_search = QLabel("Cerca:")
        lbl_search.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(lbl_search)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Codice, Tipo o Descrizione...")
        self.input_search.textChanged.connect(self._on_search)
        self.input_search.setMaximumWidth(300)
        toolbar_layout.addWidget(self.input_search)

        # Filtro tipo
        lbl_filter = QLabel("Tipo:")
        lbl_filter.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(lbl_filter)

        self.combo_type = QComboBox()
        self.combo_type.addItem("Tutti i tipi")
        self.combo_type.currentTextChanged.connect(self._on_filter_type)
        self.combo_type.setMaximumWidth(200)
        toolbar_layout.addWidget(self.combo_type)

        toolbar_layout.addStretch()

        # Pulsanti azioni
        btn_new = QPushButton("➕ Nuovo")
        btn_new.clicked.connect(self._on_new_product)
        toolbar_layout.addWidget(btn_new)

        btn_edit = QPushButton("✏️ Modifica")
        btn_edit.clicked.connect(self._on_edit_product)
        toolbar_layout.addWidget(btn_edit)

        btn_delete = QPushButton("🗑️ Elimina")
        btn_delete.clicked.connect(self._on_delete_product)
        toolbar_layout.addWidget(btn_delete)

        btn_import = QPushButton("📥 Importa JSON")
        btn_import.clicked.connect(self._on_import_json)
        toolbar_layout.addWidget(btn_import)

        main_layout.addLayout(toolbar_layout)

        # ===== TABELLA =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Codice", "Tipo", "Descrizione", "Connettore", "Note"]
        )

        # Impostazioni tabella
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self._on_edit_product)

        main_layout.addWidget(self.table)

        # ===== FOOTER INFO =====
        self.label_info = QLabel("Totale: 0 prodotti")
        self.label_info.setStyleSheet("color: #7F8C8D; font-style: italic;")
        main_layout.addWidget(self.label_info)

    def _load_products(self, products: list = None):
        """Carica prodotti nella tabella"""
        if products is None:
            products = self.products_db.get_all_products()

        self.current_products = products

        # Pulisci tabella
        self.table.setRowCount(0)

        # Popola
        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(product.code))
            self.table.setItem(row, 1, QTableWidgetItem(product.type))
            self.table.setItem(row, 2, QTableWidgetItem(product.description))
            self.table.setItem(row, 3, QTableWidgetItem(product.connector or ""))
            self.table.setItem(row, 4, QTableWidgetItem(product.notes or ""))

        # Aggiorna info
        self.label_info.setText(f"Totale: {len(products)} prodotti")

        # Aggiorna combo tipi
        self._update_type_combo()

    def _update_type_combo(self):
        """Aggiorna combo tipi"""
        current = self.combo_type.currentText()

        self.combo_type.blockSignals(True)
        self.combo_type.clear()
        self.combo_type.addItem("Tutti i tipi")

        types = self.products_db.get_product_types()
        self.combo_type.addItems(types)

        index = self.combo_type.findText(current)
        if index >= 0:
            self.combo_type.setCurrentIndex(index)

        self.combo_type.blockSignals(False)

    def _on_search(self, text: str):
        """Ricerca prodotti"""
        if not text.strip():
            self._load_products()
        else:
            products = self.products_db.search_products(text)
            self._load_products(products)

    def _on_filter_type(self, type_name: str):
        """Filtra per tipo"""
        if type_name == "Tutti i tipi":
            self._load_products()
        else:
            products = self.products_db.get_products_by_type(type_name)
            self._load_products(products)

    def _on_new_product(self):
        """Crea nuovo prodotto"""
        dialog = ProductEditDialog(parent=self)

        if dialog.exec_() == QDialog.Accepted:
            product = dialog.get_product()

            if not product.code:
                QMessageBox.warning(
                    self, "Codice Mancante", "Il codice prodotto è obbligatorio!"
                )
                return

            if self.products_db.add_product(product):
                QMessageBox.information(
                    self, "Successo", f"Prodotto '{product.code}' aggiunto!"
                )
                self._load_products()

    def _on_edit_product(self):
        """Modifica prodotto selezionato"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Selezione", "Seleziona un prodotto da modificare!"
            )
            return

        code = self.table.item(row, 0).text()
        product = self.products_db.get_product(code)

        if not product:
            return

        dialog = ProductEditDialog(product, self)

        if dialog.exec_() == QDialog.Accepted:
            updated_product = dialog.get_product()

            if self.products_db.update_product(updated_product):
                QMessageBox.information(
                    self, "Successo", f"Prodotto '{product.code}' aggiornato!"
                )
                self._load_products()

    def _on_delete_product(self):
        """Elimina prodotto selezionato"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Selezione", "Seleziona un prodotto da eliminare!"
            )
            return

        code = self.table.item(row, 0).text()

        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Vuoi davvero eliminare il prodotto '{code}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.products_db.delete_product(code):
                QMessageBox.information(
                    self, "Successo", f"Prodotto '{code}' eliminato!"
                )
                self._load_products()

    def _on_import_json(self):
        """Importa prodotti da file JSON"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleziona File JSON", "", "JSON Files (*.json);;All Files (*)"
        )

        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            count = self.products_db.import_from_json(data)

            QMessageBox.information(
                self, "Import Completato", f"Importati {count} prodotti da JSON!"
            )

            self._load_products()

        except Exception as ex:
            QMessageBox.critical(self, "Errore Import", f"Errore durante import:\n{ex}")
