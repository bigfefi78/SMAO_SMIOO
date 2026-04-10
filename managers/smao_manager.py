"""
SMAO Manager - Gestione componente SMAO (Motion Control)
"""
import win32com.client
from core.logging_tools import GuiLogger


class SMAOManager:
    """Wrapper per il componente SMAO"""

    def __init__(self):
        self.main = None
        self.info = None
        self.status = False
        self.logger = GuiLogger.instance()

    def initialize_smao(self):
        """
        Inizializza il componente SMAO.

        Returns:
            bool: True se inizializzato correttamente
        """
        prog_id = "SMAO.SMaoMain"

        try:
            self.logger.info(
                f"Tentativo di creazione oggetto COM: {prog_id}", self.__class__.__name__
            )
            self.main = win32com.client.Dispatch(prog_id)

            risultato = self.main.Initialize()

            if risultato < 0:
                self.logger.error(
                    f"Inizializzazione fallita (Codice: {risultato})", self.__class__.__name__
                )
                self.status = False
            else:
                self.info = self.main.Info
                self.status = True
                self.logger.info("Inizializzato correttamente", self.__class__.__name__)

        except Exception as ex:
            self.logger.error(f"Errore di connessione: {ex}", self.__class__.__name__)
            self.status = False

        return self.status

    def get_info(self):
        """Stampa informazioni sui driver SMAO nel log."""
        if not self.status:
            self.logger.warning("SMAO non inizializzato!", self.__class__.__name__)
            return

        main_drivers_count = self.main.DriversCount
        self.logger.info(f"Drivers installati: {main_drivers_count}", self.__class__.__name__)
        for i in range(main_drivers_count):
            self.logger.info(f"  {i+1}. {self.main.Driver(i + 1)}", self.__class__.__name__)

        info_driver_count = self.info.DriversCount
        self.logger.info(f"Drivers abilitati: {info_driver_count}", self.__class__.__name__)
        for i in range(info_driver_count):
            self.logger.info(f"  {i+1}. {self.info.Drivers(i + 1)}", self.__class__.__name__)

    def get_driver(self, index):
        """
        Ottiene un driver specifico.

        Args:
            index: Indice del driver (1-based)
        """
        if not self.status:
            self.logger.warning("SMAO non inizializzato!", self.__class__.__name__)
            return None

        try:
            return self.main.Driver(index)
        except Exception as ex:
            self.logger.error(f"Errore recupero driver {index}: {ex}", self.__class__.__name__)
            return None

    def shutdown(self):
        """Chiude e rilascia risorse SMAO."""
        if self.main:
            try:
                self.main = None
                self.info = None
                self.status = False
                self.logger.info("Shutdown completato", self.__class__.__name__)
            except Exception as ex:
                self.logger.error(f"Errore durante shutdown: {ex}", self.__class__.__name__)