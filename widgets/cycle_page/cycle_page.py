# V8
import os
import importlib.util
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QCheckBox
from .cycle_page_ui import Ui_CyclePage
from PyQt5.QtChart import QChart, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter, QColor
from core.cycle_plugin_base import CyclePluginBase
from PyQt5.QtCore import pyqtSlot, QPointF, Qt


PLUGIN_ROOT = "cycle_plugins"
MAX_ROWS_PER_COL = 2


class CyclePage(QWidget):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.ui = Ui_CyclePage()
        self.ui.setupUi(self)

        self.plugins = []
        self.plugin_labels = []
        self.load_plugins(api)

        self.ui.listCycles.clear()
        self.ui.pluginContainer.setCurrentIndex(-1)
        for label in self.plugin_labels:
            self.ui.listCycles.addItem(label)

        self.ui.listCycles.currentRowChanged.connect(self.show_plugin_widget)
        self.ui.listCycles.clicked.connect(self.reset_visualization)
        self.setup_chart()
        self.setup_data_table()

        self.data_steps = []  # Accumulo tutti i dati-step in arrivo
        self.measure_series = {}  # nome_misura -> QLineSeries
        self.measure_colors = [
            "blue",
            "red",
            "green",
            "orange",
            "magenta",
            "brown",
            "purple",
            "teal",
            "olive",
        ]
        self.checkbox_widgets = {}
        self.active_measures = set()
        self.measure_visibility = {}  # variabile per tenere traccia della visibilità di ogni misura

    def load_plugins(self, api):
        self.plugins = []
        self.plugin_labels = []
        while self.ui.pluginContainer.count():
            widget = self.ui.pluginContainer.widget(0)
            self.ui.pluginContainer.removeWidget(widget)
            widget.setParent(None)
        for cyclename in os.listdir(PLUGIN_ROOT):
            plugin_dir = os.path.join(PLUGIN_ROOT, cyclename)
            if not os.path.isdir(plugin_dir):
                continue
            main_py = None
            for file in os.listdir(plugin_dir):
                if file.endswith("plugin.py") and not file.endswith("_ui.py"):
                    main_py = file
                    break
            if not main_py:
                continue
            module_path = os.path.join(plugin_dir, main_py)
            spec = importlib.util.spec_from_file_location(cyclename, module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, CyclePluginBase)
                    and obj is not CyclePluginBase
                ):
                    widget = obj(api)
                    # Connect data and reset signals
                    if hasattr(widget, "step_data_ready"):
                        widget.step_data_ready.connect(self.receive_step_data)
                    if hasattr(widget, "reset_visualization"):
                        widget.reset_visualization.connect(self.reset_visualization)
                    self.plugins.append(widget)
                    self.plugin_labels.append(getattr(widget, "LABEL", cyclename))
                    self.ui.pluginContainer.addWidget(widget)
                    break

    def show_plugin_widget(self, idx):
        if idx < 0 or idx >= self.ui.pluginContainer.count():
            self.ui.pluginContainer.setCurrentIndex(-1)
            return
        self.ui.pluginContainer.setCurrentIndex(idx)
        # forzo refresh
        # self.force_refresh_cycle_page()

    # def force_refresh_cycle_page(self):
    #     # Ad esempio aggiorna le strutture dati in base alle misure disponibili:
    #     measure_names = self.get_current_plugin_measure_names()  # Da implementare!
    #     self.update_checkbox_panel(measure_names)
    #     self.update_visualization()

    def setup_chart(self):
        self.chart = QChart()
        self.ui.cycleChartView.setChart(self.chart)
        self.ui.cycleChartView.setRenderHint(QPainter.Antialiasing)

    def setup_data_table(self):
        t = self.ui.cycleDataTable
        t.setColumnCount(2)
        t.setHorizontalHeaderLabels(["Step", "Timestamp"])
        t.setRowCount(0)

    def update_checkbox_panel(self, measure_names):
        layout = self.ui.layoutCheckbox
        # Elimina i vecchi checkbox
        while layout.count():
            w = layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.checkbox_widgets = {}
        for idx, name in enumerate(measure_names):
            color = self.measure_colors[idx % len(self.measure_colors)]
            cbx = QCheckBox(name)
            # Recupera stato da variabile, o imposta True solo la prima volta
            checked = self.measure_visibility.get(name, True)
            cbx.setChecked(checked)
            cbx.setStyleSheet(f"color: {color}; font-weight: bold;")
            cbx.stateChanged.connect(
                lambda state, n=name: self.checkbox_state_changed(n, state)
            )
            row = idx % MAX_ROWS_PER_COL
            col = idx // MAX_ROWS_PER_COL
            layout.addWidget(cbx, row, col)
            self.checkbox_widgets[name] = cbx
            # layout.addWidget(cbx)
            # self.checkbox_widgets[name] = cbx
        # Aggiorna measure_visibility per tutte le misure (senza perdere i già impostati)
        for name in measure_names:
            if name not in self.measure_visibility:
                self.measure_visibility[name] = True
            self.active_measures.add(name)

    def checkbox_state_changed(self, measure_name, state):
        # Aggiorna la variabile di stato
        self.measure_visibility[measure_name] = state == 2  # Qt.Checked = 2
        cbx = self.checkbox_widgets.get(measure_name)
        series = self.measure_series.get(measure_name)
        if not series or not cbx:
            return
        if cbx.isChecked():
            if series not in self.chart.series():
                self.chart.addSeries(series)
        else:
            if series in self.chart.series():
                self.chart.removeSeries(series)
        self.chart.createDefaultAxes()

    def handle_checkbox(self, measure_name):
        cbx = self.checkbox_widgets.get(measure_name)
        series = self.measure_series.get(measure_name)
        if not series or not cbx:
            return
        if cbx.isChecked():
            if series not in self.chart.series():
                self.chart.addSeries(series)
        else:
            if series in self.chart.series():
                self.chart.removeSeries(series)
        self.chart.createDefaultAxes()

    def receive_step_data(self, step_data):
        # step_data: dict { "step": int, "timestamp": str, "measurements": { "nome": tuple } }
        self.data_steps.append(step_data)
        self.update_visualization()

    @pyqtSlot()
    def reset_visualization(self):
        self.data_steps.clear()
        for series in self.measure_series.values():
            series.clear()
            if series in self.chart.series():
                self.chart.removeSeries(series)
        self.measure_series.clear()
        self.checkbox_widgets.clear()
        t = self.ui.cycleDataTable
        t.clearContents()
        t.setRowCount(0)

    # def update_visualization(self):
    #     if not self.data_steps:
    #         return

    #     measure_names = sorted(
    #         set(
    #             key
    #             for sd in self.data_steps
    #             for key in sd.get("measurements", {}).keys()
    #         )
    #     )
    #     if not measure_names:
    #         return

    #     self.update_checkbox_panel(measure_names)

    #     # --- Serie visibili secondo self.measure_visibility ---
    #     visible_names = [
    #         name for name in measure_names if self.measure_visibility.get(name, True)
    #     ]

    #     max_x = len(self.data_steps) - 1
    #     min_y = float("inf")
    #     max_y = float("-inf")

    #     # Serie per ogni misura (aggiorna sempre tutti, ma regolati sulla visibilità)
    #     for idx, name in enumerate(measure_names):
    #         if name not in self.measure_series:
    #             series = QLineSeries()
    #             color = QColor(self.measure_colors[idx % len(self.measure_colors)])
    #             pen = series.pen()
    #             pen.setColor(color)
    #             series.setPen(pen)
    #             series.setName(name)
    #             self.measure_series[name] = series
    #             cbx = self.checkbox_widgets.get(name)
    #             if cbx and self.measure_visibility.get(name, True):
    #                 self.chart.addSeries(series)
    #                 self.chart.createDefaultAxes()
    #         else:
    #             series = self.measure_series[name]
    #         points = []
    #         for i, step in enumerate(self.data_steps):
    #             val = step.get("measurements", {}).get(name, None)
    #             if val is not None and isinstance(val, (tuple, list)) and len(val) > 1:
    #                 if isinstance(val[1], (int, float)):
    #                     y = float(val[1])
    #                 else:
    #                     y = float(99999)
    #                 points.append(QPointF(i, y))
    #                 # -- Calcolo min_y/max_y SOLO se la serie è visibile --
    #                 if name in visible_names:
    #                     if y < min_y:
    #                         min_y = y
    #                     if y > max_y:
    #                         max_y = y
    #         series.replace(points)
    #         cbx = self.checkbox_widgets.get(name)
    #         if cbx:
    #             if self.measure_visibility.get(name, True):
    #                 if series not in self.chart.series():
    #                     self.chart.addSeries(series)
    #                     self.chart.createDefaultAxes()
    #             else:
    #                 if series in self.chart.series():
    #                     self.chart.removeSeries(series)

    #     # --- Aggiornamento assi SOLO sul range delle serie visibili ---
    #     if self.chart.series() and min_y != float("inf"):
    #         axis_x = self.chart.axisX()
    #         if axis_x:
    #             axis_x.setRange(0, max_x if max_x > 0 else 1)
    #         axis_y = self.chart.axisY()
    #         if axis_y:
    #             padding = (max_y - min_y) * 0.1 or 1
    #             axis_y.setRange(min_y - padding, max_y + padding)

    #     self.chart.update()
    #     self.ui.cycleChartView.repaint()

    #     # Tabella: step, timestamp, tutte le misure
    #     t = self.ui.cycleDataTable
    #     t.setRowCount(len(self.data_steps))
    #     t.setColumnCount(2 + len(measure_names))
    #     t.setHorizontalHeaderLabels(["Step", "Timestamp"] + measure_names)
    #     for i, step in enumerate(self.data_steps):
    #         t.setItem(i, 0, QTableWidgetItem(str(step.get("step", ""))))
    #         t.setItem(i, 1, QTableWidgetItem(str(step.get("timestamp", ""))))
    #         for c, name in enumerate(measure_names):
    #             val = step.get("measurements", {}).get(name, "")
    #             if val is not None and isinstance(val, (tuple, list)) and len(val) > 1:
    #                 if isinstance(val[1], (int, float)):
    #                     display_val = f"{round(float(val[1]), 2):.2f}"  # 2 decimali
    #             else:
    #                 display_val = "NaN"
    #             t.setItem(
    #                 i,
    #                 2 + c,
    #                 QTableWidgetItem(display_val),
    #             )

    def update_visualization(self):
        if not self.data_steps:
            return

        measure_names = sorted(
            set(
                key
                for sd in self.data_steps
                for key in sd.get("measurements", {}).keys()
            )
        )
        if not measure_names:
            return

        self.update_checkbox_panel(measure_names)

        # --- PATCH: rimuovi TUTTE le serie e assi Y dal chart ---
        self.chart.removeAllSeries()
        # Rimuovi anche tutti gli assi Y
        for axis in self.chart.axes():
            if axis.orientation() == Qt.Vertical:
                self.chart.removeAxis(axis)

        axes_y = {}

        max_x = len(self.data_steps) - 1

        for idx, name in enumerate(measure_names):
            # (puoi ricreare ogni volta la series, oppure gestirne il dict, a piacere)
            series = QLineSeries()
            color = QColor(self.measure_colors[idx % len(self.measure_colors)])
            pen = series.pen()
            pen.setColor(color)
            series.setPen(pen)
            series.setName(name)
            self.measure_series[name] = series

            points = []
            min_y, max_y = float("inf"), float("-inf")
            for i, step in enumerate(self.data_steps):
                val = step.get("measurements", {}).get(name, None)
                if val is not None and isinstance(val, (tuple, list)) and len(val) > 1:
                    if isinstance(val[1], (int, float)):
                        y = float(val[1])
                    else:
                        y = float(99999)
                    points.append(QPointF(i, y))
                    if y < min_y:
                        min_y = y
                    if y > max_y:
                        max_y = y
            series.replace(points)

            # --- Asse Y DEDICATO per questa misura ---
            axis_y = QValueAxis()
            axis_y.setTitleText(name)
            axis_y.setLabelsColor(color)
            pad = (max_y - min_y) * 0.1 or 1
            axis_y.setRange(min_y - pad, max_y + pad)
            # Alterna sinistra/destra per leggibilità
            align = Qt.AlignLeft if idx % 2 == 0 else Qt.AlignRight
            self.chart.addAxis(axis_y, align)
            series.attachAxis(axis_y)
            axes_y[name] = axis_y

            # --- Asse X unico (in fondo) ---
            axis_x = self.chart.axisX()
            if not axis_x:
                axis_x = QValueAxis()
                axis_x.setTitleText("Step")
                self.chart.addAxis(axis_x, Qt.AlignBottom)
            axis_x.setRange(0, max_x if max_x > 0 else 1)
            series.attachAxis(axis_x)

            # --- Mostra solo se è tra i selezionati ---
            cbx = self.checkbox_widgets.get(name)
            if cbx and self.measure_visibility.get(name, True):
                self.chart.addSeries(series)
                series.show()
            # else: series.hide()   # opzionale

        self.chart.update()
        self.ui.cycleChartView.repaint()

        # Tabella: step, timestamp, tutte le misure (come già facevi)
        t = self.ui.cycleDataTable
        t.setRowCount(len(self.data_steps))
        t.setColumnCount(2 + len(measure_names))
        t.setHorizontalHeaderLabels(["Step", "Timestamp"] + measure_names)
        for i, step in enumerate(self.data_steps):
            t.setItem(i, 0, QTableWidgetItem(str(step.get("step", ""))))
            t.setItem(i, 1, QTableWidgetItem(str(step.get("timestamp", ""))))
            for c, name in enumerate(measure_names):
                val = step.get("measurements", {}).get(name, "")
                if val is not None and isinstance(val, (tuple, list)) and len(val) > 1:
                    if isinstance(val[1], (int, float)):
                        display_val = f"{round(float(val[1]), 2):.2f}"  # 2 decimali
                else:
                    display_val = "NaN"
                t.setItem(i, 2 + c, QTableWidgetItem(display_val))
