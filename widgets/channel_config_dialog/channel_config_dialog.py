"""
Dialog configurazione canale
"""

from PyQt5.QtWidgets import QDialog
from .channel_config_dialog_ui import Ui_ChannelConfigDialog


class ChannelConfigDialog(QDialog):
    """
    Dialog per configurare parametri di un canale
    """

    def __init__(self, channel_info, parent=None):
        super().__init__(parent)

        self.ui = Ui_ChannelConfigDialog()
        self.ui.setupUi(self)

        self.channel_info = channel_info

        # Imposta titolo
        self.ui.labelTitle.setText(f"Configurazione Canale {channel_info.label}")

        # Carica valori attuali
        self.ui.lineEditLabel.setText(channel_info.label)
        self.ui.lineEditUnit.setText(channel_info.unit)
        self.ui.spinBoxDecimals.setValue(channel_info.decimals)
        self.ui.doubleSpinBoxMinRange.setValue(channel_info.min_range)
        self.ui.doubleSpinBoxMaxRange.setValue(channel_info.max_range)
        self.ui.doubleSpinBoxMinLimit.setValue(channel_info.min_limit)
        self.ui.doubleSpinBoxMaxLimit.setValue(channel_info.max_limit)

        # ✅ NumSamples (int)
        self.ui.spinBoxNumSamples.setValue(channel_info.num_samples)

        # Connessioni
        self.ui.pushButtonOK.clicked.connect(self.accept)
        self.ui.pushButtonCancel.clicked.connect(self.reject)

        # Focus su campo label
        self.ui.lineEditLabel.setFocus()
        self.ui.lineEditLabel.selectAll()

    def accept(self):
        """Salva modifiche e chiudi"""
        # Aggiorna ChannelInfo
        self.channel_info.label = (
            self.ui.lineEditLabel.text().strip() or self.channel_info.label
        )
        self.channel_info.unit = self.ui.lineEditUnit.text().strip() or "µm"
        self.channel_info.decimals = self.ui.spinBoxDecimals.value()
        self.channel_info.min_range = self.ui.doubleSpinBoxMinRange.value()
        self.channel_info.max_range = self.ui.doubleSpinBoxMaxRange.value()
        self.channel_info.min_limit = self.ui.doubleSpinBoxMinLimit.value()
        self.channel_info.max_limit = self.ui.doubleSpinBoxMaxLimit.value()

        # ✅ NumSamples (int)
        self.channel_info.num_samples = int(self.ui.spinBoxNumSamples.value())

        print(
            f"[ChannelConfigDialog] Configurazione salvata per {self.channel_info.label}"
        )

        super().accept()
