#!/usr/bin/env python3
#-*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from StartWindow import StartWindow



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = StartWindow()
    screen.show()

    sys.exit(app.exec_())