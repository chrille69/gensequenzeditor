
import logging
from PySide6.QtCore import Signal, Qt

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem
from sceneitems import basenlaenge, sequenznamewidth, rahmendicke, SequenzItem, LinealItem, MarkierungItem
from bioinformatik import Sequenz, Markierung, Base
from sequenzenmodel import SequenzenModel, SequenzenViewModel

logging.basicConfig()
log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)


class SequenzenScene(QGraphicsScene):
    """
    Eine Sicht auf die Sequenzen

    Stellt die Sequenzen in einem Canvas dar.
    """

    baseClicked = Signal(Base)
    sequenzNameClicked = Signal(Sequenz)
    linealClicked = Signal(int)
    markierungNameClicked = Signal(Markierung)

    fontBase = ('Courier', 14, 'bold')
    fontLineal = ('Courier', 12, 'bold')
    abstandMarkierungen = 3
    markierunglaenge = 50

    def __init__(self, parent, sequenzenmodel: SequenzenModel, sequenzenviewmodel: SequenzenViewModel):
        super().__init__(parent)
        self._model = sequenzenmodel
        self._viewmodel = sequenzenviewmodel
        self.vorgängerMarkierungItem: MarkierungItem = None
        self.keineSequenzBemerkung = self.createkeineSequenzenBemerkung()
        self.verstecktBemerkung = self.createVerstecktBemerkung()
        self.markierungenItems = QGraphicsRectItem()
        self.sequencenItems = QGraphicsRectItem()
        self.addItem(self.markierungenItems)
        self.addItem(self.sequencenItems)

        self.verstecktBemerkung.setPos(basenlaenge, 3*basenlaenge)
        self.keineSequenzBemerkung.setPos(sequenznamewidth+rahmendicke, 6*basenlaenge)
        self.sequencenItems.setPos(0, 6*basenlaenge)
        self.markierungenItems.setPos(sequenznamewidth+rahmendicke, 2*basenlaenge)

        self.model.sequenzenChanged.connect(self.sequenzenZeichnen)
        self.model.markierungenChanged.connect(self.markierungenZeichnen)
        self.model.verstecktAdded.connect(self.pruefeVersteckt)
        self.model.verstecktRemoved.connect(self.pruefeVersteckt)

        self.verstecktBemerkung.setVisible(len(self.model.versteckt) != 0)
        self.setBackgroundBrush(Qt.white)
        self.sequenzenZeichnen()
        self.markierungenZeichnen()

    @property
    def model(self):
        return self._model

    @property
    def viewmodel(self):
        return self._viewmodel

    def sequenzenZeichnen(self):
        for item in self.sequencenItems.childItems():
            item.setParentItem(None)

        linealitem = LinealItem(self.sequencenItems, self.model, self.viewmodel)
        if self.model.sequenzen:
            self.keineSequenzBemerkung.setVisible(False)
            for sequenz in self.model.sequenzen:
                SequenzItem(self.sequencenItems, sequenz, self.model, self.viewmodel, linealitem)
        else:
            self.keineSequenzBemerkung.setVisible(True)

    def markierungenZeichnen(self):
        while self.vorgängerMarkierungItem:
            markierungitem = self.vorgängerMarkierungItem
            self.vorgängerMarkierungItem = self.vorgängerMarkierungItem.vorgänger
            self.removeItem(markierungitem)
    
        for markierung in self.model.markierungen:
            self.vorgängerMarkierungItem = MarkierungItem(self.markierungenItems, self.vorgängerMarkierungItem, markierung)

    def createkeineSequenzenBemerkung(self):
        """Zeichnet einen Infotext, falls keine Sequenzen vorhanden sind."""

        txt = 'Keine Sequenzen vorhanden. Bitte Sequenz erzeugen, laden oder importieren.'
        textitem = self.addText(txt)
        textitem.setDefaultTextColor(Qt.black)
        textitem.setTextWidth(sequenznamewidth-10)
        return textitem
    
    def createVerstecktBemerkung(self):
        """Zeichnet einen Infotext, wenn Spalten versteckt sind."""

        textitem = self.addText('Es gibt versteckte Spalten')
        textitem.setDefaultTextColor(Qt.black)
        return textitem

    def pruefeVersteckt(self):
        self.verstecktBemerkung.setVisible(len(self.model.versteckt) != 0)
