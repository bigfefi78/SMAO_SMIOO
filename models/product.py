"""
Modello dati per Prodotto
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Rappresenta un prodotto da collaudare

    Attributes:
        id: ID univoco (auto-incrementale dal database)
        code: Codice prodotto (es. "B3408104001")
        type: Tipo prodotto (es. "MICROMAR 2")
        description: Descrizione (es. "MICROMAR 2 SOLO PER RICAMBI")
        connector: Connettore (es. "VEAM (BUFFER)")
        created_at: Data creazione record
        last_tested_at: Data ultimo test
        notes: Note aggiuntive (campo libero)
    """

    code: str  # Codice prodotto (chiave principale per ricerca)
    type: str  # Tipo prodotto
    description: str  # Descrizione
    connector: Optional[str] = None  # Tipo connettore
    id: Optional[int] = None  # ID database (auto-incrementale)
    created_at: Optional[datetime] = None
    last_tested_at: Optional[datetime] = None
    notes: Optional[str] = None  # Note libere

    def __str__(self):
        return f"{self.code} - {self.type}"

    def __repr__(self):
        return f"Product(code='{self.code}', type='{self.type}')"
