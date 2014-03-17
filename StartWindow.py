from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class StartWindow(QWidget):
    def __init__(self, parent=None):
        super(StartWindow, self).__init__(parent)

        self.button1 = QPushButton("Create grammar elements")
        self.button2 = QPushButton("Create grammar rules")
        self.button3 = QPushButton("Practice")

        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.button1)
        self.layout1.addWidget(self.button2)
        self.layout1.addWidget(self.button3)

        self.setLayout(self.layout1)

        self.setWindowTitle("WordChain")