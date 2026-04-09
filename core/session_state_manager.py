from typing import Dict, Optional


class SessionStateManager:
    _instance = None

    def __init__(self):
        self._data: Dict[str, Dict] = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SessionStateManager()
        return cls._instance

    def save(
        self,
        measurement_id: str,
        product_code: str,
        serial_number: str,
        description: str,
    ):
        self._data[measurement_id] = {
            "product_code": product_code,
            "serial_number": serial_number,
            "description": description,
        }

    def get(self, measurement_id: str) -> Optional[Dict]:
        return self._data.get(measurement_id)

    def clear(self, measurement_id: str):
        if measurement_id in self._data:
            del self._data[measurement_id]

    def clear_all(self):
        self._data.clear()
