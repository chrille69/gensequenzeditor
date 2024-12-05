from PySide6.QtGui import QUndoCommand
from bioinformatik import Sequenz


class InsertSequenzCommand(QUndoCommand):
    def __init__(self, sequenzenscene, name: str, txt: str):
        super(InsertSequenzCommand, self).__init__('Sequenz hinzu '+name)
        self.sequenzenscene = sequenzenscene
        self.sequenz = Sequenz(name)
        self.sequenz.importBasenString(txt)

    def redo(self):
        self.sequenzenscene.addSequenzen([self.sequenz])

    def undo(self):
        self.sequenzenscene.removeSequenz(self.sequenz)


class RemoveSequenzCommand(QUndoCommand):
    def __init__(self, editor, sequenz):
        super(RemoveSequenzCommand, self).__init__('Sequenz entfernt '+sequenz.name())
        self.sequenzenscene = editor._sequenzscene
        self.sequenz = sequenz

    def redo(self):
        self.sequenzenscene.removeSequenz(self.sequenz)

    def undo(self):
        self.sequenzenscene.addSequenzen([self.sequenz])

class RenameSequenzCommand(QUndoCommand):
    def __init__(self, sequenz, nameneu):
        super(RenameSequenzCommand, self).__init__('Sequenz umbenannt '+nameneu)
        self.sequenz = sequenz
        self.nameneu = nameneu
        self.namealt = sequenz.name()

    def redo(self):
        self.sequenz.setName(self.nameneu)

    def undo(self):
        self.sequenz.setName(self.namealt)

class AminosaeureSequenzCommand(QUndoCommand):
    def __init__(self, sequenz):
        super(AminosaeureSequenzCommand, self).__init__('Sequenz in Aminos. '+sequenz.name())
        self.sequenz = sequenz
        self.basenalt = sequenz.basen()
        self.basenneu = sequenz.inAminosaeure()

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)

class InsertLeerBaseCommand(QUndoCommand):
    def __init__(self, sequenz, index, anzahl):
        super(InsertLeerBaseCommand, self).__init__('Insert leer')
        self.sequenz = sequenz
        self.basenalt = sequenz.basen()
        self.basenneu = sequenz.insertLeer(index, anzahl)

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)

class EntferneBaseCommand(QUndoCommand):
    def __init__(self, sequenz, index, anzahl):
        super(EntferneBaseCommand, self).__init__('Entferne Basen')
        self.sequenz = sequenz
        self.basenalt = sequenz.basen()
        self.basenneu = sequenz.entferneBasen(index, anzahl)

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)

class InsertBaseCommand(QUndoCommand):
    def __init__(self, sequenz, index, seqtext):
        super(InsertBaseCommand, self).__init__('Insert Basen')
        self.sequenz = sequenz
        self.basenalt = sequenz.basen()
        self.basenneu = sequenz.insertBasenString(index, seqtext)

    def redo(self):
        self.sequenz.setBasen(self.basenneu)

    def undo(self):
        self.sequenz.setBasen(self.basenalt)
