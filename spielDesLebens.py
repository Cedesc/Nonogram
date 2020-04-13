import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QSpinBox
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF, QPixmap
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer
import numpy as np
import spielDesLebensSettings as settings


"""
Vier Grundlegen:
1. Eine tote Zelle mit genau drei lebenden Nachbarn wird in der Folgegeneration neu geboren.
2. Lebende Zellen mit weniger als zwei lebenden Nachbarn sterben in der Folgegeneration an Einsamkeit.
3. Eine lebende Zelle mit zwei oder drei lebenden Nachbarn bleibt in der Folgegeneration am Leben.
4. Lebende Zellen mit mehr als drei lebenden Nachbarn sterben in der Folgegeneration an Überbevölkerung.
"""





class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW, self.wH = settings.FENSTERBREITE, settings.FENSTERHOEHE
        self.spalten, self.reihen = settings.ANZAHLSPALTEN, settings.ANZAHLREIHEN
        self.dataLebend = settings.LEBEND
        self.dataTot = settings.TOT
        self.indikatorLebend = settings.LEBEND_INDIKATOR
        self.indikatorTot = settings.TOT_INDIKATOR
        self.farbeLebend = settings.FARBELEBEND
        self.farbeTot = settings.FARBETOT
        self.keyPressEvent = self.fn
        self.lebendeZellenListe = set()
        self.img = QImage()
        self.pix = QPixmap()
        self.timer = QTimer(self)
        self.stepCounter = 0

        # Feld erstellen
        self.data = np.zeros((self.wW, self.wH, 3)).astype(np.uint8)
        for i in range(self.wW):
            for j in range(self.wH):
                self.data[i][j] = self.dataTot
        self.field = QLabel()
        self.bildKomplettNeuBerechnen()

        # Buttons
        self.buttonTimerStarten = QPushButton("Timer starten")
        self.buttonTimerStarten.clicked.connect(self.timerStarten)
        self.buttonTimerStoppen = QPushButton("Timer stoppen")
        self.buttonTimerStoppen.clicked.connect(self.timerStoppen)
        self.buttonNextStep = QPushButton("Naechsten Schritt berechnen")
        self.buttonNextStep.clicked.connect(self.berechneNaechsteDaten)

        # Spin-Box fuer Geschwindigkeit des Timers
        self.schrift = QLabel("Millisekunden bis zum naechsten Schritt")
        self.schrift.setAlignment(Qt.AlignBottom)
        self.spinBoxTimerGeschwindigkeit = QSpinBox()
        self.spinBoxTimerGeschwindigkeit.setAlignment(Qt.AlignTop)
        self.spinBoxTimerGeschwindigkeit.setRange(0, 5000)
        self.spinBoxTimerGeschwindigkeit.setSingleStep(20)
        self.spinBoxTimerGeschwindigkeit.setValue(200)

        # Positionen festlegen
        self.layout = QGridLayout()
        self.layout.addWidget(self.field, 0, 0, 0, 1)
        self.layout.addWidget(self.buttonTimerStarten, 0, 1)
        self.layout.addWidget(self.buttonTimerStoppen, 1, 1)
        self.layout.addWidget(self.buttonNextStep, 2, 1)
        self.layout.addWidget(self.schrift, 3, 1)
        self.layout.addWidget(self.spinBoxTimerGeschwindigkeit, 4, 1)

        self.setLayout(self.layout)
        self.show()


    def fn(self, e):
        """ Tastenbelegungen """
        if e.key() == Qt.Key_H:
            print("Figuren:\n"
                  "   Q:  Gleiter\n"
                  "   W:  SpiegelU\n"
                  "   E:  Heavyweight Spaceship\n"
                  "   R:  F-Pentominos\n"
                  "Funktionen:\n"
                  "   S:  Feld loeschen und Counter zuruecksetzen\n"
                  "   X:  Counter anzeigen lassen\n"
                  "   Y:  Counter zuruecksetzen\n")
        if e.key() == Qt.Key_Q:
            self.figurGleiter()
        if e.key() == Qt.Key_W:
            self.figurSpiegelU()
        if e.key() == Qt.Key_E:
            self.figurHWWS()
        if e.key() == Qt.Key_R:
            self.figurFPentominos()
        if e.key() == Qt.Key_S:
            print("Feld geloescht und Counter zurueckgesetzt")
            self.umaendern([], self.lebendeZellenListe)
            self.stepCounter = 0
        if e.key() == Qt.Key_X:
            print(self.stepCounter, "bisherige Iterationen")
        if e.key() == Qt.Key_Y:
            print("Counter zurueckgesetzt")
            self.stepCounter = 0

        if e.key() == Qt.Key_B:
            for i in range(5, 200, 10):
                self.figurHWWS(10, i)



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
            self.data[b[0]][b[1]] = self.dataLebend
            self.lebendeZellenListe.add(b)
            self.img.setPixel(b[0], b[1], self.farbeLebend)

        for s in sterbendeElemente:
            self.data[s[0]][s[1]] = self.dataTot
            self.img.setPixel(s[0], s[1], self.farbeTot)

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
            if self.data[koordinatenU[0]][koordinatenU[1]][0] == self.indikatorTot:
                # Zelle wird wiederbelebt, wenn genau 3 lebende Nachbarn
                if self.anzahlLebendeNachbarnBerechnen(koordinatenU[0], koordinatenU[1]) == 3:
                    belebendeZellen.add((koordinatenU[0], koordinatenU[1]))

        # betreffende Zellen beleben / toeten
        for zelleB in belebendeZellen:
            self.data[zelleB[0]][zelleB[1]] = self.dataLebend
            self.lebendeZellenListe.add((zelleB[0], zelleB[1]))
        for zelleT in sterbendeZellen:
            self.data[zelleT[0]][zelleT[1]] = self.dataTot
            self.lebendeZellenListe.remove((zelleT[0], zelleT[1]))

        # self.bildAktualisieren()
        self.umaendern(belebendeZellen, sterbendeZellen)
        self.stepCounter += 1


    def anzahlLebendeNachbarnBerechnen(self, x, y):
        """ x,y (Int, Int) sind Koordinaten eines Punktes, dessen umliegende 8 Felder betrachtet werden """
        anzahlLebendeNachbarn = 0
        if self.data[x - 1][y - 1][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1
        if self.data[x][y - 1][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1
        if self.data[x + 1][y - 1][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1

        if self.data[x - 1][y][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1
        if self.data[x + 1][y][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1

        if self.data[x - 1][y + 1][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1
        if self.data[x][y + 1][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1
        if self.data[x + 1][y + 1][0] == self.indikatorLebend:
            anzahlLebendeNachbarn += 1

        return anzahlLebendeNachbarn



    """ Hilfs- und Spassfunktionen """

    def timerStarten(self):
        self.timer.timeout.connect(self.berechneNaechsteDaten)
        self.timer.start(self.spinBoxTimerGeschwindigkeit.value())
        print("Timer gestartet")


    def timerStoppen(self):
        self.timer.stop()
        print("Timer gestoppt")

    # unfertig
    def lebendeZellenListeAktualisieren(self):
        """ Geht jeden Pixel durch um zu schauen ob die Liste noch aktuell ist ; nur zum Ueberpruefen """
        pass

    # unfertig
    def farbenKonvertieren(self):
        """ bisher nur bildlich, nicht danach berechenbar """
        for i in range(self.spalten):
            for j in range(self.reihen):
                if self.data[i][j][0] == self.indikatorLebend:
                    self.data[i][j] = self.dataTot
                elif self.data[i][j][0] == self.indikatorTot:
                    self.data[i][j] = self.dataLebend

        self.bildKomplettNeuBerechnen()

    # unfertig
    def komplettesFeldLoeschen(self):
        """ Jede Zelle toeten """
        self.umaendern([], self.lebendeZellenListe)


    """ Figuren """

    def figurGleiter(self, startX = settings.ANZAHLSPALTEN // 2, startY = settings.ANZAHLREIHEN // 2):
        """ Gleiter: bewegt sich oszillierend diagonal vorwaerts """
        listeZumAendern = [(startX    , startY - 1),
                           (startX + 1, startY    ),
                           (startX - 1, startY + 1),
                           (startX    , startY + 1),
                           (startX + 1, startY + 1)
                           ]
        self.umaendern(listeZumAendern)


    def figurSpiegelU(self, startX = settings.ANZAHLSPALTEN // 2, startY = settings.ANZAHLREIHEN // 2):
        """ SpiegelU: loest sich nach 54 (?) Iterationen auf """
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


    def figurHWWS(self, startX = settings.ANZAHLSPALTEN // 2, startY = settings.ANZAHLREIHEN // 2):
        """ Heavyweight Spaceship: bewegt sich oszillierend waagerecht vorwaerts """
        listeZumAendern = [(startX + 1, startY - 2),
                           (startX + 2, startY - 2),
                           (startX - 3, startY - 1),
                           (startX - 2, startY - 1),
                           (startX - 1, startY - 1),
                           (startX    , startY - 1),
                           (startX + 2, startY - 1),
                           (startX + 3, startY - 1),
                           (startX - 3, startY    ),
                           (startX - 2, startY    ),
                           (startX - 1, startY    ),
                           (startX    , startY    ),
                           (startX + 1, startY    ),
                           (startX + 2, startY    ),
                           (startX - 2, startY + 1),
                           (startX - 1, startY + 1),
                           (startX    , startY + 1),
                           (startX + 1, startY + 1)
                           ]
        self.umaendern(listeZumAendern)


    def figurFPentominos(self, startX = settings.ANZAHLSPALTEN // 2, startY = settings.ANZAHLREIHEN // 2):
        """ F-Pentominos: interessante Entwicklung (1102 Iterationen) """
        listeZumAendern = [(startX    , startY - 1),
                           (startX + 1, startY - 1),
                           (startX - 1, startY    ),
                           (startX    , startY    ),
                           (startX    , startY + 1)
                           ]
        self.umaendern(listeZumAendern)


app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())

