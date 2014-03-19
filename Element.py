from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MetaElement(QGraphicsItem):
    def __init__(self, leftConnector, rightConnector, elementName):
        super(MetaElement, self).__init__()

        self.leftConnector = leftConnector
        self.rightConnector = rightConnector
        self.elementName = elementName