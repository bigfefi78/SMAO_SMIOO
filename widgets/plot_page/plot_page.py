from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

import os
import csv

DATA_DIR = "data/collaudi"


class PlotPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from .plot_page_ui import Ui_PlotPage

        self.ui = Ui_PlotPage()
        self.ui.setupUi(self)
        self.update_file_list()
        self.ui.btnPlot.clicked.connect(self.on_plot)

    def update_file_list(self):
        self.ui.listFiles.clear()
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".csv"):
                self.ui.listFiles.addItem(fname)

    def on_plot(self):
        item = self.ui.listFiles.currentItem()
        if item is None:
            return
        fname = item.text()
        data = []
        with open(os.path.join(DATA_DIR, fname)) as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        chart = QChart()
        chart.setTitle("Trend Misura e Trasduttori")
        # Supponiamo misure M1, trasduttori T1 e T27
        x = list(range(len(data)))
        m1 = [float(row.get("M1", 0)) for row in data]
        t1 = [float(row.get("T1", 0)) for row in data]
        t27 = [float(row.get("T27", 0)) for row in data]
        lineM1 = QLineSeries()
        lineT1 = QLineSeries()
        lineT27 = QLineSeries()
        for i in range(len(x)):
            lineM1.append(x[i], m1[i])
            lineT1.append(x[i], t1[i])
            lineT27.append(x[i], t27[i])
        lineM1.setName("Misura M1")
        lineT1.setName("Trasduttore T1")
        lineT27.setName("Trasduttore T27")
        chart.addSeries(lineM1)
        chart.addSeries(lineT1)
        chart.addSeries(lineT27)
        axX = QValueAxis()
        axY = QValueAxis()
        chart.setAxisX(axX, lineM1)
        chart.setAxisY(axY, lineM1)
        chart.setAxisX(axX, lineT1)
        chart.setAxisY(axY, lineT1)
        chart.setAxisX(axX, lineT27)
        chart.setAxisY(axY, lineT27)
        chartView = QChartView(chart)
        chartView.setMinimumSize(600, 300)
        # Sostituisci chartFrame con chartView
        frame = self.ui.chartFrame
        layout = frame.layout() or QVBoxLayout(frame)
        layout.addWidget(chartView)
        frame.setLayout(layout)
