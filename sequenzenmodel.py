
import logging
from PySide6.QtCore import Signal, QObject
from bioinformatik import Sequenz, Markierung, Base

logger = logging.getLogger(__name__)


class SequenzenViewModel(QObject):
    """Model zur Ansicht der Sequenzen"""

    zeigeverstecktChanged = Signal(bool)
    spaltenzahlChanged = Signal(int)
    umbruchChanged = Signal(bool)

    def __init__(self, parent, umbruch: bool = True, spaltenzahl: int = 50, zeigeversteckt: bool = False):
        super().__init__(parent)
        self._umbruch = umbruch
        self._spaltenzahl = spaltenzahl
        self._zeigeversteckt = zeigeversteckt

    @property
    def umbruch(self) -> bool:
        "Soll ein Zeilenumbruch gemacht werden? Wenn nicht, werden die Sequenzen in einer langen Zeile angezeigt."
        return self._umbruch
    
    @umbruch.setter
    def umbruch(self, value) -> bool:
        self._umbruch = value
        self.umbruchChanged.emit(value)

    @property
    def spaltenzahl(self) -> bool:
        "Für umbruch: Wie viele Basen sollen in einer Zeile angezeigt werden."
        return self._spaltenzahl
    
    @spaltenzahl.setter
    def spaltenzahl(self, value) -> bool:
        self._spaltenzahl = value
        self.spaltenzahlChanged.emit(value)

    @property
    def zeigeversteckt(self) -> bool:
        "Sollen versteckte Basen angezeigt werden? Falls ja, sind sie grau unterlegt."
        return self._zeigeversteckt
    
    @zeigeversteckt.setter
    def zeigeversteckt(self, value) -> bool:
        self._zeigeversteckt = value
        self.zeigeverstecktChanged.emit(value)


class SequenzenModel(QObject):

    sequenzenRenewed = Signal()
    sequenzenAdded = Signal(list)
    sequenzenRemoved = Signal(list)
    markierungenChanged = Signal()
    verstecktAdded = Signal(list)
    verstecktRemoved = Signal(list)

    def __init__(self, parent: QObject, sequenzen: list[Sequenz] = None, markierungen: list[Markierung] = None, versteckt: list[int] = None):
        super().__init__(parent)
        self._sequenzen: list[Sequenz] = sequenzen or []
        self._markierungen: list[Markierung] = markierungen or []
        self._versteckt: list[int] = versteckt or []

    @property
    def sequenzen(self) -> list[Sequenz]:
        return self._sequenzen

    @property
    def markierungen(self) -> list[Markierung]:
        return self._markierungen

    @property
    def versteckt(self) -> list[bool]:
        return self._versteckt

    @property
    def maxlen(self):
        if not self.sequenzen:
            return 0
        return max([len(sequenz.basen) for sequenz in self.sequenzen])

    def getAllCopy(self):
        return self._sequenzen.copy(), self._markierungen.copy(), self.versteckt.copy()
    
    def setAll(self, sequenzen: list[Sequenz] = None, markierungen: list[Markierung] = None, versteckt: list[range] = None):
        self._sequenzen = sequenzen or []
        self._markierungen = markierungen or []
        self._versteckt = versteckt or []
        self.sequenzenRenewed.emit()
        self.markierungenChanged.emit()

    def addSequenzen(self, sequenzen: list[Sequenz]):
        self._sequenzen += sequenzen
        self.sequenzenAdded.emit(sequenzen)

    def removeSequenzen(self, sequenzen: list[Sequenz]):
        for sequenz in sequenzen:
            try:
                self._sequenzen.remove(sequenz)
            except ValueError:
                pass
        self.sequenzenRemoved.emit(sequenzen)

    def addMarkierungen(self, markarr: list[Markierung]):
        self._markierungen += markarr
        self.markierungenChanged.emit()

    def removeMarkierung(self, markierung: Markierung):
        self._markierungen.remove(markierung)
        self.markierungenChanged.emit()

    def addVersteckt(self, arr: list[int]):
        self._versteckt += arr
        self.verstecktAdded.emit(arr)

    def removeVersteckt(self, arr: list[int]):
        for col in arr:
            col in self._versteckt and self._versteckt.remove(col)
        self.verstecktRemoved.emit(arr)

    def markierteBasen(self, markierung: Markierung) -> list[Base]:
        basen = []
        for sequenz in self.sequenzen:
            for base in sequenz.basen:
                if base.markierung == markierung:
                    basen.append(base)
        return basen