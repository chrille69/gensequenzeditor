import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPen
from PySide6.QtWidgets import (QColorDialog, QDialog, QGraphicsLineItem, QGraphicsRectItem,
    QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QSpinBox, QComboBox, QLineEdit, QPlainTextEdit, QWidget, QGraphicsSimpleTextItem
)

from bioinformatik import Markierung

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
    def __init__(self, parent, x, y, base, versteckt, callback):
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

class BaseDialog(QDialog):
    def __init__(self, base, markierungen):
        super().__init__()
        self._base = base
        self._markierungen = markierungen
        self._auswahltexte = ['- keine -']+[m.beschreibung() for m in markierungen]
        vbox = QVBoxLayout(self)
        self.setLayout(vbox)
        gb_leerbasen = QGroupBox('Leerbasen einfügen',self)
        gb_markierbasen = QGroupBox('Basen markieren',self)
        gb_entfernebasen = QGroupBox('Basen entfernen',self)
        gb_insertbasen = QGroupBox('Basen einfügen',self)
        nummerohne = base.getNummerInSequenzOhneLeer()
        nummermit = base.getIndexInSequenz()+1
        vbox.addWidget(QLabel(f'Base: {base.char()}'))
        vbox.addWidget(QLabel(f'Basennummer mit Leerstellen: {nummermit}'))
        vbox.addWidget(QLabel(f'Basennummer ohne Leerstellen: {nummerohne}'))
        vbox.addWidget(gb_leerbasen)
        vbox.addWidget(gb_markierbasen)
        vbox.addWidget(gb_entfernebasen)
        vbox.addWidget(gb_insertbasen)

        hbox_leerbasen = QHBoxLayout()
        gb_leerbasen.setLayout(hbox_leerbasen)
        self._sb_leeranzahl = QSpinBox()
        self._sb_leeranzahl.setRange(1,99999)
        btn_leerbasen = QPushButton('Leerbasen')
        hbox_leerbasen.addWidget(QLabel('Anzahl'))
        hbox_leerbasen.addWidget(self._sb_leeranzahl)
        hbox_leerbasen.addStretch()
        hbox_leerbasen.addWidget(btn_leerbasen)
        btn_leerbasen.clicked.connect(self.leerclick)

        hbox_markierbasen = QHBoxLayout()
        gb_markierbasen.setLayout(hbox_markierbasen)
        self._sb_markieranzahl = QSpinBox()
        self._sb_markieranzahl.setRange(1,99999)
        self._cb_markierbasen = QComboBox()
        self._cb_markierbasen.addItems(self._auswahltexte)
        hbox_markierbasen.addWidget(QLabel('Anzahl'))
        hbox_markierbasen.addWidget(self._sb_markieranzahl)
        hbox_markierbasen.addStretch()
        hbox_markierbasen.addWidget(self._cb_markierbasen)
        self._cb_markierbasen.currentIndexChanged.connect(self.markierselect)

        hbox_entfernebasen = QHBoxLayout()
        gb_entfernebasen.setLayout(hbox_entfernebasen)
        self._sb_entferneanzahl = QSpinBox()
        self._sb_entferneanzahl.setRange(1,99999)
        btn_entfernebasen = QPushButton('Entferne')
        hbox_entfernebasen.addWidget(QLabel('Anzahl'))
        hbox_entfernebasen.addWidget(self._sb_entferneanzahl)
        hbox_entfernebasen.addStretch()
        hbox_entfernebasen.addWidget(btn_entfernebasen)
        btn_entfernebasen.clicked.connect(self.entferneclick)

        hbox_insertbasen = QHBoxLayout()
        gb_insertbasen.setLayout(hbox_insertbasen)
        self._le_inserttext = QLineEdit()
        btn_insertbasen = QPushButton('Einfügen')
        hbox_insertbasen.addWidget(QLabel('Sequenztext'))
        hbox_insertbasen.addWidget(self._le_inserttext)
        hbox_insertbasen.addStretch()
        hbox_insertbasen.addWidget(btn_insertbasen)
        btn_insertbasen.clicked.connect(self.insertclick)

    def leerclick(self):
        sequenz = self._base.sequenz()
        baseidx = self._base.getIndexInSequenz()
        sequenz.insertLeer(baseidx, self._sb_leeranzahl.value())
        self.close()

    def markierselect(self):
        text = self._cb_markierbasen.currentText()
        markierung = None
        for m in self._markierungen:
            if text == m.beschreibung():
                markierung = m
                break
        sequenz = self._base.sequenz()
        baseidx = self._base.getIndexInSequenz()
        sequenz.markiereBasen(baseidx,self._sb_markieranzahl.value(), markierung)
        self.close()

    def entferneclick(self):
        anzahl = self._sb_entferneanzahl.value()
        if anzahl > 0:
            sequenz = self._base.sequenz()
            sequenz.entferneBasen(self._base, anzahl)
        self.close()

    def insertclick(self):
        seqtext = self._le_inserttext.text()
        sequenz = self._base.sequenz()
        baseidx = self._base.getIndexInSequenz()
        sequenz.insertBasenString(baseidx, seqtext)
        self.close()


