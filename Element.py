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
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.setBrush(self.color)
        painter.drawPath(self.formPath)
        painter.drawText(self.boundRect, Qt.AlignCenter, self.elementName)
        #if self.isSelected():
        #    painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
        #    painter.drawRect(self.boundingRect())

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)

    def boundingRect(self):
        return self.boundRect

    def changeLeftConnector(self, connType):
        assert isinstance(connType, int)
        if connType in Connector.connectorTypes:
            self.leftConnector = LeftConnector(connType, self.leftBottom, self.leftTop)
            self.leftConnectorType = connType
            self.setDrawPath()

    def changeRightConnector(self, connType):
        assert isinstance(connType, int)
        if connType in Connector.connectorTypes:
            self.rightConnector = RightConnector(connType, self.rightBottom, self.rightTop)
            self.rightConnectorType = connType
            self.setDrawPath()

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
            obj = {'elementName': elem.elementName, 'leftConnectorType': elem.leftConnectorType,
                   'rightConnectorType': elem.rightConnectorType, 'color': elem.color.name()}
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

            if elementName is not None and leftConnectorType is not None and rightConnectorType is not None and\
                            color is not None:
                newElem = MetaElement(leftConnectorType, rightConnectorType, elementName, QColor(color))
                self.addElement(newElem)
