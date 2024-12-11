
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QDialog, 
    QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QSpinBox, QComboBox, QLineEdit, QPlainTextEdit
)

from bioinformatik import Markierung, Base, Sequenz

class BaseDialog(QDialog):

    baseLeerHinzu = Signal(Base, int)
    baseEntfernen = Signal(Base, int)
    baseSequenzHinzu = Signal(Base, str)
    baseMarkieren = Signal(Base, int, Markierung)

    def __init__(self, parent, base: Base):
        super().__init__(parent)
        self.nonebasetext = '- keine -'
        self._base = base
        self._markierungen = parent.sequenzmodel().markierungen
        self._auswahltexte = [self.nonebasetext]+[m.beschreibung for m in self._markierungen]
        vbox = QVBoxLayout(self)
        self.setLayout(vbox)
        gb_leerbasen = QGroupBox('Leerbasen einfügen',self)
        gb_markierbasen = QGroupBox('Basen markieren',self)
        gb_entfernebasen = QGroupBox('Basen entfernen',self)
        gb_insertbasen = QGroupBox('Basen einfügen',self)
        nummerohne = base.getNummerInSequenzOhneLeer()
        nummermit = base.getIndexInSequenz()+1
        vbox.addWidget(QLabel(f'Base: {base.char}'))
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
        self._cb_markierbasen.setCurrentIndex(self._auswahltexte.index(self._base.markierung.beschreibung if self._base.markierung else self.nonebasetext))
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
        self.baseLeerHinzu.emit(self._base, self._sb_leeranzahl.value())
        self.close()

    def markierselect(self):
        text = self._cb_markierbasen.currentText()
        markierung = None
        for m in self._markierungen:
            if text == m.beschreibung:
                markierung = m
                break
        self.baseMarkieren.emit(self._base, self._sb_markieranzahl.value(), markierung)
        self.close()

    def entferneclick(self):
        anzahl = self._sb_entferneanzahl.value()
        if anzahl > 0:
            self.baseEntfernen.emit(self._base, anzahl)
        self.close()

    def insertclick(self):
        seqtext = self._le_inserttext.text()
        self.baseSequenzHinzu.emit(self._base, seqtext)
        self.close()


class SequenzDialog(QDialog):

    sequenzEntfernen = Signal(Sequenz)
    sequenzUmbenennen = Signal(Sequenz, str)
    sequenzInAmino = Signal(Sequenz)

    def __init__(self, parent, sequenz: Sequenz):
        super().__init__(parent)
        self._sequenz = sequenz
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
        self._in_sequenzname = QLineEdit(sequenz.name)
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
        self.sequenzUmbenennen.emit(self._sequenz, self._in_sequenzname.text())
        self.close()

    def aminosaeure(self):
        self.sequenzInAmino.emit(self._sequenz)
        self.close()

    def entferne(self):
        self.sequenzEntfernen.emit(self._sequenz)
        self.close()


class NeueSequenzDialog(QDialog):

    sequenzHinzu = Signal(Sequenz)

    def __init__(self, parent):
        super().__init__(parent)
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
        name = self._le_name.text()
        text = self._te_sequenztext.document().toRawText()
        sequenz = Sequenz(name)
        sequenz.importBasenString(text)
        self.sequenzHinzu.emit(sequenz)
        self.close()


class LinealDialog(QDialog):

    basenVerstecken = Signal(range)
    basenEnttarnen = Signal(range)

    def __init__(self, parent, column: int):
        super().__init__()
        self.model = parent.sequenzmodel()
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
        self.basenVerstecken.emit(list(range(self.column, self.column+self._sb_verstecken.value())))
        self.close()

    def enttarnen(self):
        self.basenEnttarnen.emit(list(range(self.column, self.column+self._sb_enttarnen.value())))
        self.close()

