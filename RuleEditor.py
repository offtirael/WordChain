from math import sqrt
from PyQt5.QtCore import *
from PyQt5.QtGui import QTransform, QCursor, QPainterPath, QPen, QIcon, QColor
from PyQt5.QtWidgets import *

import os
from Connectors import RightConnector

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
        self.contextMenu = QMenu()
        self.action1 = self.contextMenu.addAction("Action 1")
        self.toInsert = None
        self.connections = []

    ###########################################################################
    def setToInert(self, item):
        assert isinstance(item, MetaElement)
        self.toInsert = item

    ###########################################################################
    def setItemType(self, itype):
        self.itemType = itype

    ###########################################################################
    """
    Set active scene mode.

    Keyword arguments:
    mode -- new scene mode
    """
    def setMode(self, mode):
        self.mode = mode

    ###########################################################################
    """
    Handler for mouse move events.

    Keyword arguments:
    event -- mouse event
    """
    def mouseMoveEvent(self, event):
        if self.mode == ChainScene.InsertLine and self.line:
            newLine = QLineF(self.line.line().p1(),
                             event.scenePos())
            self.line.setLine(newLine)
        elif self.mode == ChainScene.MoveItem:
            super(ChainScene, self).mouseMoveEvent(event)

    ###########################################################################
    """
    Handler for mouse press events.

    Keyword arguments:
    event -- mouse event
    """
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mode == ChainScene.InsertItem:
                item = MetaElement(self.toInsert.leftConnectorType,
                                   self.toInsert.rightConnectorType,
                                   self.toInsert.elementName,
                                   self.toInsert.color)
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
                    print("test")
                    self.clearSelection()
                    self.clearFocus()
        elif event.button() == Qt.RightButton:
            pass

        super(ChainScene, self).mousePressEvent(event)

    ###########################################################################
    """
    Handler for mouse release events.

    Keyword arguments:
    event -- mouse event
    """
    def mouseReleaseEvent(self, event):
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

        self.removeItem(self.line)
        super(ChainScene, self).mouseReleaseEvent(event)

    ###########################################################################
    def testRule(self):
        for itm in self.items():
            if isinstance(itm, MetaElement):
                if len(itm.connections) % 2 == 0:
                    print("Error")

    ###########################################################################
    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False

    ###########################################################################
    """
    Connectivity test for two elements.

    Keyword arguments:
    leftType -- left element connector type
    rightType -- right element connector type
    """
    @staticmethod
    def connecting(leftType, rightType):
        if leftType == 1 or rightType == 1:
            return False
        elif leftType == 2 and rightType == 3:
            return True
        elif leftType == 3 and rightType == 2:
            return True
        else:
            return False

    ###########################################################################
    """
    Compute distance between two points.

    Keyword arguments:
    qp1 -- first point, QPoint
    qp2 -- second point, QPoint
    """
    @staticmethod
    def length(qp1, qp2):
        dx = pow(qp1.x() - qp2.x(), 2)
        dy = pow(qp1.y() - qp2.y(), 2)
        return sqrt(dx + dy)

    ###########################################################################
    """
    Create connection between two elements.

    Keyword arguments:
    el1 -- start element, MetaElement
    el2 -- end element, MetaElement
    """
    def addConnection(self, el1, el2):
        if el1.pos().x() < el2.pos().x():
            conn = Connection(el1, el2)
            el1.outConnections.append(conn)
            el2.inConnections.append(conn)
        else:
            conn = Connection(el2, el1)
            el1.inConnections.append(conn)
            el2.outConnections.append(conn)

        #conn = Connection(el1, el2)
        #el1.connections.append(conn)
        #el2.connections.append(conn)
        self.connections.append(conn)
        self.addItem(conn)


###############################################################################
###############################################################################


class RuleEditorNew(QMainWindow):

    ###########################################################################
    def __init__(self, parent=None):
        super(RuleEditorNew, self).__init__(parent)

        self.currentElementFile = None
        self.currentRuleFile = None
        self.sceneElementList = []
        self.connections = []
        self.elementSet = ElementSet()
        self.rule = Rule()

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(250, 600))

        #self.scene = QGraphicsScene(-200, -200, 400, 400)
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

        self.label1 = QLabel("Elements file:")
        self.fileName = QLabel("--")
        self.chooseFile = QPushButton("Choose file")
        self.loadFile = QPushButton("Load")
        self.elemListWidget = QListWidget()

        self.leftLayout.addWidget(self.label1)
        self.leftLayout.addWidget(self.fileName)
        self.leftInnerLayout.addWidget(self.chooseFile)
        self.leftInnerLayout.addWidget(self.loadFile)
        self.leftLayout.addLayout(self.leftInnerLayout)
        self.leftLayout.addWidget(self.toolBox)

        self.chooseFile.clicked.connect(self.chooseElementsFile)
        self.loadFile.clicked.connect(self.loadElementsFile)

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
        #self.testGroup = QButtonGroup()
        testButton = QPushButton()
        testButton.setIcon(QIcon(":/images/play.png"))
        testButton.setText("Test rule")
        testButton.clicked.connect(self.testRule)
        #self.testGroup.addButton(testButton)
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
        print('ins')
        buttons = self.buttonGroup.buttons()
        for button in buttons:
            button.setChecked(False)

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
    def loadFromFile(self):
        pass

    ###########################################################################
    def saveToFile(self):
        pass

    ###########################################################################
    def showWindow(self):
        self.show()

    ###########################################################################
    def chooseElementsFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.elms')
        self.currentElementFile = ret[0]
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
        print(self.rule.firstElement.elementName)
        print(self.rule.endingElement.elementName)


###############################################################################
###############################################################################


class Connection(QGraphicsLineItem):

    ###########################################################################
    def __init__(self, start, end):
        super(Connection, self).__init__()

        self.startElement = start
        self.endElement = end
        self.color = QColor(0, 0, 0)
        self.setPen(QPen(self.color, 2, Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    ###########################################################################
    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    ###########################################################################
    def paint(self, painter, option, widget=None):
        self.setLine(QLineF(self.startElement.getRightCenter(), self.endElement.getLeftCenter()))
        painter.setPen(self.pen())
        painter.drawLine(self.line())

    ###########################################################################
    def updatePosition(self):
        line = QLineF(self.startElement.getRightCenter(), self.endElement.getLeftCenter())
        self.setLine(line)


################################################################################################
################################################################################################


class Rule(object):
    def __init__(self):
        self.elements = []
        self.connections = []
        self.firstElement = None
        self.endingElement = None

    def fromElementList(self, lst):
        for elem in lst:
            if isinstance(elem, MetaElement):
                self.elements.append(elem)
                if len(elem.inConnections) == 0:
                    self.firstElement = elem
                elif len(elem.outConnections) == 0:
                    self.endingElement = elem
            elif isinstance(elem, Connection):
                self.connections.append(elem)

    def check(self):
        return False
