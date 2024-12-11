
import logging
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

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

    Reicht Events mit Hilfe von Callbacks an den Hauptdialog weiter.
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
        self.markierungenItems = QGraphicsRectItem()
        self.sequencenItems = QGraphicsRectItem()
        self.keineSequenzText = self.createkeineSequenzenVorhanden()

        #self.keineSequenzText.setVisible(False)

        self.addItem(self.markierungenItems)
        self.addItem(self.sequencenItems)
        self.sequencenItems.setPos(0, 6*basenlaenge)
        self.markierungenItems.setPos(sequenznamewidth+rahmendicke, 2*basenlaenge)

        self.model.sequenzenChanged.connect(self.allesZeichnen)
        self.model.markierungenChanged.connect(self._markierungenZeichnen)

        self.setBackgroundBrush(Qt.white)
        self.allesZeichnen()

    @property
    def model(self):
        return self._model

    @property
    def viewmodel(self):
        return self._viewmodel

    def allesZeichnen(self):

        self._markierungenZeichnen()
        self._verstecktBemerkungZeichnen()
        self._linealZeichnen()

        for sequenz in self.model.sequenzen:
            self._sequenzZeichnen(sequenz)

    def _sequenzZeichnen(self, sequenz: Sequenz = None):
        SequenzItem(self.sequencenItems, sequenz, self.model, self.viewmodel)

    def _linealZeichnen(self):
        LinealItem(self.sequencenItems, self.model, self.viewmodel)
    
    def _verstecktBemerkungZeichnen(self):
        """Zeichnet einen Infotext, wenn keine Markierungen vorhanden sind."""

        if not self.model.versteckt:
            return
        objektid = self.addText('Es gibt versteckte Spalten')
        objektid.setDefaultTextColor(Qt.black)
        objektid.setPos(basenlaenge, rahmendicke)

    def _markierungenZeichnen(self):
        while self.vorgängerMarkierungItem:
            markierungitem = self.vorgängerMarkierungItem
            self.vorgängerMarkierungItem = self.vorgängerMarkierungItem.vorgänger
            self.removeItem(markierungitem)
    
        for markierung in self.model.markierungen:
            self.vorgängerMarkierungItem = MarkierungItem(self.markierungenItems, self.vorgängerMarkierungItem, markierung)

    def createkeineSequenzenVorhanden(self):
        """Zeichnet einen Infotext, falls keine Sequenzen vorhanden sind."""

        x = rahmendicke
        y = rahmendicke
        txt = 'Keine Sequenzen vorhanden. Bitte Sequenz erzeugen, laden oder importieren.'
        textitem = self.addText(txt)
        textitem.setDefaultTextColor(Qt.black)
        textitem.setPos(x,y)
        textitem.setTextWidth(sequenznamewidth-10)
        return textitem