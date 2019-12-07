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

        self.nachUnten = self.wH // 8     # Gesamtverschiebung nach unten
        self.nachRechts = self.wW // 8    # Gesamtverschiebung nach rechts
        self.reihen = len(self.level)
        self.spalten = len(self.level[0])

        self.reihen = 15
        self.spalten = 15

        self.keyPressEvent = self.fn

        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)

        ''' Hintergrund '''
        painter.fillRect(0, 0, self.wW, self.wH, QColor(205, 205, 205))

        ''' Netz aufbauen '''
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))

        # vertikale Linien
        y = (self.wW - 2 * self.nachRechts) // self.reihen
        for verschiebung in range(self.reihen + 1):
            if verschiebung == 0 or verschiebung == self.reihen:
                painter.setPen(QPen(QColor(0, 0, 0), 4, Qt.SolidLine))
                painter.drawLine(self.nachRechts + y * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + y * verschiebung,
                                 self.wH - self.nachUnten // 2)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts + y * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + y * verschiebung,
                                 self.wH - self.nachUnten // 2)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            else:
                painter.drawLine(self.nachRechts + y * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + y * verschiebung,
                                 self.wH - self.nachUnten // 2)

        # horizontale Linien
        x = (self.wH - 2 * self.nachUnten) // self.spalten
        for verschiebung in range(self.spalten + 1):
            if verschiebung == 0 or verschiebung == self.spalten:
                painter.setPen(QPen(QColor(0, 0, 0), 4, Qt.SolidLine))
                painter.drawLine(self.nachRechts // 2,
                                 self.nachUnten + x * verschiebung,
                                 self.wW - self.nachRechts // 2,
                                 self.nachUnten + x * verschiebung)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts // 2,
                                 self.nachUnten + x * verschiebung,
                                 self.wW - self.nachRechts // 2,
                                 self.nachUnten + x * verschiebung)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            else:
                painter.drawLine(self.nachRechts // 2,
                                self.nachUnten + x * verschiebung,
                                self.wW - self.nachRechts // 2,
                                self.nachUnten + x * verschiebung)



    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")

        # R druecken um Level neuzustarten
        if e.key() == Qt.Key_R:
            self.update()

        if e.key() == Qt.Key_Escape:
            self.close()


    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        print("               ", pos.x(), pos.y())



    def levelReset(self):
        pass

    def hinweiseBerechnen(self):
        pass




app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
