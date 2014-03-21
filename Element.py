from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import json

from Connectors import *


class MetaElement(QGraphicsItem):

    def __init__(self, leftConnectorType, rightConnectorType, elementName):
        super(MetaElement, self).__init__()

        assert isinstance(leftConnectorType, int)
        assert isinstance(rightConnectorType, int)
        assert isinstance(elementName, str)

        self.leftConnectorType = leftConnectorType
        self.rightConnectorType = rightConnectorType

        self.leftBottom = QPoint(-100, 50)
        self.leftTop = QPoint(-100, -50)

        self.rightBottom = QPoint(100, 50)
        self.rightTop = QPoint(100, -50)

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

        self.boundRect = self.formPath.boundingRect()

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.drawPath(self.formPath)
        painter.drawText(self.boundRect, Qt.AlignCenter, self.elementName)

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

    def setDrawPath(self):
        self.formPath = QPainterPath()
        self.formPath.moveTo(self.leftTop)

        self.formPath.lineTo(self.rightTop)
        self.formPath.addPath(self.rightConnector.connectorPath)

        self.formPath.lineTo(self.leftBottom)
        self.formPath.addPath(self.leftConnector.connectorPath)


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
                   'rightConnectorType': elem.rightConnectorType}
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

            if elementName is not None and leftConnectorType is not None and rightConnectorType is not None:
                newElem = MetaElement(leftConnectorType, rightConnectorType, elementName)
                self.addElement(newElem)
