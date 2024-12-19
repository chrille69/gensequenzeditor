import random

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QColorDialog,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QWidget
)

from sequenzenmodel import SequenzenModel
from bioinformatik import Markierung

import resources

class MarkierungenVerwalten(QWidget):

    markierungEntfernen = Signal(Markierung)
    markierungFarbeSetzen = Signal(Markierung, str)
    markierungUmbenennen = Signal(Markierung, str)
    markierungHinzu = Signal(Markierung)

    def __init__(self, model: SequenzenModel):
        super().__init__()
        self._model = model
        self.model.markierungenChanged.connect(self.updateMarkierungen)
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        btn_plus = QPushButton()
        btn_plus.setIcon(QIcon(':/images/add.svg'))
        btn_plus.setIconSize(QSize(25,25))
        btn_plus.clicked.connect(self._markierungAnhaengen)
        btn_plus.setFixedWidth(40)

        scroll = QScrollArea()
        frame = QWidget()
        frame.setFixedWidth(250)
        scroll.setWidget(frame)
        self._vboxframe = QVBoxLayout()
        self._vboxframe.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self._vboxframe.addStretch(2)
        frame.setLayout(self._vboxframe)

        vbox.addWidget(btn_plus)
        vbox.addWidget(scroll)
        vbox.addWidget(QLabel('Keine gleichen Namen verwenden!'))
        vbox.addWidget(QLabel('Umbenennen mit Enter bestätigen.'))

    @property
    def model(self):
        return self._model
    
    @property
    def vboxframe(self):
        return self._vboxframe
    
    def updateMarkierungen(self):
        for i in reversed(range(self.vboxframe.count())): 
            item = self.vboxframe.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        for markierung in self.model.markierungen:
            mw = MarkierungWidget(markierung)
            self.vboxframe.insertWidget(0, mw, alignment=Qt.AlignTop)
            mw.markierungRemoved.connect(self._markierungEntfernen)
            mw.markierungFarbeChanged.connect(self.markierungFarbeSetzen.emit)
            mw.markierungNameChanged.connect(self.markierungUmbenennen.emit)

    def _markierungAnhaengen(self):
        farbe = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        markierung = Markierung(f'Unbenannt{farbe}',farbe)
        self.markierungHinzu.emit(markierung)

    def _markierungEntfernen(self, mw: 'MarkierungWidget'):
        self.markierungEntfernen.emit(mw.markierung)


class MarkierungWidget(QWidget):

    markierungRemoved = Signal(Markierung)
    markierungFarbeChanged = Signal(Markierung, str)
    markierungNameChanged = Signal(Markierung, str)

    def __init__(self, markierung: Markierung):
        super().__init__()
        self._markierung = markierung
        self.markierung.nameChanged.connect(self.setName)
        self.markierung.farbeChanged.connect(self.setFarbe)
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self._le_beschreibung = QLineEdit()
        self._le_beschreibung.returnPressed.connect(self._beschreibungAktualisieren)
        self._le_beschreibung.setToolTip('Mit Enter bestätigen.')
        hbox.addWidget(self._le_beschreibung)

        self._farbchooserbutton = QPushButton('Farbe wählen')
        self._farbchooserbutton.clicked.connect(self._farbauswahl)
        self._farbchooserbutton.setStyleSheet(f'background-color:{self.markierung.farbe}; padding: 5')
        hbox.addWidget(self._farbchooserbutton)

        entfernebutton = QPushButton()
        entfernebutton.setIcon(QIcon(':/images/delete.svg'))
        entfernebutton.setIconSize(QSize(25, 25))
        entfernebutton.clicked.connect(self._markierungEntfernen)
        hbox.addWidget(entfernebutton)

        self.setName()

    @property
    def markierung(self):
        return self._markierung
    
    @property
    def beschreibung(self):
        return self._le_beschreibung
    
    @property
    def farbchooserbutton(self):
        return self._farbchooserbutton
    
    def setName(self):
        self.beschreibung.setText(self.markierung.beschreibung)

    def setFarbe(self):
        self.farbchooserbutton.setStyleSheet(f'background-color:{self.markierung.farbe};')

    def _beschreibungAktualisieren(self, *args):
        self.markierungNameChanged.emit(self.markierung, self.beschreibung.text())

    def _farbauswahl(self):
        farbe = QColorDialog.getColor(self.markierung.farbe)
        if farbe:
            self.markierungFarbeChanged.emit(self.markierung, farbe.name())
            self.farbchooserbutton.setStyleSheet(f'background-color:{farbe.name()};')

    def _markierungEntfernen(self):
        self.markierungRemoved.emit(self)
