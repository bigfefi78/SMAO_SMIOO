"""
Enum per lo stato della connessione SMAO
"""

from enum import Enum, auto


class SMAOStatus(Enum):
    """
    Stati possibili della connessione SMAO
    """
    OFF = auto()    # Non inizializzato
    OK = auto()     # Connesso e funzionante
    NOK = auto()    # Errore di connessione