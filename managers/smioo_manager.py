import win32com.client
from core.logging_tools import GuiLogger


class SMIOOManager:
    """Wrapper per il componente SMIOO (Input/Output)"""

    def __init__(self):
        self.main = None
        self.info = None
        self.status = False
        self.logger = GuiLogger().instance()

    def initialize_smioo(self):
        prog_id = "SMIOO.SMiooMain"
        try:
            self.logger.info(
                f"Tentativo di creazione oggetto COM: {prog_id}",
                self.__class__.__name__,
            )
            self.main = win32com.client.Dispatch(prog_id)
            risultato = self.main.Initialize()
            if risultato < 0:
                self.logger.error(
                    f"Inizializzazione SMIOO fallita (Codice: {risultato})",
                    self.__class__.__name__,
                )
                self.status = False
            else:
                self.info = self.main.Info
                self.status = True
                self.logger.info(
                    "SMIOO inizializzato correttamente", self.__class__.__name__
                )
        except Exception as ex:
            self.logger.error(f"Errore di connessione: {ex}", self.__class__.__name__)
            self.status = False
        return self.status

    def get_info(self):
        if not self.status:
            self.logger.warning(
                "SMIOO non inizializzato! Impossibile ottenere informazioni.",
                self.__class__.__name__,
            )
            return
        self.logger.info("Recupero informazioni I/O...", self.__class__.__name__)
        self.logger.info(
            f"Input bits: {self.info.InBitsCount}", self.__class__.__name__
        )
        self.logger.info(
            f"Output bits: {self.info.OutBitsCount}", self.__class__.__name__
        )

    def new_output_bit(self, bit_number=None):
        if not self.status:
            self.logger.warning(
                "SMIOO non inizializzato! Impossibile creare OutputBit.",
                self.__class__.__name__,
            )
            return None
        try:
            output = self.main.NewOutputBit()
            if bit_number is not None:
                output.OutputBit = bit_number
                # self.logger.info(
                #     f"OutputBit creato per bit #{bit_number}", self.__class__.__name__
                # )
            else:
                self.logger.info("OutputBit creato", self.__class__.__name__)
            return output
        except Exception as e:
            self.logger.error(
                f"Errore creazione OutputBit: {e}", self.__class__.__name__
            )
            return None

    def new_input_bit(self, bit_number=None):
        if not self.status:
            self.logger.warning(
                "SMIOO non inizializzato! Impossibile creare InputBit.",
                self.__class__.__name__,
            )
            return None
        try:
            input_bit = self.main.NewInputBit()
            if bit_number is not None:
                input_bit.InputBit = bit_number
            else:
                self.logger.info("InputBit creato", self.__class__.__name__)
            return input_bit
        except Exception as e:
            self.logger.error(
                f"Errore creazione InputBit: {e}", self.__class__.__name__
            )
            return None

    def write_output(self, bit_number, value):
        if not self.status:
            self.logger.warning(
                "SMIOO non inizializzato! Impossibile scrivere output.",
                self.__class__.__name__,
            )
            return False
        try:
            output = self.new_output_bit(bit_number)
            if output:
                output.WriteBitValue(value)
                return True
        except Exception as e:
            self.logger.error(
                f"Errore scrittura output #{bit_number}: {e}", self.__class__.__name__
            )
            return False

    def read_input(self, bit_number):
        if not self.status:
            self.logger.warning(
                "SMIOO non inizializzato! Impossibile leggere input.",
                self.__class__.__name__,
            )
            return None
        try:
            input_bit = self.new_input_bit(bit_number)
            if input_bit:
                value = input_bit.ReadBitValue()
                return value
        except Exception as e:
            self.logger.error(
                f"Errore lettura input #{bit_number}: {e}", self.__class__.__name__
            )
            return None

    def shutdown(self):
        if self.main:
            try:
                self.main = None
                self.info = None
                self.status = False
                self.logger.info("Shutdown SMIOO completato.", self.__class__.__name__)
            except Exception as e:
                self.logger.error(
                    f"Errore durante shutdown: {e}", self.__class__.__name__
                )
