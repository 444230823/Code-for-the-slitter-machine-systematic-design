from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QSpinBox,QDoubleSpinBox

class CustomQSB(QSpinBox):
    def wheelEvent(self,e):
        if e.type() == QEvent.Wheel:
            e.ignore()
class CustomQDSB(QDoubleSpinBox):
    def wheelEvent(self,e):
        if e.type() == QEvent.Wheel:
            e.ignore()