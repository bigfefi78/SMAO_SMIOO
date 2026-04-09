"""
Manager per salvare/caricare misure da file JSON
"""

import json
from typing import List
from pathlib import Path

from models import Measurement, MeasurementType, MeasurementStatus


class MeasurementsManager:
    """Gestisce persistenza misure su file JSON"""

    def __init__(self, filepath: str = "measurements.json"):
        """
        Args:
            filepath: Percorso file JSON (relativo alla directory di lavoro)
        """
        self.filepath = Path(filepath)
        print(f"[MeasurementsManager] File: {self.filepath.absolute()}")

    def save_measurements(self, measurements: List[Measurement]) -> bool:
        """
        Salva lista misure su file JSON

        Args:
            measurements: Lista di oggetti Measurement

        Returns:
            True se salvato con successo
        """
        try:
            # Converti misure in dizionari
            data = {
                "version": "1.0",
                "measurements": [self._measurement_to_dict(m) for m in measurements],
            }

            # Salva su file (con indentazione per leggibilità)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"[MeasurementsManager] ✓ Salvate {len(measurements)} misure")
            return True

        except Exception as ex:
            print(f"[MeasurementsManager] ✗ Errore salvataggio: {ex}")
            import traceback

            traceback.print_exc()
            return False

    def load_measurements(self) -> List[Measurement]:
        """
        Carica misure da file JSON

        Returns:
            Lista di oggetti Measurement (vuota se file non esiste)
        """
        if not self.filepath.exists():
            print("[MeasurementsManager] File non trovato, nessuna misura da caricare")
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            measurements = [
                self._dict_to_measurement(m_dict)
                for m_dict in data.get("measurements", [])
            ]

            print(f"[MeasurementsManager] ✓ Caricate {len(measurements)} misure")
            return measurements

        except Exception as ex:
            print(f"[MeasurementsManager] ✗ Errore caricamento: {ex}")
            import traceback

            traceback.print_exc()
            return []

    def _measurement_to_dict(self, measurement: Measurement) -> dict:
        """Converte Measurement in dict per JSON"""
        return {
            "id": measurement.id,
            "name": measurement.name,
            "description": measurement.description,
            "type": measurement.type.name,  # Enum → stringa
            "channels": measurement.channels,
            "formula": measurement.formula,
            "unit": measurement.unit,
            "decimals": measurement.decimals,
            "color": measurement.color,
            "min_limit": measurement.min_limit,
            "max_limit": measurement.max_limit,
            "enabled": measurement.enabled,
        }

    def _dict_to_measurement(self, data: dict) -> Measurement:
        """Converte dict JSON in Measurement"""
        # Converti type string → Enum
        measurement_type = MeasurementType[data["type"]]

        # Crea oggetto (status viene ricalcolato, non salvato)
        return Measurement(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            type=measurement_type,
            channels=data["channels"],
            formula=data["formula"],
            unit=data.get("unit", "µm"),
            decimals=data.get("decimals", 2),
            color=data.get("color", "#2196F3"),
            min_limit=data.get("min_limit"),
            max_limit=data.get("max_limit"),
            enabled=data.get("enabled", True),
            status=MeasurementStatus.ERROR,  # Verrà ricalcolato
        )
