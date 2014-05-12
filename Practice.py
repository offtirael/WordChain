import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Rule import RuleSet


class Practice(QMainWindow):
    def __init__(self, parent=None):
        super(Practice, self).__init__(parent)

        self.ruleSet = RuleSet()
        self.ruleFileName = None
        self.elementSet = None

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(250, 600))
        self.gBox1.setMinimumSize(QSize(250, 250))

        self.scene = QGraphicsScene(-200, -200, 400, 400)

        # Graphics view
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setMinimumSize(QSize(800, 600))

        self.leftLayout = QVBoxLayout(self.gBox1)

        self.label1 = QLabel("Rule file:")
        self.fileName = QLabel("--")
        self.chooseFile = QPushButton("Choose file")
        self.loadFile = QPushButton("Load")

        self.chooseFile.clicked.connect(self.chooseRuleFile)
        self.loadFile.clicked.connect(self.loadRuleFile)

        self.createToolBox()

        self.leftLayout.addWidget(self.label1)
        self.leftLayout.addWidget(self.fileName)
        self.leftHInnerLayout = QHBoxLayout()
        self.leftHInnerLayout.addWidget(self.chooseFile)
        self.leftHInnerLayout.addWidget(self.loadFile)
        self.leftLayout.addLayout(self.leftHInnerLayout)
        self.leftLayout.addWidget(self.toolBox)

        self.centralWidget = QWidget()
        self.centralLayout = QHBoxLayout()
        self.centralLayout.addWidget(self.gBox1)
        self.centralLayout.addWidget(self.graphicsView)
        self.centralWidget.setLayout(self.centralLayout)

        self.setWindowTitle("WordChain : Practice")

        self.setCentralWidget(self.centralWidget)

        self.resize(1200, 600)

    def showWindow(self):
        self.show()

    def createToolBox(self):
        self.toolBox = QToolBox()
        self.toolBox.setMinimumSize(QSize(250, 300))
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        self.toolBoxLayout = QGridLayout()
        self.toolBoxLayout.setRowStretch(4, 10)
        self.toolBoxLayout.setColumnStretch(2, 10)

        self.toolBoxWidget = QWidget()
        self.toolBoxWidget.setLayout(self.toolBoxLayout)
        self.toolBox.addItem(self.toolBoxWidget, "--")

    def buttonGroupClicked(self, i):
        pass

    def chooseRuleFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.rl')
        self.ruleFileName = ret[0]
        self.fileName.setText(os.path.basename(self.ruleFileName))

    def loadRuleFile(self):
        file = open(self.ruleFileName, 'r')

        st = '\n'.join(file.readlines())
        self.ruleSet.fromString(st)