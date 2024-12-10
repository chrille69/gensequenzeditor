
import logging
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

from PySide6.QtWidgets import QGraphicsScene
from sceneitems import basenlaenge, sequenznamewidth, SequenzItem, LinealItem, MarkierungItem
from bioinformatik import Sequenz, Markierung, Base
from sequenzenmodel import SequenzenModel, SequenzenViewModel

logging.basicConfig()
log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)


class SequenzenScene(QGraphicsScene):
    """
    Eine Sicht auf die Sequenzen

    Stellt die Sequenzen in einem Canvas dar.

    Reicht Events mit Hilfe von Callbacks an den Hauptdialog weiter.
    """

    baseClicked = Signal(Base)
    sequenzNameClicked = Signal(Sequenz)
    linealClicked = Signal(int)
    markierungNameClicked = Signal(Markierung)

    fontBase = ('Courier', 14, 'bold')
    fontLineal = ('Courier', 12, 'bold')
    rahmendicke = 20
    abstandMarkierungen = 3
    markierunglaenge = 50

    def __init__(self, parent, sequenzenmodel: SequenzenModel, sequenzenviewmodel: SequenzenViewModel):
        super().__init__(parent)
        self._model = sequenzenmodel
        self._viewmodel = sequenzenviewmodel
        self.vorgängerMarkierungItem: MarkierungItem = None

        self._ystart = self.rahmendicke+2*basenlaenge
        self._maxlen = 0

        self._linealitem = None
        self._sequenzitems = {}

        self.model.sequenzenChanged.connect(self.allesNeuZeichnen)
        self.model.verstecktChanged.connect(self.allesNeuZeichnen)
        self.model.markierungenChanged.connect(self._markierungenZeichnen)
        self.viewmodel.changed.connect(self.allesNeuZeichnen)
        self.setBackgroundBrush(Qt.white)
        self.allesNeuZeichnen()

    @property
    def model(self):
        return self._model

    @property
    def viewmodel(self):
        return self._viewmodel

    def _emptyCanvas(self):
        """Leert die Leinwand"""

        log.debug('_emptyCanvas Start')

        self._linealitem = None
        self._sequenzitems = {}
        self.vorgängerMarkierungItem = None
        self.clear()

        log.debug('_emptyCanvas Ende')

    def allesNeuZeichnen(self):
        """Zeichnet alles neu!
        
        * sequenzen: Ein Array des Typs Sequenz
        * markierungen: Ein Array des Typs Markierung
        * umbruch: Boolean. Gibt an, ob die Sequenzen umgebrochen werden sollen.
        * spaltenzahl: Die Zahl der Spalten, falls umgebrochern werden soll.
        * versteckt: Ein Array, das die Spaltennummern enthält, die versteckt werden sollen.
        * zeigeversteckt: Boolean. Gibt an, ob die versteckten Spalten ausgeblendet oder ausgegraut werden sollen."""

        log.debug('allesNeuZeichnen Start')
        log.debug(self.sender())

        self._emptyCanvas()
        self._markierungenZeichnen()
        self._maxlenBerechnen()
        self._verstecktBemerkungZeichnen()
        self._linealZeichnen()

        if not self.model.sequenzen:
            self._keineSequenzenVorhanden()
            return
        
        for sequenz in self.model.sequenzen:
            self._sequenzZeichnen(sequenz)
            sequenz.basenRenewed.connect(self._sequenzZeichnenTrigger)
            sequenz.basenInserted.connect(self._sequenzZeichnenTrigger)
            sequenz.basenRemoved.connect(self._sequenzZeichnenTrigger)

        log.debug('allesNeuZeichnen Ende')

    def _sequenzZeichnenTrigger(self):
        sequenz = self.sender()
        self._sequenzZeichnen(sequenz)

    def _sequenzZeichnen(self, sequenz: Sequenz = None):
        """Zeichnet eine Sequenz.

        * seqidx: Die Nummer im Sequenzarray self.sequenzen

        Soll nur Aufgerufen, wenn in einer Sequenz Basen hinzugefügt
        oder entfernt wurden. Oder wenn Basen mit einer anderen Markierung
        markiert wurden. Bei allen anderen Operationen muss sequenzenNeuZeichnen
        aufgerufen werden.
        """

        if not sequenz:
            return
        
        if self._maxlenBerechnen():
            self._linealZeichnen()

        row = self.model.sequenzen.index(sequenz)
        if row in self._sequenzitems:
            self.removeItem(self._sequenzitems[row])
        sequenzitem = SequenzItem(sequenz)
        self.addItem(sequenzitem)
        self._sequenzitems[row] = sequenzitem


        if not sequenz.basen:
            self._sequenznameZeichnen(sequenzitem, 0, row)
            return

        rotelinieschonda = False
        col = 0
        for basidx in range(len(sequenz.basen)):
            # Weil einige Basen versteckt sein können, ist die Spalte col
            # nicht mir dem Basenindex basidx identisch.

            base = sequenz.basen[basidx]

            # Hier wird entschieden, ob die rote Linie für versteckte Sequenzen
            # gezeichnet werden soll.
            aktuellversteckt = basidx in self.model.versteckt
            if aktuellversteckt and not self.viewmodel.zeigeversteckt:
                if not rotelinieschonda:
                    self._baseRoteLinieZeichnen(sequenzitem, col, row)
                    rotelinieschonda = True
                continue

            if self.viewmodel.umbruch and col % self.viewmodel.spaltenzahl == 0 or not self.viewmodel.umbruch and col == 0:
                # Bei einer neuen Zeile muss der Sequenzname neu gezeichnet werden.
                self._sequenznameZeichnen(sequenzitem, col, row)
            
            self._baseZeichnen(sequenzitem, col, row, base, aktuellversteckt)
            col += 1
            rotelinieschonda = False

    def _linealZeichnen(self):
        """Zeichnet das Lineal über den Sequenzen"""
        
        if self._linealitem:
            self.removeItem(self._linealitem)
        self._linealitem = LinealItem()
        self.addItem(self._linealitem)
        col = 0
        rotelinieschonda = False
        for i in range(self._maxlen):

            aktuellversteckt = i in self.model.versteckt
            if aktuellversteckt and not self.viewmodel.zeigeversteckt:
                    if not rotelinieschonda:
                        self._linealRoteLinieZeichnen(self._linealitem, col)
                        rotelinieschonda = True
                    continue

            # Eine Instanz der Klasse Linealtickobjekt zeichnet automatisch das Linealelement
            self._linealtickZeichnen(self._linealitem, i, col, aktuellversteckt)
            col += 1
            rotelinieschonda = False

    def _verstecktBemerkungZeichnen(self):
        """Zeichnet einen Infotext, wenn keine Markierungen vorhanden sind."""

        if not self.model.versteckt:
            return
        objektid = self.addText('Es gibt versteckte Spalten')
        objektid.setDefaultTextColor(Qt.black)
        objektid.setPos(basenlaenge,self.rahmendicke)

    def _markierungenZeichnen(self):
        while self.vorgängerMarkierungItem:
            markierungitem = self.vorgängerMarkierungItem
            self.vorgängerMarkierungItem = self.vorgängerMarkierungItem.vorgänger
            self.removeItem(markierungitem)
    
        for markierung in self.model.markierungen:
            self.vorgängerMarkierungItem = MarkierungItem(self.vorgängerMarkierungItem, markierung)
            self.addItem(self.vorgängerMarkierungItem)

