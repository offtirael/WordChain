from math import sqrt
from PyQt5.QtCore import *
from PyQt5.QtGui import QTransform, QCursor, QPainterPath, QPen, QIcon, QColor
from PyQt5.QtWidgets import *

import os
from Rule import Rule, Connection, RuleSet

from Element import ElementSet, MetaElement


class ChainScene(QGraphicsScene):
    MoveItem, InsertItem, InsertLine = range(3)
    MIN_DISTANCE = 20

    itemInserted = pyqtSignal(MetaElement)

    ###########################################################################
    def __init__(self, x, y, h, w):
        super(ChainScene, self).__init__(x, y, h, w)

        self.mode = ChainScene.InsertItem
        self.itemType = -1
        self.toInsert = None
        self.line = None

        self.contextMenu1 = QMenu()
        self.contextMenu1.addAction(QAction("Delete", self, triggered=self.deleteItem))

        self.contextMenu2 = QMenu()
        self.contextMenu2.addAction(QAction("Delete", self, triggered=self.deleteItem))
        self.contextMenu2.addAction(QAction("Properties", self, triggered=self.itemProperties))
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    ###########################################################################
    def setToInert(self, item):
        assert isinstance(item, MetaElement)
        self.toInsert = item

    ###########################################################################
    def setItemType(self, itype):
        self.itemType = itype

    ###########################################################################
    def setMode(self, mode):
        """
        Set active scene mode.

        Keyword arguments:
        mode -- new scene mode
        """
        self.mode = mode

    ###########################################################################
    def mouseMoveEvent(self, event):
        """
        Handler for mouse move events.

        Keyword arguments:
        event -- mouse event
        """
        if self.mode == ChainScene.InsertLine and self.line:
            newLine = QLineF(self.line.line().p1(),
                             event.scenePos())
            self.line.setLine(newLine)
        elif self.mode == ChainScene.MoveItem:
            super(ChainScene, self).mouseMoveEvent(event)

    ###########################################################################
    def mousePressEvent(self, event):
        """
        Handler for mouse press events.

        Keyword arguments:
        event -- mouse event
        """
        super(ChainScene, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if self.mode == ChainScene.InsertItem:
                item = MetaElement(self.toInsert.leftConnectorType,
                                   self.toInsert.rightConnectorType,
                                   self.toInsert.elementName,
                                   self.toInsert.color)
                item.addProperties(self.toInsert.properties)
                self.addItem(item)
                item.setPos(event.scenePos())
                self.itemInserted.emit(item)
                self.update()
                self.clearSelection()
            elif self.mode == ChainScene.InsertLine:
                self.line = QGraphicsLineItem(QLineF(event.scenePos(), event.scenePos()))
                self.addItem(self.line)
            elif self.mode == ChainScene.MoveItem:
                if self.focusItem() is None:
                    self.clearSelection()
                    self.clearFocus()
        elif event.button() == Qt.RightButton:
            if len(self.selectedItems()) > 0:
                if isinstance(self.selectedItems()[0], MetaElement):
                    self.contextMenu1.exec(QCursor.pos())
                elif isinstance(self.selectedItems()[0], Connection):
                    self.contextMenu2.exec(QCursor.pos())

                    #super(ChainScene, self).mousePressEvent(event)

    ###########################################################################

    def mouseReleaseEvent(self, event):
        """
        Handler for mouse release events.

        Keyword arguments:
        event -- mouse event
        """
        if self.line and self.mode == ChainScene.InsertLine:
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)
            self.line = None

            if len(startItems) and len(endItems) and \
                    isinstance(startItems[0], MetaElement) and \
                    isinstance(endItems[0], MetaElement) and \
                            startItems[0] != endItems[0]:
                startItem = startItems[0]
                endItem = endItems[0]
                self.addConnection(startItem, endItem)
        if self.line:
            self.removeItem(self.line)
        self.clearSelection()
        super(ChainScene, self).mouseReleaseEvent(event)

    ###########################################################################
    def testRule(self):
        pass

    ###########################################################################
    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False

    ###########################################################################
    @staticmethod
    def connecting(leftType, rightType):
        """
        Connectivity test for two elements.

        Keyword arguments:
        leftType -- left element connector type
        rightType -- right element connector type
        """
        if leftType == 1 or rightType == 1:
            return False
        elif leftType == 2 and rightType == 3:
            return True
        elif leftType == 3 and rightType == 2:
            return True
        else:
            return False

    ###########################################################################
    connectionCount = 1
    def addConnection(self, el1, el2, connName=None):
        """
        Create connection between two elements.

        Keyword arguments:
        el1 -- start element, MetaElement
        el2 -- end element, MetaElement
        """
        name = connName
        if connName is None:
            name = "c" + str(ChainScene.connectionCount)
        if el1.pos().x() < el2.pos().x():
            conn = Connection(el1, el2, name)
            el1.outConnections.append(conn)
            el2.inConnections.append(conn)
        else:
            conn = Connection(el2, el1, name)
            el1.inConnections.append(conn)
            el2.outConnections.append(conn)
        ChainScene.connectionCount += 1
        self.addItem(conn)

    ###########################################################################
    def deleteItem(self):
        itm = self.selectedItems()[0]
        if itm:
            if isinstance(itm, Connection):
                itm.endElement.inConnections.remove(itm)
                itm.startElement.outConnections.remove(itm)
                self.removeItem(itm)
            elif isinstance(itm, MetaElement):
                for c in itm.inConnections:
                    self.removeItem(c)
                for c in itm.outConnections:
                    self.removeItem(c)
                self.removeItem(itm)

    ###########################################################################
    def itemProperties(self):
        if isinstance(self.selectedItems()[0], Connection):
            name, ok = RulePropertiesDialog.getRuleProperties(self.selectedItems()[0])
            if name is not None and ok:
                self.selectedItems()[0].name = name
                self.update()


