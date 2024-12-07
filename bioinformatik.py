import re

from PySide6.QtCore import QObject, Signal

class Sequenz(QObject):
    """
    Klasse für eine Sequenz

    name: Name der Sequenz

    Die Basen werden entweder über einen Textstring mit importBasenString oder
    über ein Array mit importBasenArrayOfDict importiert. Das Array besteht aus Dicts
    mit den Attributen char für den Buchstaben und background für die
    Hintergrundfarbe (default weiß).
    """

    namechanged = Signal(QObject)
    basenchanged = Signal(QObject)

    def __init__(self, _name, _basen=None):
        super().__init__()
        self._name = _name
        self._basen = _basen or []

    def importBasenArrayOfDict(self, array):
        self._basen = []
        for baseobj in array:
            self._basen.append( Base(self, **baseobj))
        self.basenchanged.emit(self)

    def importBasenString(self, text):
        self._basen = []
        pattern = re.compile(r'\s+')
        text = re.sub(pattern, '', text).upper()
        for char in text:
            self._basen.append( Base(self, char) )
        self.basenchanged.emit(self)

    def insertBasenString(self, pos, text):
        pattern = re.compile(r'\s+')
        text = re.sub(pattern, '', text).upper()
        basenneu = self._basen.copy()
        for char in text[::-1]:
            basenneu.insert(pos, Base(self, char))
        return basenneu

    def insertLeer(self, pos, anzahl):
        leere = []
        for _ in range(anzahl):
            leere.append(Base(self, _char='~'))
        return self._basen[:pos]+leere+self._basen[pos:]

    def entferneBasen(self, index, anzahl):
        basenneu = self._basen.copy()
        basenneu[index:index+anzahl] = []
        return basenneu

    def inAminosaeure(self):
        neueBasen = []
        for base in self._basen:
            neueBasen.append(base)
            neueBasen.append(Base(self))
            neueBasen.append(Base(self))
        return neueBasen

    def setBasen(self, basen):
        self._basen = basen
        self.basenchanged.emit(self)

    def basen(self):
        return self._basen

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name
        self.namechanged.emit(self)

    def markiereBasen(self, idx, anzahl, markierung):
        for b in self._basen[idx:idx+anzahl]:
            b.setMarkierung(markierung)
        self.basenchanged.emit(self)

    def checkMarkierungen(self, markierungen):
        # Falls Markierungen gelöscht werden, müssen sie aus den Basen
        # entfernt werden
        for b in self._basen:
            b.checkMarkierung(markierungen)

    def __str__(self):
        return 'Sequenz'+str(self.__hash__())

    def to_json(self):
        return {'Sequenz': { '_name': self._name, '_basen': self._basen}}


class Base(QObject):
    """
    Klasse für die Base einer Sequenz

    sequenz: die Sequenz zu die die Base gehört
    char: der Buchstabe der Base
    background: die Hintergrundfarbe der Base
    """

    @staticmethod
    def colorMap(char):
        colormap = {
            'A': 'green',
            'C': 'red',
            'T': 'blue',
            'G': 'magenta'
        }
        return colormap[char] if char in colormap else 'black'

    def __init__(self, _sequenz, _char='~', _mtxt=None):
        super().__init__()
        self._sequenz = _sequenz
        self._char = _char
        self._markierung = None
        self._mtxt = _mtxt

    def char(self):
        return self._char

    def sequenz(self):
        return self._sequenz

    def markierung(self):
        return self._markierung

    def getIndexInSequenz(self):
        return self._sequenz.basen().index(self)

    def getNummerInSequenzOhneLeer(self):
        nummer = 1
        for base in self._sequenz.basen():
            if base == self:
                return nummer
            if base.char() != '~':
                nummer += 1

    def setMarkierung(self, markierung):
        self._markierung = markierung

    def getCharFarbe(self):
        return self.colorMap(self._char)

    def getBoxFarbe(self):
        farbe = ''
        if self._markierung:
            farbe = self._markierung.farbe()
        return farbe

    def checkMarkierung(self, markierungen):
        if self._markierung and self._markierung not in markierungen:
            self._markierung = None

    def __str__(self):
        return 'Base'+str(self.__hash__())

    def to_json(self):
        basedict = {'_char': self._char}
        if self._markierung:
            basedict['_mtxt'] = self._markierung.beschreibung()
        return basedict


class Markierung(QObject):

    markierungChanged = Signal()

    def __init__(self, _beschreibung, _farbe) -> None:
        super().__init__()
        self._beschreibung = _beschreibung
        self._farbe = _farbe

    def beschreibung(self):
        return self._beschreibung

    def setBeschreibung(self, beschreibung):
        self._beschreibung = beschreibung
        self.markierungChanged.emit()

    def farbe(self):
        return self._farbe

    def setFarbe(self, farbe):
        self._farbe = farbe
        self.markierungChanged.emit()

    def to_json(self):
        return { 'Markierung': { '_beschreibung': self._beschreibung, '_farbe': self._farbe } }
