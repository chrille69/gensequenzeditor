
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsSimpleTextItem

from bioinformatik import Base

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
sequenznamewidth = 200



class SequenzItem(QGraphicsRectItem):

    def __init__(self, scene, sequenz):
        super().__init__()
        scene.addItem(self)
        self._sequenz = sequenz
        self.setHandlesChildEvents(False)

    def addName(self, x, y, clickcall):
        SequenznameItem(self, x, y, self.kurzName(), sequenznamewidth, clickcall)

    def addBase(self, x, y, base, versteckt, clickcall):
        BaseItem(self, x, y, base, versteckt, clickcall)
    
    def addRoteLinie(self, x, y):
        RotelinieItem(self, x, y, basenlaenge)

    def sequenz(self):
        return self._sequenz

    def kurzName(self):
        txt = self._sequenz.name()
        w = seqfm.horizontalAdvance(txt)
        while w > sequenznamewidth:
            txt = txt[:-1]
            w = seqfm.horizontalAdvance(txt)
        if self._sequenz.name() != txt:
            txt = txt[:-3]+'...'
        return txt



class LinealItem(QGraphicsRectItem):
    def __init__(self, scene):
        super().__init__()
        scene.addItem(self)
        self.setHandlesChildEvents(False)

    def addTick(self, x, y, idx, versteckt, clickcallback):
        LinealtickItem(self, x, y, idx, versteckt, clickcallback)
    
    def addRoteLinie(self, x, y):
        RotelinieItem(self, x, y, 2*basenlaenge)



class SequenznameItem(QGraphicsRectItem):
    def __init__(self, parent, x, y, text, width, callback):
        super().__init__(x, y, width, basenlaenge, parent)
        self._callback = callback
        self._parent = parent
        self.setBrush(Qt.NoBrush)
        self.setPen(Qt.NoPen)
        gtxt = QGraphicsSimpleTextItem(text, parent)
        gtxt.setFont(seqfont)
        w =seqfm.horizontalAdvance(text)
        gtxt.setPos(x+sequenznamewidth-w, y+basenlaenge/2-seqfm.height()/2)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(brushhighlight)

    def hoverLeaveEvent(self, event):
        self.setBrush(Qt.NoBrush)

    def mousePressEvent(self, *args):
        self._callback(self._parent.sequenz())

class BaseItem(QGraphicsRectItem):
    def __init__(self, parent, x, y, base: Base, versteckt, callback):
        super().__init__(x, y, basenlaenge, basenlaenge, parent)
        self._base = base
        self._callback = callback
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
        self._callback(self._base)

class LinealtickItem(QGraphicsRectItem):
    def __init__(self, parent, x, y, idx, versteckt, callback):
        super().__init__(x, y-2*basenlaenge, basenlaenge, 2*basenlaenge, parent)
        self._idx = idx
        self._callback = callback
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
        self.setBrush(QColor('lightblue'))

    def hoverLeaveEvent(self, event):
        self.setBrush(self._brush)

    def mousePressEvent(self, *args):
        self._callback(self._idx)

class RotelinieItem(QGraphicsLineItem):
    def __init__(self, parent, x, y, length):
        super().__init__(x, y, x, y+length, parent)
        pen = QPen(QColor('red'))
        pen.setWidth(3)
        self.setPen(pen)
        self.setZValue(10)

class MarkierungItem(QGraphicsRectItem):
    def __init__(self, scene, x, y, laenge, abstand, markierung):
        super().__init__(x, y, laenge, laenge)
        self.setPen(Qt.NoPen)
        self.setBrush(QColor(markierung.farbe()))
        scene.addItem(self)
        gmark = scene.addSimpleText(markierung.beschreibung())
        gmark.setPos(x+laenge+abstand, y+laenge/3)

