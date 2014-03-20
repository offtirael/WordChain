from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Connector(object):
    connectorTypes = [1, 2, 3, 4]

    def __init__(self):
        super(Connector, self).__init__()


class LeftConnector(Connector):
    def __init__(self, type, bottom, top):
        super(LeftConnector, self).__init__()

        self.connectorPath = QPainterPath()

        assert isinstance(bottom, QPoint)
        assert isinstance(top, QPoint)

        if type in Connector.connectorTypes:
            if type == 1:
                self.connectorPath.moveTo(bottom)
                self.connectorPath.lineTo(top)
            elif type == 2:
                self.connectorPath.moveTo(bottom)
                newPoint = QPoint(bottom.x() - 20, abs(bottom.y() + top.y())/2)
                self.connectorPath.lineTo(newPoint)
                self.connectorPath.lineTo(top)
            elif type == 3:
                self.connectorPath.moveTo(bottom)
                newPoint = QPoint(bottom.x() + 20, abs(bottom.y() + top.y())/2)
                self.connectorPath.lineTo(newPoint)
                self.connectorPath.lineTo(top)

class RightConnector(Connector):
    def __init__(self, type, bottom, top):
        super(RightConnector, self).__init__()

        self.connectorPath = QPainterPath()

        assert isinstance(bottom, QPoint)
        assert isinstance(top, QPoint)

        if type in Connector.connectorTypes:
            if type == 1:
                self.connectorPath.moveTo(top)
                self.connectorPath.lineTo(bottom)
            elif type == 2:
                self.connectorPath.moveTo(top)
                newPoint = QPoint(bottom.x() + 20, abs(bottom.y() + top.y())/2)
                self.connectorPath.lineTo(newPoint)
                self.connectorPath.lineTo(bottom)
            elif type == 3:
                self.connectorPath.moveTo(top)
                newPoint = QPoint(bottom.x() - 20, abs(bottom.y() + top.y())/2)
                self.connectorPath.lineTo(newPoint)
                self.connectorPath.lineTo(bottom)