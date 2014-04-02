from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from ElementEditor import ElementEditor
from RuleEditor import RuleEditor
from Practice import PracticeWindow


class StartWindow(QMainWindow):
    def __init__(self, parent=None):
        super(StartWindow, self).__init__(parent)

        self.button1 = QPushButton("Create grammar elements")
        self.button2 = QPushButton("Create grammar rules")
        self.button3 = QPushButton("Practice")

        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.button1)
        self.layout1.addWidget(self.button2)
        self.layout1.addWidget(self.button3)

        self.cWidget = QWidget()
        self.cWidget.setLayout(self.layout1)

        self.button1.clicked.connect(self.startElementEditor)
        self.button2.clicked.connect(self.startRuleEditor)
        self.button3.clicked.connect(self.startPractice)

        self.setCentralWidget(self.cWidget)
        #self.setLayout(self.layout1)

        self.setWindowTitle("WordChain")

        self.elementEditor = ElementEditor()
        #self.elementEditorWindow = ElementEditorWindow()
        self.ruleEditor = RuleEditor()
        self.practiceWindow = PracticeWindow()

    def startElementEditor(self):
        self.elementEditor.showWindow()

    def startRuleEditor(self):
        self.ruleEditor.showWindow()

    def startPractice(self):
        self.practiceWindow.show()
        self.practiceWindow.move(self.x() + 40, self.y() + 40)