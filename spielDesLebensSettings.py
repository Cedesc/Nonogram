from PyQt5.QtGui import QColor


FENSTERBREITE = 700
FENSTERHOEHE = 700
ANZAHLSPALTEN = 200
ANZAHLREIHEN = 200

LEBEND = [255, 255, 255]        # default: [255, 255, 255]
TOT = [0, 0, 0]                 # default: [0, 0, 0]

LEBEND_INDIKATOR = LEBEND[0]    # default: 255
TOT_INDIKATOR = TOT[0]          # default: 0
if LEBEND_INDIKATOR == TOT_INDIKATOR:
    print("FEHLER! Indikatoren sind identisch!")

FARBELEBEND = QColor(LEBEND[0], LEBEND[1], LEBEND[2]).rgb()     # default: 255, 255, 255
FARBETOT = QColor(TOT[0], TOT[1], TOT[2]).rgb()                 # default: 0, 0, 0