from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class PracticeWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PracticeWindow, self).__init__(parent)

        # Frames
        self.gBox1 = QFrame()
        self.gBox1.setMaximumSize(QSize(250, 600))

        self.scene = QGraphicsScene(-200, -200, 400, 400)

        # Graphics view
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setMinimumSize(QSize(800, 600))

        self.centralWidget = QWidget()
        self.centralLayout = QHBoxLayout()
        self.centralLayout.addWidget(self.gBox1)
        self.centralLayout.addWidget(self.graphicsView)
        self.centralWidget.setLayout(self.centralLayout)

        self.setWindowTitle("WordChain : Practice")

        self.setCentralWidget(self.centralWidget)

        self.resize(1200, 600)