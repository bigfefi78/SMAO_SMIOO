"""
Engine per calcolo misure - Coordina sensori, formule e misure
"""

from typing import Dict, List
from models import Measurement, MeasurementStatus, ChannelInfo

from .sensor_manager import SensorManager
from .measurements_manager import MeasurementsManager
from .formula_evaluator import FormulaEvaluator
from .logging_tools import GuiLogger


class MeasurementsEngine:
    """
    Coordina calcolo misure combinando:
    - SensorManager (valori sensori)
    - MeasurementsManager (definizioni misure)
    - FormulaEvaluator (calcolo formule)
    """

    def __init__(
        self, sensor_manager: SensorManager, measurements_manager: MeasurementsManager
    ):
        self.sensor_manager = sensor_manager
        self.measurements_manager = measurements_manager
        self.formula_evaluator = FormulaEvaluator()
        self.logger = GuiLogger.instance()

        self._enabled_measurements: List[Measurement] = []

        self.logger.info("Inizializzato", self.__class__.__name__)

    def load_enabled_measurements(self) -> List[Measurement]:
        """
        Carica solo misure abilitate dal MeasurementsManager.

        Returns:
            Lista misure abilitate
        """
        all_measurements = self.measurements_manager.load_measurements()
        self._enabled_measurements = [m for m in all_measurements if m.enabled]

        self.logger.info(
            f"Caricate {len(self._enabled_measurements)} misure abilitate",
            self.__class__.__name__,
        )

        return self._enabled_measurements

    def get_enabled_measurements(self) -> List[Measurement]:
        """Ottieni misure abilitate dalla cache"""
        return self._enabled_measurements

    def calculate_measurement(self, measurement: Measurement) -> bool:
        """
        Calcola singola misura acquisendo prima i valori dai sensori.

        Args:
            measurement: Oggetto Measurement da calcolare

        Returns:
            True se calcolo riuscito, False altrimenti
        """
        try:
            self.sensor_manager.update_all_channels()

            status = self._check_measurement_status(measurement)
            measurement.status = status

            if status != MeasurementStatus.READY:
                self.logger.warning(
                    f"Misura '{measurement.name}' non pronta: {status.name}",
                    self.__class__.__name__,
                )
                return False

            sensor_values = {}
            for channel_label in measurement.channels:
                channel_info = self.sensor_manager.get_channel_by_label(channel_label)

                if not channel_info or channel_info.current_value is None:
                    self.logger.error(
                        f"Sensore '{channel_label}' non disponibile", self.__class__.__name__
                    )
                    return False

                sensor_values[channel_label] = channel_info.current_value

            success, value, error = self.formula_evaluator.evaluate(measurement.formula, sensor_values)

            if success and value is not None:
                measurement.current_value = value
                return True
            else:
                self.logger.error(
                    f"Errore formula '{measurement.name}': {error}", self.__class__.__name__
                )
                measurement.status = MeasurementStatus.ERROR
                return False

        except Exception as ex:
            self.logger.error(
                f"Errore calcolo '{measurement.name}': {ex}", self.__class__.__name__
            )
            measurement.status = MeasurementStatus.ERROR
            return False

    def calculate_all(self) -> Dict[str, bool]:
        """
        Calcola tutte le misure abilitate

        Returns:
            Dict {measurement_id: success}
        """
        results = {}

        for measurement in self._enabled_measurements:
            success = self.calculate_measurement(measurement)
            results[measurement.id] = success

        return results

    def _check_measurement_status(self, measurement: Measurement) -> MeasurementStatus:
        """
        Verifica stato misura (tutti sensori disponibili?)

        Args:
            measurement: Misura da verificare

        Returns:
            MeasurementStatus
        """
        if not measurement.enabled:
            return MeasurementStatus.DISABLED

        available_count = 0
        total_count = len(measurement.channels)

        for channel_label in measurement.channels:
            channel_info = self.sensor_manager.get_channel_by_label(channel_label)

            if channel_info and channel_info.current_value is not None:
                available_count += 1

        if available_count == total_count:
            return MeasurementStatus.READY
        elif available_count > 0:
            return MeasurementStatus.PARTIAL
        else:
            return MeasurementStatus.ERROR

    def get_measurement_dependencies(
        self, measurement: Measurement
    ) -> List[ChannelInfo]:
        """
        Ottieni lista sensori richiesti da una misura

        Args:
            measurement: Misura

        Returns:
            Lista ChannelInfo dei sensori
        """
        channels = []

        for channel_label in measurement.channels:
            channel_info = self.sensor_manager.get_channel_by_label(channel_label)
            if channel_info:
                channels.append(channel_info)

        return channels
