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
        self.func = self.func1


    def func1(self, x, y):            # Funktion, die ausgeführt wird, wenn das Rechteck geklickt wird
        self.farbe = QColor(0, 180, 0)
        self.func = self.func2


    def func2(self, x, y):
        pass


class Kreis:

    def __init__(self):
        pass



class Levelstruktur:

    def __init__(self, zugehoerigesFenster):
        self.rechtecke = []
        self.kreise = []
        self.zugehoerigesFenster = zugehoerigesFenster

    def rechteck_hinzufuegen(self, rechteck):
        self.rechtecke.append(rechteck)
        rechteck.zugehoerigesLevel = self

    def weiteresZeichnen(self, painterF):             # Funktion, die Nicht-Rechtecke und Nicht-Kreise zeichnet.
        pass

    def beruehrt(self, x, y):
        for rechteck in self.rechtecke:
            if (rechteck.xKoordinate <= x <= rechteck.xKoordinate + rechteck.weite) and (
                    rechteck.yKoordinate <= y <= rechteck.yKoordinate + rechteck.hoehe):
                rechteck.func(x, y)

                # Gewinnbedingung
                for i in self.rechtecke:
                    if i.farbe != QColor(0, 180, 0):
                        return True
                self.zugehoerigesFenster.nextLevel()        # setzt ein, wenn man das Level gewonnen hat
                return True
        return False





class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.wW = 800       # wW = windowWidth
        self.setGeometry(1200, 150, self.wW, self.wW)
        self.setWindowTitle("Spaß mit grünem")
        self.originalLevels = []
        self.levels = []
        self.levelCounter = 0
        self.maxLevel = -1
        self.gewonnenAnzeige = False

        self.initalisierung()
        self.keyPressEvent = self.fn

        self.show()


    def paintEvent(self, event):
        # Hintergrund zeichnen
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 180, 0), 1, Qt.SolidLine))
        painter.fillRect(0, 0, self.wW, self.wW, QColor(0, 180, 0))
        rect1 = QRect(self.wW / 2, self.wW / 40, self.wW / 20, self.wW / 20)
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.drawText(rect1, 0, str(self.levelCounter))

        if self.gewonnenAnzeige:        # Kurzer Übergang zum nächsten Level, verschwindet nach 3 Sekunden
            rect2 = QRect(self.wW / 2.5, self.wW / 2, self.wW / 2, self.wW / 2)
            rect3 = QRect(self.wW / 1.75, self.wW / 2, self.wW / 2, self.wW / 2)
            painter.drawText(rect2, 0, "Glückwunsch, du hast Level        geschafft")
            painter.drawText(rect3, 0, str(self.levelCounter-1))
            self.gewonnenAnzeige = False
            QTimer.singleShot(3000, self.update)
            return

        # Level zeichnen
        for rechteck in self.levels[self.levelCounter].rechtecke:
            painter.fillRect(rechteck.xKoordinate, rechteck.yKoordinate,
                             rechteck.weite, rechteck.hoehe, rechteck.farbe)

        for kreis in self.levels[self.levelCounter].kreise:
            pass

        self.levels[self.levelCounter].weiteresZeichnen(painter)


    def fn(self, e):
        if e.key() == Qt.Key_Left:
            print("du hast links gedrueckt")


    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        print("               ", pos.x(), pos.y())

        if self.levels[self.levelCounter].beruehrt(pos.x(), pos.y()):
            self.update()


    def initalisierung(self):       # Anfaengliche Erstellung der Level
        level0 = Levelstruktur(self)
        for j in range(5):
            for i in range(5):
                level0.rechteck_hinzufuegen(Rechteck(self.wW / 16 + self.wW * (3 / 16) * i,
                                                     self.wW / 16 + self.wW * (3 / 16) * j,
                                                     self.wW / 8, self.wW / 8, QColor(0, 90, 0)))

        level1 = Levelstruktur(self)
        for j in range(3):
            for i in range(2):
                level1.rechteck_hinzufuegen(Rechteck(self.wW / 16 + self.wW * (3 / 16) * (i + 2),
                                                     self.wW / 12 + self.wW * (3 / 16) * (j + 2),
                                                     self.wW / 8, self.wW / 8, QColor(90, 0, 0)))

        self.originalLevels = [level0, level1]
        self.levels = [level0, level1]

    def levelReset(self):
        self.levels[self.levelCounter] = self.originalLevels[self.levelCounter]

    def nextLevel(self):
        self.levelCounter += 1
        self.gewonnenAnzeige = True

    def test(self):
        print("hey")





app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec_())
