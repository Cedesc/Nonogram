import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF, QPixmap
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer
import copy
import picrossSettings as ps


""" 
Erklaerung: 
    - 3 geschachtelte Listen mit Tiefe 2, 1. mit der Loesung, 2. mit dem momentanen Stand, 3. mit Koordinaten
    - linke Maustaste um Feld zu bestaetigen, rechte Maustaste um Feld zu blocken
    - Creator-Mode ist dafuer da um leicht neue Level zu erstellen: terminiert erst wenn alle Felder besetzt sind, 
      schwarze Felder koennen mit rechter Maustaste wieder entfernt werden, blocken ist hier nicht moeglich
"""




class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW = ps.FENSTERBREITE       # wW = windowWidth
        self.wH = ps.FENSTERHOEHE        # wH = windowHeight
        self.setGeometry(500, 30, self.wW, self.wH)
        self.setWindowTitle("Picross")
        self.loesung = ps.LEVEL

        self.nachUnten = self.wH // 8     # Gesamtverschiebung nach unten
        self.nachRechts = self.wW // 8    # Gesamtverschiebung nach rechts
        self.anzahlZeilen = len(self.loesung)
        self.anzahlSpalten = len(self.loesung[0])
        self.level = self.leeresLevelErstellen()
        self.levelKoordinaten = self.koordinatenBestimmen()
        self.hinweiseSpalten, self.hinweiseZeilen = self.hinweiseErstellen()
        self.gewonnen = False
        self.creatorModeAn = False
        self.hinweiseInZahlenZeilenSpalten = self.hinweiseInZahlenAendern()

        # Reihen mit 0 bereits auskreuzen
        for i in range(self.anzahlZeilen):
            self.zeileabgeschlossen(i)
        for j in range(self.anzahlSpalten):
            self.spalteabgeschlossen(j)

        self.geaenderteHinweise = False
        self.kiErlaubt = True
        self.kiZaehler = 0  # Zaehler um bei KI Reihen nacheinander statt alle auf einmal auszufuellen

        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.something)
        #self.timer.start(2000)

        self.keyPressEvent = self.fn

        self.buttonStart = QPushButton("KI starten", self)
        self.buttonStart.clicked.connect(self.kiMitTimerDurchlaufenLassen)
        self.buttonStart.move(self.wW // 30, self.wH - self.wH // 30)
        self.buttonStop = QPushButton("KI stoppen", self)
        self.buttonStop.clicked.connect(self.timer.stop)
        self.buttonStop.move(self.wW // 30 + 80, self.wH - self.wH // 30)

        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)
        markerColor = QColor(0,0,0)     # Farbe von Netz und einzelnen Feldern

        ''' Hintergrund '''
        painter.fillRect(0, 0, self.wW, self.wH, QColor(205, 205, 205))
        if self.gewonnen:
            # Hintergrund wird gruen (wenn kein Hintergrundbild
            #painter.fillRect(0, 0, self.wW, self.wH, QColor(155, 205, 155))
            markerColor = QColor(50, 50, 50)
            self.gewinnAnimation()

        ''' Hintergrundbild '''
        painter.drawPixmap(0, 0, self.wW, self.wH, QPixmap("patrickVerstoerend.jpg"), 0, 0, 1280, 1024)
        if self.gewonnen:
            painter.drawPixmap(0, 0, self.wW, self.wH, QPixmap("patrickSchockiert.jpg"), 0, 0, 1920, 1200)
            font = painter.font()
            font.setPixelSize(40)
            painter.setFont(font)
            painter.drawText(0, 0, self.wW, 50, Qt.AlignHCenter, "Glueckwunsch, das Level ist geschafft!")
        ''' Netz aufbauen '''
        painter.setPen(QPen(markerColor, 1, Qt.SolidLine))

        # hoehe und breite eines Felds
        hoehe = (self.wH - 2 * self.nachUnten) // self.anzahlZeilen
        breite = (self.wW - 2 * self.nachRechts) // self.anzahlSpalten

        # KI - Zeilenmarkierung
        if self.kiErlaubt and not self.gewonnen:
            if self.kiZaehler < self.anzahlZeilen:
                painter.fillRect(0,
                                 self.nachUnten + hoehe * self.kiZaehler,
                                 self.wW,
                                 hoehe,
                                 QColor(200,200,0))
            else:
                painter.fillRect(self.nachRechts + breite * (self.kiZaehler - self.anzahlZeilen),
                                 0,
                                 breite,
                                 self.wH,
                                 QColor(200,200,0))


        # vertikale Linien
        for verschiebung in range(self.anzahlSpalten + 1):
            if verschiebung == 0 or verschiebung == self.anzahlSpalten:
                painter.setPen(QPen(markerColor, 4, Qt.SolidLine))
                painter.drawLine(self.nachRechts + breite * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + breite * verschiebung,
                                 self.wH - self.nachUnten // 2)
                painter.setPen(QPen(markerColor, 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(markerColor, 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts + breite * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + breite * verschiebung,
                                 self.wH - self.nachUnten // 2)
                painter.setPen(QPen(markerColor, 1, Qt.SolidLine))
            else:
                painter.drawLine(self.nachRechts + breite * verschiebung,
                                 self.nachUnten // 2,
                                 self.nachRechts + breite * verschiebung,
                                 self.wH - self.nachUnten // 2)

        # horizontale Linien
        for verschiebung in range(self.anzahlZeilen + 1):
            if verschiebung == 0 or verschiebung == self.anzahlZeilen:
                painter.setPen(QPen(markerColor, 4, Qt.SolidLine))
                painter.drawLine(self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung,
                                 self.wW - self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung)
                painter.setPen(QPen(markerColor, 1, Qt.SolidLine))
            elif verschiebung % 5 == 0:
                painter.setPen(QPen(markerColor, 3, Qt.SolidLine))
                painter.drawLine(self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung,
                                 self.wW - self.nachRechts // 2,
                                 self.nachUnten + hoehe * verschiebung)
                painter.setPen(QPen(markerColor, 1, Qt.SolidLine))
            else:
                painter.drawLine(self.nachRechts // 2,
                                self.nachUnten + hoehe * verschiebung,
                                self.wW - self.nachRechts // 2,
                                self.nachUnten + hoehe * verschiebung)


        """ Rechtecke einzeichnen """
        painter.setPen(QPen(markerColor, 3, Qt.SolidLine))
        for i in range(self.anzahlZeilen):

            for j in range(self.anzahlSpalten):

                if self.level[i][j] == 1:
                    painter.fillRect(self.levelKoordinaten[i][j][0][0],
                                     self.levelKoordinaten[i][j][0][1],
                                     self.levelKoordinaten[i][j][1][0] - self.levelKoordinaten[i][j][0][0], # hoehe
                                     self.levelKoordinaten[i][j][1][1] - self.levelKoordinaten[i][j][0][1], # weite
                                     markerColor)

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

        # Zeilen
        for zeile in range(self.anzahlZeilen):
            if self.hinweiseZeilen[zeile][1]:       # pruefen ob visible
                painter.drawText(0, self.nachUnten + hoehe * (zeile+0.5) - schriftgroesse // 2,
                                 self.nachRechts, hoehe, Qt.AlignHCenter, self.hinweiseZeilen[zeile][0])
            else:
                painter.setPen(QColor(180,180,180))
                painter.drawText(0, self.nachUnten + hoehe * (zeile + 0.5) - schriftgroesse // 2,
                                 self.nachRechts, hoehe, Qt.AlignHCenter, self.hinweiseZeilen[zeile][0])
                painter.setPen(QColor(0, 0, 0))


        # Spalten
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
        # H druecken um Steuerung anzuzeigen
        if e.key() == Qt.Key_H:
            print("- Steuerung :",
                    "\n    - H (Hilfe) : Steuerung anzeigen",
                    "\n    - esc (Escape) : Fenster schliessen",
                    "\n    - L (Loesung) : Loesung anzeigen",
                    "\n    - R (Reset) : Level Reset",
                    "\n    - N (Neu) : Neues zufaelliges Level erstellen",
                    "\n    - C (Creator) : Creator Mode anschalten",
                    "\n        - S (Save) : Level im Creator Mode Speichern",
                    "\n    - K (KI) : KI aktivieren oder deaktivieren",
                    "\n        - 1 : Je eine eindeutige Reihe vervollstaendigen",
                    "\n        - 2 : Je eine Reihe weitergehen und alle eindeutigen Felder eintragen",
                    "\n        - 3 : Alle eindeutigen Reihen vervollstaendigen",
                    "\n        - 4 : Alle Reihen je einmal abgehen und alle eindeutigen Felder eintragen",
                    "\n        - Q : KI komplett durchlaufen lassen",
                    "\n        - W : neue Hinweise eintragen",
                    "\n        - T : mit Timer alle Reihen je einmal abgehen und alle eindeutigen Felder eintragen",
                    "\n        - Z : Timer anhalten")

        # esc druecken um Level zu schliessen
        if e.key() == Qt.Key_Escape:
            self.close()

        # L druecken um Loesung anzuzeigen
        if e.key() == Qt.Key_L:
            self.loesungAnzeigen()

        # R druecken um Level neuzustarten
        if e.key() == Qt.Key_R:
            self.levelReset()
            self.update()

        # N druecken um neues zufaelliges Level zu erstellen
        if e.key() == Qt.Key_N:
            self.neuesLevelErstellen()

        # C druecken um in Creator-Mode zu wechseln
        if e.key() == Qt.Key_C:
            if self.creatorModeAn:
                print("Bereits in Creator-Mode")
            else:
                self.creatorModeAn = True
                self.loesungVollstaendigSchwarzMachen()
                print("Creator-Mode aktiv")

        # S druecken um momentanes Level zu speichern
        if e.key() == Qt.Key_S and self.creatorModeAn:
            self.creatorModelevelSpeichern()
            print("Level abgespeichert")

        # KI :  K druecken um KI zu erlauben oder zu verbieten
        if e.key() == Qt.Key_K:
            if self.kiErlaubt:
                self.kiErlaubt = False
                print("KI verboten")
            else:
                self.kiErlaubt = True
                print("KI erlaubt")
            self.update()

        # KI :  1 druecken um je eine eindeutige Reihen zu vervollstaendigen
        if e.key() == Qt.Key_1:
            self.kiSchrittEindeutigeReihen()
            self.update()

        # KI :  2 druecken um je eine Reihe/Spalte weiterzugehen und alle eindeutigen Felder einzutragen
        if e.key() == Qt.Key_2:
            self.kiSchrittEindeutigeFelder()
            self.update()

        # KI :  3 druecken um alle eindeutigen Reihen zu vervollstaendigen
        if e.key() == Qt.Key_3:
            while self.kiSchrittEindeutigeReihen():
                pass
            self.update()

        # KI :  4 druecken um alle Reihen je einmal abzugehen und alle eindeutigen Felder einzutragen
        if e.key() == Qt.Key_4:
            while not self.gewonnen:
                self.kiSchrittEindeutigeFelder()
                self.update()
                if self.kiZaehler == 0:
                    break
            self.update()

        # KI :  Q druecken um KI komplett durchlaufen zu lassen
        if e.key() == Qt.Key_Q:
            self.kiDurchlaufenLassen(1000)
            self.update()

        # KI :  W druecken um neue Hinweise einzutragen
        if e.key() == Qt.Key_W:
            self.loesungVollstaendigSchwarzMachen()
            self.hinweiseZeilen, self.hinweiseSpalten = self.hinweiseInStringsAendern(self.eingabeDerHinweise())
            self.hinweiseInZahlenZeilenSpalten = self.hinweiseInZahlenAendern()
            self.geaenderteHinweise = True
            self.update()

        # KI :  T druecken um mit Timer alle Reihen je einmal abzugehen und alle eindeutigen Felder einzutragen
        if e.key() == Qt.Key_T:
            self.kiMitTimerDurchlaufenLassen()

        # KI :  Z druecken um Timer zu stoppen
        if e.key() == Qt.Key_Z:
            self.timer.stop()
            print("Timer gestoppt")



    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        #print("               ", pos.x(), pos.y())     # zum ueberpruefen wo man klickt

        """ Eingaben moeglich machen """
        for i in range(self.anzahlZeilen):
            for j in range(self.anzahlSpalten):
                if ( self.levelKoordinaten[i][j][0][0] < pos.x() < self.levelKoordinaten[i][j][1][0] ) \
                and ( self.levelKoordinaten[i][j][0][1] < pos.y() < self.levelKoordinaten[i][j][1][1] ):

                    if self.level[i][j] == 0 or self.level[i][j] == 2:
                        # Feld blocken
                        if QMouseEvent.button() == Qt.RightButton and not self.creatorModeAn:
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
                            self.zeileabgeschlossen(i)
                            self.spalteabgeschlossen(j)

                        self.pruefenObGewonnen()

                    # schwarze Felder mit rechter Maustaste entfernen, wenn Creator-Mode an ist
                    elif self.level[i][j] == 1 and (self.creatorModeAn or self.geaenderteHinweise)\
                            and QMouseEvent.button() == Qt.RightButton:
                        self.level[i][j] = 0

                    # updatet wenn irgendein Feld getroffen wurde
                    self.update()



    def leeresLevelErstellen(self):

        result = []
        for i in range(self.anzahlZeilen):
            zeile = []
            for j in range(self.anzahlSpalten):
                zeile.append(0)
            result.append(zeile)
        return result


    def koordinatenBestimmen(self):

        # Idee: Fuer jeden Eintrag jeweils linke obere und rechte untere Koordinate für ein Rechteck bestimmen.
        #       Diese als Tupel von zwei Tupeln (2 Punkte, also 4 Koordinaten) in geschachtelter Liste so platzieren,
        #       dass sie die gleichen Indizes haben, wie die zugehoerigen Werte
        result = []

        # reine Vorberechnung
        breite = (self.wW - 2 * self.nachRechts) // self.anzahlSpalten
        hoehe = (self.wH - 2 * self.nachUnten) // self.anzahlZeilen

        for i in range(self.anzahlZeilen):
            zeile = []
            for j in range(self.anzahlSpalten):

                punktLinksOben = (self.nachRechts + breite * j, self.nachUnten + hoehe * i)
                punktRechtsUnten = (self.nachRechts + breite * (j+1), self.nachUnten + hoehe * (i+1))

                zeile.append( ( punktLinksOben , punktRechtsUnten ) )
            result.append(zeile)
        return result


    def levelReset(self):
        self.level = self.leeresLevelErstellen()

        # alle Hinweise wieder schwarz machen
        # schnellere Alternative zu hinweisSichtbarkeitpruefen
        for i in range(len(self.hinweiseZeilen)):
            self.hinweiseZeilen[i][1] = True
        for i in range(len(self.hinweiseSpalten)):
            self.hinweiseSpalten[i][1] = True

        self.gewonnen = False       # hebt Sperre auf, die Verhindert, dass man neu zeichnen kann


    def pruefenObGewonnen(self):
        """ Ueberpruefen ob Level geschafft ist """
        self.gewonnen = True
        for i in range(self.anzahlZeilen):
            for j in range(self.anzahlSpalten):
                if self.loesung[i][j] == 1 and self.level[i][j] != 1:
                    self.gewonnen = False
        if self.gewonnen:
            for i in range(len(self.hinweiseZeilen)):
                self.hinweiseZeilen[i][1] = False
            for i in range(len(self.hinweiseSpalten)):
                self.hinweiseSpalten[i][1] = False


    def loesungAnzeigen(self):
        self.level = copy.deepcopy(self.loesung)

        # alle Hinweise grau machen
        # schnellere Alternative zu hinweisSichtbarkeitpruefen
        for i in range(len(self.hinweiseZeilen)):
            self.hinweiseZeilen[i][1] = False
        for i in range(len(self.hinweiseSpalten)):
            self.hinweiseSpalten[i][1] = False
        self.gewonnen = True
        self.update()


    def hinweiseErstellen(self):

        # Hinweise fuer Spalten erstellen
        obenHinweise = []
        for i in range(self.anzahlSpalten):
            zaehler = 0
            spalteHinweise = ""
            for j in range(self.anzahlZeilen):
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

        # Hinweise fuer Zeilen erstellen
        linksHinweise = []
        for i in range(self.anzahlZeilen):
            zaehler = 0
            zeileHinweise = ""
            for j in range(self.anzahlSpalten):
                if self.loesung[i][j] == 1:
                    zaehler += 1
                else:
                    if zaehler != 0:
                        if zeileHinweise:
                            zeileHinweise += "  " + str(zaehler)
                        else:
                            zeileHinweise = str(zaehler)

                    zaehler = 0
            if not zeileHinweise and zaehler == 0:   # wenn kein Feld schwarz ist
                zeileHinweise = "0"
            if zaehler != 0:       # wenn das letzte Feld schwarz ist
                if zeileHinweise:
                    zeileHinweise += "  " + str(zaehler)
                else:
                    zeileHinweise = str(zaehler)
            linksHinweise.append([zeileHinweise, True])

        return obenHinweise, linksHinweise


    def gewinnAnimation(self):
        print("Glueckwunsch, du hast es geschafft!")
        self.level = copy.deepcopy(self.loesung)


    def zeileabgeschlossen(self, zeile):
        # pruefen ob Zeile abgeschlossen ist, indem die schwarzen Felder der Loesung in der Zeile mit den
        # schwarzen Feldern des Levels verglichen wird
        for i in range(self.anzahlSpalten):
            if self.loesung[zeile][i] == 1:
                if self.level[zeile][i] != 1:
                    return False

        # unausgefuellter Rest der Zeile blocken
        for i in range(self.anzahlSpalten):
            if self.level[zeile][i] == 0:
                self.level[zeile][i] = 2

        # Hinweise ausgrauen
        self.hinweiseZeilen[zeile][1] = False

        return True


    def spalteabgeschlossen(self, spalte):
        # pruefen ob Spalte abgeschlossen ist mit analogem Verfahren zu zeileabgeschlossen
        for i in range(self.anzahlZeilen):
            if self.loesung[i][spalte] == 1:
                if self.level[i][spalte] != 1:
                    return False

        # unausgefuellter Rest der Spalte blocken
        for i in range(self.anzahlZeilen):
            if self.level[i][spalte] == 0:
                self.level[i][spalte] = 2

        # Hinweise ausgrauen
        self.hinweiseSpalten[spalte][1] = False

        return True


    def hinweisSichtbarkeitPruefen(self):
        for i in range(self.anzahlSpalten):
            self.spalteabgeschlossen(i)
        for i in range(self.anzahlZeilen):
            self.zeileabgeschlossen(i)


    def loesungVollstaendigSchwarzMachen(self):

        # Loesung mit nur schwarzen Feldern erstellen, damit man keinen Fehler machen kann und nicht vorher abbricht
        vollstaendigeLoesung = []
        for i in range(self.anzahlZeilen):
            zeile = []
            for j in range(self.anzahlSpalten):
                zeile.append(1)
            vollstaendigeLoesung.append(zeile)

        self.loesung = vollstaendigeLoesung

        # Level leeren
        self.level = self.leeresLevelErstellen()

        # Hinweise entfernen
        for i in range(self.anzahlZeilen):
            self.hinweiseZeilen[i][0] = ""
        for i in range(self.anzahlSpalten):
            self.hinweiseSpalten[i][0] = ""

        self.update()


    def creatorModelevelSpeichern(self):
        txtDatei = open("levelSpeicher.txt", "w")

        # alles ausser Einsen und Nullen aus der Datei entfernen
        for i in range(self.anzahlZeilen):
            for j in range(self.anzahlSpalten):
                if self.level[i][j] != 1:
                    self.level[i][j] = 0
        zuSpeicherndesLevel = "[\n"
        for i in self.level:
            zuSpeicherndesLevel += ("            " + str(i) + ",\n")
        zuSpeicherndesLevel += "           ]"
        txtDatei.write(zuSpeicherndesLevel)
        txtDatei.close()


    def neuesLevelErstellen(self):
        self.levelReset()
        self.loesung = ps.picrossLevelBib.zufaelligesLevelMitSchwierigkeit(ps.ANZAHLSPALTEN, ps.ANZAHLREIHEN,
                                                                           ps.SCHWIERIGKEIT)
        self.hinweiseSpalten, self.hinweiseZeilen = self.hinweiseErstellen()
        self.gewonnen = False
        self.hinweiseInZahlenZeilenSpalten = self.hinweiseInZahlenAendern()
        self.update()


    def hinweiseInZahlenAendern(self):
        neueHinweiseZeilen = []
        for liste in self.hinweiseZeilen:
            proZeile = []
            zahlR = ""
            for zeichen in liste[0]:
                if zeichen == " " and zahlR != "":
                    proZeile.append(int(zahlR))
                    zahlR = ""
                else:
                    zahlR += zeichen
            proZeile.append(int(zahlR))
            neueHinweiseZeilen.append(proZeile)

        neueHinweiseSpalten = []
        for liste in self.hinweiseSpalten:
            proSpalte = []
            zahlS = ""
            for zeichen in liste[0]:
                if zeichen == "\n" and zahlS != "":
                    proSpalte.append(int(zahlS))
                    zahlS = ""
                else:
                    zahlS += zeichen
            proSpalte.append(int(zahlS))
            neueHinweiseSpalten.append(proSpalte)

        return neueHinweiseZeilen, neueHinweiseSpalten


    def kiAktivieren(self):
        pass


    def kiSchrittEindeutigeReihen(self):
        # eindeutige Zeilen vervollstaendigen
        for hinweisZeile in range(len(self.hinweiseInZahlenZeilenSpalten[0])):
            summeProZeile = -1
            for hinweisR in self.hinweiseInZahlenZeilenSpalten[0][hinweisZeile]:
                summeProZeile += 1 + hinweisR

            # wenn in einer Zeile kein schwarzes Feld vorhanden ist
            if summeProZeile == 0 and self.hinweiseZeilen[hinweisZeile][1]:
                self.hinweiseZeilen[hinweisZeile][1] = False
                for j in range(self.anzahlSpalten):
                    self.level[hinweisZeile][j] = 2
                return True

            # wenn es in einer Zeile eine eindeutige Loesung an schwarzen Feldern gibt
            if summeProZeile == self.anzahlSpalten and self.hinweiseZeilen[hinweisZeile][1]:
                zaehlerR = 0
                for anzahlSchwarzeFelderR in self.hinweiseInZahlenZeilenSpalten[0][hinweisZeile]:
                    for schwarzesFeld in range(anzahlSchwarzeFelderR):
                        self.level[hinweisZeile][zaehlerR] = 1
                        zaehlerR += 1
                    if zaehlerR < self.anzahlSpalten:
                        self.level[hinweisZeile][zaehlerR] = 2
                        zaehlerR += 1
                self.hinweiseZeilen[hinweisZeile][1] = False
                for j in range(self.anzahlSpalten):
                    self.spalteabgeschlossen(j)
                return True


        # eindeutige Spalten vervollstaendigen
        for hinweisSpalte in range(len(self.hinweiseInZahlenZeilenSpalten[1])):
            summeProSpalte = -1
            for hinweisS in self.hinweiseInZahlenZeilenSpalten[1][hinweisSpalte]:
                summeProSpalte += 1 + hinweisS

            # wenn in einer Spalte kein schwarzes Feld vorhanden ist
            if summeProSpalte == 0 and self.hinweiseSpalten[hinweisSpalte][1]:
                self.hinweiseSpalten[hinweisSpalte][1] = False
                for i in range(self.anzahlZeilen):
                    self.level[i][hinweisSpalte] = 2
                return True

            # wenn es in einer Spalte eine eindeutige Loesung an schwarzen Feldern gibt
            if summeProSpalte == self.anzahlZeilen and self.hinweiseSpalten[hinweisSpalte][1]:
                zaehlerS = 0
                for anzahlSchwarzeFelderS in self.hinweiseInZahlenZeilenSpalten[1][hinweisSpalte]:
                    for schwarzesFeld in range(anzahlSchwarzeFelderS):
                        self.level[zaehlerS][hinweisSpalte] = 1
                        zaehlerS += 1
                    if zaehlerS < self.anzahlZeilen:
                        self.level[zaehlerS][hinweisSpalte] = 2
                        zaehlerS += 1
                self.hinweiseSpalten[hinweisSpalte][1] = False
                for i in range(self.anzahlZeilen):
                    self.zeileabgeschlossen(i)
                return True

        return False


    def reiheUeberpruefenObMoeglicheLoesung(self, reihenNummer, reihe, istSpalte):
        if istSpalte:
            reiheLoesung = copy.copy(self.hinweiseInZahlenZeilenSpalten[1][reihenNummer])
        else:
            reiheLoesung = copy.copy(self.hinweiseInZahlenZeilenSpalten[0][reihenNummer])

        zaehler = 0
        for j in range(self.anzahlSpalten):
            if reihe[j] == 1:
                zaehler += 1
            elif reiheLoesung:
                if reiheLoesung[0] < zaehler:
                    #print("Reihe ist falsch, zu viele schwarze Felder nebeneinander.")
                    return False
                if reiheLoesung[0] > zaehler != 0:
                    #print("Reihe ist falsch, zu wenige schwarze Felder nebeneinander.")
                    return False
                elif reiheLoesung[0] == zaehler:
                    reiheLoesung.pop(0)
                    zaehler = 0

        if reiheLoesung:
            if reiheLoesung[0] == zaehler:
                reiheLoesung.pop(0)
                zaehler = 0

        if zaehler > 0:
            #print("Reihe ist falsch, zu viele schwarze Felder insgesamt")
            return False

        if not reiheLoesung:
            #print("Reihe kann richtig sein")
            return True

        if reiheLoesung == [0]:
            #print("Reihe ist richtig, da keine schwarzen Felder drin sein sollen.")
            return True

        #print("Reihe ist falsch, es ist noch kein schwarzes Feld eingetragen")
        return False


    def binaereKombinationen(self, anzahlStellen):
        result = []
        for integerZahl in range(2 ** anzahlStellen, 2 ** anzahlStellen * 2):
            binaereZahlInString = bin(integerZahl)
            zwischenergebnis = []
            for stelle in range(3, len(binaereZahlInString)):
                zwischenergebnis.append(int(binaereZahlInString[stelle]))
            result.append(zwischenergebnis)

        return result


    def alleMoeglichenLoesungenBerechnenZeile(self, zeilenNummer):
        vorhandeneReihe = copy.copy(self.level[zeilenNummer])

        anzahlFehlendeSchwarzeFelder = 0
        for zahl in self.hinweiseInZahlenZeilenSpalten[0][zeilenNummer]:
            anzahlFehlendeSchwarzeFelder += zahl
        for feld in vorhandeneReihe:
            if feld == 1:
                anzahlFehlendeSchwarzeFelder -= 1

        # Indizies raussuchen, die unbelegt sind
        anzahlNochUnbelegteFelder = 0
        zuBelegendeFelderIndizes = []
        for feldIndex in range(len(vorhandeneReihe)):
            if vorhandeneReihe[feldIndex] == 0:
                anzahlNochUnbelegteFelder += 1
                zuBelegendeFelderIndizes.append(feldIndex)

        alleKombinationen = self.binaereKombinationen(anzahlNochUnbelegteFelder)

        alleMoeglichenLoesungen = []
        for kombiIndex in range(len(alleKombinationen)):
            for stelleIndex in range(len(alleKombinationen[kombiIndex])):
                vorhandeneReihe[zuBelegendeFelderIndizes[stelleIndex]] = alleKombinationen[kombiIndex][stelleIndex]
            if self.reiheUeberpruefenObMoeglicheLoesung(zeilenNummer, vorhandeneReihe, False):
                alleMoeglichenLoesungen.append(tuple(vorhandeneReihe))

        return alleMoeglichenLoesungen


    def alleMoeglichenLoesungenBerechnenSpalte(self, spaltenNummer):
        vorhandeneReihe = self.spalteAlsEinzelneListe(spaltenNummer)

        anzahlFehlendeSchwarzeFelder = 0
        for zahl in self.hinweiseInZahlenZeilenSpalten[1][spaltenNummer]:
            anzahlFehlendeSchwarzeFelder += zahl
        for feld in vorhandeneReihe:
            if feld == 1:
                anzahlFehlendeSchwarzeFelder -= 1

        # Indizies raussuchen, die unbelegt sind
        anzahlNochUnbelegteFelder = 0
        zuBelegendeFelderIndizes = []
        for feldIndex in range(len(vorhandeneReihe)):
            if vorhandeneReihe[feldIndex] == 0:
                anzahlNochUnbelegteFelder += 1
                zuBelegendeFelderIndizes.append(feldIndex)

        alleKombinationen = self.binaereKombinationen(anzahlNochUnbelegteFelder)

        alleMoeglichenLoesungen = []
        for kombiIndex in range(len(alleKombinationen)):
            for stelleIndex in range(len(alleKombinationen[kombiIndex])):
                vorhandeneReihe[zuBelegendeFelderIndizes[stelleIndex]] = alleKombinationen[kombiIndex][stelleIndex]
            if self.reiheUeberpruefenObMoeglicheLoesung(spaltenNummer, vorhandeneReihe, True):
                alleMoeglichenLoesungen.append(tuple(vorhandeneReihe))

        return alleMoeglichenLoesungen


    def eindeutigeFelderEintragenZeile(self, zeilenNummer):
        moeglicheLoesungen = self.alleMoeglichenLoesungenBerechnenZeile(zeilenNummer)
        if not moeglicheLoesungen:
            print("Reihe ist falsch (keine moegliche Loesung), das sollte allerdings nicht vorkommen koennen.")
            return
        if len(moeglicheLoesungen) == 1:
            # print("Jau super, Zeile fertig.")
            self.level[zeilenNummer] = list(moeglicheLoesungen[0])
            for index in range(self.anzahlSpalten):
                if self.level[zeilenNummer][index] == 0:
                    self.level[zeilenNummer][index] = 2
            self.hinweiseZeilen[zeilenNummer][1] = False
            return

        abgleich = list(moeglicheLoesungen[0])
        for moeglichkeit in moeglicheLoesungen:
            for index in range(len(moeglichkeit)):
                if abgleich[index] == 1:
                    if moeglichkeit[index] != 1:
                        abgleich[index] = -2
                else:
                    if moeglichkeit[index] == 1:
                        abgleich[index] = -2

        # Gleiches ins Level uebertragen
        for index in range(self.anzahlSpalten):
            if abgleich[index] == 1:
                self.level[zeilenNummer][index] = 1
            elif abgleich[index] != -2:
                self.level[zeilenNummer][index] = 2


    def eindeutigeFelderEintragenSpalte(self, spaltenNummer):
        moeglicheLoesungen = self.alleMoeglichenLoesungenBerechnenSpalte(spaltenNummer)
        if not moeglicheLoesungen:
            print("Spalte ist falsch (keine moegliche Loesung), das sollte allerdings nicht vorkommen koennen.")
            return
        if len(moeglicheLoesungen) == 1:
            # print("Jau super, Spalte fertig.")
            for i in range(self.anzahlZeilen):
                self.level[i][spaltenNummer] = moeglicheLoesungen[0][i]
            for index in range(self.anzahlZeilen):
                if self.level[index][spaltenNummer] == 0:
                    self.level[index][spaltenNummer] = 2
            self.hinweiseSpalten[spaltenNummer][1] = False
            return

        abgleich = list(moeglicheLoesungen[0])
        for moeglichkeit in moeglicheLoesungen:
            for index in range(len(moeglichkeit)):
                if abgleich[index] == 1:
                    if moeglichkeit[index] != 1:
                        abgleich[index] = -2
                else:
                    if moeglichkeit[index] == 1:
                        abgleich[index] = -2

        # Gleiches ins Level uebertragen
        for index in range(self.anzahlSpalten):
            if abgleich[index] == 1:
                self.level[index][spaltenNummer] = 1
            elif abgleich[index] != -2:
                self.level[index][spaltenNummer] = 2


    def kiSchrittEindeutigeFelder(self):

        if self.kiZaehler < self.anzahlZeilen:
            self.eindeutigeFelderEintragenZeile(self.kiZaehler)
        else:
            self.eindeutigeFelderEintragenSpalte(self.kiZaehler - self.anzahlZeilen)
        self.kiZaehler = (self.kiZaehler + 1) % (self.anzahlZeilen + self.anzahlSpalten)

        if self.kiZaehler == 0:
            self.pruefenObGewonnen()

        # print("KI - Schritt  :   ", self.kiZaehler)


    def spalteAlsEinzelneListe(self, spaltenNummer):
        result = []
        for i in range(self.anzahlZeilen):
            result.append(self.level[i][spaltenNummer])
        return result


    def hinweiseInStringsAendern(self, liste):
        resultZeile = []
        for zeile in liste[0]:
            hinweiseStringZeile = str(zeile[0])
            if len(zeile) > 1:
                for zahlIndex in range(1, len(zeile)):
                    hinweiseStringZeile += "  " + str(zeile[zahlIndex])
            resultZeile.append([hinweiseStringZeile, True])

        resultSpalte = []
        for spalte in liste[1]:
            hinweiseStringSpalte = str(spalte[0])
            if len(spalte) > 1:
                for zahlIndex in range(1, len(spalte)):
                    hinweiseStringSpalte += "\n" + str(spalte[zahlIndex])
            resultSpalte.append([hinweiseStringSpalte, True])

        return resultZeile, resultSpalte


    def eingabeDerHinweise(self):
        datenAlleZeilen = []
        for zeilenNummer in range(self.anzahlZeilen):
            rohdatenZeile = list(input("Reihe Nr." + str(zeilenNummer) + " :  "))

            verarbeiteteDatenZeile = []
            momentaneZahlZ = ""
            for i in rohdatenZeile:
                if ',' != i != ' ':
                    momentaneZahlZ += i
                elif momentaneZahlZ != "":
                    verarbeiteteDatenZeile.append(int(momentaneZahlZ))
                    momentaneZahlZ = ""
            if momentaneZahlZ != "":
                verarbeiteteDatenZeile.append(int(momentaneZahlZ))


            datenAlleZeilen.append(verarbeiteteDatenZeile)

        datenAlleSpalten = []
        for spaltenNummer in range(self.anzahlSpalten):
            rohdatenSpalte = list(input("Spalte Nr." + str(spaltenNummer) + " :  "))

            verarbeiteteDatenSpalte = []
            momentaneZahlS = ""
            for i in rohdatenSpalte:
                if ',' != i != ' ':
                    momentaneZahlS += i
                elif momentaneZahlS != "":
                    verarbeiteteDatenSpalte.append(int(momentaneZahlS))
                    momentaneZahlS = ""
            if momentaneZahlS != "":
                verarbeiteteDatenSpalte.append(int(momentaneZahlS))

            datenAlleSpalten.append(verarbeiteteDatenSpalte)

        print("Zeilen :  ", datenAlleZeilen)
        print("Spalten :  ", datenAlleSpalten)
        while input("Eingabe korrekt? (y/n)  ") != 'y':
            inputDatenAlleZ = input("Zeilen :  ")
            inputDatenAlleS = input("Spalten :  ")
            datenAlleZeilen, datenAlleSpalten = self.eingabeDerHinweiseGanzeReihe(inputDatenAlleZ, inputDatenAlleS)
            print("Eingabe Zeilen :  ", datenAlleZeilen)
            print("Eingabe Spalten :   ", datenAlleSpalten)

        return datenAlleZeilen, datenAlleSpalten


    def eingabeDerHinweiseGanzeReihe(self, zeilenHinweiseEingabe, spaltenHinweiseEingabe):
        datenAlleZ = []
        verarbeiteteDatenZeile = []
        momentaneZahlZ = ""
        for zeichenZ in zeilenHinweiseEingabe:

            if zeichenZ not in [',', ' ', '[', ']']:
                momentaneZahlZ += zeichenZ
            elif momentaneZahlZ != "":
                verarbeiteteDatenZeile.append(int(momentaneZahlZ))
                momentaneZahlZ = ""
            if zeichenZ == ']' and verarbeiteteDatenZeile != []:
                datenAlleZ.append(verarbeiteteDatenZeile)
                verarbeiteteDatenZeile = []
                momentaneZahlZ = ""

        datenAlleS = []
        verarbeiteteDatenSpalte = []
        momentaneZahlS = ""
        for zeichenS in spaltenHinweiseEingabe:

            if zeichenS not in [',', ' ', '[', ']']:
                momentaneZahlS += zeichenS
            elif momentaneZahlS != "":
                verarbeiteteDatenSpalte.append(int(momentaneZahlS))
                momentaneZahlS = ""
            if zeichenS == ']' and verarbeiteteDatenSpalte != []:
                datenAlleS.append(verarbeiteteDatenSpalte)
                verarbeiteteDatenSpalte = []
                momentaneZahlS = ""

        return datenAlleZ, datenAlleS


    def kiDurchlaufenLassen(self, maxSchritte = 1000):
        while self.kiSchrittEindeutigeReihen():
            pass

        schrittzaehler = 0
        while not self.gewonnen and schrittzaehler < maxSchritte:
            self.kiSchrittEindeutigeFelder()
            if self.kiZaehler == 0:
                fertig = True
                for zeile in self.level:
                    for feld in zeile:
                        if feld == 0:
                            fertig = False
                if fertig:
                    break
            schrittzaehler += 1

        self.kiZaehler = 0
        if self.gewonnen:
            print("Geloest in", schrittzaehler, "Schritten")
        else:
            print("Abgebrochen nach", maxSchritte, "Schritten")


    def kiMitTimerDurchlaufenLassen(self):
        self.timer.timeout.connect(self.kiSchrittEindeutigeFelder)
        self.timer.timeout.connect(self.update)
        self.timer.timeout.connect(self.timerStop)
        self.timer.start(200)
        print("Timer gestartet")

    def timerStop(self):
        if self.gewonnen:
            self.timer.stop()







app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
