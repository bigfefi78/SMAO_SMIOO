"""
Dialog per calibrazione Rapporto Bracci (RB)
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QCheckBox,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class RBCalibrationDialog(QDialog):
    """
    Dialog per calibrare il Rapporto Bracci di un sensore

    Procedura:
    1. Inserisci spessore campione (default 50 µm)
    2. Clicca "Acquisisci CON spessore" → emette acquisitionRequested
    3. Dopo acquisizione, clicca "Acquisisci SENZA spessore"
    4. Calcola automaticamente RB = spessore / |differenza|
    5. OK per applicare, Annulla per scartare

    IMPORTANTE: Imposta calibration_mode = True all'apertura
    """

    # Signal emesso quando serve acquisire un valore
    acquisitionRequested = pyqtSignal()

    def __init__(self, channel_label: str, channel_info, parent=None):
        super().__init__(parent)

        self.channel_info = channel_info
        self.channel_label = channel_label

        # Attiva modalità calibrazione
        self.channel_info.calibration_mode = True
        print(f"[RBCalibration] Modalità calibrazione ATTIVATA per {channel_label}")

        # Valori acquisiti
        self.value_with = None
        self.value_without = None
        self.calculated_rb = None

        # Flag per sapere quale pulsante è stato premuto
        self.acquiring_for_with = None  # True = WITH, False = WITHOUT, None = nessuno

        self._setup_ui()

    def _setup_ui(self):
        """Costruisce interfaccia"""
        self.setWindowTitle(f"Calibrazione RB - {self.channel_label}")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        # === TITOLO ===
        title = QLabel(f"Calibrazione Rapporto Bracci\nCanale: {self.channel_label}")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        title.setFont(font)
        layout.addWidget(title)

        # === SPESSORE CAMPIONE ===
        group_thickness = QGroupBox("Spessore Campione")
        layout_thickness = QHBoxLayout()

        layout_thickness.addWidget(QLabel("Spessore:"))

        self.spinThickness = QDoubleSpinBox()
        self.spinThickness.setRange(0.01, 10000.0)
        self.spinThickness.setValue(50.0)
        self.spinThickness.setDecimals(2)
        self.spinThickness.setSuffix(" µm")
        layout_thickness.addWidget(self.spinThickness)

        group_thickness.setLayout(layout_thickness)
        layout.addWidget(group_thickness)

        # === ACQUISIZIONI ===
        group_acq = QGroupBox("Acquisizioni")
        layout_acq = QVBoxLayout()

        # CON spessore
        layout_with = QHBoxLayout()
        self.btnAcquireWith = QPushButton("📏 Acquisisci CON spessore")
        self.btnAcquireWith.clicked.connect(self._on_acquire_with)
        layout_with.addWidget(self.btnAcquireWith)

        self.labelValueWith = QLabel("---")
        self.labelValueWith.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_with.addWidget(self.labelValueWith)
        layout_acq.addLayout(layout_with)

        # SENZA spessore
        layout_without = QHBoxLayout()
        self.btnAcquireWithout = QPushButton("📐 Acquisisci SENZA spessore")
        self.btnAcquireWithout.clicked.connect(self._on_acquire_without)
        self.btnAcquireWithout.setEnabled(False)
        layout_without.addWidget(self.btnAcquireWithout)

        self.labelValueWithout = QLabel("---")
        self.labelValueWithout.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_without.addWidget(self.labelValueWithout)
        layout_acq.addLayout(layout_without)

        group_acq.setLayout(layout_acq)
        layout.addWidget(group_acq)

        # === RB CALCOLATO ===
        group_rb = QGroupBox("Rapporto Bracci Calcolato")
        layout_rb = QVBoxLayout()

        self.labelCalculatedRB = QLabel("--- (acquisire entrambi i valori)")
        self.labelCalculatedRB.setAlignment(Qt.AlignCenter)
        self.labelCalculatedRB.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: blue;"
        )
        layout_rb.addWidget(self.labelCalculatedRB)

        group_rb.setLayout(layout_rb)
        layout.addWidget(group_rb)

        # === INSERIMENTO MANUALE ===
        group_manual = QGroupBox("Inserimento Manuale")
        layout_manual = QVBoxLayout()

        self.checkManual = QCheckBox("Inserisci RB manualmente")
        self.checkManual.stateChanged.connect(self._on_manual_toggled)
        layout_manual.addWidget(self.checkManual)

        layout_manual_spin = QHBoxLayout()
        layout_manual_spin.addWidget(QLabel("RB:"))

        self.spinManualRB = QDoubleSpinBox()
        self.spinManualRB.setRange(-100, 100.0)
        self.spinManualRB.setValue(1.0)
        self.spinManualRB.setDecimals(4)
        self.spinManualRB.setEnabled(False)
        layout_manual_spin.addWidget(self.spinManualRB)

        layout_manual.addLayout(layout_manual_spin)
        group_manual.setLayout(layout_manual)
        layout.addWidget(group_manual)

        # === PULSANTI OK/ANNULLA ===
        layout_buttons = QHBoxLayout()

        self.btnOk = QPushButton("✓ OK")
        self.btnOk.clicked.connect(self._on_ok)
        self.btnOk.setEnabled(False)
        layout_buttons.addWidget(self.btnOk)

        btnCancel = QPushButton("✗ Annulla")
        btnCancel.clicked.connect(self.reject)
        layout_buttons.addWidget(btnCancel)

        layout.addLayout(layout_buttons)

        self.setLayout(layout)

    def _on_acquire_with(self):
        """Richiesta acquisizione CON spessore"""
        print("[RBCalibration] Richiesta acquisizione CON spessore")
        self.acquiring_for_with = True  # Imposta flag PRIMA di emettere
        self.acquisitionRequested.emit()

    def _on_acquire_without(self):
        """Richiesta acquisizione SENZA spessore"""
        print("[RBCalibration] Richiesta acquisizione SENZA spessore")
        self.acquiring_for_with = False  # ✅ Imposta flag PRIMA di emettere
        self.acquisitionRequested.emit()

    def set_acquired_value(self, value: float):
        """
        Chiamato dall'esterno dopo acquisizione.
        Usa il flag acquiring_for_with per decidere dove mettere il valore.

        Args:
            value: Valore grezzo acquisito
        """
        if self.acquiring_for_with is None:
            print(
                "[RBCalibration] ERRORE: set_acquired_value chiamato senza flag impostato!"
            )
            return

        if self.acquiring_for_with:
            # Acquisizione CON spessore
            self.value_with = value
            self.labelValueWith.setText(f"Valore acquisito: {value:.3f} µm")
            self.btnAcquireWithout.setEnabled(True)
            print(f"[RBCalibration] ✓ Valore CON spessore: {value:.3f}")

        else:
            # Acquisizione SENZA spessore
            self.value_without = value
            self.labelValueWithout.setText(f"Valore acquisito: {value:.3f} µm")
            self._calculate_rb()
            print(f"[RBCalibration] ✓ Valore SENZA spessore: {value:.3f}")

        # Reset flag dopo l'uso
        self.acquiring_for_with = None

    def _calculate_rb(self):
        """Calcola RB = spessore / |differenza|"""
        if self.value_with is None or self.value_without is None:
            return

        thickness = self.spinThickness.value()
        diff = abs(self.value_with - self.value_without)

        # ✅ PRINT DI DEBUG
        print(f"[DEBUG] value_with PRECISO:   {self.value_with}")
        print(f"[DEBUG] value_without PRECISO: {self.value_without}")
        print(f"[DEBUG] thickness:             {thickness}")

        diff = abs(self.value_with - self.value_without)

        print(f"[DEBUG] differenza:            {diff}")
        print(f"[DEBUG] RB calcolato:          {thickness / diff}")

        if diff < 0.001:
            self.labelCalculatedRB.setText("ERRORE: Differenza troppo piccola!")
            self.labelCalculatedRB.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: red;"
            )
            return

        self.calculated_rb = thickness / diff
        self.labelCalculatedRB.setText(f"RB = {self.calculated_rb:.4f}")
        self.labelCalculatedRB.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green;"
        )
        self.btnOk.setEnabled(True)

        print(f"[RBCalibration] RB calcolato: {self.calculated_rb:.4f}")

    def _on_manual_toggled(self, state):
        """Toggle inserimento manuale"""
        is_manual = state == Qt.Checked
        self.spinManualRB.setEnabled(is_manual)
        self.btnOk.setEnabled(is_manual or self.calculated_rb is not None)

    def _on_ok(self):
        """Conferma e applica RB"""
        if self.checkManual.isChecked():
            # RB manuale
            new_rb = self.spinManualRB.value()
            print(f"[RBCalibration] Applicato RB MANUALE: {new_rb:.4f}")
        else:
            # RB calcolato
            new_rb = self.calculated_rb
            print(f"[RBCalibration] Applicato RB CALCOLATO: {new_rb:.4f}")

        # Applica RB
        self.channel_info.rb = new_rb

        # ✅ DISATTIVA MODALITÀ CALIBRAZIONE
        self.channel_info.calibration_mode = False
        print(
            f"[RBCalibration] Modalità calibrazione DISATTIVATA per {self.channel_label}"
        )

        self.accept()

    def reject(self):
        """Annulla calibrazione"""
        # ✅ DISATTIVA MODALITÀ CALIBRAZIONE
        self.channel_info.calibration_mode = False
        print(
            "[RBCalibration] Calibrazione ANNULLATA - Modalità calibrazione DISATTIVATA"
        )
        super().reject()

    def closeEvent(self, event):
        """Gestisce chiusura finestra (X)"""
        # ✅ DISATTIVA MODALITÀ CALIBRAZIONE
        self.channel_info.calibration_mode = False
        print("[RBCalibration] Finestra chiusa - Modalità calibrazione DISATTIVATA")
        super().closeEvent(event)
