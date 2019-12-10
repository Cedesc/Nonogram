import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer



""" 
Erklaerung: 
    - 3 geschachtelte Listen mit Tiefe 2, 1. mit der Loesung, 2. mit dem momentanen Stand, 3. mit Koordinaten
"""

""" Beispiel-Level ist 6x5 """
beispiellevel = [[0,1,0,1,0],
                 [0,0,0,0,0],
                 [0,1,1,0,1],
                 [0,0,0,0,0],
                 [1,0,0,1,1],
                 [1,0,0,0,0]]

beispiellevel2 = [[0,1,1,1,1,1,0],
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

beispiellevel3 = [[0,1,1,1,1,1,0,
                  0,1,0,1,0,1,0],
                  [0,1,0,1,0,1,0,
                  0,1,1,1,1,1,0],
                  [0,1,0,0,0,1,0,
                  0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0,
                  0,1,0,0,0,1,0],
                  [0,1,0,0,0,1,0,
                  0,1,0,0,0,1,0],
                  [1,0,0,0,0,0,1,
                  1,1,0,1,0,1,1]]


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
        self.loesung = beispiellevel2

        self.nachUnten = self.wH // 8     # Gesamtverschiebung nach unten
        self.nachRechts = self.wW // 8    # Gesamtverschiebung nach rechts
        self.spalten = len(self.loesung)
        self.reihen = len(self.loesung[0])

        self.level = self.leeresLevelErstellen()
        self.levelKoordinaten = self.koordinatenBestimmen()

        self.hinweiseSpalten, self.hinweiseReihen = self.hinweiseErstellen()

        self.blockenAktiv = False


        #self.loesungAnzeigen()

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
                    painter.setPen(QPen(QColor(200, 0, 0), 3, Qt.SolidLine))
                    painter.drawLine(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][0][1],
                                     self.levelKoordinaten[i][j][1][0],
                                     self.levelKoordinaten[i][j][1][1])
                    painter.drawLine(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][1][1],
                                     self.levelKoordinaten[i][j][1][0],
                                     self.levelKoordinaten[i][j][0][1])

                if self.level[i][j] == 2:
                    painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))
                    painter.drawLine(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][0][1],
                                     self.levelKoordinaten[i][j][1][0],
                                     self.levelKoordinaten[i][j][1][1])
                    painter.drawLine(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][1][1],
                                     self.levelKoordinaten[i][j][1][0],
                                     self.levelKoordinaten[i][j][0][1])


        """ Hinweise einbringen """
        # Idee: an den gezeichneten Linien orientieren
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        schriftgroesse = hoehe // 6
        painter.setFont(QFont("Arial", schriftgroesse))

        # Reihen
        # Schleife durchlaeuft self.spalten, da es an der Anzahl von in einer Spalte liegenden Feldern abhaengt,
        # wie viele Reihen es gibt
        for reihe in range(self.spalten):
            if self.hinweiseReihen[reihe][1]:       # pruefen ob visible
                painter.drawText(0, self.nachUnten + hoehe * (reihe+0.5) - schriftgroesse // 2 ,
                                 self.nachRechts, hoehe, Qt.AlignHCenter , self.hinweiseReihen[reihe][0])
            else:
                painter.setPen(QColor(180,180,180))
                painter.drawText(0, self.nachUnten + hoehe * (reihe + 0.5) - schriftgroesse // 2,
                                 self.nachRechts, hoehe, Qt.AlignHCenter, self.hinweiseReihen[reihe][0])
                painter.setPen(QColor(0, 0, 0))


        # Spalten
        # Schleife durchlaeuft self.reihen, da es an der Anzahl von in einer Reihe liegenden Feldern abhaengt,
        # wie viele Spalten es gibt
        for spalte in range(self.reihen):
            if self.hinweiseSpalten[spalte][1]:     # pruefen ob visible
                painter.drawText(self.nachRechts + breite * (spalte+0.5) - schriftgroesse // 2,
                                 self.nachUnten - schriftgroesse * 7,
                                 schriftgroesse * 3, schriftgroesse * 7, Qt.AlignBottom, self.hinweiseSpalten[spalte][0])
            else:
                painter.setPen(QColor(180,180,180))
                painter.drawText(self.nachRechts + breite * (spalte + 0.5) - schriftgroesse // 2,
                                 self.nachUnten - schriftgroesse * 7,
                                 schriftgroesse * 3, schriftgroesse * 7, Qt.AlignBottom, self.hinweiseSpalten[spalte][0])
                painter.setPen(QColor(0,0,0))



    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")

        # R druecken um Level neuzustarten
        if e.key() == Qt.Key_R:
            self.update()

        if e.key() == Qt.Key_Escape:
            self.close()

        if e.key() == Qt.Key_X:
            self.blockenAktiv = True

        if e.key() == Qt.Key_Y:
            self.blockenAktiv = False


    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        print("               ", pos.x(), pos.y())

        """ Eingaben moeglich machen """
        for i in range(self.spalten):
            for j in range(self.reihen):
                if ( self.levelKoordinaten[i][j][0][0] < pos.x() < self.levelKoordinaten[i][j][1][0] ) \
                and ( self.levelKoordinaten[i][j][0][1] < pos.y() < self.levelKoordinaten[i][j][1][1] ) \
                and (self.level[i][j] == 0 or self.level[i][j] == 2):

                    if self.blockenAktiv:   # Feld blocken
                        if self.level[i][j] == 0:
                            self.level[i][j] = 2
                        elif self.level[i][j] == 2:
                            self.level[i][j] = 0

                    elif self.level[i][j] == 0:   # regulaer, wenn man was trifft und ungeblockt ist
                        if self.loesung[i][j] == 0:
                            print("falsch")
                            self.level[i][j] = -1
                        elif self.loesung[i][j] == 1:
                            print("richtig")
                            self.level[i][j] = 1

                        """ Ueberpruefen ob Level geschafft ist """
                        gewonnen = True
                        for i in range(self.spalten):
                            for j in range(self.reihen):
                                if self.loesung[i][j] == 1 and self.level[i][j] != 1:
                                    gewonnen = False
                        if gewonnen:
                            print("Glueckwunsch, du hast es geschafft!")

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

    def hinweiseNeuBerechnen(self):
        pass

    def loesungAnzeigen(self):
        self.level = self.loesung
        self.update()


    def hinweiseErstellen(self):

        # Hinweise fuer Spalten erstellen
        obenHinweise = []
        for i in range(self.reihen):
            zaehler = 0
            spalteHinweise = ""
            for j in range(self.spalten):
                if self.loesung[j][i] == 1:
                    zaehler += 1
                else:
                    if zaehler != 0:
                        if spalteHinweise:
                            spalteHinweise += "\n" + str(zaehler)
                        else:
                            spalteHinweise = str(zaehler)

                    zaehler = 0
            if not spalteHinweise and zaehler == 0:  # wenn kein Feld schwarz ist
                spalteHinweise = "0"
            if zaehler != 0:  # wenn das letzte Feld schwarz ist
                if spalteHinweise:
                    spalteHinweise += "\n" + str(zaehler)
                else:
                    spalteHinweise = str(zaehler)
            obenHinweise.append([spalteHinweise, True])

        # Hinweise fuer Reihen erstellen
        linksHinweise = []
        for i in range(self.spalten):
            zaehler = 0
            reiheHinweise = ""
            for j in range(self.reihen):
                if self.loesung[i][j] == 1:
                    zaehler += 1
                else:
                    if zaehler != 0:
                        if reiheHinweise:
                            reiheHinweise += "  " + str(zaehler)
                        else:
                            reiheHinweise = str(zaehler)

                    zaehler = 0
            if not reiheHinweise and zaehler == 0:   # wenn kein Feld schwarz ist
                reiheHinweise = "0"
            if zaehler != 0:       # wenn das letzte Feld schwarz ist
                if reiheHinweise:
                    reiheHinweise += "  " + str(zaehler)
                else:
                    reiheHinweise = str(zaehler)
            linksHinweise.append([reiheHinweise, True])

        return obenHinweise, linksHinweise



app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
