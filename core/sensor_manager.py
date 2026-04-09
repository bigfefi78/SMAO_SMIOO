"""
Gestione connessione e acquisizione dati da SMAO
"""

import win32com.client
from typing import List, Callable, Optional
from models import ChannelInfo, SMAOStatus
from core.logging_tools import GuiLogger


class SensorManager:
    """
    Gestisce la connessione a SMAO e l'acquisizione dai sensori
    """

    def __init__(self):
        self.smao_main = None
        self.smao_info = None
        self.status = SMAOStatus.OFF
        self.all_channels: List[ChannelInfo] = []
        self.active_channels: List[ChannelInfo] = []
        self.logger = GuiLogger.instance()

        # Callbacks
        self._on_status_changed: Optional[Callable] = None
        self._on_channels_updated: Optional[Callable] = None

    def on_status_changed(self, callback: Callable):
        """Registra callback per cambio stato"""
        self._on_status_changed = callback

    def on_channels_updated(self, callback: Callable):
        """Registra callback per aggiornamento canali"""
        self._on_channels_updated = callback

    def _set_status(self, new_status: SMAOStatus):
        """Cambia stato e notifica"""
        if self.status != new_status:
            self.status = new_status
            if self._on_status_changed:
                self._on_status_changed(new_status)

    def is_connected(self) -> bool:
        """Verifica se SMAO è connesso"""
        return self.status == SMAOStatus.OK

    def initialize(self) -> SMAOStatus:
        """
        Inizializza connessione a SMAO
        Returns:
            SMAOStatus corrente
        """
        prog_id = "SMAO.SMaoMain"

        try:
            self.smao_main = win32com.client.Dispatch(prog_id)
            result = self.smao_main.Initialize("")

            if result < 0:
                self.logger.error(
                    f"Inizializzazione SMAO fallita (Codice: {result})",
                    self.__class__.__name__,
                )
                self._set_status(SMAOStatus.NOK)
            else:
                self.smao_info = self.smao_main.Info
                self._set_status(SMAOStatus.OK)
                self.logger.info(
                    "SMAO inizializzato correttamente", self.__class__.__name__
                )

            return self.status

        except Exception as ex:
            self.logger.error(
                f"Errore connessione a SMAO: {ex}", sender=self.__class__.__name__
            )
            # print(f"[SensorManager] ✗ Errore connessione: {ex}")
            import traceback

            traceback.print_exc()
            self._set_status(SMAOStatus.NOK)
            return self.status

    def scan_channels(self) -> int:
        """
        Scansiona tutti i canali configurati

        Returns:
            Numero di canali attivi trovati
        """
        if not self.is_connected():
            self.logger.error(
                "SMAO non connesso. Impossibile scansionare canali.",
                self.__class__.__name__,
            )
            # print("[SensorManager] ERRORE: SMAO non connesso")
            return 0

        self.all_channels.clear()
        self.active_channels.clear()

        try:
            total_sensors = self.smao_info.SensorsCount
            self.logger.info(
                f"Scansione {total_sensors} sensori configurati...",
                self.__class__.__name__,
            )
            # print(f"[SensorManager] Scansione {total_sensors} sensori configurati...")

            for sensor_idx in range(1, total_sensors + 1):
                driver_name = self.smao_info.SensorDriver(sensor_idx)
                channel_number = self.smao_info.SensorChannel(sensor_idx)

                channel = ChannelInfo(
                    driver_name=driver_name,
                    channel_number=channel_number,
                    user_channel_number=sensor_idx,
                )

                try:
                    single_ch = self.smao_main.NewSingleChannel()
                    single_ch.Driver = driver_name
                    single_ch.Channel = channel_number
                    single_ch.DoAcquisition()

                    if single_ch.ChannelStatus == 0:
                        channel.is_active = True
                        channel.current_value = float(single_ch.Value)
                        self.active_channels.append(channel)
                        self.logger.debug(
                            f"{channel.label} ({driver_name} Ch.{channel_number}): {channel.current_value:.3f} µm",
                            self.__class__.__name__,
                        )
                        # print(
                        #     f"  ✓ {channel.label} ({driver_name} Ch.{channel_number}): {channel.current_value:.3f} µm"
                        # )

                    del single_ch

                except Exception as ex:
                    self.logger.error(
                        f"Errore acquisizione canale {channel.label}: {ex}",
                        self.__class__.__name__,
                    )
                    # print(f"  ✗ {channel.label}: {ex}")

                self.all_channels.append(channel)

            # print(
            #     f"[SensorManager] ✓ Scansione completata: {len(self.active_channels)} canali attivi su {len(self.all_channels)}"
            # )
            self.logger.info(
                f"Scansione completata: {len(self.active_channels)} canali attivi su {len(self.all_channels)}.",
                self.__class__.__name__,
            )

            if self._on_channels_updated:
                self._on_channels_updated()

            return len(self.active_channels)

        except Exception as ex:
            self.logger.error(
                f"Errore durante scansione canali: {ex}", self.__class__.__name__
            )
            # print(f"[SensorManager] ERRORE durante scansione: {ex}")
            import traceback

            traceback.print_exc()
            return 0

    def acquire_all_active_channels(self) -> bool:
        """
        Acquisisce valori da tutti i canali attivi usando SingleChannel
        """
        if not self.is_connected():
            return False

        try:
            for channel in self.active_channels:
                single_ch = self.smao_main.NewSingleChannel()
                single_ch.Driver = channel.driver_name
                single_ch.Channel = channel.channel_number

                single_ch.NumSamples = channel.num_samples

                single_ch.DoAcquisition()

                # Leggi status acquisizione
                ch_status = single_ch.ChannelStatus

                # Aggiorna current_status nel ChannelInfo
                from models import ChannelStatus

                channel.current_status = ChannelStatus(ch_status)

                # Solo se OK, aggiorna valore corrente applicando RB
                if ch_status == 0:
                    raw_value = float(single_ch.Value)
                    corrected_value = raw_value * channel.rb
                    channel.current_value = corrected_value

                del single_ch

            return True

        except Exception as ex:
            self.logger.error(
                f"Errore durante acquisizione canali: {ex}.", {self.__class__.__name__}
            )
            import traceback

            traceback.print_exc()
            return False

    def get_active_channels(self) -> List[ChannelInfo]:
        """Ritorna lista canali attivi"""
        return self.active_channels

    def get_all_channels(self) -> List[ChannelInfo]:
        """Ritorna tutti i canali"""
        return self.all_channels

    def get_channel_by_user_number(self, user_number: int) -> Optional[ChannelInfo]:
        """Trova canale per numero utente"""
        for ch in self.all_channels:
            if ch.user_channel_number == user_number:
                return ch
        return None

    def shutdown(self):
        """Chiude connessione SMAO"""
        if self.smao_main:
            try:
                self.smao_main = None
                self.smao_info = None
                self._set_status(SMAOStatus.OFF)
                self.logger.info("Shutdown SMAO completato.", self.__class__.__name__)
            except Exception as e:
                self.logger.error(
                    f"Errore durante shutdown: {e}.", self.__class__.__name__
                )

    # ======================================
    # METODI ALIAS PER COMPATIBILITÀ
    # ======================================

    def connect(self) -> bool:
        """
        Alias per initialize() - connette a SMAO

        Returns:
            True se connesso, False altrimenti
        """
        status = self.initialize()
        return status == SMAOStatus.OK

    def disconnect(self):
        """
        Alias per shutdown() - disconnette da SMAO
        """
        self.shutdown()

    def get_channel_by_label(self, label: str) -> Optional[ChannelInfo]:
        """
        Trova canale per label (es. "T-01")

        Args:
            label: Label canale

        Returns:
            ChannelInfo o None
        """
        for ch in self.all_channels:
            if ch.label == label:
                return ch
        return None

    def update_all_channels(self):
        """
        Alias per acquire_all_active_channels() - aggiorna valori
        """
        return self.acquire_all_active_channels()
