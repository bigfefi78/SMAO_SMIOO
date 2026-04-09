from PyQt5 import QtWidgets, QtCore
from .io_widget_generic_ui import Ui_IOWidgetGeneric

MAX_WIDGET_ROW_COUNT = 16  # massimo righe per widget


class IOWidgetGeneric(QtWidgets.QWidget):
    def __init__(self, channels, tipo="input", parent=None):
        super().__init__(parent)
        self.ui = Ui_IOWidgetGeneric()
        self.ui.setupUi(self)
        self.channels = channels  # lista di dict: [{"name": "...", ...}, ...]
        self.tipo = tipo
        self._setup_headers()
        self._populate_channels()

    def _setup_headers(self):
        if self.tipo == "input":
            self.ui.labelHeader.setText("INPUT DIGITALI")
            self.ui.tableIO.setHorizontalHeaderLabels(
                ["Nome", "Stato IN", "Toggle", "Note"]
            )
        elif self.tipo == "output":
            self.ui.labelHeader.setText("OUTPUT DIGITALI")
            self.ui.tableIO.setHorizontalHeaderLabels(
                ["Nome", "Stato OUT", "Toggle", "Note"]
            )
        else:
            self.ui.labelHeader.setText("Digital I/O")

    def _populate_channels(self):
        table = self.ui.tableIO
        table.setRowCount(MAX_WIDGET_ROW_COUNT)
        for idx in range(MAX_WIDGET_ROW_COUNT):
            # Se il canale esiste, riempi, altrimenti lascia vuoto
            if idx < len(self.channels):
                channel = self.channels[idx]
                nome = channel.get("name", f"{self.tipo.upper()}{idx}")
                stato = channel.get("state", "N/A")
                toggle = channel.get("toggle", "")
                note = channel.get("note", "")

                table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(nome)))
                table.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(stato)))

                # Toggle: checkbox se output, label disabled se input
                if self.tipo == "output":
                    cbx = QtWidgets.QCheckBox()
                    cbx.setChecked(bool(toggle))
                    cbx.setDisabled(False)
                    table.setCellWidget(idx, 2, cbx)
                else:
                    cbx_label = QtWidgets.QLabel(" — ")
                    cbx_label.setAlignment(QtCore.Qt.AlignCenter)
                    table.setCellWidget(idx, 2, cbx_label)

                table.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(note)))
            else:
                # Riga vuota
                table.setItem(idx, 0, QtWidgets.QTableWidgetItem(""))
                table.setItem(idx, 1, QtWidgets.QTableWidgetItem(""))
                table.setCellWidget(idx, 2, QtWidgets.QLabel(""))
                table.setItem(idx, 3, QtWidgets.QTableWidgetItem(""))

    def set_channel_state(self, idx, state, note=""):
        # aggiorna stato e note del canale idx
        self.ui.tableIO.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(state)))
        self.ui.tableIO.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(note)))

    def set_channel_toggle(self, idx, value):
        widget = self.ui.tableIO.cellWidget(idx, 2)
        if isinstance(widget, QtWidgets.QCheckBox):
            widget.setChecked(bool(value))
