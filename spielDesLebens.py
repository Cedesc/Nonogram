import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF, QPixmap
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer
import numpy as np


FENSTERBREITE = 100
FENSTERHOEHE = 100

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW, self.wH = FENSTERBREITE, FENSTERHOEHE
        self.img = QImage(self.wW, self.wH, QImage.Format_RGBA8888)
        self.img.fill(Qt.white)
        self.img.setPixelColor(20, 50, Qt.black)
        self.field = QLabel()
        self.field.setPixmap(QPixmap.fromImage(self.img))

        self.next = QPushButton("Next")
        self.next.clicked.connect(self.machWas)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.field)
        self.layout.addWidget(self.next)

        self.setLayout(self.layout)

        matrix = np.zeros(shape = (20,20), dtype=np.int8)
        # print(matrix)





        width = 100
        height = 100
        data = np.random.randint(0, 256, size=(self.wW, self.wH, 3)).astype(np.uint8)
        data = np.random.randint(0, 256, size=(self.wW, self.wH, 3)).astype(np.uint8)

        data = np.array(data)

        data = np.zeros((self.wW, self.wH, 3)).astype(np.uint8)

        data[1][2] = WHITE

        print(data[0])


        img = QImage(self.wW, self.wH, QImage.Format_RGB32)
        for x in range(self.wW):
            for y in range(self.wH):
                img.setPixel(x, y, QColor(*data[x][y]).rgb())

        pix = QPixmap.fromImage(img)
        pix = QPixmap.scaledToWidth(pix, 700)


        self.field.setPixmap(pix)




        self.show()


    def machWas(self):
        print("ggg")
        self.img.setPixelColor(25, 50, Qt.black)
        self.field.setPixmap(QPixmap.fromImage(self.img))








app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())

