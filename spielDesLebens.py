import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF, QPixmap
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer
import numpy as np


"""
Vier Grundlegen:
1. Eine tote Zelle mit genau drei lebenden Nachbarn wird in der Folgegeneration neu geboren.
2. Lebende Zellen mit weniger als zwei lebenden Nachbarn sterben in der Folgegeneration an Einsamkeit.
3. Eine lebende Zelle mit zwei oder drei lebenden Nachbarn bleibt in der Folgegeneration am Leben.
4. Lebende Zellen mit mehr als drei lebenden Nachbarn sterben in der Folgegeneration an Überbevölkerung.
"""


FENSTERBREITE = 700
FENSTERHOEHE = 700
ANZAHLSPALTEN = 200
ANZAHLREIHEN = 200

LEBEND = [255, 255, 255]
TOT = [0, 0, 0]

FARBELEBEND = QColor(255, 255, 255).rgb()
FARBETOT = QColor(0, 0, 0).rgb()



class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW, self.wH = FENSTERBREITE, FENSTERHOEHE
        self.spalten, self.reihen = ANZAHLSPALTEN, ANZAHLREIHEN
        self.keyPressEvent = self.fn
        self.lebendeZellenListe = set()
        self.img = QImage()
        self.pix = QPixmap()

        # Feld erstellen
        self.data = np.zeros((self.wW, self.wH, 3)).astype(np.uint8)
        self.field = QLabel()
        self.bildKomplettNeuBerechnen()

        # Buttons
        self.button1 = QPushButton("unbelegt")

        self.button2 = QPushButton("unbelegt")

        self.button3 = QPushButton("Konvertieren")
        self.button3.clicked.connect(self.farbenKonvertieren)
        self.button4 = QPushButton("unbelegt")

        self.button5 = QPushButton("richtiger berechnen?")
        self.button5.clicked.connect(self.berechneNaechsteDaten)

        # Positionen festlegen
        self.layout = QGridLayout()
        self.layout.addWidget(self.field, 0, 0, 0, 1)
        self.layout.addWidget(self.button1, 0, 1)
        self.layout.addWidget(self.button2, 1, 1)
        self.layout.addWidget(self.button3, 2, 1)
        self.layout.addWidget(self.button4, 3, 1)
        self.layout.addWidget(self.button5, 4, 1)


        self.setLayout(self.layout)
        self.show()


    def fn(self, e):
        """ Tastenbelegungen """
        if e.key() == Qt.Key_Q:
            self.figurGleiter()
        if e.key() == Qt.Key_W:
            self.figurSpiegelU()



    """ Grundlegende Funktionen """

    def bildKomplettNeuBerechnen(self):
        """ Nicht mehr benoetigt, fuer normales Programm zu langsam. Kann man theoretisch in init packen um nur einmal
        ausfuehren zu lassen. Berechnet jeden Pixel aus 'data' fuer 'img'. """
        self.img = QImage(self.spalten, self.reihen, QImage.Format_RGB32)
        for x in range(self.spalten):
            for y in range(self.reihen):
                self.img.setPixel(x, y, QColor(*self.data[x][y]).rgb())
        self.pix = QPixmap.fromImage(self.img)
        self.pix = QPixmap.scaledToWidth(self.pix, self.wW)
        self.field.setPixmap(self.pix)
        self.show()


    def umaendern(self, belebendeElemente, sterbendeElemente=None):
        """ Als Eingabe zwei Listen mit Tupeln (Koordinaten). Aendert das aktuelle Bild bei den angegebenen Pixeln """
        if sterbendeElemente is None:
            sterbendeElemente = []
        for b in belebendeElemente:
            self.data[b[0]][b[1]] = LEBEND
            self.lebendeZellenListe.add(b)
            self.img.setPixel(b[0], b[1], FARBELEBEND)

        for s in sterbendeElemente:
            self.data[s[0]][s[1]] = TOT
            self.img.setPixel(s[0], s[1], FARBETOT)

        self.pix = QPixmap.fromImage(self.img)
        self.pix = QPixmap.scaledToWidth(self.pix, self.wW)
        self.field.setPixmap(self.pix)


    def berechneNaechsteDaten(self):
        """ Berechnet die Daten fuer den naechsten Schritt des Spiel des Lebens """
        belebendeZellen = set()
        sterbendeZellen = set()
        zuUeberpruefendeUmliegendeZellen = set()

        # jede Zelle, deren Koordinaten in "lebendeZellenListe" vermerkt sind, durchgehen
        for koordinaten in self.lebendeZellenListe:
            lebendeNachbarn = self.anzahlLebendeNachbarnBerechnen(koordinaten[0], koordinaten[1])

            # Zelle überlebt nur, wenn genau 2 oder 3 Nachbarn leben
            if not (lebendeNachbarn == 2 or lebendeNachbarn == 3):
                sterbendeZellen.add((koordinaten[0], koordinaten[1]))

            # umliegende Zellen durch moegliche Wiederbelebungen betrachten
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0] - 1, koordinaten[1] - 1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]    , koordinaten[1] - 1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0] + 1, koordinaten[1] - 1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0] - 1, koordinaten[1]    ))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0] + 1, koordinaten[1]    ))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0] - 1, koordinaten[1] + 1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]    , koordinaten[1] + 1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0] + 1, koordinaten[1] + 1))
        # Alle umliegenden Zellen pruefen, 1. ob sie tot sind 2. ob sie wiederbelebt werden koennen
        for koordinatenU in zuUeberpruefendeUmliegendeZellen:
            if self.data[koordinatenU[0]][koordinatenU[1]][0] == 0:
                # Zelle wird wiederbelebt, wenn genau 3 lebende Nachbarn
                if self.anzahlLebendeNachbarnBerechnen(koordinatenU[0], koordinatenU[1]) == 3:
                    belebendeZellen.add((koordinatenU[0], koordinatenU[1]))

        # betreffende Zellen beleben / toeten
        for zelleB in belebendeZellen:
            self.data[zelleB[0]][zelleB[1]] = LEBEND
            self.lebendeZellenListe.add((zelleB[0], zelleB[1]))
        for zelleT in sterbendeZellen:
            self.data[zelleT[0]][zelleT[1]] = TOT
            self.lebendeZellenListe.remove((zelleT[0], zelleT[1]))

        # self.bildAktualisieren()
        self.umaendern(belebendeZellen, sterbendeZellen)


    def anzahlLebendeNachbarnBerechnen(self, x, y):
        """ x,y (Int, Int) sind Koordinaten eines Punktes, dessen umliegende 8 Felder betrachtet werden """
        anzahlLebendeNachbarn = 0
        if self.data[x - 1][y - 1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x][y - 1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x + 1][y - 1][0] == 255:
            anzahlLebendeNachbarn += 1

        if self.data[x - 1][y][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x + 1][y][0] == 255:
            anzahlLebendeNachbarn += 1

        if self.data[x - 1][y + 1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x][y + 1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x + 1][y + 1][0] == 255:
            anzahlLebendeNachbarn += 1

        return anzahlLebendeNachbarn



    """ Hilfs- und Spassfunktionen """

    def lebendeZellenListeAktualisieren(self):
        """ Geht jeden Pixel durch um zu schauen ob die Liste noch aktuell ist ; nur zum Ueberpruefen """
        pass


    def farbenKonvertieren(self):
        """ bisher nur bildlich, nicht danach berechenbar """
        for i in range(ANZAHLSPALTEN):
            for j in range(ANZAHLREIHEN):
                if self.data[i][j][0] == 255:
                    self.data[i][j] = TOT
                elif self.data[i][j][0] == 0:
                    self.data[i][j] = LEBEND

        self.bildKomplettNeuBerechnen()



    """ Figuren """

    def figurGleiter(self):
        """ Gleiter: bewegt sich oszillierend diagonal vorwaerts """
        startX = ANZAHLSPALTEN // 2
        startY = ANZAHLREIHEN // 2
        listeZumAendern = [(startX    , startY - 1),
                           (startX + 1, startY    ),
                           (startX - 1, startY + 1),
                           (startX    , startY + 1),
                           (startX + 1, startY + 1)
                           ]
        self.umaendern(listeZumAendern)


    def figurSpiegelU(self):
        """ SpiegelU: loest sich nach 54 (?) Iterationen auf """
        startX = ANZAHLSPALTEN // 2
        startY = ANZAHLREIHEN // 2
        listeZumAendern = [(startX - 1, startY - 3),    # obere Haelfte
                           (startX    , startY - 3),
                           (startX + 1, startY - 3),
                           (startX - 1, startY - 2),
                           (startX + 1, startY - 2),
                           (startX - 1, startY - 1),
                           (startX + 1, startY - 1),

                           (startX - 1, startY + 1),    # untere Haelfte
                           (startX + 1, startY + 1),
                           (startX - 1, startY + 2),
                           (startX + 1, startY + 2),
                           (startX - 1, startY + 3),
                           (startX    , startY + 3),
                           (startX + 1, startY + 3)
                           ]
        self.umaendern(listeZumAendern)





app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())

