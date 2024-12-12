
from PySide6.QtCore import Signal, Qt

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem
from sceneitems import basenlaenge, sequenznamewidth, rahmendicke, SequenzItem, LinealItem, MarkierungItem
from bioinformatik import Sequenz, Markierung, Base
from sequenzenmodel import SequenzenModel, SequenzenViewModel

import logging
from logdecorator import logme
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
        self.sequenzenRect = QGraphicsRectItem()
        self.sequenzenItems = QGraphicsRectItem(self.sequenzenRect)
        self.linealitem = LinealItem(self.sequenzenRect, self.model, self.viewmodel)
        self.addItem(self.markierungenItems)
        self.addItem(self.sequenzenRect)

        self.verstecktBemerkung.setPos(basenlaenge, 3*basenlaenge)
        self.keineSequenzBemerkung.setPos(sequenznamewidth+rahmendicke, 6*basenlaenge)
        self.sequenzenRect.setPos(0, 6*basenlaenge)
        self.markierungenItems.setPos(sequenznamewidth+rahmendicke, 2*basenlaenge)

        self.model.sequenzenRenewed.connect(self.sequenzenZeichnen)
        self.model.sequenzenAdded.connect(self.sequenzenAdd)
        self.model.sequenzenRemoved.connect(self.sequenzenRemove)
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

    @logme(log.debug)
    def sequenzenZeichnen(self):
        for item in self.sequenzenItems.childItems():
            item.setParentItem(None)

        if self.model.sequenzen:
            self.keineSequenzBemerkung.setVisible(False)
            for sequenz in self.model.sequenzen:
                SequenzItem(self.sequenzenItems, sequenz, self.model, self.viewmodel, self.linealitem)
        else:
            self.keineSequenzBemerkung.setVisible(True)
        self.updateBoxPos()

    def updateBoxPos(self):
        for item in self.sequenzenItems.childItems():
            item.setBoxPos()
        self.linealitem.updateTicks()
        self.linealitem.setBoxPos()

    def sequenzenAdd(self, sequenzen: list[Sequenz]):
        for sequenz in sequenzen:
            SequenzItem(self.sequenzenItems, sequenz, self.model, self.viewmodel, self.linealitem)
        self.updateBoxPos()
    
    def sequenzenRemove(self, sequenzen: list[Sequenz]):
        for item in self.sequenzenItems.childItems():
            if type(item) == SequenzItem and item.sequenz in sequenzen:
                item.setParentItem(None)
        self.updateBoxPos()
            
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
