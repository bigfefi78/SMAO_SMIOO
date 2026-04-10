"""
API esposta al sistema di cicli di collaudo (CyclePluginBase).
Fornisce accesso ai manager già inizializzati dall'applicazione.
"""


class CollaudoAPI:
    """
    Facade che espone le funzionalità core ai plugin di ciclo.
    Riceve i manager già istanziati: non crea né possiede risorse proprie.
    """

    def __init__(
        self, sensor_manager, smioo_manager, measurements_engine, products_db, logger
    ):
        self.sensor_manager = sensor_manager
        self.smioo_manager = smioo_manager
        self.measurements_engine = measurements_engine
        self.products_db = products_db
        self.logger = logger

    def read_sensor(self, label):
        """Legge il valore corrente di un sensore per etichetta."""
        ch = self.sensor_manager.get_channel_by_label(label)
        return ch.current_value if ch else None

    def set_output(self, channel, value):
        """Scrive un valore su un canale di output digitale."""
        return self.smioo_manager.write_output(channel, value)

    def read_input(self, channel):
        """Legge il valore di un canale di input digitale."""
        return self.smioo_manager.read_input(channel)

    def get_enabled_measurements(self):
        """Restituisce la lista delle misure abilitate."""
        return self.measurements_engine.get_enabled_measurements()

    def calculate_measurement(self, measurement):
        """Calcola una singola misura e aggiorna il suo valore corrente."""
        return self.measurements_engine.calculate_measurement(measurement)

    def log_test(self, data_dict: dict):
        """
        Registra un risultato di test nel log applicazione.

        Args:
            data_dict: Dizionario con i dati del test (es. misure, esito, matricola).
        """
        entries = ", ".join(f"{k}={v}" for k, v in data_dict.items())
        self.logger.info(f"Test result: {entries}", sender="CollaudoAPI")

    def get_product(self, code):
        """Recupera un prodotto dal database per codice."""
        return self.products_db.get_product(code)
