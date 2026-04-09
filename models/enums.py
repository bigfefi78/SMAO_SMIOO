"""
Enumerazioni del progetto
"""

from enum import IntEnum


class SMAOStatus(IntEnum):
    """Stati connessione SMAO"""

    OFF = 0  # Non connesso
    OK = 1  # Connesso OK
    NOK = 2  # Connesso con errori


class ChannelStatus(IntEnum):
    """Stati canale (da SMAO API)"""

    CS_OK = 0  # Acquisizione OK
    CS_NO_SENSOR = 1  # Nessun sensore
    CS_ERROR = 2  # Errore generico
