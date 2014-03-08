#!/usr/bin/env python3
#-*- coding: utf-8 -*-
 
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

import mainwindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    scene = QtWidgets.QGraphicsScene()
    ui = mainwindow.Ui_MainWindow()
    ui.setupUi(mainWindow)
    ui.graphicsView.setScene(scene)

    ui.graphicsView.show()
    mainWindow.show()

    app.exec_()

if __name__ == '__main__':
    main()