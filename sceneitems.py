
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsSimpleTextItem, QGraphicsItem

from bioinformatik import Base, Sequenz, Markierung

basefont = QFont()
basefont.setFamily('Courier')
basefont.setBold(QFont.Bold)
basefont.setPointSize(13)
basefm = QFontMetrics(basefont)
seqfont = QFont()
seqfont.setFamily('Helvetica')
seqfont.setPointSize(12)
seqfm = QFontMetrics(seqfont)
basenlaenge = 20
brushversteckt = QColor('lightgray')
brushhighlight = QColor('lightblue')
penhighlight = QColor('red')
sequenznamewidth = 200



class SequenzItem(QGraphicsRectItem):

    def __init__(self, sequenz: Sequenz, index: int = 0, maxindex: int = 0):
        super().__init__()
        self._sequenz = sequenz
        self._index = index
        self._maxindex = maxindex

    def addName(self, x: int, y: int):
        SequenznameItem(self, x, y, self._sequenz)

    def addBase(self, x: int, y: int, base: Base, versteckt: bool):
        BaseItem(self, x, y, base, versteckt)

    def addRoteLinie(self, x: int, y: int):
        RotelinieItem(self, x, y, basenlaenge)

    def sequenz(self) -> Sequenz:
        return self._sequenz


