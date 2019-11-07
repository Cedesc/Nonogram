import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QImage, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QEvent, QRect, QPointF, QPropertyAnimation, QTimer




class Rechteck:

    def __init__(self, xKoordinate, yKoordinate, weite, hoehe, farbe):
        self.xKoordinate = xKoordinate
        self.yKoordinate = yKoordinate
        self.weite = weite
        self.hoehe = hoehe
        self.farbe = farbe
        self.zugehoerigesLevel = None


    def func(self, x, y):            # Funktion, die ausgeführt wird, wenn das Rechteck geklickt wird
        print("Laenge :  ", len(self.zugehoerigesLevel.rechtecke), "   x :  ", x, "  y :  ", y)


    def funci(self, x, y):
        print("Laenge :  ", len(self.zugehoerigesLevel.rechtecke), "   x :  ", x, "  y :  ", y)


class Kreis:

    def __init__(self):
        pass



class Levelstruktur:

    def __init__(self):
        self.rechtecke = []
        self.kreise = []

    def rechteck_hinzufuegen(self, rechteck):
        self.rechtecke.append(rechteck)
        rechteck.zugehoerigesLevel = self

    def weiteresZeichnen(self):             # Funktion, die Nicht-Rechtecke und Nicht-Kreise zeichnet.
        pass

    def beruehrt(self, x, y):
        for rechteck in self.rechtecke:
            if (rechteck.xKoordinate <= x <= rechteck.xKoordinate + rechteck.weite) and (
                    rechteck.yKoordinate <= y <= rechteck.yKoordinate + rechteck.hoehe):
                rechteck.func(x, y)
                return True
        return False





class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.levelCounter = 0
        self.maxLevel = -1
        self.levels = []
        self.momentaneslevel = None
        self.wW = 800       # wW = windowWidth
        self.setGeometry(1200, 150, self.wW, self.wW)
        self.setWindowTitle("Spaß mit grünem")
        self.initalisierung()
        self.show()
        self.keyPressEvent = self.fn
        self.setMouseTracking(True)


    def paintEvent(self, event):
        # Hintergrund zeichnen
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 180, 0), 1, Qt.SolidLine))
        painter.fillRect(0, 0, self.wW, self.wW, QColor(0, 180, 0))
        rect1 = QRect(self.wW / 2, self.wW / 40, self.wW / 20, self.wW / 20)
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.drawText(rect1, 0, str(self.levelCounter))

        # Unterscheidungen je Level
        self.auswahl()

    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")

    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        print("               ", pos.x(), pos.y())

        if self.levels[self.levelCounter].beruehrt(pos.x(), pos.y()):
            self.update()

    def initalisierung(self):
        level0 = Levelstruktur()
        for j in range(5):
            for i in range(5):
                level0.rechteck_hinzufuegen(Rechteck(self.wW / 16 + self.wW * (3 / 16) * i,
                                                     self.wW / 16 + self.wW * (3 / 16) * j,
                                                     self.wW / 8, self.wW / 8, QColor(0, 90, 0)))
        self.levels.append(level0)

    def auswahl(self):
        print("Level : ", self.levelCounter)

        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 90, 0), 1, Qt.SolidLine))

        if self.levelCounter == 0:
            """
            # Levelstruktur erstellen
            for j in range(5):
                for i in range(5):
                    self.level.rechteck_hinzufuegen(Rechteck(self.wW / 16 + self.wW * (3 / 16) * i,
                                                                      self.wW / 16 + self.wW * (3/16) * j,
                                                                      self.wW / 8, self.wW / 8, QColor(0, 90, 0)))
            """
            # Level zeichnen
            for rechteck in self.levels[self.levelCounter].rechtecke:
                painter.fillRect(rechteck.xKoordinate, rechteck.yKoordinate,
                                 rechteck.weite, rechteck.hoehe, rechteck.farbe)

            for kreis in self.levels[self.levelCounter].kreise:
                pass
            self.levels[self.levelCounter].weiteresZeichnen()






app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
