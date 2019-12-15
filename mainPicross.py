import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer
import random
import copy


""" Spiel-Settings """
FENSTERBREITE = 1300
FENSTERHOEHE = 1000
ANZAHLREIHEN = 15
ANZAHLSPALTEN = 15


""" 
Erklaerung: 
    - 3 geschachtelte Listen mit Tiefe 2, 1. mit der Loesung, 2. mit dem momentanen Stand, 3. mit Koordinaten
    - linke Maustaste um Feld zu bestaetigen, rechte Maustaste um Feld zu blocken
"""

""" Beispiel-Level """
beispiellevel = [[0,1,1,1,0],
                 [0,0,1,0,0],
                 [0,1,1,0,1],
                 [0,0,0,0,0],
                 [1,0,1,1,1],
                 [1,0,1,0,0]]

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

beispiellevel3 = [
                 [0,1,1,1,1,1,0,
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


def zufaelligesLevel(weite, hoehe):
    resultlevel = []
    for y in range(hoehe):
        zeile = []
        for x in range(weite):
            zeile.append(random.randint(0,1))
        resultlevel.append(zeile)
    return resultlevel


def zufaelligesLevelMitSchwierigkeit(weite, hoehe, schwierigkeit):  # leichter: negative Zahl, schwerer: positive Zahl
    # abs(schwierigkeit) viele zufaellige Level erstellen. Fuer leichtere Level, die mit den meisten schwarzen Feldern,
    # fuer schwierigere, die mit den wenigsten schwarzen Feldern zurueckgeben
    zufaelligeLevel = []
    for i in range(abs(schwierigkeit)):
        templevel = zufaelligesLevel(weite, hoehe)
        zaehler = 0
        for j in templevel:
            for k in j:
                if k == 1:
                    zaehler += 1
        zufaelligeLevel.append((templevel, zaehler))
    if schwierigkeit < 0:
        maxim = zufaelligeLevel[0]
        for i in zufaelligeLevel:

            if i[1] > maxim[1]:
                maxim = i

        return maxim[0]
    if schwierigkeit > 0:
        mindest = zufaelligeLevel[0]
        for i in zufaelligeLevel:
            if i[1] < mindest[1]:
                mindest = i
        return mindest[0]



class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW = FENSTERBREITE       # wW = windowWidth
        self.wH = FENSTERHOEHE        # wH = windowHeight
        self.setGeometry(500, 30, self.wW, self.wH)
        self.setWindowTitle("Picross")
        self.loesung = zufaelligesLevelMitSchwierigkeit(ANZAHLSPALTEN, ANZAHLREIHEN, -1000)

        self.nachUnten = self.wH // 8     # Gesamtverschiebung nach unten
        self.nachRechts = self.wW // 8    # Gesamtverschiebung nach rechts
        self.anzahlReihen = len(self.loesung)
        self.anzahlSpalten = len(self.loesung[0])

        self.level = self.leeresLevelErstellen()
        self.levelKoordinaten = self.koordinatenBestimmen()

        self.hinweiseSpalten, self.hinweiseReihen = self.hinweiseErstellen()

        self.gewonnen = False


        #self.loesungAnzeigen()


        self.keyPressEvent = self.fn

        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)

        ''' Hintergrund '''
        painter.fillRect(0, 0, self.wW, self.wH, QColor(205, 205, 205))
        if self.gewonnen:
            painter.fillRect(0, 0, self.wW, self.wH, QColor(155, 205, 155))
            self.gewinnAnimation()


        ''' Netz aufbauen '''
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))

        # vertikale Linien
        breite = (self.wW - 2 * self.nachRechts) // self.anzahlSpalten
        for verschiebung in range(self.anzahlSpalten + 1):
            if verschiebung == 0 or verschiebung == self.anzahlSpalten:
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
        hoehe = (self.wH - 2 * self.nachUnten) // self.anzahlReihen
        for verschiebung in range(self.anzahlReihen + 1):
            if verschiebung == 0 or verschiebung == self.anzahlReihen:
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
        for i in range(self.anzahlReihen):

            for j in range(self.anzahlSpalten):

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
        for reihe in range(self.anzahlReihen):
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
        for spalte in range(self.anzahlSpalten):
            if self.hinweiseSpalten[spalte][1]:     # pruefen ob visible
                painter.drawText(self.nachRechts + breite * (spalte+0.5) - schriftgroesse // 2,
                                 self.nachUnten - schriftgroesse * 20,
                                 schriftgroesse * 3, schriftgroesse * 20, Qt.AlignBottom, self.hinweiseSpalten[spalte][0])
            else:
                painter.setPen(QColor(180,180,180))
                painter.drawText(self.nachRechts + breite * (spalte + 0.5) - schriftgroesse // 2,
                                 self.nachUnten - schriftgroesse * 20,
                                 schriftgroesse * 3, schriftgroesse * 20, Qt.AlignBottom, self.hinweiseSpalten[spalte][0])
                painter.setPen(QColor(0,0,0))



    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")

        # R druecken um Level neuzustarten
        if e.key() == Qt.Key_R:
            self.levelReset()
            self.update()

        # L druecken um Loesung anzuzeigen
        if e.key() == Qt.Key_L:
            self.loesungAnzeigen()

        # esc druecken um Level zu schliessen
        if e.key() == Qt.Key_Escape:
            self.close()



    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        #print("               ", pos.x(), pos.y())     # zum ueberpruefen wo man klickt

        """ Eingaben moeglich machen """
        for i in range(self.anzahlReihen):
            for j in range(self.anzahlSpalten):
                if ( self.levelKoordinaten[i][j][0][0] < pos.x() < self.levelKoordinaten[i][j][1][0] ) \
                and ( self.levelKoordinaten[i][j][0][1] < pos.y() < self.levelKoordinaten[i][j][1][1] ) \
                and (self.level[i][j] == 0 or self.level[i][j] == 2):

                    # Feld blocken
                    if QMouseEvent.button() == Qt.RightButton:
                        if self.level[i][j] == 0:
                            self.level[i][j] = 2
                        elif self.level[i][j] == 2:
                            self.level[i][j] = 0

                    # regulaer, wenn man was trifft und ungeblockt ist
                    if QMouseEvent.button() == Qt.LeftButton and self.level[i][j] == 0:
                        if self.loesung[i][j] == 0:     # falsches Feld
                            self.level[i][j] = -1
                        elif self.loesung[i][j] == 1:
                            self.level[i][j] = 1        # richtiges Feld
                            self.reiheabgeschlossen(i)
                            self.spalteabgeschlossen(j)

                        """ Ueberpruefen ob Level geschafft ist """
                        self.gewonnen = True
                        for i in range(self.anzahlReihen):
                            for j in range(self.anzahlSpalten):
                                if self.loesung[i][j] == 1 and self.level[i][j] != 1:
                                    self.gewonnen = False

                    self.update()



    def leeresLevelErstellen(self):

        result = []
        for i in range(self.anzahlReihen):
            reihe = []
            for j in range(self.anzahlSpalten):
                reihe.append(0)
            result.append(reihe)
        return result


    def koordinatenBestimmen(self):

        # Idee: Fuer jeden Eintrag jeweils linke obere und rechte untere Koordinate für ein Rechteck bestimmen.
        #       Diese als Tupel von zwei Tupeln (2 Punkte, also 4 Koordinaten) in geschachtelter Liste so platzieren,
        #       dass sie die gleichen Indizes haben, wie die zugehoerigen Werte
        result = []

        # reine Vorberechnung
        breite = (self.wW - 2 * self.nachRechts) // self.anzahlSpalten
        hoehe = (self.wH - 2 * self.nachUnten) // self.anzahlReihen

        for i in range(self.anzahlReihen):
            reihe = []
            for j in range(self.anzahlSpalten):

                punktLinksOben = (self.nachRechts + breite * j, self.nachUnten + hoehe * i)
                punktRechtsUnten = (self.nachRechts + breite * (j+1), self.nachUnten + hoehe * (i+1))

                reihe.append( ( punktLinksOben , punktRechtsUnten ) )
            result.append(reihe)
        return result


    def levelReset(self):
        self.level = self.leeresLevelErstellen()
        self.gewonnen = False       # hebt Sperre auf, die Verhindert, dass man neu zeichnen kann


    def loesungAnzeigen(self):
        self.level = copy.deepcopy(self.loesung)
        self.update()


    def hinweiseErstellen(self):

        # Hinweise fuer Spalten erstellen
        obenHinweise = []
        for i in range(self.anzahlSpalten):
            zaehler = 0
            spalteHinweise = ""
            for j in range(self.anzahlReihen):
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
        for i in range(self.anzahlReihen):
            zaehler = 0
            reiheHinweise = ""
            for j in range(self.anzahlSpalten):
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


    def gewinnAnimation(self):
        print("Glueckwunsch, du hast es geschafft!")
        self.level = copy.deepcopy(self.loesung)


    def reiheabgeschlossen(self, reihe):
        # pruefen ob Reihe abgeschlossen ist, indem die schwarzen Felder der Loesung in der Reihe mit den
        # schwarzen Feldern des Levels verglichen wird
        for i in range(self.anzahlSpalten):
            if self.loesung[reihe][i] == 1:
                if self.level[reihe][i] != 1:
                    return False

        # unausgefuellter Rest der Reihe blocken
        for i in range(self.anzahlSpalten):
            if self.level[reihe][i] == 0:
                self.level[reihe][i] = 2

        # Hinweise ausgrauen
        self.hinweiseReihen[reihe][1] = False

        return True


    def spalteabgeschlossen(self, spalte):
        # pruefen ob Spalte abgeschlossen ist mit analogem Verfahren zu reiheabgeschlossen
        for i in range(self.anzahlReihen):
            if self.loesung[i][spalte] == 1:
                if self.level[i][spalte] != 1:
                    return False

        # unausgefuellter Rest der Spalte blocken
        for i in range(self.anzahlReihen):
            if self.level[i][spalte] == 0:
                self.level[i][spalte] = 2

        # Hinweise ausgrauen
        self.hinweiseSpalten[spalte][1] = False

        return True







app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
