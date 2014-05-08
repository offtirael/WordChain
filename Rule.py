import json
from PyQt5.QtCore import QRectF, QSizeF, QLineF, Qt
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsItem
from Element import MetaElement, ElementSet


class Connection(QGraphicsLineItem):
    ###########################################################################
    def __init__(self, start, end):
        super(Connection, self).__init__()

        self.startElement = start
        self.endElement = end
        self.color = QColor(0, 0, 0)
        self.setPen(QPen(self.color, 4, Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    ###########################################################################
    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1,
                      QSizeF(p2.x() - p1.x(),
                             p2.y() - p1.y())).normalized().adjusted(-extra,
                                                                     -extra,
                                                                     extra,
                                                                     extra)

    ###########################################################################
    def paint(self, painter, option, widget=None):
        self.setLine(QLineF(self.startElement.getRightCenter(),
                            self.endElement.getLeftCenter()))
        painter.setPen(self.pen())
        painter.drawLine(self.line())

    ###########################################################################
    def updatePosition(self):
        line = QLineF(self.startElement.getRightCenter(), self.endElement.getLeftCenter())
        self.setLine(line)

    ###########################################################################
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene().clearSelection()
            self.setSelected(True)
            super(Connection, self).mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            self.scene().clearSelection()
            self.setSelected(True)

class Rule(object):
    def __init__(self):
        self.name = None
        self.elements = []
        self.connections = []

    def setName(self, name):
        self.name = name

    def setElementsFileName(self, elementsFileName):
        self.elementsFileName = elementsFileName

    def fromString(self, string):
        assert isinstance(string, str)

        jsObj = json.loads(string, 'utf8')
        self.fromJSON(jsObj)

    def fromJSON(self, data):
        self.elements = data.get('elements', None)
        self.connections = data.get('connections', None)
        self.name = data.get('name', None)

    def fromElementList(self, lst):
        self.elements = []
        self.connections = []
        for elem in lst:
            if isinstance(elem, MetaElement):
                self.elements.append({
                    'elementName': elem.elementName,
                    'x': elem.pos().x(),
                    'y': elem.pos().y()
                })
        for elem in lst:
            if isinstance(elem, Connection):
                self.connections.append({
                    'p1': self.elements.index({'elementName': elem.startElement.elementName,
                                               'x': elem.startElement.pos().x(),
                                               'y': elem.startElement.pos().y()}),
                    'p2': self.elements.index({'elementName': elem.endElement.elementName,
                                               'x': elem.endElement.pos().x(),
                                               'y': elem.endElement.pos().y()})
                })

    def toJSON(self):
        jsn = {'name': self.name,
               'elements': self.elements,
               'connections': self.connections}
        return jsn

    def toString(self):
        return json.dumps(self.toJSON(),
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '))

    def toBytes(self):
        return bytes(self.toString(), encoding='utf8')

    def check(self):
        return False


class RuleSet(object):
    def __init__(self):
        super(RuleSet, self).__init__()

        self.ruleList = []
        self.elementsFileName = None

    def addRule(self, rule):
        self.ruleList.append(rule)

    def deleteRule(self, idx):
        if idx < len(self.ruleList):
            self.ruleList.remove(self.ruleList[idx])

    def getRule(self, idx):
        if idx < len(self.ruleList):
            return self.ruleList[idx]
        else:
            return None

    def setElementsFileName(self, name):
        assert isinstance(name, str)
        self.elementsFileName = name

    def clear(self):
        self.ruleList = []

    def toJSON(self):
        lst = []
        for rule in self.ruleList:
            lst.append(rule.toJSON())
        jsn = {
            'elementsFile': self.elementsFileName,
            'rules': lst
        }

        return jsn

    def toString(self):
        return json.dumps(self.toJSON(),
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '))

    def toBytes(self):
        return bytes(self.toString(), encoding='utf8')
