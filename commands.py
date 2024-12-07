
from PySide6.QtGui import QUndoCommand
from bioinformatik import Sequenz, Markierung, Base
from sequenzenmodel import SequenzenModel


class InsertSequenzCommand(QUndoCommand):

    def __init__(self, model:SequenzenModel, name: str, txt: str):
        super(InsertSequenzCommand, self).__init__('Sequenz hinzu '+name)
        self.model = model
        self.sequenz = Sequenz(name)
        self.sequenz.importBasenString(txt)

    def redo(self):
        self.model.addSequenzen([self.sequenz])

    def undo(self):
        self.model.removeSequenz(self.sequenz)


class RemoveSequenzCommand(QUndoCommand):

    def __init__(self, model: SequenzenModel, sequenz: Sequenz):
        super(RemoveSequenzCommand, self).__init__('Sequenz entfernt '+sequenz.name())
        self.model = model
        self.sequenz = sequenz

    def redo(self):
        self.model.removeSequenz(self.sequenz)

    def undo(self):
        self.model.addSequenzen([self.sequenz])


class RenameSequenzCommand(QUndoCommand):

    def __init__(self, sequenz: Sequenz, nameneu: str):
        super(RenameSequenzCommand, self).__init__('Sequenz umbenannt '+nameneu)
        self.sequenz = sequenz
        self.nameneu = nameneu
        self.namealt = sequenz.name()

    def redo(self):
        self.sequenz.setName(self.nameneu)

    def undo(self):
        self.sequenz.setName(self.namealt)


class AminosaeureSequenzCommand(QUndoCommand):

    def __init__(self, sequenz: Sequenz):
        super(AminosaeureSequenzCommand, self).__init__('Sequenz in Aminos. '+sequenz.name())
        self.sequenz = sequenz
        self.basenalt = sequenz.basen()
        self.basenneu = sequenz.inAminosaeure()

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)


class InsertLeerBaseCommand(QUndoCommand):

    def __init__(self, base: Base, anzahl: int):
        super(InsertLeerBaseCommand, self).__init__('Insert leer')
        index = base.getIndexInSequenz()
        self.sequenz = base.sequenz()
        self.basenalt = self.sequenz.basen()
        self.basenneu = self.sequenz.insertLeer(index, anzahl)

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)


class EntferneBaseCommand(QUndoCommand):

    def __init__(self, base: Base, anzahl: int):
        super(EntferneBaseCommand, self).__init__('Entferne Basen')
        index = base.getIndexInSequenz()
        self.sequenz = base.sequenz()
        self.basenalt = self.sequenz.basen()
        self.basenneu = self.sequenz.entferneBasen(index, anzahl)

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)


class InsertBaseCommand(QUndoCommand):

    def __init__(self, base: Base, seqtext: int):
        super(InsertBaseCommand, self).__init__('Insert Basen')
        index = base.getIndexInSequenz()
        self.sequenz = base.sequenz()
        self.basenalt = self.sequenz.basen()
        self.basenneu = self.sequenz.insertBasenString(index, seqtext)

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)


class RemoveMarkierungCommand(QUndoCommand):

    def __init__(self, model: SequenzenModel, markierung: Markierung):
        super(RemoveMarkierungCommand, self).__init__('Markierung entfernt '+markierung.beschreibung())
        self.model = model
        self.markierung = markierung

    def redo(self):
        self.model.removeMarkierung(self.markierung)

    def undo(self):
        self.model.addMarkierungen([self.markierung])


class AddMarkierungCommand(QUndoCommand):

    def __init__(self, model: SequenzenModel, markierung: Markierung):
        super(AddMarkierungCommand, self).__init__('Markierung hinzu '+markierung.beschreibung())
        self.model = model
        self.markierung = markierung

    def redo(self):
        self.model.addMarkierungen([self.markierung])

    def undo(self):
        self.model.removeMarkierung(self.markierung)


class changeColorMarkierungCommand(QUndoCommand):

    def __init__(self, markierung: Markierung, farbe: str):
        super(changeColorMarkierungCommand, self).__init__('Markierung Farbe '+farbe)
        self.markierung = markierung
        self.farbeneu = farbe
        self.farbealt = markierung.farbe()

    def redo(self):
        self.markierung.setFarbe(self.farbeneu)

    def undo(self):
        self.markierung.setFarbe(self.farbealt)


class changeBeschreibungMarkierungCommand(QUndoCommand):

    def __init__(self, markierung: Markierung, name: str):
        super(changeBeschreibungMarkierungCommand, self).__init__('Markierung Name '+name)
        self.markierung = markierung
        self.nameneu = name
        self.namealt = markierung.beschreibung()

    def redo(self):
        self.markierung.setBeschreibung(self.nameneu)

    def undo(self):
        self.markierung.setBeschreibung(self.namealt)
