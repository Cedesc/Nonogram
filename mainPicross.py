import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer



""" 
Erklaerung: 
    - 3 geschachtelte Listen mit Tiefe 2, 1. mit der Loesung, 2. mit dem momentanen Stand, 3. mit Koordinaten
    - in "level" steht "0" fuer "leer", "1" fuer "richtig", "-1" fuer "falsch", "2" fuer "blockiert"
"""

""" Beispiel-Level ist 6x5 """
beispiellevel = [ [0,1,1,1,1,1,0],
                  [0,1,0,1,0,1,0],
                  [0,1,0,1,0,1,0],
                  [0,1,1,1,1,1,0],
                  [0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0],
                  [1,0,0,0,0,0,1],
                  [1,1,0,1,0,1,1],
                  [0,1,1,0,1,1,0]]

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
        self.loesung = beispiellevel

        self.nachUnten = self.wH // 8     # Gesamtverschiebung nach unten
        self.nachRechts = self.wW // 8    # Gesamtverschiebung nach rechts
        self.spalten = len(self.loesung)
        self.reihen = len(self.loesung[0])

        self.level = self.leeresLevelErstellen()
        self.levelKoordinaten = self.koordinatenBestimmen()


        self.keyPressEvent = self.fn

        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)

        ''' Hintergrund '''
        painter.fillRect(0, 0, self.wW, self.wH, QColor(205, 205, 205))

        ''' Netz aufbauen '''
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))

        # vertikale Linien
        breite = (self.wW - 2 * self.nachRechts) // self.reihen
        for verschiebung in range(self.reihen + 1):
            if verschiebung == 0 or verschiebung == self.reihen:
                painter.setPen(QPen(QColor(0, 0, 0), 4, Qt.SolidLine))
                painter.drawLine(self.nachRechts + breite * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + breite * verschiebung,
                                 self.wH - self.nachUnten // 2)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts + breite * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + breite * verschiebung,
                                 self.wH - self.nachUnten // 2)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            else:
                painter.drawLine(self.nachRechts + breite * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + breite * verschiebung,
                                 self.wH - self.nachUnten // 2)

        # horizontale Linien
        hoehe = (self.wH - 2 * self.nachUnten) // self.spalten
        for verschiebung in range(self.spalten + 1):
            if verschiebung == 0 or verschiebung == self.spalten:
                painter.setPen(QPen(QColor(0, 0, 0), 4, Qt.SolidLine))
                painter.drawLine(self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung,
                                 self.wW - self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung,
                                 self.wW - self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung)
                painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            else:
                painter.drawLine(self.nachRechts // 2,
                                self.nachUnten + hoehe * verschiebung,
                                self.wW - self.nachRechts // 2,
                                self.nachUnten + hoehe * verschiebung)


        """ Rechtecke einzeichnen """
        painter.setPen(QPen(QColor(200, 0, 0), 3, Qt.SolidLine))
        for i in range(self.spalten):

            for j in range(self.reihen):

                if self.level[i][j] == 1:
                    painter.fillRect(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][0][1],
                                     self.levelKoordinaten[i][j][1][0] - self.levelKoordinaten[i][j][0][0], # hoehe
                                     self.levelKoordinaten[i][j][1][1] - self.levelKoordinaten[i][j][0][1], # weite
                                     QColor(0,0,0))

                if self.level[i][j] == -1:
                    painter.drawLine(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][0][1],
                                     self.levelKoordinaten[i][j][1][0],
                                     self.levelKoordinaten[i][j][1][1])
                    painter.drawLine(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][1][1],
                                     self.levelKoordinaten[i][j][1][0],
                                     self.levelKoordinaten[i][j][0][1])


    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")

        if e.key() == Qt.Key_Q:
            print("gedrueckt")

        if e.key() == Qt.Key_Escape:
            self.close()


        """ Ideen: neustarten, feld blockieren """


    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        print("               ", pos.x(), pos.y())

        for i in range(self.spalten):

            for j in range(self.reihen):

                if ( self.levelKoordinaten[i][j][0][0] < pos.x() < self.levelKoordinaten[i][j][1][0] ) \
                and ( self.levelKoordinaten[i][j][0][1] < pos.y() < self.levelKoordinaten[i][j][1][1] ) \
                and self.level[i][j] == 0:
                    if self.loesung[i][j] == 0:
                        print("falsch")
                        self.level[i][j] = -1
                    elif self.loesung[i][j] == 1:
                        print("richtig")
                        self.level[i][j] = 1
                    self.update()




    def leeresLevelErstellen(self):

        result = []
        for i in range(self.spalten):
            reihe = []
            for j in range(self.reihen):
                reihe.append(0)
            result.append(reihe)
        return result

    def koordinatenBestimmen(self):

        # Idee: Fuer jeden Eintrag jeweils linke obere und rechte untere Koordinate für ein Rechteck bestimmen.
        #       Diese als Tupel von zwei Tupeln (2 Punkte, also 4 Koordinaten) in geschachtelter Liste so platzieren,
        #       dass sie die gleichen Indizes haben, wie die zugehoerigen Werte
        result = []

        # reine Vorberechnung
        breite = (self.wW - 2 * self.nachRechts) // self.reihen
        hoehe = (self.wH - 2 * self.nachUnten) // self.spalten

        for i in range(self.spalten):
            reihe = []
            for j in range(self.reihen):

                punktLinksOben = (self.nachRechts + breite * j, self.nachUnten + hoehe * i)
                punktRechtsUnten = (self.nachRechts + breite * (j+1), self.nachUnten + hoehe * (i+1))

                reihe.append( ( punktLinksOben , punktRechtsUnten ) )
            result.append(reihe)
        return result


    def levelReset(self):
        pass

    def eckkoordinatenBerechnen(self):
        pass

    def hinweiseBerechnen(self):
        pass

    def loesungAnzeigen(self):
        self.level = self.loesung
        self.update()




app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