class LinealItem(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setHandlesChildEvents(False)

    def addTick(self, x: int, y: int, idx: int, versteckt: bool):
        LinealtickItem(self, x, y, idx, versteckt)
    
    def addRoteLinie(self, x: int, y: int):
        RotelinieItem(self, x, y, 2*basenlaenge)


class SequenznameItem(QGraphicsRectItem):

    def __init__(self, parent, x: int, y: int, sequenz: Sequenz):
        super().__init__ (x, y, sequenznamewidth, basenlaenge, parent)
        self._x = x
        self._y = y
        self._sequenz = sequenz
        self.setBrush(Qt.NoBrush)
        self.setPen(Qt.NoPen)
        self.gtxt = QGraphicsSimpleTextItem(parent)
        self.gtxt.setFont(seqfont)
        self.setName()
        self._sequenz.namechanged.connect(self.setName)
        self.setAcceptHoverEvents(True)

    def setName(self):
        text = self.kurzName()
        self.gtxt.setText(text)
        w = seqfm.horizontalAdvance(text)
        self.gtxt.setPos(self._x+sequenznamewidth-w, self._y+basenlaenge/2-seqfm.height()/2)

    def kurzName(self) -> str:
        txt = self._sequenz.name()
        w = seqfm.horizontalAdvance(txt)
        while w > sequenznamewidth:
            txt = txt[:-1]
            w = seqfm.horizontalAdvance(txt)
        if self._sequenz.name() != txt:
            txt = txt[:-3]+'...'
        return txt

    def hoverEnterEvent(self, event):
        self.setBrush(brushhighlight)

    def hoverLeaveEvent(self, event):
        self.setBrush(Qt.NoBrush)

    def mousePressEvent(self, *args):
        self.scene().sequenzNameClicked.emit(self.parentItem().sequenz())


class BaseItem(QGraphicsRectItem):

    def __init__(self, parent, x: int, y: int, base: Base, versteckt: bool):
        super().__init__(x, y, basenlaenge, basenlaenge, parent)
        self._base = base
        self._versteckt = versteckt
        self.brush = Qt.NoBrush
        char = base.char()
        self.setBoxfarbe()
        self.setPen(Qt.NoPen)
        gchar = QGraphicsSimpleTextItem(char, parent)
        gchar.setFont(basefont)
        gcharw = basefm.horizontalAdvance(char)
        gcharh = basefm.height()
        gchar.setPos(x+basenlaenge/2-gcharw/2, y+basenlaenge/2-gcharh/2)
        gchar.setBrush(QColor(base.getCharFarbe()))
        self.setAcceptHoverEvents(True)
        base.changed.connect(self.setBoxfarbe)

    def setBoxfarbe(self):
        boxfarbe = self._base.getBoxFarbe()
        if boxfarbe:
            self.brush = QColor(boxfarbe)
        else:
            self.brush = Qt.NoBrush
        if self._versteckt:
            self.brush = brushversteckt
        self.setBrush(self.brush)
        
    def hoverEnterEvent(self, event):
        self.setBrush(brushhighlight)

    def hoverLeaveEvent(self, event):
        self.setBrush(self.brush)

    def mousePressEvent(self, *args):
        self.scene().baseClicked.emit(self._base)


class LinealtickItem(QGraphicsRectItem):

    def __init__(self, parent: LinealItem, x: int, y: int, idx: int, versteckt: bool):
        super().__init__(x, y-2*basenlaenge, basenlaenge, 2*basenlaenge, parent)
        self._idx = idx
        self._brush = Qt.NoBrush
        if versteckt:
            self._brush = brushversteckt
        self.setBrush(self._brush)
        self.setPen(Qt.NoPen)
        self.setZValue(-10)
        nummer = idx+1
        marke = '∙'
        gcharh = 0
        if nummer%10 == 0:
            marke = '|'
            gcharh = basefm.descent()
            gnummer = QGraphicsSimpleTextItem(str(nummer), parent)
            gnummer.setFont(basefont)
            gnummerw = basefm.horizontalAdvance(str(nummer))
            gnummer.setPos(x+basenlaenge/2-gnummerw/2, y-basenlaenge*2)
        gchar = QGraphicsSimpleTextItem(marke, parent)
        gchar.setFont(basefont)
        gcharw = basefm.horizontalAdvance(marke)
        gchar.setPos(x+basenlaenge/2-gcharw/2, y-basenlaenge/2-gcharh-4)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(brushhighlight)

    def hoverLeaveEvent(self, event):
        self.setBrush(self._brush)

    def mousePressEvent(self, *args):
        self.scene().linealClicked.emit(self._idx)


class RotelinieItem(QGraphicsLineItem):

    def __init__(self, parent: LinealItem, x: int, y: int, length: int):
        super().__init__(x, y, x, y+length, parent)
        pen = QPen(QColor('red'))
        pen.setWidth(3)
        self.setPen(pen)
        self.setZValue(10)


class MarkierungItem(QGraphicsRectItem):

    def __init__(self, vorgänger: 'MarkierungItem', markierung: Markierung):
        super().__init__()
        self.markierung = markierung
        self.vorgänger = vorgänger
        self.setRect(0, 0, basenlaenge, 20)
        self.setPen(Qt.NoPen)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.nameItem = QGraphicsTextItem(self)
        self.nameItem.setDefaultTextColor(QColor('black'))
        self.nameItem.setFont(seqfont)
        self.nameItem.setPos(basenlaenge, 0)
        self.setFarbe()
        self.setName()
        self.setX(True)
        self.markierung.farbeChanged.connect(self.setFarbe)
        self.markierung.nameChanged.connect(self.setName)
        if self.vorgänger:
            self.vorgänger.nameItem.document().contentsChanged.connect(self.setX)
    
    def sceneRight(self):
        "Gibt den x-Wert der rechten Kante des Items zurück."

        rect = self.sceneBoundingRect()
        textrect = self.nameItem.boundingRect()
        return rect.x() + rect.width() + basenlaenge + textrect.width()
    
    def setX(self, nosignal: bool = False):
        "Setzt auf der Grundlage des Vorgängers die x-Position."

        x = sequenznamewidth+basenlaenge
        if self.vorgänger:
            x = self.vorgänger.sceneRight()
        self.setPos(x, basenlaenge)
        nosignal or self.nameItem.document().contentsChanged.emit()

    def setFarbe(self):
        "Setzt die Farbe auf Grundlage der Markerung."

        self.setBrush(QColor(self.markierung.farbe()))

    def setName(self):
        "Setzt den Text auf Grundlage der Beschreibung der Markierung."

        self.nameItem.setPlainText(self.markierung.beschreibung())

