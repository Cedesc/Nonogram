import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer


""" Beispiel-Level ist 5x5 """
beispiellevel = [ [0,0,0,1,0],
                  [0,0,1,1,1],
                  [1,1,1,0,1],
                  [1,1,0,0,1],
                  [0,0,1,0,0]]

def levelAnzeigen(level):
    for zeile in level:
        print(zeile)
    return

# levelAnzeigen(beispiellevel)

class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW = 800       # wW = windowWidth
        self.wH = 800       # wH = windowHeight
        self.setGeometry(500, 50, self.wW, self.wH)
        self.setWindowTitle("Picross")
        self.level = beispiellevel

        self.nachUnten = 50     # Gesamtverschiebung nach unten
        self.nachRechts = 50    # Gesamtverschiebung nach rechts
        self.laengeVertikal = len(self.level)
        self.laengeHorizontal = len(self.level[0])

        self.laengeVertikal = 15
        self.laengeHorizontal = 15

        self.keyPressEvent = self.fn

        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)

        # Hintergrund
        painter.fillRect(0, 0, self.wW, self.wH, QColor(205, 205, 205))

        # "Netz" aufbauen
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        # vertikal
        for verschiebung in range(self.laengeVertikal + 1):
            """if verschiebung == 0 or verschiebung == self.laengeVertikal:
                painter.setPen(QPen(QColor(200, 0, 0), 3, Qt.SolidLine))
                painter.drawLine((self.nachRechts + 50) + 60 * verschiebung, self.nachUnten,
                                 (self.nachRechts + 50) + 60 * verschiebung,
                                 self.nachUnten + (self.laengeHorizontal + 1) * 60 + 40)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
                painter.drawLine((self.nachRechts + 50) + 60 * verschiebung, self.nachUnten,
                                 (self.nachRechts + 50) + 60 * verschiebung, self.nachUnten + (self.laengeHorizontal + 1) * 60 + 40)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))"""
            #else:
            painter.drawLine((self.nachRechts + self.wW // 16) + int(self.wW // 13 * 10 / 15) * verschiebung, self.nachUnten,
                                   (self.nachRechts + self.wW // 16) + int(self.wW // 13 * 10 / 15) * verschiebung, self.nachUnten + (self.laengeHorizontal + 1) * int(self.wH // 13 * 10 / 15) + (self.wH // 20))
        # horizontal
        for verschiebung in range(self.laengeHorizontal + 1):
            """if verschiebung == 0 or verschiebung == self.laengeHorizontal:
                painter.setPen(QPen(QColor(200, 0, 0), 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts, (self.nachUnten + 50) + 60 * verschiebung,
                                 self.nachRechts + (self.laengeVertikal + 1) * 60 + 40,
                                 (self.nachUnten + 50) + 60 * verschiebung)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts, (self.nachUnten + 50) + 60 * verschiebung,
                                 self.nachRechts + (self.laengeVertikal + 1) * 60 + 40, (self.nachUnten + 50) + 60 * verschiebung)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))"""
            #else:
            painter.drawLine(self.nachRechts, (self.nachUnten + (self.wH // 16)) + int(self.wH // 13 * 10 / 15) * verschiebung,
                                   self.nachRechts + (self.laengeVertikal + 1) * int(self.wW // 13 * 10 / 15) + (self.wW // 20), (self.nachUnten + (self.wH // 16)) + int(self.wH // 13 * 10 / 15) * verschiebung)




    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")

        """ R druecken um Level neuzustarten """
        if e.key() == Qt.Key_R:
            self.update()

        if e.key() == Qt.Key_Escape:
            self.close()


    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        print("               ", pos.x(), pos.y())



    def levelReset(self):
        pass




app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
