
import re
from PySide6.QtCore import QObject, Signal

gaga=1

class Sequenz(QObject):
    """
    Klasse für eine Sequenz

    name: Name der Sequenz

    Die Basen werden entweder über einen Textstring mit importBasenString oder
    über ein Array mit importBasenArrayOfDict importiert. Das Array besteht aus Dicts
    mit den Attributen char für den Buchstaben und background für die
    Hintergrundfarbe (default weiß).
    """

    nameChanged = Signal()
    basenRenewed = Signal()
    basenInserted = Signal(int, list)
    basenRemoved = Signal(int, list)

    def __init__(self, _name, _basen: list['Base']=None):
        super().__init__()
        self._name = _name
        self._basen = _basen or []

    def importBasenArrayOfDict(self, array):
        self.basen = [Base(self, **baseobj) for baseobj in array]

    def importBasenString(self, text: str):
        pattern = re.compile(r'\s+')
        text = re.sub(pattern, '', text).upper()
        self.basen = [Base(self, char) for char in text]

    def createBasenFromString(self, text: str) -> list['Base']:
        pattern = re.compile(r'\s+')
        text = re.sub(pattern, '', text).upper()
        return [Base(self, char) for char in text]

    def createLeereBasen(self, anzahl: int):
        return [Base(self) for _ in range(anzahl)]
    
    def inAminosaeure(self):
        neueBasen = []
        for base in self.basen:
            neueBasen.append(base)
            neueBasen.append(Base(self))
            neueBasen.append(Base(self))
        return neueBasen

    def insertBasen(self, pos: int, basen: list['Base']):
        self._basen[pos:pos] = basen
        self.basenInserted.emit(pos, basen)
        return basen

    def removeBasen(self, pos: int, anzahl: int):
        muell = self._basen[pos:pos+anzahl]
        self._basen[pos:pos+anzahl] = []
        self.basenRemoved.emit(pos, muell)
        return muell

    @property
    def basen(self) -> list['Base']:
        return self._basen

    @basen.setter
    def basen(self, basen: list['Base']):
        self._basen = basen
        self.basenRenewed.emit()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.nameChanged.emit()

    def __str__(self) -> str:
        return 'Sequenz'+str(self.__hash__())

    def to_json(self) -> str:
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

    changed = Signal()

    def __init__(self, _sequenz: Sequenz, _char: str = '~', _mtxt: str = None, _versteckt: bool = False):
        super().__init__()
        self._sequenz = _sequenz
        self._char = _char
        self._versteckt = _versteckt
        self._markierung = None
        self._mtxt = _mtxt

    @property
    def char(self) -> str:
        return self._char

    @property
    def sequenz(self) -> Sequenz:
        return self._sequenz

    @property
    def markierung(self) -> 'Markierung':
        return self._markierung

    @markierung.setter
    def markierung(self, markierung: 'Markierung'):
        self._markierung = markierung
        if self._markierung:
            self._markierung.deleted.connect(self.removeMarkierung)
            self._markierung.farbeChanged.connect(self.changed.emit)
        self.changed.emit()

    @property
    def versteckt(self):
        return self._versteckt

    @versteckt.setter
    def versteckt(self, value):
        self._versteckt = value
        self.changed.emit(value)

    def getIndexInSequenz(self) -> int:
        return self.sequenz.basen.index(self)

    def getNummerInSequenzOhneLeer(self) -> int:
        nummer = 1
        for base in self.sequenz.basen:
            if base == self:
                return nummer
            if base.char != '~':
                nummer += 1

    def removeMarkierung(self):
        self.markierung = None
    
    def getCharFarbe(self) -> str:
        return self.colorMap(self.char)

    def getBoxFarbe(self) -> str:
        farbe = ''
        if self.markierung:
            farbe = self.markierung.farbe
        return farbe

    def __str__(self) -> str:
        return 'Base'+str(self.__hash__())

    def to_json(self) -> str:
        basedict = {'_char': self.char}
        if self._markierung:
            basedict['_mtxt'] = self.markierung.beschreibung
        return basedict


class Markierung(QObject):

    farbeChanged = Signal()
    nameChanged = Signal()
    deleted = Signal()

    def __init__(self, _beschreibung: str, _farbe: str) -> None:
        super().__init__()
        self._beschreibung = _beschreibung
        self._farbe = _farbe

    @property
    def beschreibung(self) -> str:
        return self._beschreibung

    @beschreibung.setter
    def beschreibung(self, beschreibung: str):
        self._beschreibung = beschreibung
        self.nameChanged.emit()

    @property
    def farbe(self) -> str:
        return self._farbe

    @farbe.setter
    def farbe(self, farbe: str):
        self._farbe = farbe
        self.farbeChanged.emit()

    def to_json(self) -> str:
        return { 'Markierung': { '_beschreibung': self._beschreibung, '_farbe': self._farbe } }
