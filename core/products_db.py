"""
Manager database prodotti (SQLite)
"""

import sqlite3
import traceback
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from models import Product
from core.logging_tools import GuiLogger


class ProductsDB:
    """Gestisce database prodotti SQLite"""

    def __init__(self, db_path: str = "products.db"):
        self.db_path = Path(db_path)
        self.logger = GuiLogger.instance()
        self._init_db()
        self.logger.info(
            f"Database prodotti inizializzato: {self.db_path.absolute()}",
            sender=self.__class__.__name__,
        )

    def _init_db(self):
        """Crea tabelle se non esistono"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabella prodotti
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    connector TEXT,
                    created_at TEXT,
                    last_tested_at TEXT,
                    notes TEXT
                )
            """)

            # Tabella sessioni test
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_code TEXT NOT NULL,
                    serial_number TEXT NOT NULL,
                    test_date TEXT NOT NULL,
                    measurements TEXT,
                    result TEXT,
                    operator TEXT,
                    FOREIGN KEY (product_code) REFERENCES products (code)
                )
            """)

            # Indici per performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_code ON products(code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON products(type)")

            conn.commit()

    def _row_to_product(self, row) -> Product:
        """Converte una riga del database in oggetto Product."""
        return Product(
            id=row[0],
            code=row[1],
            type=row[2],
            description=row[3],
            connector=row[4],
            created_at=datetime.fromisoformat(row[5]) if row[5] else None,
            last_tested_at=datetime.fromisoformat(row[6]) if row[6] else None,
            notes=row[7],
        )

    def import_from_json(self, json_data: List[Dict]) -> int:
        """
        Importa prodotti da lista JSON (come ELENCO.json)

        Args:
            json_data: Lista dizionari con struttura ELENCO.json

        Returns:
            Numero prodotti importati
        """
        count = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for item in json_data:
                try:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO products 
                        (code, type, description, connector, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            item.get("CODICE", ""),
                            item.get("TIPO", ""),
                            item.get("DESCRIZIONE", ""),
                            item.get("CONNETTORE"),
                            datetime.now().isoformat(),
                        ),
                    )
                    count += 1
                except Exception as ex:
                    self.logger.error(
                        f"Errore import '{item.get('CODICE')}': {ex}",
                        sender=self.__class__.__name__,
                    )

            conn.commit()

        self.logger.info(
            f"Importati {count} prodotti da JSON", sender=self.__class__.__name__
        )
        return count

    def add_product(self, product: Product) -> bool:
        """Aggiungi prodotto al database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO products 
                    (code, type, description, connector, created_at, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        product.code,
                        product.type,
                        product.description,
                        product.connector,
                        datetime.now().isoformat(),
                        product.notes,
                    ),
                )

                conn.commit()
            self.logger.info(
                f"Prodotto salvato: {product.code}", sender=self.__class__.__name__
            )
            return True

        except Exception as ex:
            self.logger.error(
                f"Errore add_product '{product.code}': {ex}",
                sender=self.__class__.__name__,
            )
            return False

    def update_product(self, product: Product) -> bool:
        """Aggiorna prodotto esistente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE products 
                    SET type = ?, description = ?, connector = ?, notes = ?
                    WHERE code = ?
                """,
                    (
                        product.type,
                        product.description,
                        product.connector,
                        product.notes,
                        product.code,
                    ),
                )

                conn.commit()

            self.logger.info(
                f"Prodotto aggiornato: {product.code}", sender=self.__class__.__name__
            )
            return True

        except Exception as ex:
            self.logger.error(
                f"Errore update_product '{product.code}': {ex}",
                sender=self.__class__.__name__,
            )
            return False

    def delete_product(self, code: str) -> bool:
        """Elimina prodotto per codice"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE code = ?", (code,))
                conn.commit()
            self.logger.info(
                f"Prodotto eliminato: {code}", sender=self.__class__.__name__
            )
            return True

        except Exception as ex:
            self.logger.error(
                f"Errore delete_product '{code}': {ex}",
                sender=self.__class__.__name__,
            )
            return False

    def get_product(self, code: str) -> Optional[Product]:
        """Ottieni prodotto per codice"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, code, type, description, connector, 
                           created_at, last_tested_at, notes
                    FROM products WHERE code = ?
                """,
                    (code,),
                )

                row = cursor.fetchone()

                if row:
                    return self._row_to_product(row)

                return None

        except Exception as ex:
            self.logger.error(
                f"Errore get_product '{code}': {ex}", sender=self.__class__.__name__
            )
            return None

    def search_products(self, query: str) -> List[Product]:
        """Cerca prodotti per codice/tipo/descrizione"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Query base
                if not query or query.strip() == "":
                    cursor.execute("""
                        SELECT id, code, type, description, connector, 
                               created_at, last_tested_at, notes
                        FROM products 
                        ORDER BY code
                    """)
                else:
                    cursor.execute(
                        """
                        SELECT id, code, type, description, connector, 
                               created_at, last_tested_at, notes
                        FROM products 
                        WHERE code LIKE ? OR type LIKE ? OR description LIKE ?
                        ORDER BY code
                    """,
                        (f"%{query}%", f"%{query}%", f"%{query}%"),
                    )

                rows = cursor.fetchall()
                return [self._row_to_product(row) for row in rows]

        except Exception as ex:
            self.logger.error(
                f"Errore search_products '{query}': {ex}",
                sender=self.__class__.__name__,
            )
            traceback.print_exc()
            return []

    def get_all_products(self) -> List[Product]:
        """Ottieni tutti i prodotti"""
        return self.search_products("")

    def get_product_types(self) -> List[str]:
        """Ottieni lista tipi prodotto univoci"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT type FROM products WHERE type IS NOT NULL AND type != '' ORDER BY type"
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as ex:
            self.logger.error(
                f"Errore get_product_types: {ex}", sender=self.__class__.__name__
            )
            return []

    def get_products_by_type(self, product_type: str) -> List[Product]:
        """Ottieni prodotti per tipo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, code, type, description, connector, 
                           created_at, last_tested_at, notes
                    FROM products 
                    WHERE type = ?
                    ORDER BY code
                """,
                    (product_type,),
                )

                rows = cursor.fetchall()
                return [self._row_to_product(row) for row in rows]

        except Exception as ex:
            self.logger.error(
                f"Errore get_products_by_type '{product_type}': {ex}",
                sender=self.__class__.__name__,
            )
            return []

    def get_stats(self) -> Dict:
        """Ottieni statistiche database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM products")
                total = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT type, COUNT(*) 
                    FROM products 
                    GROUP BY type 
                    ORDER BY COUNT(*) DESC
                """)
                by_type = dict(cursor.fetchall())

                return {"total": total, "by_type": by_type}

        except Exception as ex:
            self.logger.error(f"Errore get_stats: {ex}", sender=self.__class__.__name__)
            return {"total": 0, "by_type": {}}
