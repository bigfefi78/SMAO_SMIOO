from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from PyQt5.QtWidgets import QPushButton

class MinimalButtonPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initialized = False

    def initialize(self, core):
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return QPushButton("Test", parent)

    def name(self): return "MinimalButton"
    def group(self): return "Test"
    def toolTip(self): return "MinimalButton"
    def isContainer(self): return False
    def includeFile(self): return "PyQt5.QtWidgets"
    def domXml(self):
        return """
    <ui language="c++">
        <widget class="QPushButton" name="minimalButton"/>
    </ui>
    """

def customWidgets():
    return [MinimalButtonPlugin()]