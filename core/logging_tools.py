from datetime import datetime

LOG_COLORS = {
    "DEBUG": "#0176D3",
    "INFO": "#138F13",
    "WARNING": "#FFA500",
    "ERROR": "#E74C3C",
}


class GuiLogger:
    _instance = None

    def __init__(self, log_widget=None):
        self.log_widget = log_widget

    @classmethod
    def instance(cls, log_widget=None):
        if cls._instance is None:
            cls._instance = GuiLogger(log_widget)
        elif log_widget is not None:
            cls._instance.log_widget = log_widget
        return cls._instance

    def _write(self, msg, sender, level):
        color = LOG_COLORS.get(level.upper(), "#000")
        now = datetime.now().strftime("%d-%m-%Y\t%H:%M:%S")
        if self.log_widget is not None:
            self.log_widget.append(
                f'<span style="color:{color};">[{now} --- {sender} ] {msg}</span>'
            )
            scrollbar = self.log_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            print(f"[{level}] {msg}")

    def debug(self, msg, sender=""):
        self._write(msg, sender, "DEBUG")

    def info(self, msg, sender=""):
        self._write(msg, sender, "INFO")

    def warning(self, msg, sender=""):
        self._write(msg, sender, "WARNING")

    def error(self, msg, sender=""):
        self._write(msg, sender, "ERROR")
    
    def clear(self):
        if self.log_widget is not None:
            self.log_widget.clear()
