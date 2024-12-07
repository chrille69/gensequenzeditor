import sys
import logging
import json

from PySide6.QtCore import QSize, QRectF, Qt
from PySide6.QtGui import QColor, QAction, QImage, QPainter, QPixmap, QIcon, QUndoStack, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QFileDialog, 
    QGraphicsView, QCheckBox, QToolBar,
    QSpinBox, QMessageBox
)

VERSION = "1.8"
from bioinformatik import Markierung, Sequenz, Base
from sequenzenscene import SequenzenScene
from sequenzenmodel import SequenzenModel
from dialoge import NeueSequenzDialog, BaseDialog, SequenzDialog, LinealDialog, MarkierungenVerwaltenDialog
from commands import (RemoveMarkierungCommand, changeColorMarkierungCommand, changeBeschreibungMarkierungCommand, AddMarkierungCommand,
                      RenameSequenzCommand, AminosaeureSequenzCommand, RemoveSequenzCommand, InsertSequenzCommand,
                      InsertLeerBaseCommand, EntferneBaseCommand, InsertBaseCommand
)

import resources

# Zum Erzeugen der exe:
# pyinstaller.exe -F -i resources/oszli-icon.ico -w .\sequenzeditor.py
#
# Falls sich Resourcen geändert haben:
# pyside6-rcc resources.qrc -o resources.py

log = logging.getLogger(__name__)

padding={'padx': 6, 'pady': 6}

