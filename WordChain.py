#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

import mainwindow

app = QtWidgets.QApplication(sys.argv)
mainWindow = QtWidgets.QMainWindow()
scene = QtWidgets.QGraphicsScene()
ui = mainwindow.Ui_MainWindow()

sceneMargin = 1


@QtCore.pyqtSlot()
def onSceneRectChanged():
    global ui
    r = ui.graphicsView.scene().sceneRect()
    r.moveLeft(r.left() - sceneMargin)
    r.moveTop(r.top() - sceneMargin)
    r.setWidth(r.width() + 2 * sceneMargin)
    r.setHeight(r.height() + 2 * sceneMargin)
    ui.graphicsView.setSceneRect(r)



def main():
    ui.setupUi(mainWindow)
    ui.graphicsView.setScene(scene)

    categoriesList = [
        "Adjective phrase", "Adverb phrase", "Prepositional phrase", "Noun phrase",
        "Verb phrase"
    ]

    i = 0
    for categoryName in categoriesList:
        pushButton = QtWidgets.QPushButton(ui.widget)
        pushButton.setObjectName("pushButton" + str(i))
        ui.verticalLayout.addWidget(pushButton)
        pushButton.setText(categoryName)
        i += 1

    ui.graphicsView.show()
    mainWindow.show()

    scene.sceneRectChanged.connect(onSceneRectChanged)
    onSceneRectChanged()

    app.exec_()


if __name__ == '__main__':
    main()