class SequenzDialog(QDialog):
    def __init__(self, parent, sequenz):
        super().__init__()
        self._sequenz = sequenz
        self._parent = parent
        vbox = QVBoxLayout(self)
        self.setLayout(vbox)
        gb_umbenennen = QGroupBox('Sequenz umbenennen',self)
        gb_animo = QGroupBox('Sequenz in Aminosäure umwandeln',self)
        gb_entferne = QGroupBox('Sequenz entfernen',self)
        vbox.addWidget(gb_umbenennen)
        vbox.addWidget(gb_animo)
        vbox.addWidget(gb_entferne)

        hbox_umbenennen = QHBoxLayout()
        gb_umbenennen.setLayout(hbox_umbenennen)
        self._in_sequenzname = QLineEdit(sequenz.name())
        btn_umbenennen = QPushButton('Umbenennen')
        hbox_umbenennen.addWidget(self._in_sequenzname)
        hbox_umbenennen.addWidget(btn_umbenennen)
        btn_umbenennen.clicked.connect(self.umbenennenclick)

        hbox_amino = QHBoxLayout()
        gb_animo.setLayout(hbox_amino)
        btn_amino = QPushButton('In Aminosäure')
        hbox_amino.addStretch()
        hbox_amino.addWidget(btn_amino)
        btn_amino.clicked.connect(self.aminosaeure)

        hbox_entferne = QHBoxLayout()
        gb_entferne.setLayout(hbox_entferne)
        btn_entferne = QPushButton('Entfernen')
        hbox_entferne.addStretch()
        hbox_entferne.addWidget(btn_entferne)
        btn_entferne.clicked.connect(self.entferne)


    def umbenennenclick(self):
        self._sequenz.setName(self._in_sequenzname.text())
        self.close()

    def aminosaeure(self):
        self._sequenz.inAminosaeure()
        self.close()

    def entferne(self):
        self._parent.removeSequenz(self._sequenz)
        self.close()

class LinealDialog(QDialog):
    def __init__(self, parent, column):
        super().__init__()
        self._parent = parent
        self.column = column
        vbox = QVBoxLayout(self)
        self.setLayout(vbox)
        gb_verstecken = QGroupBox('Spalten verstecken',self)
        gb_enttarnen = QGroupBox('Spalten enttarnen',self)
        vbox.addWidget(gb_verstecken)
        vbox.addWidget(gb_enttarnen)

        hbox_verstecken = QHBoxLayout()
        gb_verstecken.setLayout(hbox_verstecken)
        self._sb_verstecken = QSpinBox()
        self._sb_verstecken.setRange(1,99999)
        btn_verstecken = QPushButton('Verstecken')
        hbox_verstecken.addWidget(QLabel('Anzahl ab hier'))
        hbox_verstecken.addWidget(self._sb_verstecken)
        hbox_verstecken.addStretch()
        hbox_verstecken.addWidget(btn_verstecken)
        btn_verstecken.clicked.connect(self.verstecken)

        hbox_enttarnen = QHBoxLayout()
        gb_enttarnen.setLayout(hbox_enttarnen)
        self._sb_enttarnen = QSpinBox()
        self._sb_enttarnen.setRange(1,99999)
        btn_enttarnen = QPushButton('Enttarnen')
        hbox_enttarnen.addWidget(QLabel('Anzahl ab hier'))
        hbox_enttarnen.addWidget(self._sb_enttarnen)
        hbox_enttarnen.addStretch()
        hbox_enttarnen.addWidget(btn_enttarnen)
        btn_enttarnen.clicked.connect(self.enttarnen)

    def verstecken(self):
        self._parent.addVersteckt(range(self.column, self.column+self._sb_verstecken.value()))
        self.close()

    def enttarnen(self):
        self._parent.removeVersteckt(range(self.column, self.column+self._sb_enttarnen.value()))
        self.close()


