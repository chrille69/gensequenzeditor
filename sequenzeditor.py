import sys
import logging
import json

from PySide6.QtCore import QSize, QRectF, QByteArray, Signal, Qt
from PySide6.QtGui import QColor, QAction, QImage, QPainter, QPixmap, QIcon, QUndoStack, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QFileDialog, 
    QGraphicsView, QCheckBox, QToolBar,
    QSpinBox, QMessageBox
)

VERSION = "1.7"
from bioinformatik import Markierung, Sequenz
from sequenzenscene import SequenzenScene
from dialoge import NeueSequenzDialog, BaseDialog, SequenzDialog, LinealDialog, MarkierungenVerwaltenDialog
from commands import InsertSequenzCommand

# Zum Erzeugen der exe:
# pyinstaller.exe -F -i "oszli-icon.ico" -w sequenzeditor.py

icon = """AAABAAEAMDAAAAEACACoDgAAFgAAACgAAAAwAAAAYAAAAAEACAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAB6OAAAdzoAAHg6AAB1PAAAdjwAAHc8AABzPgAAdD4AAHY+AABzPwAAcUAAAHJAAABxQQAA
cEQGAG9EBwBxRQgAb0cNAG9HDgBtSxUAaksWAGZQIQBlUSQAZVElAF5WLgBbWDMAXFgzAFlaOABZ
WzkAWFw9AFddPgBXYEQAVWJIAE9oVgBKbF4AS2xeAEtsXwBJbWAASG5jAElwZwBFcWoAOX2DADaA
iwAwg5IALYaYACaQrQAkkbAAJJGxACKTtQAgl7wAH5e9AB6YvwAbmMEAGJ3LABiezAAUodQAEKXb
ABCl3AAOp+EACqroAAir6wAIrOsAB6zsAACq+AAGre0ABq3uAAWt7wAFru8ABK7wAAWu8AAArfkA
BK/yAACu+QAAr/kAArD2AACw+QABsfcAAbH4AACx+QAAsvgAALL5AAGy+QACsvkAALL6AAGz+QAC
s/kAA7P5AACz+gAEs/kAALP7AACz/AAFtPkABrT5AAe0+QAAtP0AALT+AAm1+QAKtfkAC7X5AAm1
+gAAtf8AELb6AAC2/wAPt/kAELf6AAC3/wAUuPkAFLj6ABW5+gAYufoAGbn6ABq6+gAcuvoAHrv6
AB+7+gAivPoAJb36ACe++gAqv/oALL/6ADDA+gAxwPoAMsH6ADTC+gA3wvoANsL7ADfD+gA4w/oA
OMP7ADnD+wA7xPoAPsT7AD/F+gA/xfsAQ8b7AETG+wBEx/sAS8n7AFbM+wBXzPsAWs37AFvN+wBd
zvsAYtD7AGPQ+wBk0PsAZdH7AGjR+wBr0vwAbNL8AHDT/ABw1PwAddX8AHrW/AB61/wAfNj8AIDZ
/ACB2fwAgtn8AITa/ACG2v0AiNr9AIfb/ACI2/0Ai9z9AJLe/QCX3/0AmOD9AJ/h/QCq5f4AsOf9
ALTo/QC46v0Auer9ALzq/gC96v4Aw+3+AMbu/gDH7v4AyO7+AMnv/gDK7/4Aze/+AM3w/wDS8f4A
1/P+ANjz/gDk9/4A5ff/AOb3/wDn+P8A6vj/AOr5/wDr+f8A7Pn/AO35/wDv+v8A8fr/APH7/wD0
/P8A9fz/APb8/wD3/f8A+v3/AP3+/wD+//8A////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT15lZWVlZWVlZWVl
ZWVlXk9YZWVlZWVPT09PT09PT09PT09PT09PT09PT09PT09PZSgYGxsbGxsbGxsbGxsbKWU0Fxsb
Gh5ET09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwMDAwMDAwMDAwMJ2gxAQwMChE/T09PT09P
T09PT09PT09PT09PT09PT09PaCQHDAwMDAwMDAwMDAwMJ2gxAQwMChE/T09PT09PT09PT09PT09P
T09PT09PT09PaCQHDAwMCwQEBAQEBAQFJWgxAQwMChE/T09PT09PT09PT09PT09PT09PT09PT09P
aCQHDAwKEyorKysrKysrM2MxAQwMChE/T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFklj
Y2NjY2NjXV0xAQwMChE/T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10x
AQwMChE/T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10xAQwMChE/T09P
T09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10xAQwMChE/T09PT09PT09PT09P
T09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10xAQwMChE/T09PT09PT09PT09PT09PT09PT09P
T09PaCQHDAwLFUJPT09PT09PT10xAQwMChE/T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwL
FUJPT09PT09PT10xAQwMChE/T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09P
T10xAQwMChE/T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10xAQwMChE/
T09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10xAgwMCxA/T09PT09PT09P
T09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT1k1GR0dHB9DT09PT09PT09PT09PT09PT09P
T09PT09PaCQHDAwLFUJPT09PT09PT09JOzw8PD1OT09PT09PT09PT09PT09PT09PT09PT09PaCQH
DAwLFUJPT09PT09PT09PS0tLS0tPT09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09P
T09PT1k2ICMjIiZGT09PT09PT09PT09PT09PT09PT09PT09PaCQHDAwLFUJPT09PT09PT10wAAYG
Bw8/T09PT09PT09PT09PT09PT09PT09PT09PaCEDCwsJFEFPT09PT09PT10xAQwMChE/T09PT09P
T09PT09PT09PT09PT09PT09PVjo3ODg4OUxPT09PT09PT10yCA4ODRJAT09PT09PT09PT09PT09P
T09PT09PT09PT1hZWVlZWE9PT09PT09PT1Y6LC4uLS9JT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PUlJSUlJPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT01KTU9PT09NSkpNT09NTU1NTU1PT09PT09PT09PT09PT09PT09PT09P
T09PT09NSniHcUhPT09igoVpSE9qb29vb3BXT09PT09PT09PT09PT09PT09PT09PT09PT099vc3L
zbRrTUjNzMzNo0ivzc3Nzc1yT09PT09PT09PT09PT09PT09PT09PT09PT2zGvI6Ams24ZEqehoay
zXWczaaJio1hT09PT09PT09PT09PT09PT09PT09PT09PSKDNik1NSKfNjE1KSj6lzYNfsb5bTU1P
T09PT09PT09PT09PT09PT09PT09PT09PR7W/dk9PSobNnU9UfrDNunNPfcitR09PT09PT09PT09P
T09PT09PT09PT09PT09PRbi7dE9PTX/NoU2kzcOrhE1PTZ/NlkpPT09PT09PT09PT09PT09PT09P
T09PT09PR6jNgU9PR5jNk23NsXxVSk9PT1S2xXdPT09PT09PT09PT09PT09PT09PT09PT09PTXvN
rlNNccTAdm7NqVxNT1BPTU1nzaxcT09PT09PT09PT09PT09PT09PT09PT09PT02hy8mzzcGVSEeq
zbm3rVSZx8LAys1mT09PT09PT09PT09PT09PT09PT09PT09PT09RhJeilHlIT09gi56biFB6kpCQ
j5FaT09PT09PT09PT09PT09PT09PT09PT09PT09PT1BUT09PT09PT1FQT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09P
T09PT09PT09PT09PT09PT09PT09PT09PT09PAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAA
"""

