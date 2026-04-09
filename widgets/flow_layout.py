"""
FlowLayout - Layout che va a capo automaticamente
(Adattato dagli esempi ufficiali Qt)
"""

from PyQt5.QtWidgets import QLayout, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """Layout che posiziona widget in righe, andando a capo quando necessario"""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
    
    def _do_layout(self, rect, test_only):
        """Posiziona gli item con wrap automatico"""
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing + widget.style().layoutSpacing(
                QSizePolicy.PushButton,
                QSizePolicy.PushButton,
                Qt.Horizontal
            )
            space_y = spacing + widget.style().layoutSpacing(
                QSizePolicy.PushButton,
                QSizePolicy.PushButton,
                Qt.Vertical
            )
            
            next_x = x + item.sizeHint().width() + space_x
            
            # Se va oltre il bordo, vai a capo
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()