class NeueSequenzDialog(QDialog):
    def __init__(self, parent, neuesequenzcall):
        super().__init__(parent)
        self._neuesequenzcall = neuesequenzcall
        vbox = QVBoxLayout(self)
        self.setLayout(vbox)
        self._le_name = QLineEdit()
        self._te_sequenztext = QPlainTextEdit()
        self._btn_ok = QPushButton('OK')
        self._btn_ok.clicked.connect(self.fertig)
        vbox.addWidget(QLabel('Name:'))
        vbox.addWidget(self._le_name)
        vbox.addWidget(QLabel('Sequenztext:'))
        vbox.addWidget(self._te_sequenztext)
        vbox.addWidget(self._btn_ok)

    def fertig(self):
        self._neuesequenzcall(self._le_name.text(), self._te_sequenztext.document().toRawText())
        self.close()


class MarkierungenVerwaltenDialog(QDialog):
    def __init__(self, markierungen):
        super().__init__()
        self._markierungen = markierungen
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        btn_plus = QPushButton('+')
        btn_plus.clicked.connect(self._markierungAnhaengen)
        btn_plus.setFixedWidth(40)
        self._frame = QWidget()
        self._vboxframe = QVBoxLayout()
        self._frame.setLayout(self._vboxframe)

        vbox.addWidget(QLabel('Keine gleichen Namen verwenden!'))
        vbox.addWidget(btn_plus)
        vbox.addWidget(self._frame)
        for markierung in self._markierungen:
            mw = MarkierungWidget(self._frame, markierung, self._markierungEntfernen)
            self._vboxframe.addWidget(mw)

    def _markierungAnhaengen(self):
        farbe = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        m = Markierung(f'Unbenannt{farbe}',farbe)
        self._markierungen.append(m)
        self._vboxframe.addWidget(MarkierungWidget(self._frame, m, self._markierungEntfernen))

    def _markierungEntfernen(self, mw):
        self._markierungen.remove(mw.markierung)
        mw.setParent(None)



class MarkierungWidget(QWidget):
    def __init__(self, parent, markierung, entfernecallback):
        super().__init__(parent)
        self._markierung = markierung
        self._entfernecallback = entfernecallback
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self._le_beschreibung = QLineEdit(markierung.beschreibung())
        self._le_beschreibung.textChanged.connect(self._beschreibungAktualisieren)
        hbox.addWidget(self._le_beschreibung)

        self._farbchooserbutton = QPushButton('Farbe wählen')
        self._farbchooserbutton.clicked.connect(self._farbauswahl)
        self._farbchooserbutton.setStyleSheet(f'background-color:{self._markierung.farbe()}; padding: 5')
        hbox.addWidget(self._farbchooserbutton)

        entfernebutton = QPushButton('-')
        entfernebutton.clicked.connect(self._markierungEntfernen)
        hbox.addWidget(entfernebutton)

    def _beschreibungAktualisieren(self, *args):
        self._markierung.setBeschreibung(self._le_beschreibung.text())

    def _farbauswahl(self):
        farbe = QColorDialog.getColor(self._markierung.farbe())
        if farbe:
            self._markierung.setFarbe(farbe.name())
            self._farbchooserbutton.setStyleSheet(f'background-color:{farbe.name()};')

    def _markierungEntfernen(self):
        self._entfernecallback(self)
