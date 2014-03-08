#!/usr/bin/env python3
#-*- coding: utf-8 -*-
 
import sys
from PyQt5 import QtWidgets, QtGui, QtCore


class DemoWind(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(300, 300, 200, 200)
        self.setWindowTitle('Demo window')
        quit = QtGui.QPushButton('Close', self)
        quit.setGeometry(10, 10, 70, 40)
        self.connect(quit, QtCore.SIGNAL('clicked()'), QtGui.qApp,
                     QtCore.slot('quit()'))


def main():
    app = QtGui.QGuiApplication(sys.argv)
    dw = DemoWind()
    dw.show()
    sys.exit(app.exec_())

 
if __name__ == '__main__':
    main()