#################################################################
# elementare Funktionen zum Zeichnen
#################################################################

    def _sequenznameZeichnen(self, sequenzitem: SequenzItem, col: int, seqidx: int):
        """Zeichnet den Sequenznamen
        
        Für den Sequenznamen wird ein Platz von self.raumFuerSequenznamen reserviert.
        Der Sequenzname wird verkürzt, falls er zu lang ist"""

        x, y = self._xyBaseFuerColRow(col, seqidx)
        sequenzitem.addName(0, y)

    def _keineSequenzenVorhanden(self):
        """Zeichnet einen Infotext, falls keine Sequenzen vorhanden sind."""

        x = self.rahmendicke
        y = self.rahmendicke
        txt = 'Keine Sequenzen vorhanden. Bitte Sequenz erzeugen, laden oder importieren.'
        objektid = self.addText(txt)
        objektid.setDefaultTextColor(Qt.black)
        objektid.setPos(x,y)
        objektid.setTextWidth(sequenznamewidth-10)

    def _baseZeichnen(self, sequenzitem: SequenzItem, col: int, seqidx: int, base: Base, versteckt: bool):
        """Zeichnet die Base mit dahintergelegten Rechteck, das bei Mouseover gehighlited werden kann."""

        x, y = self._xyBaseFuerColRow(col, seqidx)
        sequenzitem.addBase(x, y, base, versteckt)

    def _baseRoteLinieZeichnen(self, sequenzitem: SequenzItem, basidx: int, seqidx: int):
        """Zeichnet die rote Linie einer versteckten Base"""

        x, y = self._xyBaseFuerColRow(basidx, seqidx)
        sequenzitem.addRoteLinie(x, y)

    def _linealtickZeichnen(self, linealitem: LinealItem, idx: int, col: int, versteckt: bool):
        """Zeichnet dein Linealtick mit dahintergelegten Rechteck, das bei Mouseover gehighlited werden kann."""

        x, y = self._xyBaseFuerColRow(col, 0)
        linealitem.addTick(x, y, idx, versteckt)

    def _linealRoteLinieZeichnen(self, linealitem: LinealItem, col: int):
        """Zeichnet die rote Linie eines versteckten Linealticks"""

        x, y = self._xyLinealFuerCol(col)
        linealitem.addRoteLinie(x, y)

