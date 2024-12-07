
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsSimpleTextItem

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

    def __init__(self, sequenz: Sequenz):
        super().__init__()
        self._sequenz = sequenz
        self.setHandlesChildEvents(False)

    def addName(self, x: int, y: int):
        SequenznameItem(self, x, y, self.kurzName(), sequenznamewidth)

    def addBase(self, x: int, y: int, base: Base, versteckt: bool):
        BaseItem(self, x, y, base, versteckt)

    def addRoteLinie(self, x: int, y: int):
        RotelinieItem(self, x, y, basenlaenge)

    def sequenz(self) -> Sequenz:
        return self._sequenz

    def kurzName(self) -> str:
        txt = self._sequenz.name()
        w = seqfm.horizontalAdvance(txt)
        while w > sequenznamewidth:
            txt = txt[:-1]
            w = seqfm.horizontalAdvance(txt)
        if self._sequenz.name() != txt:
            txt = txt[:-3]+'...'
        return txt


class LinealItem(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setHandlesChildEvents(False)

    def addTick(self, x: int, y: int, idx: int, versteckt: bool):
        LinealtickItem(self, x, y, idx, versteckt)
    
    def addRoteLinie(self, x: int, y: int):
        RotelinieItem(self, x, y, 2*basenlaenge)


class SequenznameItem(QGraphicsRectItem):

    def __init__(self, parent, x: int, y: int, text: str, width: int):
        super().__init__ (x, y, width, basenlaenge, parent)
        self.setBrush(Qt.NoBrush)
        self.setPen(Qt.NoPen)
        gtxt = QGraphicsSimpleTextItem(text, parent)
        gtxt.setFont(seqfont)
        w = seqfm.horizontalAdvance(text)
        gtxt.setPos(x+sequenznamewidth-w, y+basenlaenge/2-seqfm.height()/2)

        self.setAcceptHoverEvents(True)

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
        self.brush = Qt.NoBrush
        char = base.char()
        boxfarbe = base.getBoxFarbe()
        if boxfarbe:
            self.brush = QColor(boxfarbe)
        if versteckt:
            self.brush = brushversteckt
        self.setBrush(self.brush)
        self.setPen(Qt.NoPen)
        gchar = QGraphicsSimpleTextItem(char, parent)
        gchar.setFont(basefont)
        gcharw = basefm.horizontalAdvance(char)
        gcharh = basefm.height()
        gchar.setPos(x+basenlaenge/2-gcharw/2, y+basenlaenge/2-gcharh/2)
        gchar.setBrush(QColor(base.getCharFarbe()))
        self.setAcceptHoverEvents(True)

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

    def __init__(self, x: int, y: int, laenge: int, abstand: int, markierung: Markierung):
        super().__init__(x, y, laenge, laenge)
        self.markierung = markierung
        self.farbe = QColor(markierung.farbe())
        self.setPen(Qt.NoPen)
        self.setBrush(self.farbe)
        markierungColorItem = MarkierungColorItem(x, y, laenge, markierung, self)
        markierungNameItem = MarkierungNameItem(markierung, self)
        markierungNameItem.setPos(x+laenge+abstand, y)


class MarkierungColorItem(QGraphicsRectItem):
    def __init__(self, x: int, y: int, laenge: int, markierung: Markierung, parent: MarkierungItem):
        super().__init__(x, y, laenge, laenge, parent)
        self.markierung = markierung
        self.farbe = QColor(markierung.farbe())
        self.setPen(Qt.NoPen)
        self.setBrush(self.farbe)


class MarkierungNameItem(QGraphicsSimpleTextItem):

    def __init__(self, markierung: Markierung, parent: MarkierungItem):
        super().__init__(markierung.beschreibung(), parent)
        self.markierung = markierung
        self.backgroundBrush = Qt.NoBrush
        self.setFont(seqfont)
        self.setAcceptHoverEvents(True)

    def paint(self, painter, option, widget):
        painter.fillRect(option.rect, self.backgroundBrush)
        return super().paint(painter, option, widget)

    def hoverEnterEvent(self, event):
        self.backgroundBrush = brushhighlight
        self.update()

    def hoverLeaveEvent(self, event):
        self.backgroundBrush = Qt.NoBrush
        self.update()

    def mousePressEvent(self, *args):
        self.scene().markierungNameClicked.emit(self.markierung)