###############################################################################
###############################################################################


class RuleEditor(QMainWindow):
    ###########################################################################
    def __init__(self, parent=None):
        super(RuleEditor, self).__init__(parent)

        self.currentElementFile = None
        self.currentRuleFile = None
        self.sceneElementList = []
        self.connections = []
        self.elementSet = ElementSet()
        self.rule = Rule()
        self.ruleSet = RuleSet()

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(250, 600))

        self.scene = ChainScene(-200, -200, 400, 400)
        self.scene.itemInserted.connect(self.itemInserted)

        # Graphics view
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setMinimumSize(QSize(800, 600))

        #Toolbox
        self.createToolBox()
        self.loadToolBox()

        # Left menu
        self.leftLayout = QVBoxLayout(self.gBox1)
        self.leftInnerLayout = QHBoxLayout()
        self.leftInnerLayout2 = QHBoxLayout()

        self.label1 = QLabel("Elements file:")
        self.fileName = QLabel("--")
        self.chooseFile = QPushButton("Choose file")
        self.loadFile = QPushButton("Load")
        self.ruleListWidget = QListWidget()
        self.addRule = QPushButton("Add rule")
        self.deleteRule = QPushButton("Delete")

        self.leftLayout.addWidget(self.label1)
        self.leftLayout.addWidget(self.fileName)
        self.leftInnerLayout.addWidget(self.chooseFile)
        self.leftInnerLayout.addWidget(self.loadFile)
        self.leftLayout.addLayout(self.leftInnerLayout)
        self.leftLayout.addWidget(self.ruleListWidget)
        self.leftInnerLayout2.addWidget(self.addRule)
        self.leftInnerLayout2.addWidget(self.deleteRule)
        self.leftLayout.addLayout(self.leftInnerLayout2)
        self.leftLayout.addWidget(self.toolBox)

        self.chooseFile.clicked.connect(self.chooseElementsFile)
        self.loadFile.clicked.connect(self.loadElementsFile)
        self.addRule.clicked.connect(self.newRule)
        self.deleteRule.clicked.connect(self.removeRule)
        self.ruleListWidget.currentRowChanged[int].connect(self.changeCurrentRule)


        # Layout
        self.centralWidget = QWidget()
        self.centralLayout = QHBoxLayout()
        self.centralLayout.addWidget(self.gBox1)
        self.centralLayout.addWidget(self.graphicsView)
        self.centralWidget.setLayout(self.centralLayout)

        self.setCentralWidget(self.centralWidget)

        self.resize(1200, 600)

        self.setWindowTitle("WordChain : Rule editor")

        # ToolBars
        self.fileToolBar = self.addToolBar("File")

        self.saveAction = QAction(QIcon(':/images/save.png'), "Save to &File", self,
                                  shortcut="Ctrl+S", triggered=self.saveToFile)
        self.openAction = QAction(QIcon(':/images/open.png'), "Open &File", self,
                                  shortcut="Ctrl+O", triggered=self.loadFromFile)
        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.openAction)

        self.pointerToolbar = self.addToolBar("Pointer type")

        pointerButton = QToolButton()
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        pointerButton.setIcon(QIcon(":/images/arrow.png"))
        lineButton = QToolButton()
        lineButton.setCheckable(True)
        lineButton.setIcon(QIcon(":/images/line.png"))

        self.pointerTypeGroup = QButtonGroup()
        self.pointerTypeGroup.addButton(pointerButton, ChainScene.MoveItem)
        self.pointerTypeGroup.addButton(lineButton, ChainScene.InsertLine)

        self.pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)

        self.pointerToolbar.addWidget(pointerButton)
        self.pointerToolbar.addWidget(lineButton)

        self.testToolbar = self.addToolBar("Model testing")
        testButton = QPushButton()
        testButton.setIcon(QIcon(":/images/play.png"))
        testButton.setText("Test rule")
        testButton.clicked.connect(self.testRule)
        self.testToolbar.addWidget(testButton)

    ###########################################################################
    def createToolBox(self):
        self.toolBox = QToolBox()
        self.toolBox.setMinimumSize(QSize(250, 600))
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        self.toolBoxLayout = QGridLayout()
        self.toolBoxLayout.setRowStretch(4, 10)
        self.toolBoxLayout.setColumnStretch(2, 10)

        self.toolBoxWidget = QWidget()
        self.toolBoxWidget.setLayout(self.toolBoxLayout)
        self.toolBox.addItem(self.toolBoxWidget, "Grammar elements")

    ###########################################################################
    def buttonGroupClicked(self, i):
        if i == len(self.elementSet.elementList):
            pass
        else:
            el = self.elementSet.elementList[i]
            self.scene.setToInert(el)
            self.scene.setMode(ChainScene.InsertItem)

            buttons = self.buttonGroup.buttons()
            for button in buttons:
                if self.buttonGroup.button(i) != button:
                    button.setChecked(False)

    ###########################################################################
    def itemInserted(self, item):
        self.pointerTypeGroup.button(ChainScene.MoveItem).setChecked(True)
        self.scene.setMode(self.pointerTypeGroup.checkedId())

        buttons = self.buttonGroup.buttons()
        for button in buttons:
            button.setChecked(False)
        self.rule.fromElementList(self.scene.items())

    ###########################################################################
    def pointerGroupClicked(self, i):
        self.scene.setMode(self.pointerTypeGroup.checkedId())

    ###########################################################################
    def layoutToolBox(self):
        self.clearToolBox()
        self.loadToolBox()

    ###########################################################################
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

    ###########################################################################
    def clearToolBox(self):
        cnt = self.toolBoxLayout.count()

        while cnt > 0:
            itm = self.toolBoxLayout.itemAt(cnt - 1)
            if itm is not None:
                wdg = itm.widget()
                self.toolBoxLayout.removeWidget(wdg)
                wdg.hide()
                wdg.deleteLater()
                cnt -= 1

    ###########################################################################
    def createCellWidget(self, text, elementImage, num):
        icon = QIcon(elementImage)
        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, num)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    ###########################################################################
    def saveToFile(self):
        self.rule.fromElementList(self.scene.items())
        if self.currentRuleFile is not None:
            saveFile = QSaveFile(self.currentRuleFile)
            saveFile.open(QIODevice.WriteOnly)
            data = self.ruleSet.toBytes()
            saveFile.writeData(data)
            saveFile.commit()
        else:
            self.saveAs()
        self.setWindowTitle("WordChain : Rule editor : " + self.currentRuleFile)

    ###########################################################################
    def saveAs(self):
        ret = QFileDialog.getSaveFileName(filter='*.rl')
        self.currentRuleFile = ret[0]
        self.saveToFile()
        self.setWindowTitle("WordChain : Rule editor : " + self.currentRuleFile)

    ###########################################################################
    def loadFromFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.rl')
        self.currentRuleFile = ret[0]
        file = open(self.currentRuleFile, 'r')

        st = '\n'.join(file.readlines())
        self.ruleSet.fromString(st)

        if len(self.scene.items()) > 0:
            for item in self.scene.items():
                self.scene.removeItem(item)

        self.currentElementFile = self.ruleSet.elementsFileName
        self.fileName.setText(os.path.basename(self.currentElementFile))
        self.loadElementsFile()
        self.scene.setMode(ChainScene.MoveItem)
        self.updateRuleList()
        self.changeCurrentRule(0)

        self.setWindowTitle("WordChain : Rule editor : " + self.currentRuleFile)

    ###########################################################################
    def showWindow(self):
        self.show()
        self.updateRuleList()

    def updateRuleList(self):
        self.ruleListWidget.clear()
        rowCount = 0
        for rule in self.ruleSet.ruleList:
            self.ruleListWidget.insertItem(rowCount, rule.name)
            rowCount += 1

    def newRule(self):
        name, ok = QInputDialog.getText(None, "Create new rule", "Enter new rule name:")
        if name is not None and ok:
            self.rule = Rule()
            self.rule.setName(name)
            self.ruleSet.addRule(self.rule)
        self.updateRuleList()
        self.changeCurrentRule(len(self.ruleSet.ruleList) - 1)
        self.ruleListWidget.setCurrentRow(len(self.ruleSet.ruleList) - 1)

    def changeCurrentRule(self, idx):
        self.rule.fromElementList(self.scene.items())
        self.rule = self.ruleSet.getRule(idx)
        self.loadRuleToScene()

    def removeRule(self):
        self.ruleSet.deleteRule(self.ruleListWidget.currentRow())
        self.updateRuleList()

    def loadRuleToScene(self):
        self.scene.clear()
        for ruleElem in self.rule.elements:
            for el in self.elementSet.elementList:
                if el.elementName == ruleElem['elementName']:
                    item = MetaElement(el.leftConnectorType,
                                       el.rightConnectorType,
                                       el.elementName,
                                       el.color)
                    item.addProperties(el.properties)
                    self.scene.addItem(item)
                    item.setPos(QPoint(ruleElem['x'], ruleElem['y']))

        for ruleConn in self.rule.connections:
            el1 = self.scene.items()[ruleConn['p1']]
            el2 = self.scene.items()[ruleConn['p2']]
            name = ruleConn.get('name', '')
            self.scene.addConnection(el2, el1, name)

    ###########################################################################
    def chooseElementsFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.elms')
        self.currentElementFile = ret[0]
        self.ruleSet.setElementsFileName(self.currentElementFile)
        self.fileName.setText(os.path.basename(self.currentElementFile))

    ###########################################################################
    def loadElementsFile(self):
        if self.currentElementFile is not None:
            file = open(self.currentElementFile, 'r')

            st = '\n'.join(file.readlines())

            self.elementSet.fromString(st)
            file.close()
            self.layoutToolBox()

    ###########################################################################
    def updateElementListView(self):
        self.elemListWidget.clear()

        for item in self.elementSet.elementList:
            self.elemListWidget.addItem(item.elementName)

    ###########################################################################
    def testRule(self):
        self.rule.fromElementList(self.scene.items())
        print(self.ruleSet.toString())


