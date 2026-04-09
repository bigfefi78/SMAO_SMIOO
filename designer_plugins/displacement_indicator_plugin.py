"""
Plugin DisplacementIndicator per Qt Designer
"""

try:
    import sys
    import os

    from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
    from PyQt5.QtGui import QIcon, QPixmap, QColor

    # Import widget finale
    from widgets import DisplacementIndicator
except ImportError as e:
    with open(r"F:/LAVORO/PRODAR/CLAUDIA/CARRELLI/carrelli elettrici/PYTHON/CARRELLI_SMAO_SMIOO/displacement_indicator_plugin_debug.txt", "a") as f:
        f.write(f"[PLUGIN ERROR] displacement_indicator_plugin.py: {e}\n")

# Aggiungi path progetto
plugin_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(plugin_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

try:

    class DisplacementIndicatorPlugin(QPyDesignerCustomWidgetPlugin):
        """Plugin per Designer"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.initialized = False

        def initialize(self, core):
            if self.initialized:
                return
            self.initialized = True

        def isInitialized(self):
            return self.initialized

        def createWidget(self, parent):
            return DisplacementIndicator(parent)

        def name(self):
            return "DisplacementIndicator"

        def group(self):
            return "Industrial Controls"

        def icon(self):
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(76, 175, 80))
            return QIcon(pixmap)

        def toolTip(self):
            return "Indicatore di spostamento professionale"

        def whatsThis(self):
            return "Indicatore per sensori di spostamento con barra colorata e limiti"

        def isContainer(self):
            return False

        def includeFile(self):
            return "displacement_indicator"

        def domXml(self):
            return """
    <ui language="c++">
        <widget class="DisplacementIndicator" name="displacementIndicator">
            <property name="geometry">
                <rect><x>0</x><y>0</y><width>600</width><height>45</height></rect>
            </property>
            <property name="label"><string>T-01</string></property>
            <property name="unit"><string>µm</string></property>
            <property name="value"><double>25.0</double></property>
            <property name="minRange"><double>-100.0</double></property>
            <property name="maxRange"><double>100.0</double></property>
            <property name="minLimit"><double>-80.0</double></property>
            <property name="maxLimit"><double>80.0</double></property>
            <property name="decimals"><number>2</number></property>
            <property name="barHeightRatio"><double>0.5</double></property>
            <property name="barMargin"><number>30</number></property>
            <property name="widgetHeight"><number>45</number></property>
        </widget>
    </ui>
    """

    # IMPORTANTE: Questa funzione è richiesta
    def customWidgets():
        return [DisplacementIndicatorPlugin()]
except Exception as e:
    with open(r"F:/LAVORO/PRODAR/CLAUDIA/CARRELLI/carrelli elettrici/PYTHON/CARRELLI_SMAO_SMIOO/displacement_indicator_plugin_debug.txt", "a") as f:
        f.write(f"[PLUGIN ERROR] DisplacementIndicatorPlugin class: {e}\n")
