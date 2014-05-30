from math import sqrt
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import *
from Element import ElementSet, Element
from Rule import RuleSet


class Practice(QMainWindow):
    def __init__(self, parent=None):
        super(Practice, self).__init__(parent)

        self.ruleSet = RuleSet()
        self.ruleFileName = ''
        self.elementSet = None

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(250, 600))
        self.gBox1.setMinimumSize(QSize(250, 250))

        self.scene = PracticeScene(-200, -200, 400, 400)
        self.scene.itemInserted.connect(self.itemInserted)

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

    def itemInserted(self, item):
        buttons = self.buttonGroup.buttons()
        for button in buttons:
            button.setChecked(False)

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
        metaElem = self.elementSet.elementList[self.toolBox.currentIndex()]
        element = Element(metaElem.leftConnectorType,
                          metaElem.rightConnectorType,
                          metaElem.words[i]['word'],
                          metaElem.color)
        element.properties = metaElem.words[i]['properties']
        element.setMetaName(metaElem.elementName)
        self.scene.setElementToInsert(element)

    def chooseRuleFile(self):
        ret = QFileDialog.getOpenFileName(filter='*.rl')
        self.ruleFileName = ret[0]
        self.fileName.setText(os.path.basename(self.ruleFileName))

    def clearToolBox(self):
        cnt = self.toolBox.count()
        i = 0
        while i < cnt:
            self.toolBox.removeItem(i)
            i += 1

    def loadToolBox(self):
        for elem in self.elementSet.elementList:
            toolBoxLayout = QGridLayout()
            toolBoxLayout.setRowStretch(4, 10)
            toolBoxLayout.setColumnStretch(2, 10)

            toolBoxWidget = QWidget()
            toolBoxWidget.setLayout(toolBoxLayout)
            self.toolBox.addItem(toolBoxWidget, elem.elementName)

            rowNum = 0
            colNum = 0
            num = 0
            for word in elem.words:
                toolBoxLayout.addWidget(self.createCellWidget(word['word'], elem.image(), num), rowNum, colNum)
                colNum += 1
                num += 1
                if colNum > 1:
                    colNum = 0
                    rowNum += 1

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

    def layoutToolBox(self):
        self.clearToolBox()
        self.loadToolBox()

    def loadRuleFile(self):
        file = open(self.ruleFileName, 'r')

        st = '\n'.join(file.readlines())
        self.ruleSet.fromString(st)

        elementsFileName = self.ruleSet.elementsFileName

        if elementsFileName is not None:
            file = open(elementsFileName, 'r')

            st = '\n'.join(file.readlines())
            self.elementSet = ElementSet()
            self.elementSet.fromString(st)
            file.close()
            self.layoutToolBox()
        self.scene.setRuleSet(self.ruleSet)


