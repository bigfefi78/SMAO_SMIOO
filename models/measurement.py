"""
Modello dati per Misura calcolata
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto
import uuid


class MeasurementType(Enum):
    """Tipo di misura"""

    DIFFERENCE = auto()  # Differenza tra sensori
    SUM = auto()  # Somma di N sensori
    AVERAGE = auto()  # Media di N sensori
    CUSTOM = auto()  # Formula personalizzata


class MeasurementStatus(Enum):
    """Stato di una misura"""

    READY = auto()  # Tutti i sensori disponibili
    PARTIAL = auto()  # Alcuni sensori mancanti
    ERROR = auto()  # Errore critico
    DISABLED = auto()  # Misura disabilitata


@dataclass
class Measurement:
    """
    Rappresenta una misura calcolata da uno o più sensori

    Attributes:
        id: UUID univoco
        name: Nome misura
        description: Descrizione estesa
        type: Tipo misura (MeasurementType)
        channels: Lista label sensori usati (es. ["T-01", "T-02"])
        formula: Formula di calcolo (es. "{T-01} - {T-02}")
        unit: Unità misura risultato
        decimals: Decimali visualizzati
        color: Colore card (hex)
        min_limit: Limite minimo tolleranza
        max_limit: Limite massimo tolleranza
        enabled: Misura abilitata
        current_value: Ultimo valore calcolato
        status: Stato corrente
        product_code: Codice prodotto (validato da database)
        product_serial_number: Matricola esemplare
        product_description: Descrizione prodotto (da database)
    """

    name: str
    type: MeasurementType
    channels: List[str]
    formula: str
    product_code: Optional[str] = "None"
    product_serial_number: Optional[str] = "None"
    product_description: Optional[str] = "None"

    # Opzionali con default
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    unit: str = "µm"
    decimals: int = 2
    color: str = "#3498DB"
    min_limit: Optional[float] = None
    max_limit: Optional[float] = None
    enabled: bool = True
    current_value: Optional[float] = None
    status: MeasurementStatus = MeasurementStatus.READY

    def __str__(self):
        return f"{self.name} ({self.type.name})"

    def __repr__(self):
        return f"Measurement(name='{self.name}', formula='{self.formula}')"

    def to_dict(self) -> dict:
        """Converte in dizionario per serializzazione JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.name,
            "channels": self.channels,
            "formula": self.formula,
            "unit": self.unit,
            "decimals": self.decimals,
            "color": self.color,
            "min_limit": self.min_limit,
            "max_limit": self.max_limit,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Measurement":
        """Crea Measurement da dizionario JSON"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            type=MeasurementType[data.get("type", "CUSTOM")],
            channels=data.get("channels", []),
            formula=data.get("formula", ""),
            unit=data.get("unit", "µm"),
            decimals=data.get("decimals", 2),
            color=data.get("color", "#3498DB"),
            min_limit=data.get("min_limit"),
            max_limit=data.get("max_limit"),
            enabled=data.get("enabled", True),
        )
