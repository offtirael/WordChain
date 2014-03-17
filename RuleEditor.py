from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class RuleEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(RuleEditorWindow, self).__init__(parent)

        self.label1 = QLabel("TODO: Rule editor")

        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.label1)

        self.cWidget = QWidget()
        self.cWidget.setLayout(self.layout1)
        self.setCentralWidget(self.cWidget)

        self.setWindowTitle("WordChain : Rule editor")