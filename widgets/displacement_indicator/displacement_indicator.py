"""
Widget indicatore di spostamento per sensori
"""

try:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import pyqtSignal, pyqtProperty, Qt
    from PyQt5.QtGui import QPainter, QColor, QPen
    from widgets.displacement_indicator.displacement_indicator_widget_ui import Ui_Form
except ImportError as e:
    with open(
        r"F:/LAVORO/PRODAR/CLAUDIA/CARRELLI/carrelli elettrici/PYTHON/CARRELLI_SMAO_SMIOO/displacement_indicator_import_error.txt",
        "w",
    ) as f:
        f.write(f"Errore durante fase di importazione:\n{str(e)}")
try:

    class DisplacementIndicator(QWidget):
        """
        Widget che mostra valore sensore con barra grafica
        """

        # Signals
        # valueChanged = pyqtSignal(float)
        valueChanged = pyqtSignal(
            object
        )  # Cambiato a object per supportare anche None o tuple
        limitExceeded = pyqtSignal(bool)
        rbChanged = pyqtSignal(float)
        calibrationAcquisitionRequested = pyqtSignal(object)

        def __init__(self, parent=None):
            super().__init__(parent)

            # CARICA UI COMPILATA
            self.ui = Ui_Form()
            self.ui.setupUi(self)

            # Proprietà interne
            self._value = 0.0
            self._label = "T-01"
            self._unit = "µm"
            self._min_range = -100.0
            self._max_range = 100.0
            self._min_limit = -80.0
            self._max_limit = 80.0
            self._decimals = 2
            self._rb = 1.0

            # Riferimento al ChannelInfo
            self.channel_info = None

            # Connessioni
            self.ui.pushButtonRB.clicked.connect(self._on_rb_clicked)
            # Doppio click su label
            self.ui.labelChannel.mouseDoubleClickEvent = self._on_label_double_click

            # Override di paintEvent del frameBar
            self.ui.frameBar.paintEvent = self._paint_bar

            # Imposto la label per RB
            self.ui.labelRB.setText(f"{self._rb:.2f}")

            # Inizializza display
            self._update_display()

        # ===== PROPERTIES (tutti uguali) =====

        # @pyqtProperty(float)
        @pyqtProperty(float)  # Cambiato a object per supportare anche None o tuple
        def value(self):
            return self._value

        @value.setter
        def value(self, val):
            if self._value != val:
                self._value = val
                self._update_display()
                self.valueChanged.emit(val)

                # Se è None, consideriamo che il limite sia "superato" (o errore)
                if val is None:
                    self.limitExceeded.emit(True)
                else:
                    # Gestione tuple se arrivano dal driver (prendiamo il primo elemento)
                    check_val = val[1] if isinstance(val, tuple) else val
                    if isinstance(check_val, (int, float)):
                        is_exceeded = val < self._min_limit or val > self._max_limit
                        self.limitExceeded.emit(is_exceeded)

        def setValue(self, val):
            self.value = val

        @pyqtProperty(str)
        def label(self):
            return self._label

        @label.setter
        def label(self, val):
            self._label = val
            self.ui.labelChannel.setText(val)

        @pyqtProperty(str)
        def unit(self):
            return self._unit

        @unit.setter
        def unit(self, val):
            self._unit = val
            self.ui.labelUnit.setText(val)

        @pyqtProperty(float)
        def minRange(self):
            return self._min_range

        @minRange.setter
        def minRange(self, val):
            self._min_range = val
            self._update_bar()

        @pyqtProperty(float)
        def maxRange(self):
            return self._max_range

        @maxRange.setter
        def maxRange(self, val):
            self._max_range = val
            self._update_bar()

        @pyqtProperty(float)
        def minLimit(self):
            return self._min_limit

        @minLimit.setter
        def minLimit(self, val):
            self._min_limit = val
            self._update_bar()

        @pyqtProperty(float)
        def maxLimit(self):
            return self._max_limit

        @maxLimit.setter
        def maxLimit(self, val):
            self._max_limit = val
            self._update_bar()

        @pyqtProperty(int)
        def decimals(self):
            return self._decimals

        @decimals.setter
        def decimals(self, val):
            self._decimals = val
            self._update_display()

        @pyqtProperty(float)
        def rb(self):
            return self._rb

        @rb.setter
        def rb(self, val):
            if self._rb != val:
                self._rb = val
                self.ui.labelRB.setText(f"{val:.2f}")
                self.rbChanged.emit(val)

                if self.channel_info:
                    self.channel_info.rb = val

        # ===== METODI =====
        def set_channel_info(self, channel_info):
            """
            Collega il ChannelInfo e carica tutti i parametri
            """
            self.channel_info = channel_info

            # Carica tutti i parametri dal ChannelInfo
            self.label = channel_info.label
            self.unit = channel_info.unit
            self._decimals = channel_info.decimals
            self._min_range = channel_info.min_range
            self._max_range = channel_info.max_range
            self._min_limit = channel_info.min_limit
            self._max_limit = channel_info.max_limit

            # Carica RB da channel_info
            self.rb = channel_info.rb

            self._update_display()

        def _update_display(self):
            """Aggiorna SOLO il testo del valore"""

            # CASO ERRORE (None)
            if self._value is None:
                self.ui.labelValue.setText("ERR")
                # 🔴 STILE ROSSO PER ERRORE
                self.ui.labelValue.setStyleSheet(
                    "background-color: black; color: #FF0000; border: 2px solid #D32F2F; font-weight: bold;"
                )
                self._update_bar()  # Pulisce la barra
                return

            # CASO NORMALE (Float)
            val = self._value
            if isinstance(val, tuple):
                val = val[1]

            if not isinstance(val, (int, float)):
                # Caso fallback se arriva spazzatura
                self.ui.labelValue.setText("NaN")
                return

            # Formattazione numero
            try:
                text = f"{val:06.{self._decimals}f}"
            except Exception:
                text = str(val)

            self.ui.labelValue.setText(text)

            # Gestione colori limiti (Verde vs Rosso standard)
            if val < self._min_limit or val > self._max_limit:
                # Fuori tolleranza
                self.ui.labelValue.setStyleSheet(
                    "background-color: black; color: #FF0000; border: 2px solid #FF0000;"
                )
            else:
                # In tolleranza
                self.ui.labelValue.setStyleSheet(
                    "background-color: black; color: #00FF00; border: 2px solid #555;"
                )

            self._update_bar()

            """# Proteggi: converti None in 0.0, tuple in primo elemento se del caso
            val = self._value
            if val is None:
                val = 9999.9999  # Valore di errore per evidenziare problema
            if isinstance(val, tuple):
                val = val[0]
            try:
                text = f"{val:06.{self._decimals}f}"
            except Exception:
                text = str(val)

            self.ui.labelValue.setText(text)

            if val < self._min_limit or val > self._max_limit:
                current_style = self.ui.labelValue.styleSheet()
                new_style = current_style.replace("color: #00FF00", "color: #FF0000")
                self.ui.labelValue.setStyleSheet(new_style)
            else:
                self.ui.labelValue.setStyleSheet(
                    "background-color: black; color: #00FF00; border: 2px solid #555;"
                )

            self._update_bar()"""

        def _update_bar(self):
            """Forza ridisegno della barra"""
            self.ui.frameBar.update()

        def _paint_bar(self, event):
            """
            Disegna la barra grafica con rettangolo riempito.
            Gestisce in modo robusto None e tuple.
            """
            painter = QPainter(self.ui.frameBar)
            painter.setRenderHint(QPainter.Antialiasing)

            # =========================================================
            # 1. CONTROLLI DI SICUREZZA (ROBUSTEZZA)
            # =========================================================

            # Recupera il valore locale
            current_val = self._value

            # Se è None (es. sensore staccato, errore misura), esci subito.
            # Non disegniamo barre "impazzite". La label mostrerà "ERR".
            if current_val is None:
                return

            # Se è una tupla (es. arriva dal driver come (valore, status)), prendi il primo elemento
            if isinstance(current_val, tuple):
                current_val = current_val[1]

            # Se per qualche motivo non è ancora un numero, esci
            if not isinstance(current_val, (int, float)):
                return

            # =========================================================
            # 2. CALCOLI GEOMETRICI
            # =========================================================

            width = self.ui.frameBar.width()
            height = self.ui.frameBar.height()

            # Evita crash su resize molto piccoli o range nullo
            if width <= 10 or height <= 10:
                return

            range_span = self._max_range - self._min_range
            if range_span == 0:
                return

            def value_to_x(val):
                """Converte valore in coordinata X (clamped ai bordi)"""
                # Normalizza tra 0.0 e 1.0
                normalized = (val - self._min_range) / range_span
                # Scala alla larghezza widget e limita ai bordi
                pixel = int(normalized * width)
                return max(0, min(width, pixel))

            # =========================================================
            # 3. DISEGNO ELEMENTI STATICI (Linee Zero e Limiti)
            # =========================================================

            # LINEA ZERO (gialla spessa al centro)
            # Disegnala solo se lo zero è compreso nel range visualizzato
            if self._min_range <= 0 <= self._max_range:
                zero_x = value_to_x(0)
                painter.setPen(QPen(QColor(255, 255, 0), 2))
                painter.drawLine(zero_x, 0, zero_x, height)
            else:
                # Se lo zero è fuori, usiamo il bordo come riferimento logico per la barra
                zero_x = 0 if self._min_range > 0 else width

            # LINEE LIMITI (rosse tratteggiate)
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))

            if self._min_range <= self._min_limit <= self._max_range:
                min_x = value_to_x(self._min_limit)
                painter.drawLine(min_x, 0, min_x, height)

            if self._min_range <= self._max_limit <= self._max_range:
                max_x = value_to_x(self._max_limit)
                painter.drawLine(max_x, 0, max_x, height)

            # =========================================================
            # 4. DISEGNO BARRA DINAMICA
            # =========================================================

            bar_height = height // 2
            bar_y = (height - bar_height) // 2  # Centrato verticalmente

            # Posizione X del valore corrente
            value_x = value_to_x(current_val)

            # Colore: verde se OK, rosso se fuori limiti
            if current_val < self._min_limit or current_val > self._max_limit:
                color = QColor(255, 0, 0, 200)  # Rosso semi-trasparente
            else:
                color = QColor(0, 255, 0, 200)  # Verde semi-trasparente

            # Logica rettangolo: parte sempre dallo Zero (o dal bordo più vicino allo zero)
            if current_val >= 0:
                # Positivo: da zero verso DESTRA
                rect_x = zero_x
                rect_width = value_x - zero_x
            else:
                # Negativo: da value verso zero (cioè verso SINISTRA rispetto allo zero)
                rect_x = value_x
                rect_width = zero_x - value_x

            # Disegna il rettangolo
            painter.fillRect(rect_x, bar_y, rect_width, bar_height, color)

            # =========================================================
            # 5. INDICATORI FUORI SCALA (Frecce Bianche)
            # =========================================================

            # Se il valore esce dal grafico (Range, non Limite), disegniamo una freccia
            if current_val < self._min_range or current_val > self._max_range:
                painter.setPen(QPen(QColor(255, 255, 255), 3))
                painter.setBrush(QColor(255, 255, 255))

                arrow_y = height // 2

                if current_val < self._min_range:
                    # Freccia SINISTRA (<--)
                    arrow_x = 10
                    painter.drawLine(arrow_x + 10, arrow_y, arrow_x, arrow_y)  # Asta
                    painter.drawLine(
                        arrow_x + 5, arrow_y - 5, arrow_x, arrow_y
                    )  # Ala su
                    painter.drawLine(
                        arrow_x + 5, arrow_y + 5, arrow_x, arrow_y
                    )  # Ala giù

                elif current_val > self._max_range:
                    # Freccia DESTRA (-->)
                    arrow_x = width - 10
                    painter.drawLine(arrow_x - 10, arrow_y, arrow_x, arrow_y)  # Asta
                    painter.drawLine(
                        arrow_x - 5, arrow_y - 5, arrow_x, arrow_y
                    )  # Ala su
                    painter.drawLine(
                        arrow_x - 5, arrow_y + 5, arrow_x, arrow_y
                    )  # Ala giù

        def _on_rb_clicked(self):
            """Gestisce click su pulsante RB"""
            from widgets import RBCalibrationDialog

            if not self.channel_info:
                print("[DisplacementIndicator] ERRORE: channel_info non impostato!")
                return

            print(f"[DisplacementIndicator] Apertura calibrazione RB per {self.label}")

            dialog = RBCalibrationDialog(self.label, self.channel_info, self)
            dialog.acquisitionRequested.connect(
                lambda: self.calibrationAcquisitionRequested.emit(dialog)
            )

            if dialog.exec_() == RBCalibrationDialog.Accepted:
                new_rb = self.channel_info.rb
                self.rb = new_rb
                print(f"[DisplacementIndicator] RB aggiornato a {new_rb:.4f}")

        def _on_label_double_click(self, event):
            """Apre dialog configurazione canale"""
            from widgets import ChannelConfigDialog

            if not self.channel_info:
                print("[DisplacementIndicator] ERRORE: channel_info non impostato!")
                return

            print(f"[DisplacementIndicator] Apertura configurazione per {self.label}")

            dialog = ChannelConfigDialog(self.channel_info, self)

            if dialog.exec_() == ChannelConfigDialog.Accepted:
                # Aggiorna widget con nuovi valori
                self.label = self.channel_info.label
                self.unit = self.channel_info.unit
                self._decimals = self.channel_info.decimals
                self._min_range = self.channel_info.min_range
                self._max_range = self.channel_info.max_range
                self._min_limit = self.channel_info.min_limit
                self._max_limit = self.channel_info.max_limit

                self._update_display()

                print(
                    f"[DisplacementIndicator] Configurazione aggiornata: {self.channel_info}"
                )
except Exception as e:
    with open(
        r"F:/LAVORO/PRODAR/CLAUDIA/CARRELLI/carrelli elettrici/PYTHON/CARRELLI_SMAO_SMIOO/displacement_indicator_import_error.txt",
        "w",
    ) as f:
        f.write(f"Errore durante la creazione della classe:\n{str(e)}")
