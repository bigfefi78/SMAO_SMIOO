"""
Manager per salvare/caricare misure da file JSON
"""

import json
import traceback
from typing import List
from pathlib import Path

from models import Measurement, MeasurementType, MeasurementStatus
from core.logging_tools import GuiLogger


class MeasurementsManager:
    """Gestisce persistenza misure su file JSON"""

    def __init__(self, filepath: str = "measurements.json"):
        self.filepath = Path(filepath)
        self.logger = GuiLogger.instance()
        self.logger.info(f"File misure: {self.filepath.absolute()}", self.__class__.__name__)

    def save_measurements(self, measurements: List[Measurement]) -> bool:
        """
        Salva lista misure su file JSON.

        Args:
            measurements: Lista di oggetti Measurement

        Returns:
            True se salvato con successo
        """
        try:
            data = {
                "version": "1.0",
                "measurements": [m.to_dict() for m in measurements],
            }

            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Salvate {len(measurements)} misure", self.__class__.__name__)
            return True

        except Exception as ex:
            self.logger.error(f"Errore salvataggio: {ex}", self.__class__.__name__)
            traceback.print_exc()
            return False

    def load_measurements(self) -> List[Measurement]:
        """
        Carica misure da file JSON.

        Returns:
            Lista di oggetti Measurement (vuota se file non esiste)
        """
        if not self.filepath.exists():
            self.logger.info("File non trovato, nessuna misura da caricare", self.__class__.__name__)
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            measurements = [
                self._load_measurement(m_dict)
                for m_dict in data.get("measurements", [])
            ]

            self.logger.info(f"Caricate {len(measurements)} misure", self.__class__.__name__)
            return measurements

        except Exception as ex:
            self.logger.error(f"Errore caricamento: {ex}", self.__class__.__name__)
            traceback.print_exc()
            return []

    def _load_measurement(self, data: dict) -> Measurement:
        """
        Deserializza un Measurement da dizionario JSON.
        Lo stato viene impostato a ERROR perché dovrà essere ricalcolato.
        """
        return Measurement(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            type=MeasurementType[data["type"]],
            channels=data["channels"],
            formula=data["formula"],
            unit=data.get("unit", "µm"),
            decimals=data.get("decimals", 2),
            color=data.get("color", "#3498DB"),
            min_limit=data.get("min_limit"),
            max_limit=data.get("max_limit"),
            enabled=data.get("enabled", True),
            status=MeasurementStatus.ERROR,  # sarà ricalcolato da MeasurementsEngine
        )
