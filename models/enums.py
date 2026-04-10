"""
Tutte le enumerazioni del progetto in un unico posto.
"""

from enum import IntEnum, Enum, auto


class SMAOStatus(IntEnum):
    """Stati connessione SMAO"""

    OFF = 0   # Non inizializzato
    OK = 1    # Connesso e funzionante
    NOK = 2   # Errore di connessione


class ChannelStatus(IntEnum):
    """
    Stati canale (corrispondono ai valori di ChannelStatusConstant nell'API SMAO).
    """

    CS_OK = 0               # Canale OK
    CS_UNDEFINED = 1        # Non definito
    CS_UNCALIBRATED = 2     # Non calibrato
    CS_WRONG_MODE = 3       # Modalità errata
    CS_NOT_CONNECTED = 4    # Non connesso
    CS_HW_ERROR_OFFSET = 5  # Errore HW offset
    CS_HW_ERROR_GAIN = 6    # Errore HW gain
    CS_NOT_READY = 7        # Non pronto
    CS_HW_ERROR = 20        # Errore HW generico


class MeasurementType(Enum):
    """Tipo di misura"""

    DIFFERENCE = auto()  # Differenza tra sensori
    SUM = auto()         # Somma di N sensori
    AVERAGE = auto()     # Media di N sensori
    CUSTOM = auto()      # Formula personalizzata


class MeasurementStatus(Enum):
    """Stato di una misura"""

    READY = auto()    # Tutti i sensori disponibili
    PARTIAL = auto()  # Alcuni sensori mancanti
    ERROR = auto()    # Errore critico
    DISABLED = auto()  # Misura disabilitata
