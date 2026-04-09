"""
Pagina gestione database prodotti (Model-Based)
"""

from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QFileDialog,
    QHeaderView,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QLineEdit,
    QTextEdit,
)


from .products_management_page_ui import Ui_ProductsManagementPage
from .products_table_model import ProductsTableModel
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
    """Pagina gestione database prodotti (Model-Based)"""

    def __init__(self, products_db: ProductsDB, parent=None):
        super().__init__(parent)

        self.products_db = products_db

        # Carica UI
        self.ui = Ui_ProductsManagementPage()
        self.ui.setupUi(self)

        # Crea model
        self.table_model = ProductsTableModel()
        self.ui.tableProducts.setModel(self.table_model)

        # Configura tabella
        self._configure_table()

        # Connetti signals
        self._connect_signals()

        # Carica dati
        self._load_products()

        print("[ProductsManagementPage] Inizializzata (Model-Based)")

    def _configure_table(self):
        """Configura QTableView"""
        header = self.ui.tableProducts.horizontalHeader()

        # Codice
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # Tipo
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # Descrizione (stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        # Connettore
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # Note
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # Nascondi header verticale (numeri riga)
        self.ui.tableProducts.verticalHeader().setVisible(False)

    def _connect_signals(self):
        """Connetti signals UI"""
        self.ui.inputSearch.textChanged.connect(self._on_search)
        self.ui.comboType.currentTextChanged.connect(self._on_filter_type)
        self.ui.btnNew.clicked.connect(self._on_new_product)
        self.ui.btnEdit.clicked.connect(self._on_edit_product)
        self.ui.btnDelete.clicked.connect(self._on_delete_product)
        self.ui.btnImportJSON.clicked.connect(self._on_import_json)
        self.ui.tableProducts.doubleClicked.connect(self._on_edit_product)

    def _load_products(self, products: list = None):
        """Carica prodotti nel model"""
        if products is None:
            products = self.products_db.get_all_products()

        # Aggiorna model
        self.table_model.set_products(products)

        # Aggiorna info
        self.ui.labelInfo.setText(f"Totale: {len(products)} prodotti")

        # Aggiorna combo tipi
        self._update_type_combo()

    def _update_type_combo(self):
        """Aggiorna combo tipi"""
        current = self.ui.comboType.currentText()

        self.ui.comboType.blockSignals(True)
        self.ui.comboType.clear()
        self.ui.comboType.addItem("Tutti i tipi")

        types = self.products_db.get_product_types()
        self.ui.comboType.addItems(types)

        index = self.ui.comboType.findText(current)
        if index >= 0:
            self.ui.comboType.setCurrentIndex(index)

        self.ui.comboType.blockSignals(False)

        # Auto-adatta larghezza al contenuto
        self.ui.comboType.setSizeAdjustPolicy(self.ui.comboType.AdjustToContents)

        # Imposta minimo/massimo
        self.ui.comboType.setMinimumWidth(250)
        # Rimuovo il massimo per permettere espansione completa
        self.ui.comboType.setMaximumWidth(500)

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
        # Ottieni selezione corrente
        selection = self.ui.tableProducts.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(
                self, "Selezione", "Seleziona un prodotto da modificare!"
            )
            return

        # Ottieni riga selezionata
        index = selection.currentIndex()
        row = index.row()

        # Ottieni prodotto dal model
        product = self.table_model.get_product(row)
        if not product:
            return

        # Dialog modifica
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
        # Ottieni selezione corrente
        selection = self.ui.tableProducts.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(
                self, "Selezione", "Seleziona un prodotto da eliminare!"
            )
            return

        # Ottieni riga selezionata
        index = selection.currentIndex()
        row = index.row()

        # Ottieni prodotto dal model
        product = self.table_model.get_product(row)
        if not product:
            return

        # Conferma
        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Vuoi davvero eliminare il prodotto '{product.code}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.products_db.delete_product(product.code):
                QMessageBox.information(
                    self, "Successo", f"Prodotto '{product.code}' eliminato!"
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
