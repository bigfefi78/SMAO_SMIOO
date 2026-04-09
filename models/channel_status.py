"""
Enum per lo stato di un canale SMAO
"""

from enum import IntEnum


class ChannelStatus(IntEnum):
    """
    Stati possibili di un canale SMAO.
    Corrispondono ai valori dell'enum ChannelStatusConstant di SMAO.
    """
    CS_OK = 0                   # Canale OK
    CS_UNDEFINED = 1            # Non definito
    CS_UNCALIBRATED = 2         # Non calibrato
    CS_WRONG_MODE = 3           # Modalità errata
    CS_NOT_CONNECTED = 4        # Non connesso
    CS_HW_ERROR_OFFSET = 5      # Errore HW offset
    CS_HW_ERROR_GAIN = 6        # Errore HW gain
    CS_NOT_READY = 7            # Non pronto
    CS_HW_ERROR = 20            # Errore HW generico