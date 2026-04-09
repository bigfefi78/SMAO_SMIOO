from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import  QTimer
from .io_page_ui import Ui_IOPage
from widgets.container_widget.container import ContainerWidget

NUM_INPUTS_DEFAULT = 8
NUM_OUTPUTS_DEFAULT = 16
MAX_WIDGET_ROW_COUNT = 16  # max numero di righe per container


class IOPage(QWidget):
    def __init__(
        self,
        smioo_manager,
        parent=None,
        num_inputs=NUM_INPUTS_DEFAULT,
        num_outputs=NUM_OUTPUTS_DEFAULT,
    ):
        super().__init__(parent)
        self.smioo_manager = smioo_manager
        self.ui = Ui_IOPage()
        self.ui.setupUi(self)
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.input_leds = []
        self.input_read_btns = []
        self.output_leds = []
        self.output_toggles = []
        self.timer = None
        self.input_containers = []
        self.output_containers = []

        # Se hai btnConnectSmioo: decommenta qui!
        # self.ui.btnConnectSmioo.clicked.connect(self._connect_smioo)

        self.set_enabled_controls(False)

    def _connect_smioo(self):
        ok = self.smioo_manager.initialize_smioo()
        if ok:
            self._build_page()
            self.set_enabled_controls(True)
            self.start_timer()
        else:
            self.set_enabled_controls(False)

    def set_enabled_controls(self, enabled):
        for btn in self.input_read_btns + self.output_toggles:
            btn.setEnabled(enabled)

    def _build_page(self):
        layout = self.ui.layoutContainerHBox  # QHBoxLayout nel file ui!
        # Svuota layout dai vecchi container
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.input_leds.clear()
        self.input_read_btns.clear()
        self.output_leds.clear()
        self.output_toggles.clear()
        self.input_containers.clear()
        self.output_containers.clear()

        # INPUT: blocchi da MAX_WIDGET_ROW_COUNT, TUTTI PRIMA
        idx = 0
        nin = self.num_inputs
        while nin > 0:
            nchan = min(MAX_WIDGET_ROW_COUNT, nin)
            cont = ContainerWidget("INPUT", is_input=True)
            for k in range(nchan):
                lbl, led, btn = cont.add_row(name=f"IN-{idx + 1}", btn_label="Read")
                btn.clicked.connect(lambda _, ch=idx + 1: self.slot_read_input(ch))
                self.input_leds.append(led)
                self.input_read_btns.append(btn)
                idx += 1
            self.input_containers.append(cont)
            layout.addWidget(cont)
            nin -= nchan

        # OUTPUT: blocchi da MAX_WIDGET_ROW_COUNT, TUTTI DOPO
        idx = self.num_inputs
        nout = self.num_outputs
        while nout > 0:
            nchan = min(MAX_WIDGET_ROW_COUNT, nout)
            cont = ContainerWidget("OUTPUT", is_input=False)
            for k in range(nchan):
                lbl, led, btn = cont.add_row(
                    name=f"OUT-{idx + 1}", btn_label="Toggle", btn_checkable=True
                )
                btn.toggled.connect(
                    lambda state, ch=idx + 1: self.slot_toggle_output(ch, state)
                )
                self.output_leds.append(led)
                self.output_toggles.append(btn)
                idx += 1
            self.output_containers.append(cont)
            layout.addWidget(cont)
            nout -= nchan

    def start_timer(self):
        if self.timer:
            self.timer.stop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_io)
        self.timer.start(200)

    def _update_io(self):
        for i, led in enumerate(self.input_leds):
            val = self.smioo_manager.read_input(i + 1)
            led.set_on(bool(val))
        for i, led in enumerate(self.output_leds):
            led.set_on(self.output_toggles[i].isChecked())

    def slot_toggle_output(self, ch, state):
        self.smioo_manager.write_output(ch, state)

    def slot_read_input(self, ch):
        val = self.smioo_manager.read_input(ch)
        self.input_leds[ch - 1].set_on(bool(val))
        print(f"[Read] Ingresso {ch}: {bool(val)}")


# from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSpacerItem, QSizePolicy
# from PyQt5.QtCore import Qt, QTimer
# from .io_page_ui import Ui_IOPage
# from widgets.led_indicator.led_indicator_widget import LedIndicatorWidget

# NUM_INPUTS_DEFAULT = 8
# NUM_OUTPUTS_DEFAULT = 32
# MAX_WIDGET_ROW_COUNT = 16  # max numero di righe per widget.


