"""
Gestione connessione e acquisizione dati da SMAO
"""

import traceback
import win32com.client
from typing import List, Callable, Optional
from models import ChannelInfo, ChannelStatus, SMAOStatus
from core.logging_tools import GuiLogger


class SensorManager:
    """
    Gestisce la connessione a SMAO e l'acquisizione dai sensori.

    Ciclo di utilizzo tipico:
        manager = SensorManager()
        ok = manager.connect()
        manager.scan_channels()
        manager.update_all_channels()   # ripetuto nel loop di acquisizione
        manager.disconnect()
    """

    def __init__(self):
        self.smao_main = None
        self.smao_info = None
        self.status = SMAOStatus.OFF
        self.all_channels: List[ChannelInfo] = []
        self.active_channels: List[ChannelInfo] = []
        self.logger = GuiLogger.instance()

        self._on_status_changed: Optional[Callable] = None
        self._on_channels_updated: Optional[Callable] = None

    # ======================================
    # CALLBACKS
    # ======================================

    def on_status_changed(self, callback: Callable):
        """Registra callback per cambio stato"""
        self._on_status_changed = callback

    def on_channels_updated(self, callback: Callable):
        """Registra callback per aggiornamento canali"""
        self._on_channels_updated = callback

    # ======================================
    # CONNESSIONE
    # ======================================

    def connect(self) -> bool:
        """
        Connette e inizializza SMAO.

        Returns:
            True se connesso con successo, False altrimenti.
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
                self.logger.info("SMAO inizializzato correttamente", self.__class__.__name__)

        except Exception as ex:
            self.logger.error(f"Errore connessione a SMAO: {ex}", self.__class__.__name__)
            traceback.print_exc()
            self._set_status(SMAOStatus.NOK)

        return self.status == SMAOStatus.OK

    def disconnect(self):
        """Chiude la connessione a SMAO e rilascia le risorse."""
        if self.smao_main:
            try:
                self.smao_main = None
                self.smao_info = None
                self._set_status(SMAOStatus.OFF)
                self.logger.info("SMAO disconnesso.", self.__class__.__name__)
            except Exception as ex:
                self.logger.error(f"Errore durante disconnessione: {ex}", self.__class__.__name__)

    def is_connected(self) -> bool:
        """Verifica se SMAO è connesso e funzionante."""
        return self.status == SMAOStatus.OK

    # ======================================
    # ACQUISIZIONE
    # ======================================

    def scan_channels(self) -> int:
        """
        Scansiona tutti i canali configurati e aggiorna le liste
        `all_channels` e `active_channels`.

        Returns:
            Numero di canali attivi trovati.
        """
        if not self.is_connected():
            self.logger.error("SMAO non connesso. Impossibile scansionare canali.", self.__class__.__name__)
            return 0

        self.all_channels.clear()
        self.active_channels.clear()

        try:
            total_sensors = self.smao_info.SensorsCount
            self.logger.info(
                f"Scansione {total_sensors} sensori configurati...", self.__class__.__name__
            )

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

                    del single_ch

                except Exception as ex:
                    self.logger.error(
                        f"Errore acquisizione canale {channel.label}: {ex}", self.__class__.__name__
                    )

                self.all_channels.append(channel)

            self.logger.info(
                f"Scansione completata: {len(self.active_channels)} canali attivi su {len(self.all_channels)}.",
                self.__class__.__name__,
            )

            if self._on_channels_updated:
                self._on_channels_updated()

            return len(self.active_channels)

        except Exception as ex:
            self.logger.error(f"Errore durante scansione canali: {ex}", self.__class__.__name__)
            traceback.print_exc()
            return 0

    def update_all_channels(self) -> bool:
        """
        Acquisisce i valori aggiornati da tutti i canali attivi.

        Returns:
            True se l'acquisizione è riuscita, False altrimenti.
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

                channel.current_status = ChannelStatus(single_ch.ChannelStatus)

                if single_ch.ChannelStatus == 0:
                    channel.current_value = float(single_ch.Value) * channel.rb

                del single_ch

            return True

        except Exception as ex:
            self.logger.error(f"Errore durante acquisizione canali: {ex}", sender=self.__class__.__name__)
            traceback.print_exc()
            return False

    # ======================================
    # RICERCA CANALI
    # ======================================

    def get_active_channels(self) -> List[ChannelInfo]:
        """Ritorna la lista dei canali attivi."""
        return self.active_channels

    def get_all_channels(self) -> List[ChannelInfo]:
        """Ritorna la lista di tutti i canali (attivi e non)."""
        return self.all_channels

    def get_channel_by_label(self, label: str) -> Optional[ChannelInfo]:
        """Trova un canale per etichetta (es. "T-01")."""
        for ch in self.all_channels:
            if ch.label == label:
                return ch
        return None

    def get_channel_by_user_number(self, user_number: int) -> Optional[ChannelInfo]:
        """Trova un canale per numero utente."""
        for ch in self.all_channels:
            if ch.user_channel_number == user_number:
                return ch
        return None

    # ======================================
    # PRIVATI
    # ======================================

    def _set_status(self, new_status: SMAOStatus):
        """Aggiorna lo stato e notifica i listener."""
        if self.status != new_status:
            self.status = new_status
            if self._on_status_changed:
                self._on_status_changed(new_status)