class RulePropertiesDialog(QDialog):
    def __init__(self, connection, parent=None):
        super(RulePropertiesDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        self.label1 = QLabel("Name")
        self.name = QLineEdit()

        self.hLayout1 = QHBoxLayout()
        self.label2 = QLabel("Start element properties")
        self.label3 = QLabel("End element properties")
        self.hLayout1.addWidget(self.label2)
        self.hLayout1.addWidget(self.label3)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                        QDialogButtonBox.Cancel,
                                        Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.propertiesLayout = QHBoxLayout()

        self.leftPropertiesLayout = QVBoxLayout()
        self.rightPropertiesLayout = QVBoxLayout()

        self.leftCombos = []
        self.leftPropNames = []

        self.rightCombos = []
        self.rightPropNames = []

        for prop in connection.startElement.properties:
            innerLayout = QHBoxLayout()
            label = QLabel(prop['name'])
            combo = QComboBox()
            combo.addItem('--')
            for val in prop['values']:
                combo.addItem(val)
            innerLayout.addWidget(label)
            innerLayout.addWidget(combo)

            self.leftCombos.append(combo)
            self.leftPropNames.append(prop['name'])

            self.leftPropertiesLayout.addLayout(innerLayout)

        for prop in connection.endElement.properties:
            innerLayout = QHBoxLayout()
            label = QLabel(prop['name'])
            combo = QComboBox()
            combo.addItem('--')
            for val in prop['values']:
                combo.addItem(val)
            innerLayout.addWidget(label)
            innerLayout.addWidget(combo)

            self.rightCombos.append(combo)
            self.rightPropNames.append(prop['name'])

            self.rightPropertiesLayout.addLayout(innerLayout)

        self.propertiesLayout.addLayout(self.leftPropertiesLayout)
        self.propertiesLayout.addLayout(self.rightPropertiesLayout)

        # Layout
        layout.addWidget(self.label1)
        layout.addWidget(self.name)
        layout.addLayout(self.hLayout1)
        layout.addLayout(self.propertiesLayout)
        layout.addWidget(self.buttons)

    @staticmethod
    def getRuleProperties(connection, parent=None):
        dialog = RulePropertiesDialog(connection, parent)
        dialog.name.setText(connection.name)

        result = dialog.exec_()

        name = dialog.name.text()

        return name, result == QDialog.Accepted




