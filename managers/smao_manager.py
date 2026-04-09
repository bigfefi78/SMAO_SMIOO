"""
SMAO Manager - Gestione componente SMAO (Motion Control)
"""
import win32com.client


class SMAOManager:
    """Wrapper per il componente SMAO"""

    def __init__(self):
        """Inizializzazione del componente SMAO"""
        self.main = None
        self.info = None
        self.status = False

    def initialize_smao(self):
        """
        Inizializza il componente SMAO
        
        Returns:
            bool: True se inizializzato correttamente
        """
        prog_id = "SMAO.SMaoMain"

        try:
            print(f"[SMAO] Tentativo di creazione oggetto COM: {prog_id}")
            self.main = win32com.client.Dispatch(prog_id)

            risultato = self.main.Initialize()

            if risultato < 0:
                print(f"[SMAO] ✗ Inizializzazione fallita (Codice: {risultato})")
                self.status = False
            else:
                self.info = self.main.Info
                self.status = True
                print("[SMAO] ✓ Inizializzato correttamente")

        except Exception as ex:
            print(f"[SMAO] ✗ Errore di connessione: {ex}")
            self.status = False

        return self.status

    def get_info(self):
        """Stampa informazioni sui driver SMAO"""
        if not self.status:
            print("[SMAO] ✗ SMAO non inizializzato!")
            return

        print(f"\n{'='*60}")
        print("[SMAO] INFORMAZIONI DRIVER")
        print(f"{'='*60}")
        
        main_drivers_count = self.main.DriversCount
        print(f"\n📦 Drivers installati: {main_drivers_count}")
        for i in range(main_drivers_count):
            driver_name = self.main.Driver(i + 1)
            print(f"   {i+1}. {driver_name}")
        
        info_driver_count = self.info.DriversCount
        print(f"\n✓ Drivers abilitati: {info_driver_count}")
        for i in range(info_driver_count):
            driver_name = self.info.Drivers(i + 1)
            print(f"   {i+1}. {driver_name}")
        
        print(f"{'='*60}\n")

    def get_driver(self, index):
        """
        Ottiene un driver specifico
        
        Args:
            index: Indice del driver (1-based)
        """
        if not self.status:
            print("[SMAO] ✗ SMAO non inizializzato!")
            return None
        
        try:
            driver = self.main.Driver(index)
            return driver
        except Exception as e:
            print(f"[SMAO] ✗ Errore recupero driver {index}: {e}")
            return None

    def shutdown(self):
        """Chiude e rilascia risorse SMAO"""
        if self.main:
            try:
                self.main = None
                self.info = None
                self.status = False
                print("[SMAO] ✓ Shutdown completato")
            except Exception as e:
                print(f"[SMAO] ⚠ Errore durante shutdown: {e}")