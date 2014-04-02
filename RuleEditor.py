from math import sqrt
from PyQt5.QtCore import *
from PyQt5.QtGui import QTransform, QCursor, QPainterPath, QPen
from PyQt5.QtWidgets import *

import os
from Connectors import RightConnector

from Element import ElementSet, MetaElement


def length(qp1, qp2):
    dx = pow(qp1.x() - qp2.x(), 2)
    dy = pow(qp1.y() - qp2.y(), 2)
    return sqrt(dx + dy)


class ChainView(QGraphicsView):
    def __init__(self, scene=None):
        super(ChainView, self).__init__(scene)

    def mouseMoveEvent(self, event):
        print("Moved")
        event.accept()

    def mousePressEvent(self, event):
        print("Pressed")


class ChainScene(QGraphicsScene):
    MIN_DISTANCE = 20

    def __init__(self, x, y, h, w):
        super(ChainScene, self).__init__(x, y, h, w)

        self.contextMenu = QMenu()
        self.action1 = self.contextMenu.addAction("Action 1")

    def mouseMoveEvent(self, event):
        itm = self.itemAt(event.scenePos(), QTransform())

        for item in self.items():
            if not isinstance(itm, QGraphicsItemGroup):
                if itm != item:

                    dist1 = length(itm.getLeftCenter(), item.getRightCenter())
                    dist2 = length(itm.getRightCenter(), item.getLeftCenter())

                    if dist1 < self.MIN_DISTANCE and self.connecting(itm.leftConnectorType, item.rightConnectorType):
                        print("Left to right")
                        #rl = QGraphicsItemGroup()
                        #rl.addToGroup(itm)
                        #rl.addToGroup(item)
                        rl = Rule(itm)
                        rl.addElementLeft(item)
                        self.removeItem(itm)
                        self.removeItem(item)
                        self.addItem(rl)
                    elif dist2 < self.MIN_DISTANCE and self.connecting(item.leftConnectorType, itm.rightConnectorType):
                        print("Right to left")
                        #rl = QGraphicsItemGroup()
                        #rl.addToGroup(itm)
                        #rl.addToGroup(item)
                        rl = Rule(itm)
                        rl.addElementRight(item)
                        self.removeItem(itm)
                        self.removeItem(item)
                        self.addItem(rl)

        if itm != 0 or not None:
            #self.sendEvent(itm, event)
            itm.setPos(event.scenePos())

    def mousePressEvent(self, event):
        itm = self.itemAt(event.scenePos(), QTransform())
        if itm != 0:
            if event.button() == Qt.RightButton:
                print("Right button")
                self.contextMenu.exec(QCursor.pos())

            elif event.button() == Qt.LeftButton:
                print("Left button")

    def connecting(self, leftType, rightType):
        if leftType == 1 or rightType == 1:
            return False
        elif leftType == 2 and rightType == 3:
            return True
        elif leftType == 3 and rightType == 2:
            return True
        else:
            return False


class RuleEditorWindow(QMainWindow):
    def __init__(self, editor, parent=None):
        super(RuleEditorWindow, self).__init__(parent)

        self.editor = editor

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(200, 600))
        self.gBox2 = QFrame()
        self.gBox2.setMaximumSize(QSize(200, 200))

        #self.scene = QGraphicsScene(-200, -200, 400, 400)
        self.scene = ChainScene(-200, -200, 400, 400)

        # Graphics view
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setMinimumSize(QSize(800, 600))

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
        self.leftLayout.addWidget(self.elemListWidget)

        self.chooseFile.clicked.connect(self.editor.chooseFile)
        self.loadFile.clicked.connect(self.editor.loadFile)
        self.elemListWidget.itemDoubleClicked.connect(self.editor.addElementToScene)

        # Layout
        self.centralWidget = QSplitter()
        self.centralWidget.addWidget(self.gBox1)
        self.centralWidget.addWidget(self.graphicsView)
        self.centralWidget.addWidget(self.gBox2)

        self.setCentralWidget(self.centralWidget)

        self.resize(1200, 600)

        self.setWindowTitle("WordChain : Rule editor")


class RuleEditor(object):
    def __init__(self):
        self.window = RuleEditorWindow(editor=self)
        self.currentElementFile = None
        self.currentRuleFile = None
        self.sceneElementList = []
        self.elementSet = ElementSet()

    def showWindow(self):
        self.window.show()

    def chooseFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.elms')
        self.currentElementFile = ret[0]
        self.window.fileName.setText(os.path.basename(self.currentElementFile))

    def loadFile(self):
        if self.currentElementFile is not None:
            file = open(self.currentElementFile, 'r')

            st = '\n'.join(file.readlines())

            self.elementSet.fromString(st)
            file.close()

            self.updateElementListView()

    def updateElementListView(self):
        self.window.elemListWidget.clear()

        for item in self.elementSet.elementList:
            self.window.elemListWidget.addItem(item.elementName)

    def addElementToScene(self):
        index = self.window.elemListWidget.currentRow()
        if index != -1:
            el = self.elementSet.elementList[index]
            newElement = MetaElement(el.leftConnectorType, el.rightConnectorType, el.elementName)
            self.sceneElementList.append(newElement)

            self.window.scene.addItem(newElement)


class Rule(QGraphicsItem):
    def __init__(self, elem):
        super(Rule, self).__init__()
        self.elements = []
        self.formPath = QPainterPath()

        self.pen = QPen()
        self.pen.setWidth(2)

        self.elements.append(elem)

    def addElementLeft(self, element):
        self.elements.insert(0, element)
        self.setPath()

    def setPath(self):
        self.formPath.moveTo(QPoint(-100, -50))

        rightTop = QPoint(-100 + (200 * len(self.elements)), -50)
        rightBottom = QPoint(rightTop.x(), 50)

        self.formPath.lineTo(rightTop)

        endConnector = RightConnector(self.elements[-1].rightConnectorType, rightBottom, rightTop)

        self.formPath.addPath(endConnector.connectorPath)

        self.formPath.lineTo(QPoint(-100, 50))
        self.formPath.addPath(self.elements[0].leftConnector.connectorPath)

        deltaY = 200
        for elem in self.elements:
            bot = QPoint(-100 + deltaY, 50)
            top = QPoint(-100 + deltaY, -50)
            endConnector = RightConnector(elem.rightConnectorType, bot, top)
            self.formPath.addPath(endConnector.connectorPath)
            deltaY += 200

    def addElementRight(self, element):
        self.elements.append(element)
        self.setPath()

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.drawPath(self.formPath)
        for elem in self.elements:
            painter.drawText(elem.boundingRect(), Qt.AlignCenter, elem.elementName)

    def boundingRect(self):
        return self.formPath.boundingRect()

    def addPathRight(self, path):
        assert isinstance(path, QPainterPath)
        self.formPath.moveTo(self.boundingRect().topRight())
        self.formPath.addPath(path)

    def addPathLeft(self, path):
        assert isinstance(path, QPainterPath)
        self.formPath.moveTo(self.boundingRect().topLeft())
        self.formPath.addPath(path)

    def dispose(self):
        pass