class PracticeScene(QGraphicsScene):
    # Minimal distance between connectors
    MIN_DISTANCE = 20

    # The signal emitted when you insert an item into the scene
    itemInserted = pyqtSignal(Element)

    def __init__(self, x, y, h, w):
        super(PracticeScene, self).__init__(x, y, h, w)

        self.elementToInsert = None

        self.contextMenu1 = QMenu()
        self.contextMenu1.addAction(QAction("Disconnect", self, triggered=self.disconnectItems))

        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    def setRuleSet(self, ruleSet):
        self.ruleSet = ruleSet

    def disconnectItems(self):
        if len(self.selectedItems()) > 0:
            compoundItem = self.selectedItems()[0]
            pos = compoundItem.pos()
            for item in compoundItem.parts:
                item.compound = False
                self.addItem(item)
                pos.setX(pos.x() + 40)
                item.setPos(pos)
            self.removeItem(compoundItem)
            self.clearSelection()

    def setElementToInsert(self, element):
        assert isinstance(element, Element)

        self.elementToInsert = element

    def mousePressEvent(self, event):
        """
        Handler for mouse press events.

        Keyword arguments:
        event -- mouse event
        """
        super(PracticeScene, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if self.elementToInsert:
                self.addItem(self.elementToInsert)
                self.itemInserted.emit(self.elementToInsert)
                self.elementToInsert.setPos(event.scenePos())
                self.elementToInsert = None
        elif event.button() == Qt.RightButton:
            if len(self.selectedItems()) and self.selectedItems()[0].compound > 0:
                self.contextMenu1.exec(QCursor.pos())

    def connect(self, el1, el2):
        if not el1.compound and not el2.compound:
            for rule in self.ruleSet.ruleList:
                namesList = [elem['elementName'] for elem in rule.elements]

                el1Index = namesList.index(el1.metaName)
                el2Index = namesList.index(el2.metaName)
                if el2Index - el1Index == 1:
                    for conn in rule.connections:
                        if conn['p1'] == el1Index and conn['p2'] == el2Index:
                            if conn['p1Properties'] == el1.properties \
                                    and conn['p2Properties'] == el2.properties \
                                    or conn['p1Properties'] == [] \
                                    and conn['p2Properties'] == []:
                                lst = [el1, el2]
                                compound = Element(lst=lst)
                                compound.setPos(el2.pos())
                                self.removeItem(el1)
                                self.removeItem(el2)
                                self.addItem(compound)
                                return
        elif el1.compound and not el2.compound:
            for rule in self.ruleSet.ruleList:
                namesList = [elem['elementName'] for elem in rule.elements]

                el_1 = el1.parts[len(el1.parts)-1]

                el1Index = namesList.index(el1.parts[len(el1.parts)-1].metaName)
                el2Index = namesList.index(el2.metaName)

                if el2Index - el1Index == 1:
                    for conn in rule.connections:
                        if conn['p1'] == el1Index and conn['p2'] == el2Index:
                            if conn['p1Properties'] == el_1.properties \
                                    and conn['p2Properties'] == el2.properties \
                                    or conn['p1Properties'] == [] \
                                    and conn['p2Properties'] == []:
                                lst = el1.parts
                                lst.append(el2)
                                compound = Element(lst=lst)
                                compound.setPos(el2.pos())
                                self.removeItem(el1)
                                self.removeItem(el2)
                                self.addItem(compound)
                                return
        elif not el1.compound and el2.compound:
            for rule in self.ruleSet.ruleList:
                namesList = [elem['elementName'] for elem in rule.elements]

                el_2 = el2.parts[0]

                el1Index = namesList.index(el1.metaName)
                el2Index = namesList.index(el_2.metaName)

                if el2Index - el1Index == 1:
                    for conn in rule.connections:
                        if conn['p1'] == el1Index and conn['p2'] == el2Index:
                            if conn['p1Properties'] == el1.properties \
                                    and conn['p2Properties'] == el_2.properties \
                                    or conn['p1Properties'] == [] \
                                    and conn['p2Properties'] == []:
                                lst = [el1, ]
                                lst.extend(el2.parts)
                                compound = Element(lst=lst)
                                compound.setPos(el2.pos())
                                self.removeItem(el1)
                                self.removeItem(el2)
                                self.addItem(compound)
                                return
        elif el1.compound and el2.compound:
            for rule in self.ruleSet.ruleList:
                namesList = [elem['elementName'] for elem in rule.elements]

                el_1 = el1.parts[len(el1.parts)-1]
                el_2 = el2.parts[0]
                el1Index = namesList.index(el_1.metaName)
                el2Index = namesList.index(el_2.metaName)

                if el2Index - el1Index == 1:
                    for conn in rule.connections:
                        if conn['p1'] == el1Index and conn['p2'] == el2Index:
                            if conn['p1Properties'] == el_1.properties \
                                    and conn['p2Properties'] == el_2.properties \
                                    or conn['p1Properties'] == [] \
                                    and conn['p2Properties'] == []:
                                lst = el1.parts
                                lst.extend(el2.parts)
                                compound = Element(lst=lst)
                                compound.setPos(el2.pos())
                                self.removeItem(el1)
                                self.removeItem(el2)
                                self.addItem(compound)
                                return

    def mouseMoveEvent(self, event):
        """
        Handler for mouse move events.

        Keyword arguments:
        event -- mouse event
        """
        super(PracticeScene, self).mouseMoveEvent(event)

        if len(self.selectedItems()) > 0:
            selected = self.selectedItems()[0]
            for item in self.items():
                if PracticeScene.distance(selected.getLeftCenter(),
                                          item.getRightCenter()) <\
                        PracticeScene.MIN_DISTANCE and item is not selected:
                    self.connect(item, selected)
                elif PracticeScene.distance(selected.getRightCenter(),
                                            item.getLeftCenter()) <\
                        PracticeScene.MIN_DISTANCE and item is not selected:
                    self.connect(selected, item)

    @staticmethod
    def distance(p1, p2):
        """
        Compute the distance between two points.

        Keyword arguments:
        qp1 -- first point, QPoint
        qp2 -- second point, QPoint
        """
        dx = pow(p1.x() - p2.x(), 2)
        dy = pow(p1.y() - p2.y(), 2)
        return sqrt(dx + dy)


