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

        # Left menu
        self.itemListWidget = QListWidget()
        self.itemListWidget.addItem("Item 1")
        self.itemListWidget.addItem("Item 2")

        self.leftLayout = QVBoxLayout(self.gBox1)

        self.leftInnerLayout = QHBoxLayout()
        self.leftLayout.addLayout(self.leftInnerLayout)

        self.newElementName = QLineEdit()
        self.addNewElement = QPushButton("Add")
        self.leftInnerLayout.addWidget(self.newElementName)
        self.leftInnerLayout.addWidget(self.addNewElement)

        self.addNewElement.clicked.connect(self.addItem)

        self.leftLayout.addWidget(self.itemListWidget)

        # Layout
        self.centralWidget = QSplitter()
        self.centralWidget.addWidget(self.gBox1)
        self.centralWidget.addWidget(self.graphicsView)
        self.centralWidget.addWidget(self.gBox2)

        self.setCentralWidget(self.centralWidget)

        self.resize(1000, 600)

        self.setWindowTitle("WordChain : Element editor")

        self.lst = []
        self.loadElementList(self.lst)

    def loadElementList(self, lst):
        self.itemListWidget.clear()

        for item in lst:
            self.itemListWidget.addItem(item)

    def addItem(self):
        name = self.newElementName.text()
        self.newElementName.clear()
        self.lst.append(name)
        self.loadElementList(self.lst)




class ElementEditor(object):
    def __init__(self):
        self.window = ElementEditorWindow()

    def showWindow(self):
        self.window.show()