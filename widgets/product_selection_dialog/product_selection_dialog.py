"""
Dialog selezione prodotto da database (Model-Based)
"""

from PyQt5.QtWidgets import QDialog, QHeaderView
from PyQt5.QtCore import Qt, QSortFilterProxyModel

from .product_selection_dialog_ui import Ui_ProductSelectionDialog
from widgets.products_management_page import ProductsTableModel
from core import ProductsDB
from models import Product


class ProductSelectionDialog(QDialog):
    """
    Dialog per selezione prodotto da database
    Usa ProductsTableModel (Model-Based) con filtri
    """

    def __init__(self, products_db: ProductsDB, parent=None):
        super().__init__(parent)

        self.products_db = products_db
        self.selected_product = None

        # Carica UI
        self.ui = Ui_ProductSelectionDialog()
        self.ui.setupUi(self)

        # Crea model
        self.table_model = ProductsTableModel()

        # Crea proxy per filtri e sorting
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Cerca in tutte le colonne

        self.ui.tableProducts.setModel(self.proxy_model)

        # Configura tabella
        self._configure_table()

        # Connetti signals
        self._connect_signals()

        # Carica prodotti
        self._load_products()

        print("[ProductSelectionDialog] Inizializzato")

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

        # Nascondi header verticale
        self.ui.tableProducts.verticalHeader().setVisible(False)

        # Abilita sorting
        self.ui.tableProducts.setSortingEnabled(True)

    def _connect_signals(self):
        """Connetti signals"""
        # Ricerca real-time
        self.ui.inputSearch.textChanged.connect(self._on_search)

        # Filtro tipo
        self.ui.comboType.currentTextChanged.connect(self._on_filter_type)

        # Selezione riga → aggiorna info
        self.ui.tableProducts.selectionModel().currentRowChanged.connect(
            self._on_selection_changed
        )

        # Doppio click → conferma
        self.ui.tableProducts.doubleClicked.connect(self.accept)

    def _load_products(self, products: list = None):
        """Carica prodotti nel model"""
        if products is None:
            products = self.products_db.get_all_products()

        # Aggiorna model
        self.table_model.set_products(products)

        # Aggiorna combo tipi
        self._update_type_combo()

        # Seleziona prima riga
        if len(products) > 0:
            first_index = self.proxy_model.index(0, 0)
            self.ui.tableProducts.setCurrentIndex(first_index)

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

    def _on_search(self, text: str):
        """Filtro ricerca real-time"""
        self.proxy_model.setFilterFixedString(text)

    def _on_filter_type(self, type_name: str):
        """Filtro per tipo"""
        if type_name == "Tutti i tipi":
            self._load_products()
        else:
            products = self.products_db.get_products_by_type(type_name)
            self.table_model.set_products(products)

    def _on_selection_changed(self, current, previous):
        """Aggiorna info prodotto selezionato"""
        if not current.isValid():
            self._clear_product_info()
            return

        # Ottieni riga nel source model (non proxy!)
        source_index = self.proxy_model.mapToSource(current)
        row = source_index.row()

        # Ottieni prodotto dal model
        product = self.table_model.get_product(row)

        if product:
            self._display_product_info(product)
            self.selected_product = product
        else:
            self._clear_product_info()

    def _display_product_info(self, product: Product):
        """Mostra dettagli prodotto nel GroupBox"""
        self.ui.labelCode.setText(product.code)
        self.ui.labelType.setText(product.type)
        self.ui.labelDescription.setText(product.description)
        self.ui.labelConnector.setText(product.connector or "-")

    def _clear_product_info(self):
        """Pulisci info prodotto"""
        self.ui.labelCode.setText("-")
        self.ui.labelType.setText("-")
        self.ui.labelDescription.setText("-")
        self.ui.labelConnector.setText("-")
        self.selected_product = None

    def get_selected_product(self) -> Product:
        """Ottieni prodotto selezionato"""
        return self.selected_product
