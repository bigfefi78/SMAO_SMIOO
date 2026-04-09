from PyQt5.QtWidgets import QWidget


class CyclePluginBase(QWidget):
    LABEL = "Unnamed Cycle"
    DESCRIPTION = "Nessuna descrizione"

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
