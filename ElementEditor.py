from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ElementEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ElementEditorWindow, self).__init__(parent)

        # Menu options
        self.fileMenu = QMenu("&File", self)
        self.openAction = self.fileMenu.addAction("&Open...")
        #openAction.setShortcut("Ctrl+O")
        self.saveAction = self.fileMenu.addAction("&Save As...")
        #saveAction.setShortcut("Ctrl+S")
        self.quitAction = self.fileMenu.addAction("Exit")
        #quitAction.setShortcut("Ctrl+Q")

        self.menuBar().addMenu(self.fileMenu)

        # Groupboxes
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(200, 600))
        self.gBox2 = QFrame()
        self.gBox2.setMaximumSize(QSize(200, 200))

        # Graphics view
        self.graphicsView = QGraphicsView()
        self.graphicsView.setMinimumSize(QSize(600, 600))

        # Right menu
        self.label1 = QLabel("Element name")
        self.nameEdit = QLineEdit()

        self.label2 = QLabel("Left connector")
        self.leftConnectorCombo = QComboBox()
        self.leftConnectorCombo.addItem("Type 1")
        self.leftConnectorCombo.addItem("Type 2")
        self.leftConnectorCombo.addItem("Type 3")
        self.leftConnectorCombo.addItem("Type 4")

        self.label3 = QLabel("Right connector")
        self.rightConnectorCombo = QComboBox()
        self.rightConnectorCombo.addItem("Type 1")
        self.rightConnectorCombo.addItem("Type 2")
        self.rightConnectorCombo.addItem("Type 3")
        self.rightConnectorCombo.addItem("Type 4")

        self.rightLayout = QVBoxLayout(self.gBox2)
        self.rightLayout.addWidget(self.label1)
        self.rightLayout.addWidget(self.nameEdit)
        self.rightLayout.addWidget(self.label2)
        self.rightLayout.addWidget(self.leftConnectorCombo)
        self.rightLayout.addWidget(self.label3)
        self.rightLayout.addWidget(self.rightConnectorCombo)

        # Layout
        self.centralWidget = QSplitter()
        self.centralWidget.addWidget(self.gBox1)
        self.centralWidget.addWidget(self.graphicsView)
        self.centralWidget.addWidget(self.gBox2)

        self.setCentralWidget(self.centralWidget)

        self.resize(1000, 600)

        self.setWindowTitle("WordChain : Element editor")