class SequenzEditor(QMainWindow):
    """
    Der Hauptdialog

    Gilt als Controller der ganzen Anwendung.

    """

    def __init__(self, filenames):
        super().__init__()
        sequenzen = []
        versteckt = []
        markierungen = []
        if filenames:
            try:
                sequenzen, markierungen, versteckt = self.importJSONFile(filenames[0])
            except Exception as e:
                self.Fehlermeldung(str(e))

        self._sequenzmodel = SequenzenModel(self, sequenzen, markierungen, versteckt)
        self._sequenzscene = SequenzenScene(self, self.sequenzmodel())
        self._grafik = QGraphicsView(self.sequenzscene())
        self._ungespeichert = False
        self._undoStack = QUndoStack(self)

        neuAction = QAction('&Neu', self)
        neuAction.setShortcut(QKeySequence.New)
        oeffnenAction = QAction('&Öffnen', self)
        oeffnenAction.setShortcut(QKeySequence.Open)
        speichernAction = QAction('&Speichern', self)
        speichernAction.setShortcut(QKeySequence.Save)
        fastaimportAction = QAction('&FASTA importieren', self)
        fastaimportAction.setShortcut(Qt.CTRL | Qt.Key_I)
        pngexportAction = QAction('&PNG exportieren', self)
        pngexportAction.setShortcut(Qt.CTRL | Qt.Key_P)
        beendenAction = QAction('&Beenden', self)
        beendenAction.setShortcut(Qt.CTRL | Qt.Key_Q)
        neuesequenzAction = QAction('Neue &Sequenz anhängen', self)
        neuesequenzAction.setShortcut(QKeySequence.SelectAll)
        markierungenAction = QAction('&Markierungen verwalten', self)
        markierungenAction.setShortcut(Qt.CTRL | Qt.Key_M)
        undoAction = self._undoStack.createUndoAction(self)
        undoAction.setShortcut(QKeySequence.Undo)
        redoAction = self._undoStack.createRedoAction(self)
        redoAction.setShortcut(QKeySequence.Redo)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Datei')
        editMenu = menubar.addMenu('&Bearbeiten')
        fileMenu.addActions([neuAction, oeffnenAction, speichernAction])
        fileMenu.addSeparator()
        fileMenu.addAction(fastaimportAction)
        fileMenu.addAction(pngexportAction)
        fileMenu.addSeparator()
        fileMenu.addActions([beendenAction])
        editMenu.addActions([neuesequenzAction, markierungenAction, undoAction, redoAction])

        self.cb_zeilenumbrechen = QCheckBox('Zeilen umbrechen')
        self.cb_zeilenumbrechen.setChecked(True)
        self.sb_spaltenzahl = QSpinBox()
        self.sb_spaltenzahl.setRange(1,1000)
        self.sb_spaltenzahl.setValue(50)
        self.sb_spaltenzahl.setToolTip('Mit Enter bestätigen')
        self.cb_verstecktanzeigen = QCheckBox('Versteckte Spalten anzeigen')
        self.cb_verstecktanzeigen.setChecked(False)

        tools = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, tools)
        tools.addAction(undoAction)
        tools.addAction(redoAction)
        tools.addSeparator()
        tools.addWidget(self.cb_zeilenumbrechen)
        tools.addSeparator()
        tools.addWidget(self.sb_spaltenzahl)
        tools.addSeparator()
        tools.addWidget(self.cb_verstecktanzeigen)
        tools.addSeparator()
        tools.addAction(neuesequenzAction)
        tools.addAction(markierungenAction)

        self.statusBar().addPermanentWidget(QLabel(f'Version {VERSION}'))
        self.setCentralWidget(self._grafik)

        neuAction.triggered.connect(self.fileNew)
        oeffnenAction.triggered.connect(self.fileOpen)
        speichernAction.triggered.connect(self.fileSave)
        fastaimportAction.triggered.connect(self.importFasta)
        pngexportAction.triggered.connect(self.exportPNG)
        beendenAction.triggered.connect(self.close)
        neuesequenzAction.triggered.connect(self.neueSequenzDialog)
        markierungenAction.triggered.connect(self.openMarkierungenVerwalten)
        self.cb_zeilenumbrechen.stateChanged.connect(self.sequenzscene().umbruchTrigger)
        self.sb_spaltenzahl.editingFinished.connect(self._setze_spaltenzahl)
        self.cb_verstecktanzeigen.stateChanged.connect(self.sequenzscene().verstecktStateTrigger)
        self._sequenzscene.painted.connect(self.paintedTrigger)
        self._sequenzscene.baseClicked.connect(self.openBaseDialog)
        self._sequenzscene.sequenzNameClicked.connect(self.openSequenzDialog)
        self._sequenzscene.linealClicked.connect(self.openLinealDialog)
        self._sequenzscene.markierungNameClicked.connect(self.openMarkierungenVerwalten)

    def sequenzscene(self) -> SequenzenScene:
        return self._sequenzscene

    def sequenzmodel(self) -> SequenzenModel:
        return self._sequenzmodel

    def is_umbruch(self) -> bool:
        return self.cb_zeilenumbrechen.isChecked()

    def is_zeige_versteckt(self) -> bool:
        return self.cb_verstecktanzeigen.isChecked()
    
    def spaltenzahl(self) -> int:
        return self.sb_spaltenzahl.value()
    
    def closeEvent(self, event):
        if not self.ungespeichertFortfahren('Editor beenden'):
            event.ignore()
            return
        event.accept()

    def ungespeichertFortfahren(self, titel: str) -> bool:
        if self._ungespeichert:
            mb = QMessageBox()
            ret = mb.critical(self,titel,"Es gibt ungesicherte Änderungen.\nWollen Sie wirklich fortfahren?", QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return False
        self._ungespeichert = False
        return True

    def importFasta(self):
        filename = QFileDialog.getOpenFileName(self, "Open Image")[0]
        if not filename:
            return
        with open(filename) as fastafile:
            lines = fastafile.readlines()

        try:
            seqarr = []
            name = 'Unbekannt'
            text = ''
            for line in lines:
                if line[:1] == '#':
                    continue
                if line[:1] == '>':
                    if text:
                        seqarr.append(self.neueSequenz(name, text))
                        text = ''
                        name = 'Unbekannt'
                    name = line[1:].strip()
                    continue
                text += line
            seqarr.append(self.neueSequenz(name, text))
            self._sequenzmodel.addSequenzen(seqarr)
        except Exception as e:
            self.Fehlermeldung(str(e))

    def paintedTrigger(self):
        r = self._grafik.scene().itemsBoundingRect()
        self._grafik.scene().setSceneRect(r)
        self._ungespeichert = True



    def fileNew(self):
        if not self.ungespeichertFortfahren('Neue Datei beginnen'):
            return
        self._sequenzmodel.setAll()

    def fileOpen(self):
        if not self.ungespeichertFortfahren('Neue Datei laden'):
            return
        filename = QFileDialog.getOpenFileName(self, "Datei öffnen", filter='JSON-Dateien (*.json);;Alle Dateien (*.*)')[0]
        if not filename:
            return
        try:
            sequenzen, markierungen, versteckt = self.importJSONFile(filename)
            self._sequenzmodel.setAll(sequenzen, markierungen, versteckt)
        except Exception as e:
            self.Fehlermeldung(str(e))

    def importJSONFile(self, filename: str) -> list[list[Sequenz],list[Markierung],list[bool]]:
        with open(filename) as file:
            dict = json.load(file, cls=SequenzenDecoder)
        sequenzen = dict['sequenzen']
        versteckt = dict['versteckt']
        markierungen = dict['markierungen']
        mtxtdict = {}
        for m in markierungen:
            mtxtdict[m._beschreibung]=m
        for s in sequenzen:
            for b in s.basen():
                if b._mtxt:
                    b.setMarkierung(mtxtdict[b._mtxt])
                    del b._mtxt
        return sequenzen, markierungen, versteckt

    def fileSave(self):
        filename = QFileDialog.getSaveFileName(self, "Datei speichern", filter='JSON-Dateien (*.json);;Alle Dateien (*.*)')[0]
        if not filename:
            return
        with open(filename, 'w') as file:
            json.dump({
                'markierungen': self._sequenzmodel.markierungen(),
                'versteckt': self._sequenzmodel.versteckt(),
                'sequenzen': self._sequenzmodel.sequenzen()
            }, file, cls=SequenzenEncoder)
        self._ungespeichert = False

    def exportPNG(self):
        filename = QFileDialog.getSaveFileName(self, "PNG-Export nach", filter='PNG-Image (*.png);;Alle Dateien (*.*)')[0]
        if not filename:
            return

        rect_f = self._sequenzscene.sceneRect()
        img = QImage(QSize(rect_f.width(),rect_f.height()), QImage.Format_RGB888)
        img.fill(QColor('white'))
        p = QPainter(img)
        self._sequenzscene.render(p, target=QRectF(img.rect()), source=rect_f)
        p.end()
    
        saving = img.save(filename)

    def _setze_spaltenzahl(self):
        self.sequenzscene().spaltenzahlTrigger(self.sb_spaltenzahl.value())

##########################################
# Kommandos, die das Model betreffen
##########################################

    def base_leer_hinzu(self, base: Base, anzahl: int):
        self._undoStack.push(InsertLeerBaseCommand(base, anzahl))

    def base_markieren(self, base: Base, anzahl: int, markierung: Markierung):
        sequenz = base.sequenz()
        baseidx = base.getIndexInSequenz()
        sequenz.markiereBasen(baseidx, anzahl, markierung)

    def base_entfernen(self, base: Base, anzahl: int):
        self._undoStack.push(EntferneBaseCommand(base, anzahl))

    def base_sequenz_hinzu(self, base: Base, seqtext: str):
        self._undoStack.push(InsertBaseCommand(base, seqtext))

    def sequenz_hinzu(self, name: str, text: str):
        self._undoStack.push(InsertSequenzCommand(self.sequenzmodel(), name, text))

    def sequenz_umbenennen(self, sequenz: Sequenz, name: str):
        self._undoStack.push(RenameSequenzCommand(sequenz, name))

    def sequenz_in_aminosaeure(self, sequenz: Sequenz):
        self._undoStack.push(AminosaeureSequenzCommand(sequenz))

    def sequenz_entfernen(self, sequenz: Sequenz):
        self._undoStack.push(RemoveSequenzCommand(self.sequenzmodel(), sequenz))

    def basen_verstecken(self, bereich: range):
        self.sequenzmodel().addVersteckt(bereich)

    def basen_enttarnen(self, bereich: range):
        self.sequenzmodel().removeVersteckt(bereich)

    def markierung_hinzu(self, markierung: Markierung):
        self._undoStack.push(AddMarkierungCommand(self.sequenzmodel(), markierung))

    def markierung_entfernen(self, markierung: Markierung):
        self._undoStack.push(RemoveMarkierungCommand(self.sequenzmodel(), markierung))

    def markierung_farbe_setzen(self, markierung: Markierung, farbe: str):
        self._undoStack.push(changeColorMarkierungCommand(markierung, farbe))

    def markierung_name_setzen(self, markierung: Markierung, name: str):
        self._undoStack.push(changeBeschreibungMarkierungCommand(markierung, name))

##########################################
# Dialoge
##########################################

    def Fehlermeldung(self, text: str):
        msgBox = QMessageBox()
        msgBox.warning(self, 'Fehler!', text)

    def openBaseDialog(self, base):
        dlg = BaseDialog(self, base)
        dlg.baseLeerHinzu.connect(self.base_leer_hinzu)
        dlg.baseMarkieren.connect(self.base_markieren)
        dlg.baseEntfernen.connect(self.base_entfernen)
        dlg.baseSequenzHinzu.connect(self.base_sequenz_hinzu)
        dlg.exec()

    def neueSequenzDialog(self):
        dlg = NeueSequenzDialog(self)
        dlg.sequenzHinzu.connect(self.sequenz_hinzu)
        dlg.exec()

    def openSequenzDialog(self, sequenz):
        dlg = SequenzDialog(self, sequenz)
        dlg.sequenzUmbenennen.connect(self.sequenz_umbenennen)
        dlg.sequenzEntfernen.connect(self.sequenz_entfernen)
        dlg.sequenzInAmino.connect(self.sequenz_in_aminosaeure)
        dlg.exec()

    def openLinealDialog(self, spalte):
        dlg = LinealDialog(self, spalte)
        dlg.basenVerstecken.connect(self.basen_verstecken)
        dlg.basenEnttarnen.connect(self.basen_enttarnen)
        dlg.exec()

    def openMarkierungenVerwalten(self):
        dlg = MarkierungenVerwaltenDialog(self)
        dlg.markierungHinzu.connect(self.markierung_hinzu)
        dlg.markierungEntfernen.connect(self.markierung_entfernen)
        dlg.markierungFarbeSetzen.connect(self.markierung_farbe_setzen)
        dlg.markierungUmbenennen.connect(self.markierung_name_setzen)
        dlg.exec()


class SequenzenEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json') and callable(obj.to_json):
            return obj.to_json()
        else:
            return json.JSONEncoder.default(self, obj)


class SequenzenDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_sequenz, *args, **kwargs)
    
    def object_sequenz(self, dct):
        if 'Sequenz' in dct:
            seq = Sequenz(**dct['Sequenz'])
            seq.importBasenArrayOfDict(dct['Sequenz']['_basen'])
            return seq
        elif 'Markierung' in dct:
            return Markierung(**dct['Markierung'])
        return dct


if __name__ == "__main__":
    #logwidgets = logging.getLogger('widgets')
    #logleinwand = logging.getLogger('leinwandelemente')
    #ch = logging.StreamHandler()
    #logwidgets.setLevel(logging.DEBUG)
    #logwidgets.addHandler(ch)
    #logleinwand.setLevel(logging.DEBUG)
    #logleinwand.addHandler(ch)
    #log.warning('Starte Sequenzeditor')

    app = QApplication()
    app.setWindowIcon(QIcon(QPixmap(':/images/oszli-icon.ico')))
    d = SequenzEditor(sys.argv[1:2])
    d.show()
    sys.exit(app.exec())
