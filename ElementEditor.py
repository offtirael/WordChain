from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Element import *
from Connectors import *


class ElementEditorWindow(QMainWindow):
    def __init__(self, editor, parent=None):
        super(ElementEditorWindow, self).__init__(parent)

        self.editor = editor

        # Menu options
        self.fileMenu = QMenu("&File", self)
        self.openAction = self.fileMenu.addAction("&Open...")
        #openAction.setShortcut("Ctrl+O")
        self.saveAction = self.fileMenu.addAction("&Save As...")
        #saveAction.setShortcut("Ctrl+S")
        self.quitAction = self.fileMenu.addAction("Exit")
        #quitAction.setShortcut("Ctrl+Q")

        self.menuBar().addMenu(self.fileMenu)

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(200, 600))
        self.gBox2 = QFrame()
        self.gBox2.setMaximumSize(QSize(200, 200))

        self.scene = QGraphicsScene(-200, -200, 400, 400)

        # Graphics view
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setMinimumSize(QSize(600, 600))

        # Right menu
        self.label1 = QLabel("Element name")
        self.nameEdit = QLineEdit()

        self.label2 = QLabel("Left connector")
        self.leftConnectorCombo = QComboBox()
        self.leftConnectorCombo.addItem("Type 1")
        self.leftConnectorCombo.addItem("Type 2")
        self.leftConnectorCombo.addItem("Type 3")
        self.leftConnectorCombo.currentIndexChanged.connect(self.editor.changeLeftConnector)

        self.label3 = QLabel("Right connector")
        self.rightConnectorCombo = QComboBox()
        self.rightConnectorCombo.addItem("Type 1")
        self.rightConnectorCombo.addItem("Type 2")
        self.rightConnectorCombo.addItem("Type 3")
        self.rightConnectorCombo.currentIndexChanged.connect(self.editor.changeRightConnector)

        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(self.editor.applyChanges)

        self.rightLayout = QVBoxLayout(self.gBox2)
        self.rightLayout.addWidget(self.label1)
        self.rightLayout.addWidget(self.nameEdit)
        self.rightLayout.addWidget(self.label2)
        self.rightLayout.addWidget(self.leftConnectorCombo)
        self.rightLayout.addWidget(self.label3)
        self.rightLayout.addWidget(self.rightConnectorCombo)
        self.rightLayout.addWidget(self.applyButton)

        # Left menu
        self.itemListWidget = QListWidget()
        self.itemListWidget.currentItemChanged.connect(self.editor.chooseElement)

        self.leftLayout = QVBoxLayout(self.gBox1)

        self.leftInnerLayout = QHBoxLayout()
        self.leftLayout.addLayout(self.leftInnerLayout)

        self.newElementName = QLineEdit()
        self.addNewElement = QPushButton("Add")
        self.leftInnerLayout.addWidget(self.newElementName)
        self.leftInnerLayout.addWidget(self.addNewElement)

        self.addNewElement.clicked.connect(self.editor.addElement)

        self.leftLayout.addWidget(self.itemListWidget)

        self.deleteButton = QPushButton("Delete element")
        self.leftLayout.addWidget(self.deleteButton)
        self.deleteButton.clicked.connect(self.editor.deleteElement)

        # Layout
        self.centralWidget = QSplitter()
        self.centralWidget.addWidget(self.gBox1)
        self.centralWidget.addWidget(self.graphicsView)
        self.centralWidget.addWidget(self.gBox2)

        self.setCentralWidget(self.centralWidget)

        self.resize(1000, 600)

        self.setWindowTitle("WordChain : Element editor")


class ElementEditor(object):
    def __init__(self):
        self.elementList = []
        self.window = ElementEditorWindow(editor=self)
        self.currentElement = None

    def showWindow(self):
        self.window.show()

    def addElement(self):
        name = self.window.newElementName.text()
        self.window.newElementName.clear()

        element = MetaElement(2, 2, elementName=name)

        self.elementList.append(element)

        self.updateElementListView()

    def deleteElement(self):
        index = self.window.itemListWidget.currentRow()
        if index != -1:
            self.elementList.pop(index)
            self.updateElementListView()

    def updateElementListView(self):
        self.window.itemListWidget.clear()

        for item in self.elementList:
            self.window.itemListWidget.addItem(item.elementName)

    def chooseElement(self):
        self.window.scene.removeItem(self.currentElement)
        index = self.window.itemListWidget.currentRow()
        if index != -1:
            self.currentElement = self.elementList[index]
            self.window.nameEdit.setText(self.currentElement.elementName)
            self.window.scene.addItem(self.currentElement)

            print(self.currentElement.leftConnectorType - 1)
            print(self.currentElement.rightConnectorType - 1)

            self.window.leftConnectorCombo.setCurrentIndex(self.currentElement.leftConnectorType - 1)
            self.window.rightConnectorCombo.setCurrentIndex(self.currentElement.rightConnectorType - 1)

    def applyChanges(self):
        newName = self.window.nameEdit.text()
        self.currentElement.elementName = newName
        self.updateElementListView()
        self.updateScene()

    def updateScene(self):
        if self.currentElement is not None:
            self.window.scene.removeItem(self.currentElement)
            self.window.scene.addItem(self.currentElement)

    def changeLeftConnector(self):
        index = self.window.leftConnectorCombo.currentIndex()
        index += 1
        self.window.scene.removeItem(self.currentElement)

        self.currentElement.changeLeftConnector(index)

        self.window.scene.addItem(self.currentElement)

    def changeRightConnector(self):
        index = self.window.rightConnectorCombo.currentIndex()
        index += 1
        self.window.scene.removeItem(self.currentElement)

        self.currentElement.changeRightConnector(index)

        self.window.scene.addItem(self.currentElement)