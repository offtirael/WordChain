from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import json

from Connectors import *


class MetaElement(QGraphicsPolygonItem):

    def __init__(self, leftConnectorType, rightConnectorType, elementName, color=QColor(255, 255, 255)):
        super(MetaElement, self).__init__()

        assert isinstance(leftConnectorType, int)
        assert isinstance(rightConnectorType, int)
        assert isinstance(elementName, str)

        self.leftConnectorType = leftConnectorType
        self.rightConnectorType = rightConnectorType

        self.leftBottom = QPoint(-50, 25)
        self.leftTop = QPoint(-50, -25)

        self.rightBottom = QPoint(50, 25)
        self.rightTop = QPoint(50, -25)

        if leftConnectorType not in Connector.connectorTypes:
            self.leftConnector = LeftConnector(1, self.leftBottom, self.leftTop)
        else:
            self.leftConnector = LeftConnector(leftConnectorType, self.leftBottom, self.leftTop)

        if rightConnectorType not in Connector.connectorTypes:
            self.rightConnector = RightConnector(1, self.rightBottom, self.rightTop)
        else:
            self.rightConnector = RightConnector(rightConnectorType, self.rightBottom, self.rightTop)

        self.elementName = elementName

        self.formPath = QPainterPath()
        self.setDrawPath()

        self.pen = QPen()
        self.pen.setWidth(2)
        self.color = color

        self.itemPolygon = self.formPath.toFillPolygon(QTransform())
        self.setPolygon(self.itemPolygon)

        self.boundRect = self.formPath.boundingRect()

        self.outConnections = []
        self.inConnections = []
        self.words = []
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def addWord(self, word):
        self.words.append(word)

    def addWords(self, wordList):
        if isinstance(wordList, list):
            self.words = wordList

    def removeWord(self, idx):
        if idx < len(self.words):
            self.words.remove(self.words[idx])

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.setBrush(self.color)
        painter.drawPath(self.formPath)
        painter.drawText(self.boundRect, Qt.AlignCenter, self.elementName)

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)

    def boundingRect(self):
        return self.formPath.boundingRect()

    def changeLeftConnector(self, connType):
        assert isinstance(connType, int)
        if connType in Connector.connectorTypes:
            self.leftConnector = LeftConnector(connType, self.leftBottom, self.leftTop)
            self.leftConnectorType = connType
            self.setDrawPath()

            self.boundRect = self.formPath.boundingRect()

    def changeRightConnector(self, connType):
        assert isinstance(connType, int)
        if connType in Connector.connectorTypes:
            self.rightConnector = RightConnector(connType, self.rightBottom, self.rightTop)
            self.rightConnectorType = connType
            self.setDrawPath()

            self.boundRect = self.formPath.boundingRect()

    def changeColor(self, color):
        assert isinstance(color, QColor)
        self.color = color

    def setDrawPath(self):
        self.formPath = QPainterPath()
        self.formPath.moveTo(self.leftTop)

        self.formPath.lineTo(self.rightTop)
        self.formPath.connectPath(self.rightConnector.connectorPath)

        self.formPath.lineTo(self.leftBottom)
        self.formPath.connectPath(self.leftConnector.connectorPath)

    def getLeftCenter(self):
        point = self.pos()
        delta = 0
        if self.leftConnectorType == 1:
            delta = 0
        elif self.leftConnectorType == 2:
            delta = -20
        elif self.leftConnectorType == 3:
            delta = 20
        point.setX(point.x() - 50 + delta)
        return point

    def getRightCenter(self):
        point = self.pos()
        delta = 0
        if self.rightConnectorType == 1:
            delta = 0
        elif self.rightConnectorType == 2:
            delta = 20
        elif self.rightConnectorType == 3:
            delta = -20
        point.setX(point.x() + 50 + delta)
        return point

    def image(self):
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 8))
        painter.setBrush(self.color)
        painter.translate(125, 125)
        painter.drawPath(self.formPath)
        return pixmap

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for conn in self.connections:
                conn.updatePosition()

        return value

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene().clearSelection()
            self.setSelected(True)
            super(MetaElement, self).mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            self.scene().clearSelection()
            self.setSelected(True)


class ElementSet(object):
    def __init__(self):
        super(ElementSet, self).__init__()
        self.elementList = []

    def addElement(self, element):
        assert isinstance(element, MetaElement)
        self.elementList.append(element)

    def removeElement(self, index):
        assert isinstance(index, int)
        if index < len(self.elementList):
            self.elementList.pop(index)

    def toJSON(self):
        lst = []
        for elem in self.elementList:
            obj = {'elementName': elem.elementName,
                   'leftConnectorType': elem.leftConnectorType,
                   'rightConnectorType': elem.rightConnectorType,
                   'color': elem.color.name(),
                   'words': elem.words}
            lst.append(obj)
        return lst

    def toString(self):
        return json.dumps(self.toJSON(), sort_keys=True, indent=4, separators=(',', ': '))

    def toBytes(self):
        return bytes(self.toString(), encoding='utf8')

    def fromString(self, string):
        assert isinstance(string, str)

        jsObj = json.loads(string, 'utf8')
        self.fromJSON(jsObj)

    def fromJSON(self, data):
        assert isinstance(data, list)

        self.elementList.clear()

        for obj in data:
            elementName = obj.get('elementName', None)
            leftConnectorType = obj.get('leftConnectorType', None)
            rightConnectorType = obj.get('rightConnectorType', None)
            color = obj.get('color', None)
            wordList = obj.get('words', [])

            if elementName is not None and leftConnectorType is not None and rightConnectorType is not None and\
                            color is not None:
                newElem = MetaElement(leftConnectorType, rightConnectorType, elementName, QColor(color))
                newElem.addWords(wordList)
                self.addElement(newElem)