# class IOPage(QWidget):
#     def __init__(
#         self,
#         smioo_manager,
#         parent=None,
#         num_inputs=NUM_INPUTS_DEFAULT,
#         num_outputs=NUM_OUTPUTS_DEFAULT,
#     ):
#         super().__init__(parent)
#         self.smioo_manager = smioo_manager
#         self.ui = Ui_IOPage()
#         self.ui.setupUi(self)
#         self.num_inputs = num_inputs
#         self.num_outputs = num_outputs
#         self.input_leds = []
#         self.input_read_btns = []
#         self.output_leds = []
#         self.output_toggles = []
#         self.timer = None

#         # self.ui.btnConnectSmioo.clicked.connect(self._connect_smioo)
#         self.set_enabled_controls(False)

#     def _connect_smioo(self):
#         ok = self.smioo_manager.initialize_smioo()
#         if ok:
#             self._build_page()
#             self.set_enabled_controls(True)
#             self.start_timer()
#         else:
#             self.set_enabled_controls(False)

#     def set_enabled_controls(self, enabled):
#         for btn in self.input_read_btns + self.output_toggles:
#             btn.setEnabled(enabled)

#     def _build_page(self):
#         grid = self.ui.gridLayoutMain
#         # Cancella oggetti esistenti
#         for row in reversed(range(1, grid.rowCount() + 1)):
#             for col in range(grid.columnCount()):
#                 item = grid.itemAtPosition(row, col)
#                 if item and item.widget():
#                     item.widget().setParent(None)

#         self.input_leds.clear()
#         self.input_read_btns.clear()
#         self.output_leds.clear()
#         self.output_toggles.clear()
#         # max_io = max(self.num_inputs, self.num_outputs)
#         for i in range(self.num_inputs + self.num_outputs):
#             if i < self.num_inputs:
#                 lbl_in = QLabel(f"IN-{i + 1}")
#                 lbl_in.setAlignment(Qt.AlignCenter)
#                 grid.addWidget(lbl_in, i + 1, 0)
#                 led_in = LedIndicatorWidget(self)
#                 led_in.setMinimumSize(32, 20)
#                 led_in.setMaximumSize(32, 20)
#                 grid.addWidget(led_in, i + 1, 1)
#                 self.input_leds.append(led_in)
#                 btn_read = QPushButton("Read", self)
#                 btn_read.setEnabled(False)
#                 btn_read.setMinimumWidth(60)
#                 btn_read.clicked.connect(lambda _, ch=i + 1: self.slot_read_input(ch))
#                 grid.addWidget(btn_read, i + 1, 2)
#                 self.input_read_btns.append(btn_read)
#             else:
#                 # if i < self.num_outputs:
#                 lbl_out = QLabel(f"OUT-{i + 1}")
#                 lbl_out.setAlignment(Qt.AlignCenter)
#                 grid.addWidget(lbl_out, i + 1, 4)
#                 led_out = LedIndicatorWidget(self)
#                 led_out.setMinimumSize(32, 20)
#                 led_out.setMaximumSize(32, 20)
#                 grid.addWidget(led_out, i + 1, 5)
#                 self.output_leds.append(led_out)
#                 btn_toggle = QPushButton("Toggle", self)
#                 btn_toggle.setEnabled(False)
#                 btn_toggle.setMinimumWidth(60)
#                 btn_toggle.setCheckable(True)
#                 btn_toggle.toggled.connect(
#                     lambda state, ch=i + 1: self.slot_toggle_output(ch, state)
#                 )
#                 grid.addWidget(btn_toggle, i + 1, 6)
#                 self.output_toggles.append(btn_toggle)
#         grid.addItem(
#             QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 7
#         )

#     def start_timer(self):
#         if self.timer:
#             self.timer.stop()
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self._update_io)
#         self.timer.start(200)  # 200ms polling

#     def _update_io(self):
#         # INPUT: aggiorna led ingressi
#         for i, led in enumerate(self.input_leds):
#             val = self.smioo_manager.read_input(i + 1)
#             led.set_on(bool(val))
#         # OUTPUT: aggiorna led uscite (se vuoi feedback hardware, modifica qui)
#         for i, led in enumerate(self.output_leds):
#             # Visualizza stato come toggle, oppure leggi dallo stato HW se vuoi
#             led.set_on(self.output_toggles[i].isChecked())

#     def slot_toggle_output(self, ch, state):
#         self.smioo_manager.write_output(ch, state)

#     def slot_read_input(self, ch):
#         val = self.smioo_manager.read_input(ch)
#         self.input_leds[ch - 1].set_on(bool(val))
#         print(f"[Read] Ingresso {ch}: {bool(val)}")