log = logging.getLogger(__name__)

padding={'padx': 6, 'pady': 6}

class Editor(QMainWindow):
    """
    Der Hauptdialog

    Gilt als Controller der ganzen Anwendung.

    Enthält ein Array aus Sequenzen (self.sequenzen).

    Alle Ereignisse erzeugen Dialoge, denen ein oder mehrere callback-
    Funktionen übergeben werden, damit das Array von Sequenzen nur hier
    geändert wird.
    """

    neuesequenzadded = Signal

    def __init__(self, filenames):
        super().__init__()
        self._ungespeichert = False
        self.undoStack = QUndoStack(self)

        neuAction = QAction('&Neu', self)
        neuAction.triggered.connect(self.fileNew)
        neuAction.setShortcut(QKeySequence.New)
        oeffnenAction = QAction('&Öffnen', self)
        oeffnenAction.triggered.connect(self.fileOpen)
        oeffnenAction.setShortcut(QKeySequence.Open)
        speichernAction = QAction('&Speichern', self)
        speichernAction.triggered.connect(self.fileSave)
        speichernAction.setShortcut(QKeySequence.Save)
        fastaimportAction = QAction('&FASTA importieren', self)
        fastaimportAction.triggered.connect(self.importFasta)
        pngexportAction = QAction('&PNG exportieren', self)
        pngexportAction.triggered.connect(self.exportPNG)
        beendenAction = QAction('&Beenden', self)
        beendenAction.triggered.connect(self.close)

        neuesequenzAction = QAction('Neue &Sequenz anhängen', self)
        neuesequenzAction.triggered.connect(self.neueSequenzDialog)
        markierungenAction = QAction('&Markierungen verwalten', self)

        undoAction = self.undoStack.createUndoAction(self)
        undoAction.setShortcut(QKeySequence.Undo)
        redoAction = self.undoStack.createRedoAction(self)
        undoAction.setShortcut(QKeySequence.Redo)

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

        cb_zeilenumbrechen = QCheckBox('Zeilen umbrechen')
        cb_zeilenumbrechen.setChecked(True)
        sb_spaltenzahl = QSpinBox()
        sb_spaltenzahl.setRange(1,1000)
        sb_spaltenzahl.setValue(50)
        cb_verstecktanzeigen = QCheckBox('Versteckte Spalten anzeigen')

        self.sequenzen = []
        self.versteckt = []
        self.markierungen = []
        if filenames:
            try:
                self.sequenzen, self.markierungen, self.versteckt = self.importJSONFile(filenames[0])
            except Exception as e:
                self.Fehlermeldung(str(e))

        self._sequenzscene = SequenzenScene(self, self.sequenzen, self.markierungen, self.versteckt, cb_zeilenumbrechen.isChecked(), sb_spaltenzahl.value(), cb_verstecktanzeigen.isChecked())
        self._grafik = QGraphicsView(self._sequenzscene)
        cb_zeilenumbrechen.stateChanged.connect(self._sequenzscene.umbruchTrigger)
        sb_spaltenzahl.valueChanged.connect(self._sequenzscene.spaltenzahlTrigger)
        cb_verstecktanzeigen.stateChanged.connect(self._sequenzscene.verstecktStateTrigger)
        markierungenAction.triggered.connect(self.openMarkierungenVerwalten)
        self._sequenzscene.painted.connect(self.paintedTrigger)

        tools = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, tools)
        tools.addAction(undoAction)
        tools.addAction(redoAction)
        tools.addSeparator()
        tools.addWidget(cb_zeilenumbrechen)
        tools.addSeparator()
        tools.addWidget(sb_spaltenzahl)
        tools.addSeparator()
        tools.addWidget(cb_verstecktanzeigen)

        self.statusBar().addPermanentWidget(QLabel(f'Version {VERSION}'))
        self.setCentralWidget(self._grafik)



    def closeEvent(self, event):
        if not self.ungespeichertFortfahren('Editor beenden'):
            event.ignore()
            return
        event.accept()

    def ungespeichertFortfahren(self, titel):
        if self._ungespeichert:
            mb = QMessageBox()
            ret = mb.critical(self,titel,"Es gibt ungesicherte Änderungen.\nWollen Sie wirklich fortfahren?", QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return False
        self._ungespeichert = False
        return True

    def neueSequenzDialog(self):
        dlg = NeueSequenzDialog(self,self._neueSequenzDialogFertig)
        dlg.exec()

    def _neueSequenzDialogFertig(self, name, text):
        self.undoStack.push(InsertSequenzCommand(self._sequenzscene, name, text))

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
            self._sequenzscene.addSequenzen(seqarr)
        except Exception as e:
            self.Fehlermeldung(str(e))

    def paintedTrigger(self):
        r = self._grafik.scene().itemsBoundingRect()
        self._grafik.scene().setSceneRect(r)
        self._ungespeichert = True



    def fileNew(self):
        if not self.ungespeichertFortfahren('Neue Datei beginnen'):
            return
        self._sequenzscene.setAll()

    def fileOpen(self):
        if not self.ungespeichertFortfahren('Neue Datei laden'):
            return
        filename = QFileDialog.getOpenFileName(self, "Datei öffnen", filter='JSON-Dateien (*.json);;Alle Dateien (*.*)')[0]
        if not filename:
            return
        try:
            sequenzen, markierungen, versteckt = self.importJSONFile(filename)
            self._sequenzscene.setAll(sequenzen, markierungen, versteckt)
        except Exception as e:
            self.Fehlermeldung(str(e))

    def importJSONFile(self, filename):
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
                'markierungen': self._sequenzscene.markierungen(),
                'versteckt': self._sequenzscene.versteckt(),
                'sequenzen': self._sequenzscene.sequenzen()
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

##########################################
# Dialogcallbacks
##########################################

    def Fehlermeldung(self, text):
        msgBox = QMessageBox()
        msgBox.warning(self, 'Fehler!', text)

    def openBaseDialog(self, base):
        dlg = BaseDialog(self, base)
        dlg.exec()

    def openSequenzDialog(self,sequenz):
        dlg = SequenzDialog(self, sequenz)
        dlg.exec()

    def openLinealDialog(self, spalte):
        dlg = LinealDialog(self, spalte)
        dlg.exec()

    def openMarkierungenVerwalten(self):
        dlg = MarkierungenVerwaltenDialog(self.markierungen)
        dlg.exec()
        for seq in self.sequenzen:
            seq.checkMarkierungen(self.markierungen)
        self._sequenzscene.updateMarkierungen(self.markierungen)


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
    img = QImage()
    img.loadFromData(QByteArray.fromBase64(icon.encode('utf8')))
    app.setWindowIcon(QIcon(QPixmap(img)))
    d = Editor(sys.argv[1:2])
    d.show()
    sys.exit(app.exec())
