"""
Modello dati per un canale sensore
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChannelInfo:
    """
    Contiene tutte le informazioni di un canale sensore.
    """

    # ===== OBBLIGATORI =====
    driver_name: str
    channel_number: int
    user_channel_number: int

    # ===== OPZIONALI =====
    is_active: bool = False
    label: str = ""
    unit: str = "µm"
    min_range: float = -100.0
    max_range: float = 100.0
    min_limit: float = -80.0
    max_limit: float = 80.0
    decimals: int = 2
    rb: float = 1.0
    num_samples: int = 16

    # ===== DATI RUNTIME (non salvati) =====
    current_value: Optional[float] = None
    current_status: Optional[int] = None

    def __post_init__(self):
        """
        Chiamato DOPO __init__()
        Se label è vuoto, genera automaticamente "T-01", "T-02", ecc.
        """
        if not self.label:
            self.label = f"T-{self.user_channel_number:02d}"

    def __str__(self):
        """
        Rappresentazione testuale del canale
        """
        status = "ATTIVO" if self.is_active else "NON ATTIVO"
        return f"{self.label} ({self.driver_name}#{self.channel_number}) - {status}"

    def to_dict(self):
        """
        Converte il canale in dizionario (per salvare in JSON)
        NON include current_value/current_status (dati runtime)
        """
        return {
            "driver_name": self.driver_name,
            "channel_number": self.channel_number,
            "user_channel_number": self.user_channel_number,
            "label": self.label,
            "unit": self.unit,
            "min_range": self.min_range,
            "max_range": self.max_range,
            "min_limit": self.min_limit,
            "max_limit": self.max_limit,
            "decimals": self.decimals,
            "rb": self.rb,
            "num_samples": self.num_samples,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Crea un ChannelInfo da dizionario (carica da JSON)
        """
        return cls(**data)