#########################################################
# Koordinatenfunktionen
#########################################################

    def _koordinaten(self, col: int, row: int) -> tuple[int,int]:
        "Wandelt col,row in x,y der Leinwand um"
        return [ col*basenlaenge+sequenznamewidth+self.rahmendicke, row*basenlaenge+self._ystart ]
    
    def _rowMitUmbruchBerechnen(self, col: int, row: int) -> int:
        "Berechnet die Zeile, wenn die Sequenzen umgebrochen werden"
        return int(col/self.viewmodel.spaltenzahl) * (len(self.model.sequenzen)+2.5) + row

    def _colrowHolen(self, baseidx: int, sequenzidx: int) -> tuple[int,int]:
        "Berechnet aus der Sequenznummer und der Basennummer die Zeile und Spalte"
        if self.viewmodel.umbruch:
            row = self._rowMitUmbruchBerechnen(baseidx, sequenzidx)
            col = baseidx % self.viewmodel.spaltenzahl
        else:
            row = sequenzidx
            col = baseidx
        return (col, row)

    def _xyBaseFuerColRow(self, col: int, row: int) -> tuple[int,int]:
        """
        Gibt die Leinwand-XY-Koordinaten für eine Base zurück.
        Es handelt sich um die linke, obere Ecke einer Basenbox.
        """

        (col2,row2) = self._colrowHolen(col, row)
        row2 += 2
        return self._koordinaten(col2, row2)

    def _xyLinealFuerCol(self, col: int) -> tuple[int,int]:
        """
        Gibt die Leinwand-XY-Koordinaten für ein Linealtick zurück.
        Es handelt sich um die linke, obere Ecke einer Linealbox.
        """

        (col2,row2) = self._colrowHolen(col, 0)
        return self._koordinaten(col2, row2)

    def _maxlenBerechnen(self) -> bool:
        """
        Schaut, ob sich die Maximallänge aller Sequenzen
        geändert hat. Falls das der Fall ist, wird True
        zurückgegeben.
        """

        maxlen = 0
        for sequenz in self.model.sequenzen:
            seqlen = len(sequenz.basen)
            if maxlen < seqlen:
                maxlen = seqlen
        if maxlen != self._maxlen:
            self._maxlen = maxlen
            return True
        return False
