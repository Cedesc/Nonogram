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
ANZAHLSPALTEN = 500
ANZAHLREIHEN = 500

LEBEND = [255, 255, 255]
TOT = [0, 0, 0]


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW, self.wH = FENSTERBREITE, FENSTERHOEHE
        self.spalten, self.reihen = ANZAHLSPALTEN, ANZAHLREIHEN
        self.keyPressEvent = self.fn
        self.lebendeZellenListe = set()

        # Feld erstellen
        self.data = np.zeros((self.wW, self.wH, 3)).astype(np.uint8)
        self.field = QLabel()
        self.bildAktualisieren()

        # Buttons
        self.button1 = QPushButton("kleiner Test")
        self.button1.clicked.connect(self.machWas)
        self.button2 = QPushButton("Testmuster erstellen")
        self.button2.clicked.connect(self.anfangErstellen)
        self.button3 = QPushButton("Konvertieren")
        self.button3.clicked.connect(self.farbenKonvertieren)
        self.button4 = QPushButton("richtig berechnen")
        self.button4.clicked.connect(self.berechneNaechsteDaten)
        self.button5 = QPushButton("richtiger berechnen?")
        self.button5.clicked.connect(self.berechneNaechsteDatenV2)

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
        if e.key() == Qt.Key_Q:
            self.figurGleiter()
        if e.key() == Qt.Key_W:
            self.figurSpiegelU()

    def bildAktualisieren(self):
        img = QImage(self.spalten, self.reihen, QImage.Format_RGB32)
        for x in range(self.spalten):
            for y in range(self.reihen):
                img.setPixel(x, y, QColor(*self.data[x][y]).rgb())

        pix = QPixmap.fromImage(img)
        pix = QPixmap.scaledToWidth(pix, self.wW)
        self.field.setPixmap(pix)
        self.show()


    def machWas(self):
        print("ggg")

        self.data[2][3] = LEBEND
        self.data[2][30] = LEBEND
        self.data[2][32] = LEBEND
        self.bildAktualisieren()


    def anfangErstellen(self):
        for i in range(ANZAHLSPALTEN // 3, int(ANZAHLSPALTEN * (2/3)), 5):
            for j in range(ANZAHLREIHEN // 3, int(ANZAHLREIHEN * (2/3))):
                self.data[i][j] = LEBEND
        self.bildAktualisieren()

    def farbenKonvertieren(self):
        for i in range(ANZAHLSPALTEN):
            for j in range(ANZAHLREIHEN):
                if self.data[i][j][0] == 255:
                    self.data[i][j] = TOT
                elif self.data[i][j][0] == 0:
                    self.data[i][j] = LEBEND

        self.bildAktualisieren()

    def berechneNaechsteDaten(self):
        belebendeZellen = set()
        sterbendeZellen = set()
        # Rausfinden welche Zellen geaendert werden muessen
        for i in range(1, ANZAHLSPALTEN-1):
            for j in range(1, ANZAHLREIHEN-1):
                lebendeNachbarn = self.anzahlLebendeNachbarnBerechnen(i, j)

                # Zelle wird wiederbelebt, wenn genau 3 lebende Nachbarn
                if self.data[i][j][0] == 0:
                    if lebendeNachbarn == 3:
                        belebendeZellen.add((i, j))
                        #self.data[i][j] = LEBEND

                # Zelle überlebt nur, wenn genau 2 oder 3 Nachbarn leben
                else:
                    if not (lebendeNachbarn == 2 or lebendeNachbarn == 3):
                        sterbendeZellen.add((i, j))
                        #self.data[i][j] = TOT

        # betreffende Zellen aendern
        for zelleB in belebendeZellen:
            self.data[zelleB[0]][zelleB[1]] = LEBEND
        for zelleT in sterbendeZellen:
            self.data[zelleT[0]][zelleT[1]] = TOT


        self.bildAktualisieren()



    def anzahlLebendeNachbarnBerechnen(self, x, y):
        anzahlLebendeNachbarn = 0
        if self.data[x-1][y-1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x][y-1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x+1][y-1][0] == 255:
            anzahlLebendeNachbarn += 1

        if self.data[x-1][y][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x+1][y][0] == 255:
            anzahlLebendeNachbarn += 1

        if self.data[x-1][y+1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x][y+1][0] == 255:
            anzahlLebendeNachbarn += 1
        if self.data[x+1][y+1][0] == 255:
            anzahlLebendeNachbarn += 1

        return anzahlLebendeNachbarn


    def figurGleiter(self):
        startX = ANZAHLSPALTEN // 2
        startY = ANZAHLREIHEN // 2

        self.data[startX][startY-1] = LEBEND
        self.data[startX+1][startY] = LEBEND
        self.data[startX-1][startY+1] = LEBEND
        self.data[startX][startY+1] = LEBEND
        self.data[startX+1][startY+1] = LEBEND

        self.lebendeZellenListe.add((startX, startY-1))
        self.lebendeZellenListe.add((startX+1, startY))
        self.lebendeZellenListe.add((startX-1, startY+1))
        self.lebendeZellenListe.add((startX, startY+1))
        self.lebendeZellenListe.add((startX+1, startY+1))

        self.bildAktualisieren()

    def figurSpiegelU(self):
        startX = ANZAHLSPALTEN // 2
        startY = ANZAHLREIHEN // 2

        # obere Haelfte
        self.data[startX-1][startY-3] = LEBEND
        self.data[startX][startY-3] = LEBEND
        self.data[startX+1][startY-3] = LEBEND
        self.data[startX-1][startY-2] = LEBEND
        self.data[startX+1][startY-2] = LEBEND
        self.data[startX-1][startY-1] = LEBEND
        self.data[startX+1][startY-1] = LEBEND

        # untere Haelfte
        self.data[startX-1][startY+1] = LEBEND
        self.data[startX+1][startY+1] = LEBEND
        self.data[startX-1][startY+2] = LEBEND
        self.data[startX+1][startY+2] = LEBEND
        self.data[startX-1][startY+3] = LEBEND
        self.data[startX][startY+3] = LEBEND
        self.data[startX+1][startY+3] = LEBEND


        #obere Haelfte
        self.lebendeZellenListe.add((startX-1, startY-3))
        self.lebendeZellenListe.add((startX, startY-3))
        self.lebendeZellenListe.add((startX+1, startY-3))
        self.lebendeZellenListe.add((startX-1, startY-2))
        self.lebendeZellenListe.add((startX+1, startY-2))
        self.lebendeZellenListe.add((startX-1, startY-1))
        self.lebendeZellenListe.add((startX+1, startY-1))


        # untere Haelfte
        self.lebendeZellenListe.add((startX-1, startY+1))
        self.lebendeZellenListe.add((startX+1, startY+1))
        self.lebendeZellenListe.add((startX-1, startY+2))
        self.lebendeZellenListe.add((startX+1, startY+2))
        self.lebendeZellenListe.add((startX-1, startY+3))
        self.lebendeZellenListe.add((startX, startY+3))
        self.lebendeZellenListe.add((startX+1, startY+3))



        self.bildAktualisieren()


    def berechneNaechsteDatenV2(self):
        belebendeZellen = set()
        sterbendeZellen = set()
        zuUeberpruefendeUmliegendeZellen = set()


        for koordinaten in self.lebendeZellenListe:
            lebendeNachbarn = self.anzahlLebendeNachbarnBerechnen(koordinaten[0], koordinaten[1])

            # Zelle überlebt nur, wenn genau 2 oder 3 Nachbarn leben
            if not (lebendeNachbarn == 2 or lebendeNachbarn == 3):
                sterbendeZellen.add((koordinaten[0], koordinaten[1]))

            # umliegende Zellen durch moegliche Wiederbelebungen betrachten
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]-1, koordinaten[1]-1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0], koordinaten[1]-1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]+1, koordinaten[1]-1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]-1, koordinaten[1]))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]+1, koordinaten[1]))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]-1, koordinaten[1]+1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0], koordinaten[1]+1))
            zuUeberpruefendeUmliegendeZellen.add((koordinaten[0]+1, koordinaten[1]+1))

        for koordinatenU in zuUeberpruefendeUmliegendeZellen:
            if self.data[koordinatenU[0]][koordinatenU[1]][0] == 0:
                # Zelle wird wiederbelebt, wenn genau 3 lebende Nachbarn
                if self.anzahlLebendeNachbarnBerechnen(koordinatenU[0], koordinatenU[1]) == 3:
                    belebendeZellen.add((koordinatenU[0], koordinatenU[1]))


        # betreffende Zellen aendern
        for zelleB in belebendeZellen:
            self.data[zelleB[0]][zelleB[1]] = LEBEND
            self.lebendeZellenListe.add((zelleB[0], zelleB[1]))
        for zelleT in sterbendeZellen:
            self.data[zelleT[0]][zelleT[1]] = TOT
            self.lebendeZellenListe.remove((zelleT[0], zelleT[1]))

        self.bildAktualisieren()


    def lebendeZellenListeAktualisieren(self):
        pass





app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())

