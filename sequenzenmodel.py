
import logging
from PySide6.QtCore import Signal, QObject
from bioinformatik import Sequenz, Markierung

log = logging.getLogger(__name__)

class SequenzenModel(QObject):

    modelchanged = Signal()

    def __init__(self, parent: QObject, sequenzen: list[Sequenz] = None, markierungen: list[Markierung] = None, versteckt: list[range] = None):
        super().__init__(parent)
        self._sequenzen = sequenzen or []
        self._markierungen = markierungen or []
        self._versteckt = versteckt or []

        self.connectMarkierungenSignals()

    def sequenzen(self):
        return self._sequenzen

    def markierungen(self):
        return self._markierungen

    def versteckt(self):
        return self._versteckt

    def setAll(self, sequenzen: list[Sequenz] = None, markierungen: list[Markierung] = None, versteckt: list[range] = None):
        self._sequenzen = sequenzen or []
        self._markierungen = markierungen or []
        self._versteckt = versteckt or []
        self.connectMarkierungenSignals()
        self.modelchanged.emit()

    def addSequenzen(self, seqarr: list[Sequenz]):
        self._sequenzen += seqarr
        self.modelchanged.emit()

    def removeSequenz(self, sequenz: Sequenz):
        self._sequenzen.remove(sequenz)
        self.modelchanged.emit()

    def addMarkierungen(self, markarr: list[Markierung]):
        self._markierungen += markarr
        self.connectMarkierungenSignals(markarr)
        self.modelchanged.emit()

    def removeMarkierung(self, markierung: Markierung):
        self._markierungen.remove(markierung)
        self.updateMarkierungen()
        self.modelchanged.emit()

    def addVersteckt(self, arr: list[range]):
        self._versteckt += arr
        self.modelchanged.emit()

    def removeVersteckt(self, arr: list[range]):
        for col in arr:
            col in self._versteckt and self._versteckt.remove(col)
        self.modelchanged.emit()
    
    def updateMarkierungen(self):
        for seq in self._sequenzen:
            seq.checkMarkierungen(self._markierungen)

    def connectMarkierungenSignals(self, markierungen=None):
        for markierung in markierungen or self._markierungen:
            markierung.markierungChanged.connect(self.modelchanged.emit)
            