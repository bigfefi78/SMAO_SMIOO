"""
Action Timer - Timer con azioni start/end
"""
import threading


class ActionTimer:
    def __init__(self, duration_seconds, start_action, end_action):
        """
        Timer con azioni configurabili
        
        Args:
            duration_seconds: Durata in secondi (es. 0.5 o 5)
            start_action: Funzione da eseguire SUBITO allo start
            end_action: Funzione da eseguire quando scade il tempo
        """
        self.duration = duration_seconds
        self.start_action = start_action
        self.end_action = end_action
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """Avvia il timer"""
        # 1. Esegui l'azione di START (immediata)
        if self.start_action:
            print("[TIMER] Eseguo azione di START...")
            self.start_action()

        # 2. Reset evento di stop
        self._stop_event.clear()

        # 3. Avvia thread
        self._thread = threading.Thread(target=self._run_timer)
        self._thread.daemon = True
        self._thread.start()

    def _run_timer(self):
        """Thread che aspetta la durata specificata"""
        is_stopped = self._stop_event.wait(self.duration)

        if not is_stopped:
            print(f"[TIMER] Tempo scaduto ({self.duration}s). Eseguo azione di END.")
            if self.end_action:
                self.end_action()
        else:
            print("[TIMER] Timer fermato manualmente.")

    def stop(self):
        """Ferma il timer prima della scadenza"""
        self._stop_event.set()