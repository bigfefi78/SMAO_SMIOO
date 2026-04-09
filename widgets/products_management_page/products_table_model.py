"""
Model per tabella prodotti (Model-View pattern)
"""

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from typing import List
from models import Product


class ProductsTableModel(QAbstractTableModel):
    """
    Model per visualizzazione prodotti in QTableView
    """

    # Definizione colonne
    COLUMNS = [
        ("Codice", "code"),
        ("Tipo", "type"),
        ("Descrizione", "description"),
        ("Connettore", "connector"),
        ("Note", "notes"),
    ]

    def __init__(self, products: List[Product] = None, parent=None):
        super().__init__(parent)
        self._products = products or []

    def rowCount(self, parent=QModelIndex()):
        """Numero righe"""
        if parent.isValid():
            return 0
        return len(self._products)

    def columnCount(self, parent=QModelIndex()):
        """Numero colonne"""
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """Dati cella"""
        if not index.isValid():
            return QVariant()

        if index.row() >= len(self._products) or index.row() < 0:
            return QVariant()

        product = self._products[index.row()]
        column_name = self.COLUMNS[index.column()][1]

        if role == Qt.DisplayRole:
            value = getattr(product, column_name, None)
            return str(value) if value is not None else ""

        elif role == Qt.TextAlignmentRole:
            # Allinea a sinistra
            return Qt.AlignLeft | Qt.AlignVCenter

        elif role == Qt.UserRole:
            # Ritorna oggetto Product completo
            return product

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Header colonne/righe"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if 0 <= section < len(self.COLUMNS):
                    return self.COLUMNS[section][0]
            elif orientation == Qt.Vertical:
                return str(section + 1)

        return QVariant()

    def flags(self, index: QModelIndex):
        """Flags cella (read-only)"""
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def get_product(self, row: int) -> Product:
        """Ottieni prodotto per riga"""
        if 0 <= row < len(self._products):
            return self._products[row]
        return None

    def set_products(self, products: List[Product]):
        """Imposta lista prodotti (refresh completo)"""
        self.beginResetModel()
        self._products = products
        self.endResetModel()

    def add_product(self, product: Product):
        """Aggiungi prodotto"""
        row = len(self._products)
        self.beginInsertRows(QModelIndex(), row, row)
        self._products.append(product)
        self.endInsertRows()

    def update_product(self, row: int, product: Product):
        """Aggiorna prodotto"""
        if 0 <= row < len(self._products):
            self._products[row] = product
            # Notifica cambio dati
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right)

    def remove_product(self, row: int):
        """Rimuovi prodotto"""
        if 0 <= row < len(self._products):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._products[row]
            self.endRemoveRows()

    def clear(self):
        """Pulisci tabella"""
        self.beginResetModel()
        self._products.clear()
        self.endResetModel()

    def get_all_products(self) -> List[Product]:
        """Ottieni tutti i prodotti"""
        return self._products
