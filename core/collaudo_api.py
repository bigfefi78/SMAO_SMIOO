
class CollaudoAPI:
    """
    Espone le API del motore base a ciclo plug-in.
    Usa i manager già istanziati!
    """

    def __init__(
        self, sensor_manager, smioo_manager, measurements_engine, products_db, logger
    ):
        self.sensor_manager = sensor_manager
        self.smioo_manager = smioo_manager
        self.measurements_engine = measurements_engine
        self.products_db = products_db
        self.logger = logger

    # Lettura sensori
    def read_sensor(self, label):
        ch = self.sensor_manager.get_channel_by_label(label)
        return ch.current_value if ch else None

    # Scrittura output
    def set_output(self, channel, value):
        return self.smioo_manager.write_output(channel, value)

    # Lettura input
    def read_input(self, channel):
        return self.smioo_manager.read_input(channel)

    # Misure
    def get_enabled_measurements(self):
        return self.measurements_engine.get_enabled_measurements()

    def calculate_measurement(self, measurement):
        return self.measurements_engine.calculate_measurement(measurement)

    # Logging (collaudo/results)
    def log_test(self, data_dict):
        # append data_dict to log (implement as needed)
        pass

    # DB prodotto
    def get_product(self, code):
        return self.products_db.get_product_by_code(code)