class Element(QGraphicsPolygonItem):
    MULT = 15

    def __init__(self, leftConnectorType=1, rightConnectorType=1, text=1, color=QColor(255, 255, 255), lst=None):
        super(Element, self).__init__()

        if not lst:
            self.leftConnectorType = leftConnectorType
            self.rightConnectorType = rightConnectorType
            self.text = text
            self.color = color
            self.compound = False
            self.parts = [self, ]
            self.pen = QPen()

            self.pen.setWidth(2)

            self.leftBottom = QPoint(-50, 25)
            self.leftTop = QPoint(-50, -25)

            self.width = Element.MULT * len(self.text)
            if self.width < 100:
                self.width = 100

            self.rightBottom = QPoint(-50 + self.width, 25)
            self.rightTop = QPoint(-50 + self.width, -25)

            if leftConnectorType not in Connector.connectorTypes:
                self.leftConnector = LeftConnector(1, self.leftBottom, self.leftTop)
            else:
                self.leftConnector = LeftConnector(leftConnectorType, self.leftBottom, self.leftTop)

            if rightConnectorType not in Connector.connectorTypes:
                self.rightConnector = RightConnector(1, self.rightBottom, self.rightTop)
            else:
                self.rightConnector = RightConnector(rightConnectorType, self.rightBottom, self.rightTop)
        else:
            assert isinstance(lst, list)

            self.compound = True
            self.parts = lst
            self.text = ' '.join([w.text for w in lst])
            self.width = sum([w.width for w in lst]) / 1.5

            self.leftConnectorType = self.parts[0].leftConnectorType
            self.rightConnectorType = self.parts[len(self.parts) - 1].rightConnectorType

            self.pen = QPen()
            self.pen.setWidth(2)

            self.color = lst[0].color

            self.leftBottom = QPoint(-50, 25)
            self.leftTop = QPoint(-50, -25)

            self.rightBottom = QPoint(-50 + self.width, 25)
            self.rightTop = QPoint(-50 + self.width, -25)

            self.leftConnector = LeftConnector(self.leftConnectorType, self.leftBottom, self.leftTop)
            self.rightConnector = RightConnector(self.rightConnectorType, self.rightBottom, self.rightTop)

        self.formPath = None
        self.setDrawPath()

        self.itemPolygon = self.formPath.toFillPolygon(QTransform())
        self.setPolygon(self.itemPolygon)

        self.boundRect = self.formPath.boundingRect()

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def boundingRect(self):
        return self.formPath.boundingRect()

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.setBrush(self.color)
        painter.drawPath(self.formPath)
        painter.drawText(self.boundRect, Qt.AlignCenter, self.text)

    def setMetaName(self, metaName):
        self.metaName = metaName

    def setDrawPath(self):
        self.formPath = QPainterPath()
        self.formPath.moveTo(self.leftTop)

        self.formPath.lineTo(self.rightTop)
        self.formPath.connectPath(self.rightConnector.connectorPath)

        self.formPath.lineTo(self.leftBottom)
        self.formPath.connectPath(self.leftConnector.connectorPath)
        # if not self.compound:
        #     self.formPath = QPainterPath()
        #     self.formPath.moveTo(self.leftTop)
        #
        #     self.formPath.lineTo(self.rightTop)
        #     self.formPath.connectPath(self.rightConnector.connectorPath)
        #
        #     self.formPath.lineTo(self.leftBottom)
        #     self.formPath.connectPath(self.leftConnector.connectorPath)
        # else:
        #     self.formPath = QPainterPath()
        #     first = self.parts[0]
        #     last = self.parts[len(self.parts) - 1]
        #
        #     self.formPath.moveTo(first.leftTop)
        #
        #     self.formPath.lineTo(last.rightTop)
        #     self.formPath.connectPath(last.rightConnector.connectorPath)
        #
        #     self.formPath.lineTo(last.leftBottom)
        #     self.formPath.connectPath(first.leftConnector.connectorPath)

    def getLeftCenter(self):
        point = self.pos()
        delta = 0
        if self.leftConnectorType == 1:
            delta = 0
        elif self.leftConnectorType == 2:
            delta = -20
        elif self.leftConnectorType == 3:
            delta = 20
        point.setX(point.x() - (self.width / 2) + delta)
        return point

    def getRightCenter(self):
        point = self.pos()
        delta = 0
        if self.rightConnectorType == 1:
            delta = 0
        elif self.rightConnectorType == 2:
            delta = 20
        elif self.rightConnectorType == 3:
            delta = -20
        point.setX(point.x() + (self.width / 2) + delta)
        return point

    def attach(self, elem):
        self.compound = True

        self.parts.append(elem)
