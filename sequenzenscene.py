
from PySide6.QtCore import Signal, Qt, QRect

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem
from sceneitems import basenlaenge, sequenznamewidth, rahmendicke, SequenzItem, LinealItem, MarkierungItem
from bioinformatik import Sequenz, Markierung, Base
from sequenzenmodel import SequenzenModel, SequenzenViewModel

import logging
from logger import logme
logger = logging.getLogger(__name__)

class SequenzenScene(QGraphicsScene):
    """
    Eine Sicht auf die Sequenzen

    Stellt die Sequenzen in einem Canvas dar.
    """

    baseClicked = Signal(Base)
    sequenzNameClicked = Signal(Sequenz)
    linealClicked = Signal(int)
    markierungNameClicked = Signal(Markierung)
    painted = Signal()

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
        self.painted.connect(self.recalculateSceneRect)

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

    @logme(logger.debug)
    def updateBoxPos(self):
        for item in self.sequenzenItems.childItems():
            item.setBoxPos()
        self.linealitem.updateTicks()
        self.linealitem.setBoxPos()
        self.recalculateSceneRect()

    @logme(logger.debug)
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

    @logme(logger.debug)
    def sequenzenAdd(self, sequenzen: list[Sequenz]):
        self.keineSequenzBemerkung.setVisible(False)
        for sequenz in sequenzen:
            SequenzItem(self.sequenzenItems, sequenz, self.model, self.viewmodel, self.linealitem)
        self.updateBoxPos()
    
    @logme(logger.debug)
    def sequenzenRemove(self, sequenzen: list[Sequenz]):
        if not self.model.sequenzen:
            self.keineSequenzBemerkung.setVisible(True)
        for item in self.sequenzenItems.childItems():
            if item.sequenz in sequenzen:
                self.removeItem(item)
        self.updateBoxPos()
            
    @logme(logger.debug)
    def markierungenZeichnen(self):
        while self.vorgängerMarkierungItem:
            markierungitem = self.vorgängerMarkierungItem
            self.vorgängerMarkierungItem = self.vorgängerMarkierungItem.vorgänger
            self.removeItem(markierungitem)
    
        for markierung in self.model.markierungen:
            self.vorgängerMarkierungItem = MarkierungItem(self.markierungenItems, self.vorgängerMarkierungItem, markierung)
        self.recalculateSceneRect()

    @logme(logger.debug)
    def createkeineSequenzenBemerkung(self):
        """Zeichnet einen Infotext, falls keine Sequenzen vorhanden sind."""

        txt = 'Keine Sequenzen vorhanden. Bitte Sequenz erzeugen, laden oder importieren.'
        textitem = self.addText(txt)
        textitem.setDefaultTextColor(Qt.black)
        textitem.setTextWidth(sequenznamewidth-10)
        return textitem
    
    @logme(logger.debug)
    def createVerstecktBemerkung(self):
        """Zeichnet einen Infotext, wenn Spalten versteckt sind."""

        textitem = self.addText('Es gibt versteckte Spalten')
        textitem.setDefaultTextColor(Qt.black)
        return textitem

    @logme(logger.debug)
    def pruefeVersteckt(self, _):
        self.verstecktBemerkung.setVisible(len(self.model.versteckt) != 0)

    def recalculateSceneRect(self):
        items = self.items()
        logger.info("\n"+"\n".join([str(item) for item in items]))
        logger.info(len(items))
        logger.info("--------------------------------------\n")
        self.setSceneRect(self.itemsBoundingRect())
