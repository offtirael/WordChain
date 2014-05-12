from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json

from Element import *
from Connectors import *

import resources


class ElementEditor(QMainWindow):
    def __init__(self, parent=None):
        super(ElementEditor, self).__init__(parent)

        self.elementSet = ElementSet()
        self.currentElement = None
        self.saved = True
        self.fileName = None

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMinimumSize(QSize(200, 600))
        self.gBox2 = QFrame()
        self.gBox2.setMinimumSize(QSize(200, 600))

        self.scene = QGraphicsScene(-200, -200, 400, 400)

        # Graphics view
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setMinimumSize(QSize(700, 600))

        # Right menu
        self.createRightMenu()

        # Left menu
        self.itemListWidget = QListWidget()
        self.itemListWidget.currentItemChanged.connect(self.chooseElement)

        self.leftLayout = QVBoxLayout(self.gBox1)

        self.leftInnerLayout = QHBoxLayout()
        self.leftLayout.addLayout(self.leftInnerLayout)

        self.newElementName = QLineEdit()
        self.addNewElement = QPushButton("Add")
        self.leftInnerLayout.addWidget(self.newElementName)
        self.leftInnerLayout.addWidget(self.addNewElement)

        self.addNewElement.clicked.connect(self.addElement)

        self.leftLayout.addWidget(self.itemListWidget)

        self.deleteButton = QPushButton("Delete element")
        self.leftLayout.addWidget(self.deleteButton)
        self.deleteButton.clicked.connect(self.deleteElement)

        #Toolbox
        self.createToolBox()
        self.loadToolBox()

        # Layout
        self.centralWidget = QWidget()

        self.centralLayout = QHBoxLayout()
        self.centralLayout.addWidget(self.toolBox)
        self.centralLayout.addWidget(self.graphicsView)
        self.centralLayout.addWidget(self.gBox2)
        self.centralWidget.setLayout(self.centralLayout)

        self.setCentralWidget(self.centralWidget)

        self.resize(1200, 700)

        self.setWindowTitle("WordChain : Element editor")

        # ToolBars
        self.fileToolBar = self.addToolBar("File")

        self.saveAction = QAction(QIcon(':/images/save.png'), "Save to &File", self,
                                  shortcut="Ctrl+S", triggered=self.saveToFile)
        self.openAction = QAction(QIcon(':/images/open.png'), "Open &File", self,
                                  shortcut="Ctrl+O", triggered=self.loadFromFile)

        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.openAction)

    def createRightMenu(self):
        # Name edit
        self.label1 = QLabel("Element name")
        self.nameEdit = QLineEdit()

        # Choosing left connector type
        self.label2 = QLabel("Left connector")
        self.leftConnectorCombo = QComboBox()
        self.leftConnectorCombo.addItem("Type 1")
        self.leftConnectorCombo.addItem("Type 2")
        self.leftConnectorCombo.addItem("Type 3")
        self.leftConnectorCombo.currentIndexChanged.connect(self.changeLeftConnector)

        # Choosing right connector type
        self.label3 = QLabel("Right connector")
        self.rightConnectorCombo = QComboBox()
        self.rightConnectorCombo.addItem("Type 1")
        self.rightConnectorCombo.addItem("Type 2")
        self.rightConnectorCombo.addItem("Type 3")
        self.rightConnectorCombo.currentIndexChanged.connect(self.changeRightConnector)

        # Choosing color
        self.label4 = QLabel("Color")
        self.colorWidget = QWidget()
        self.colorLayout = QHBoxLayout()
        self.colorName = QLineEdit()
        self.colorName.setReadOnly(True)
        self.colorChoose = QPushButton("Choose")
        self.colorChoose.clicked.connect(self.chooseColor)
        self.colorLayout.addWidget(self.colorName)
        self.colorLayout.addWidget(self.colorChoose)
        self.colorWidget.setLayout(self.colorLayout)

        # Applying changes
        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(self.applyChanges)

        # Word list
        self.wordList = QListWidget()
        self.wordListLayout = QHBoxLayout()
        self.addWord = QPushButton("Add word")
        self.deleteWord = QPushButton("Delete")
        self.wordListLayout.addWidget(self.addWord)
        self.wordListLayout.addWidget(self.deleteWord)

        self.addWord.clicked.connect(self.newWord)
        self.deleteWord.clicked.connect(self.removeWord)

        # Layout
        self.rightLayout = QVBoxLayout(self.gBox2)
        self.rightLayout.setAlignment(Qt.AlignTop)
        self.rightLayout.addWidget(self.label1)
        self.rightLayout.addWidget(self.nameEdit)
        self.rightLayout.addWidget(self.label2)
        self.rightLayout.addWidget(self.leftConnectorCombo)
        self.rightLayout.addWidget(self.label3)
        self.rightLayout.addWidget(self.rightConnectorCombo)
        self.rightLayout.addWidget(self.label4)
        self.rightLayout.addWidget(self.colorWidget)
        self.rightLayout.addWidget(self.wordList)
        self.rightLayout.addLayout(self.wordListLayout)
        self.rightLayout.addWidget(self.applyButton)

    def newWord(self):
        word, ok = QInputDialog.getText(None, "Add new word", "Enter new word:")
        if word is not None and ok:
            self.currentElement.addWord(word)
        self.updateWordList()
        self.wordList.setCurrentRow(len(self.currentElement.words) - 1)

    def removeWord(self):
        self.currentElement.removeWord(self.wordList.currentRow())
        self.updateWordList()

    def updateWordList(self):
        self.wordList.clear()
        for word in self.currentElement.words:
            self.wordList.addItem(word)

    def createToolBox(self):
        self.toolBox = QToolBox()
        self.toolBox.setMinimumSize(QSize(250, 600))
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        self.toolBoxLayout = QGridLayout()
        self.toolBoxLayout.setRowStretch(4, 10)
        self.toolBoxLayout.setColumnStretch(2, 10)

        self.toolBoxWidget = QWidget()
        self.toolBoxWidget.setLayout(self.toolBoxLayout)
        self.toolBox.addItem(self.toolBoxWidget, "Grammar elements")

    def buttonGroupClicked(self, id):
        if id == len(self.elementSet.elementList):
            self.addElement()
        else:
            self.chooseElement(id)

    def layoutToolBox(self):
        self.clearToolBox()
        self.loadToolBox()

    def clearToolBox(self):
        cnt = self.toolBoxLayout.count()

        while cnt > 0:
            itm = self.toolBoxLayout.itemAt(cnt-1)
            if itm is not None:
                wdg = itm.widget()
                self.toolBoxLayout.removeWidget(wdg)
                wdg.hide()
                wdg.deleteLater()
                cnt -= 1

    def loadToolBox(self):
        rowNum = 0
        colNum = 0
        num = 0
        for elem in self.elementSet.elementList:
            self.toolBoxLayout.addWidget(self.createCellWidget(elem.elementName, elem.image(), num), rowNum, colNum)
            colNum += 1
            num += 1
            if colNum > 1:
                colNum = 0
                rowNum += 1

        self.toolBoxLayout.addWidget(self.createCellWidget("New element", ':images/plus.png', num), rowNum, colNum)

    def closeEvent(self, event):
        if not self.saved:
            msgBox = QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setDetailedText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            ret = msgBox.exec()
            if ret == QMessageBox.Save:
                self.saveToFile()
            elif ret == QMessageBox.Cancel:
                event.ignore()
            elif ret == QMessageBox.Discard:
                pass
            event.accept()
        else:
            event.accept()

    count = 0

    def createCellWidget(self, text, elementImage, num):
        #assert isinstance(elementImage, QPi)

        icon = QIcon(elementImage)
        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        if not isinstance(elementImage, str):
            button.setCheckable(True)
        self.buttonGroup.addButton(button, num)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def showWindow(self):
        self.show()

    def addElement(self):
        name, ok = QInputDialog.getText(None, "Create new element", "Enter new element name:")
        if name is not None and ok:
            element = MetaElement(2, 2, elementName=name)
            self.elementSet.addElement(element)

            self.layoutToolBox()

    def deleteElement(self):
        index = self.itemListWidget.currentRow()
        if index != -1:
            self.elementSet.removeElement(index)
            self.updateElementListView()

    def updateElementListView(self):
        self.itemListWidget.clear()

        for item in self.elementSet.elementList:
            self.itemListWidget.addItem(item.elementName)

    def chooseElement(self, index):
        self.scene.removeItem(self.currentElement)
        if index != -1:
            self.currentElement = self.elementSet.elementList[index]
            self.nameEdit.setText(self.currentElement.elementName)
            self.scene.addItem(self.currentElement)

            self.leftConnectorCombo.setCurrentIndex(self.currentElement.leftConnectorType - 1)
            self.rightConnectorCombo.setCurrentIndex(self.currentElement.rightConnectorType - 1)
            self.colorName.setText(self.currentElement.color.name())
            self.updateWordList()

    def applyChanges(self):
        newName = self.nameEdit.text()
        self.currentElement.elementName = newName
        self.layoutToolBox()
        self.updateScene()
        self.saved = False

    def updateScene(self):
        if self.currentElement is not None:
            self.scene.removeItem(self.currentElement)
            self.scene.addItem(self.currentElement)

    def changeLeftConnector(self):
        index = self.leftConnectorCombo.currentIndex()
        index += 1
        self.scene.removeItem(self.currentElement)

        self.currentElement.changeLeftConnector(index)

        self.scene.addItem(self.currentElement)
        self.layoutToolBox()
        self.saved = False

    def changeRightConnector(self):
        index = self.rightConnectorCombo.currentIndex()
        index += 1
        self.scene.removeItem(self.currentElement)

        self.currentElement.changeRightConnector(index)

        self.scene.addItem(self.currentElement)
        self.layoutToolBox()
        self.saved = False

    def chooseColor(self):
        col = QColorDialog.getColor()
        self.colorName.setText(col.name())
        self.scene.removeItem(self.currentElement)
        self.currentElement.changeColor(col)
        self.scene.addItem(self.currentElement)
        self.layoutToolBox()

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
        self.layoutToolBox()
        self.saved = True