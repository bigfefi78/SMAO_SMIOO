import os
import importlib.util

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import QTimer, Qt

from core import (
    SensorManager,
    MeasurementsManager,
    MeasurementsEngine,
    ProductsDB,
    GuiLogger,
    CollaudoAPI,
)
from widgets import (
    DisplacementIndicator,
    MeasurementsPage,
    MeasurementsMonitorPage,
    ProductsManagementPage,
    IOPage,
)
from managers import SMIOOManager


# AGGIUNTE per i nuovi tab:
from widgets.cycle_page.cycle_page import CyclePage
from widgets.plot_page.plot_page import PlotPage

from .main_window_ui import Ui_MainWindow  # Generato da uic su main_window.ui

PLUGIN_ROOT = "cycle_plugins"


def load_cycle_plugins(api):
    loaded = []
    for cyclename in os.listdir(PLUGIN_ROOT):
        plugin_dir = os.path.join(PLUGIN_ROOT, cyclename)
        main_py = None
        for file in os.listdir(plugin_dir):
            if file.endswith("plugin.py"):
                main_py = file
                break
        if not main_py:
            continue
        module_path = os.path.join(plugin_dir, main_py)
        spec = importlib.util.spec_from_file_location(cyclename, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Cerca una classe che eredita da QWidget (o meglio CyclePluginBase)
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if (
                isinstance(obj, type)
                and hasattr(obj, "__bases__")
                and QWidget in obj.__bases__
            ):
                widget = obj(api)
                loaded.append((getattr(widget, "LABEL", cyclename), widget))
                break
    return loaded


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # === UI ===
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # === Logger GUI ===
        self.logger = GuiLogger.instance(self.ui.logTextEdit)
        self.logger.info("MainWindow inizializzata")

        # === Managers ===
        self.sensor_manager = SensorManager()
        self.measurements_manager = MeasurementsManager()
        self.measurements_engine = MeasurementsEngine(
            self.sensor_manager, self.measurements_manager
        )
        self.measurements_engine.load_enabled_measurements()
        self.products_db = ProductsDB("products.db")
        self.smioo_mgr = SMIOOManager()
        self.smioo_mgr.initialize_smioo()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.setInterval(100)
        self.is_connected = False

        self.collaudo_api = CollaudoAPI(
            self.sensor_manager,
            self.smioo_mgr,
            self.measurements_engine,
            self.products_db,
            self.logger,
        )

        # === Setup pages ===
        self._setup_pages()

    def _setup_pages(self):
        self.ui.tabWidget.clear()
        self.monitor_page = self._create_monitor_page()
        self.ui.tabWidget.addTab(self.monitor_page, "📡 Monitoraggio Sensori")

        self.measurements_monitor_page = MeasurementsMonitorPage(
            self.measurements_engine, self
        )
        self.ui.tabWidget.addTab(
            self.measurements_monitor_page, "📊 Visualizzazione Misure"
        )

        self.io_page = IOPage(self.smioo_mgr)
        self.ui.tabWidget.addTab(self.io_page, "🔌 I/O DIGITALI")

        self.measurements_page = MeasurementsPage(self.sensor_manager, self)
        self.ui.tabWidget.addTab(self.measurements_page, "⚙️ Gestione Misure")

        self.products_page = ProductsManagementPage(self.products_db, self)
        self.ui.tabWidget.addTab(self.products_page, "🗄️ Database Prodotti")

        # === NUOVI TAB CICLI E GRAFICO ===
        self.cycle_page = CyclePage(self.collaudo_api)
        self.ui.tabWidget.addTab(self.cycle_page, "🧪 Cicli di Collaudo")

        self.plot_page = PlotPage()
        self.ui.tabWidget.addTab(self.plot_page, "📈 Grafico Collaudo")

        self.ui.tabWidget.currentChanged.connect(self._on_tab_changed)

        self.ui.btnConnect.clicked.connect(self._toggle_connection)
        self.ui.btnScan.clicked.connect(self._scan_channels)
        self.ui.btnAcquire.clicked.connect(self._start_acquisition)
        self.ui.labelChannelsInfo.setText("Canali: 0")
        self.ui.labelUpdateRate.setText("Update: 10 Hz")
        self.ui.btnClearLog.clicked.connect(self.logger.clear)
        self.ui.btnConnectSmioo.clicked.connect(self.io_page._connect_smioo)

    def _create_monitor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        page_header = QLabel("📡 MONITORAGGIO SENSORI")
        page_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(page_header)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.sensors_container = QWidget()
        self.sensors_layout = QVBoxLayout(self.sensors_container)
        self.sensors_layout.addStretch()
        scroll.setWidget(self.sensors_container)
        layout.addWidget(scroll)
        return page

    def _on_tab_changed(self, index: int):
        # Visualizzazione Misure tab
        if index == self.ui.tabWidget.indexOf(self.measurements_monitor_page):
            self.measurements_monitor_page.refresh_measurements()
            self.logger.info(
                "Visualizzazione Misure: refresh effettuato",
                sender=self.__class__.__name__,
            )
        # Gestione Misure tab
        if index == self.ui.tabWidget.indexOf(self.measurements_page):
            self.measurements_page.update_sensors_list()
            self.logger.info(
                "Gestione Misure: lista sensori aggiornata",
                sender=self.__class__.__name__,
            )
        # Grafico tab: rinfresca lista file
        if index == self.ui.tabWidget.indexOf(self.plot_page):
            if hasattr(self.plot_page, "update_file_list"):
                self.plot_page.update_file_list()
        # Cicli tab: rinfresca lista cicli disponibili
        if index == self.ui.tabWidget.indexOf(self.cycle_page):
            if hasattr(self.cycle_page, "load_cycles"):
                self.cycle_page.load_cycles()

    def _toggle_connection(self):
        if not self.is_connected:
            ok = self.sensor_manager.connect()
            if ok:
                self.is_connected = True
                self.ui.btnConnect.setText("Disconnetti SMAO")
            else:
                self.logger.error("Errore connessione SMAO", self.__class__.__name__)
        else:
            self.sensor_manager.disconnect()
            self.is_connected = False
            self.ui.btnConnect.setText("Connetti SMAO")
            self.update_timer.stop()
            self.ui.btnConnect.setStyleSheet("""""")
            self.logger.info("SMAO disconnesso", self.__class__.__name__)

    def _scan_channels(self):
        if not self.is_connected:
            self.logger.warning(
                "Provata scansione senza connessione SMAO", self.__class__.__name__
            )
            return
        self.sensor_manager.scan_channels()
        channels = self.sensor_manager.get_active_channels()
        self._create_channel_widgets(channels)
        self.ui.labelChannelsInfo.setText(f"Canali: {len(channels)}")
        if channels:
            self.logger.info(
                f"Scansione completata: {len(channels)} canali attivi",
                sender=self.__class__.__name__,
            )
        else:
            self.logger.warning(
                "Scansione: nessun canale trovato", self.__class__.__name__
            )

    def _create_channel_widgets(self, channels):
        for i in reversed(range(self.sensors_layout.count())):
            item = self.sensors_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        for channel in channels:
            widget = DisplacementIndicator(self)
            widget.set_channel_info(channel)
            widget.calibrationAcquisitionRequested.connect(self._handle_rb_calibration)
            self.sensors_layout.insertWidget(self.sensors_layout.count() - 1, widget)

    def _start_acquisition(self):
        if not self.is_connected:
            self.logger.warning(
                "Provata acquisizione senza connessione SMAO", self.__class__.__name__
            )
            return
        if not self.update_timer.isActive():
            self.update_timer.start()
            self.ui.btnAcquire.setText("Ferma Acquisizione")
            self.logger.info(
                msg="Acquisizione sensori avviata", sender=self.__class__.__name__
            )
        else:
            self.update_timer.stop()
            self.ui.btnAcquire.setText("Start Acquisizione")
            self.logger.info(
                "Acquisizione sensori fermata", sender=self.__class__.__name__
            )

    def _update_data(self):
        self.sensor_manager.update_all_channels()
        if self.ui.tabWidget.currentIndex() == self.ui.tabWidget.indexOf(
            self.monitor_page
        ):
            for i in range(self.sensors_layout.count() - 1):
                item = self.sensors_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, "channel_info"):
                        channel = widget.channel_info
                        if channel:
                            widget.setValue(channel.current_value)
        elif self.ui.tabWidget.currentIndex() == self.ui.tabWidget.indexOf(
            self.measurements_monitor_page
        ):
            self.measurements_monitor_page.update_measurements_values()

    def _handle_rb_calibration(self, calibration_dialog):
        channel = getattr(calibration_dialog, "channel_info", None)
        if channel is not None:
            # Forza una nuova acquisizione hardware
            self.sensor_manager.update_all_channels()
            # Ora puoi leggere il valore appena acquisito:
            value = channel.current_value
        else:
            self.logger.error(
                f"Errore durante l'acquisizione del singolo canale {channel.channel_number}.",
                {self.__class__.__name__},
            )
            value = 0.0

        calibration_dialog.set_acquired_value(value)

    def closeEvent(self, event):
        if self.is_connected:
            self.sensor_manager.disconnect()
            self.update_timer.stop()
            self.logger.info(
                "Connessione e timer chiusi", sender=self.__class__.__name__
            )
        event.accept()
