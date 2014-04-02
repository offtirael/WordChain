from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json

from Element import *
from Connectors import *

import resources

class ElementEditorWindow(QMainWindow):
    def __init__(self, editor, parent=None):
        super(ElementEditorWindow, self).__init__(parent)

        self.editor = editor

        # Menu options
        #self.fileMenu = QMenu("&File", self)
        #self.openAction = self.fileMenu.addAction("&Open...")
        #self.openAction.setShortcut("Ctrl+O")
        #self.saveAsAction = self.fileMenu.addAction("Save As...")
        #self.saveAction = self.fileMenu.addAction("&Save")
        #self.saveAction.setShortcut("Ctrl+S")

        #self.saveAsAction.triggered.connect(self.editor.saveAs)
        #self.saveAction.triggered.connect(self.editor.saveToFile)
        #self.openAction.triggered.connect(self.editor.loadFromFile)

        #self.menuBar().addMenu(self.fileMenu)

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
        self.rightLayout.setAlignment(Qt.AlignTop)
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
        self.centralWidget = QWidget()

        self.centralLayout = QHBoxLayout()
        self.centralLayout.addWidget(self.gBox1)
        self.centralLayout.addWidget(self.graphicsView)
        self.centralLayout.addWidget(self.gBox2)
        self.centralWidget.setLayout(self.centralLayout)

        self.setCentralWidget(self.centralWidget)

        self.resize(1000, 600)

        self.setWindowTitle("WordChain : Element editor")

        # ToolBars
        self.fileToolBar = self.addToolBar("File")

        self.saveAction = QAction(QIcon(':/images/save.png'), "Save to &File", self,
                                  shortcut="Ctrl+S", triggered=self.editor.saveToFile)
        self.openAction = QAction(QIcon(':/images/open.png'), "Open &File", self,
                                  shortcut="Ctrl+O", triggered=self.editor.loadFromFile)

        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.openAction)

    def closeEvent(self, event):
        if not self.editor.saved:
            msgBox = QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setDetailedText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            ret = msgBox.exec()
            if ret == QMessageBox.Save:
                self.editor.saveToFile()
            elif ret == QMessageBox.Cancel:
                event.ignore()
            elif ret == QMessageBox.Discard:
                pass
            event.accept()
        else:
            event.accept()


class ElementEditor(object):
    def __init__(self):
        self.elementSet = ElementSet()
        self.window = ElementEditorWindow(editor=self)
        self.currentElement = None
        self.saved = True
        self.fileName = None

    def showWindow(self):
        self.window.show()

    def addElement(self):
        name = self.window.newElementName.text()
        self.window.newElementName.clear()

        element = MetaElement(2, 2, elementName=name)

        self.elementSet.addElement(element)
        #self.elementList.append(element)

        self.updateElementListView()

    def deleteElement(self):
        index = self.window.itemListWidget.currentRow()
        if index != -1:
            self.elementSet.removeElement(index)
            #self.elementList.pop(index)
            self.updateElementListView()

    def updateElementListView(self):
        self.window.itemListWidget.clear()

        for item in self.elementSet.elementList:
            self.window.itemListWidget.addItem(item.elementName)

    def chooseElement(self):
        self.window.scene.removeItem(self.currentElement)
        index = self.window.itemListWidget.currentRow()
        if index != -1:
            self.currentElement = self.elementSet.elementList[index]
            self.window.nameEdit.setText(self.currentElement.elementName)
            self.window.scene.addItem(self.currentElement)

            self.window.leftConnectorCombo.setCurrentIndex(self.currentElement.leftConnectorType - 1)
            self.window.rightConnectorCombo.setCurrentIndex(self.currentElement.rightConnectorType - 1)

    def applyChanges(self):
        newName = self.window.nameEdit.text()
        self.currentElement.elementName = newName
        self.updateElementListView()
        self.updateScene()
        self.saved = False

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
        self.saved = False

    def changeRightConnector(self):
        index = self.window.rightConnectorCombo.currentIndex()
        index += 1
        self.window.scene.removeItem(self.currentElement)

        self.currentElement.changeRightConnector(index)

        self.window.scene.addItem(self.currentElement)
        self.saved = False

    def saveToFile(self):
        if self.fileName is not None:
            saveFile = QSaveFile(self.fileName)
            saveFile.open(QIODevice.WriteOnly)
            data = self.elementSet.toBytes()
            saveFile.writeData(data)
            saveFile.commit()
            self.saved = True
        else:
            self.saveAs()

    def saveAs(self):
        ret = QFileDialog.getSaveFileName(filter='*.elms')
        self.fileName = ret[0]
        self.saveToFile()

    def loadFromFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.elms')
        self.fileName = ret[0]
        file = open(self.fileName, 'r')

        st = '\n'.join(file.readlines())

        self.elementSet.fromString(st)
        file.close()
        self.updateElementListView()
        self.saved = True