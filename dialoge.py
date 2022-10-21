import tkinter as tk
import tkinter.ttk as ttk
from tkinter.colorchooser import askcolor
from typing import Callable
import random

from bioinformatik import Markierung, Sequenz, Base


paddings = { 'padx': 5, 'pady': 5 }

class BaseDialog(tk.Toplevel):
    "Dialog, um Änderungen an einer oder mehreren Basen vornehmen zu können"

    def __init__(self, parent: tk.Widget, highlightobjekt, markierungen,
            leereinfuegencallback: Callable,
            entfernencallback: Callable,
            markierencallback: Callable):
        super().__init__(parent)

        highlightobjekt.boxRahmen('red')
        self.parent = parent
        self.highlightobjekt = highlightobjekt
        self.base = highlightobjekt.getObjekt()
        if type(self.base) != Base:
            raise TypeError('Das Objekt in Leinwandobjekt muss vom Typ Base sein')
        self.markierungen = markierungen
        self.farbe = 'red'
        self.leereinfuegencallback = leereinfuegencallback
        self.entfernencallback = entfernencallback
        self.markierencallback = markierencallback
        self.auswahltexte = ['- keine -']+[m.beschreibung for m in markierungen]

        frame = ttk.Frame(self)

        leerframe = ttk.LabelFrame(frame, text='Leerbasen einfügen')
        leerlabel = ttk.Label(leerframe, text='Anzahl ab hier')
        self.leeranzahl = ConstrainedEntry(leerframe, width=4)
        self.leeranzahl.insert(0, '1')
        leerbutton = ttk.Button(leerframe, text='OK', command=self._leer)
        leerlabel.pack(side=tk.LEFT, **paddings)
        self.leeranzahl.pack(side=tk.LEFT, **paddings)
        leerbutton.pack(side=tk.RIGHT, **paddings)

        markierungframe = ttk.LabelFrame(frame, text='Basen markieren')
        markierungLabel = ttk.Label(markierungframe, text='Anzahl ab hier')
        self.markiereAnzahl = ConstrainedEntry(markierungframe, width=4)
        self.markiereAnzahl.insert(0,1)
        self.markierungWahl = ttk.Combobox(markierungframe, values=self.auswahltexte)
        self.markierungWahl.bind("<<ComboboxSelected>>", self._markiere)
        markierungLabel.pack(side=tk.LEFT, **paddings)
        self.markiereAnzahl.pack(side=tk.LEFT, **paddings)
        self.markierungWahl.pack(side=tk.RIGHT, **paddings)

        deleteframe = ttk.LabelFrame(frame, text='Basen entfernen')
        deletelabel = ttk.Label(deleteframe, text='Anzahl ab hier')
        self.deleteanzahl = ConstrainedEntry(deleteframe, width=4)
        self.deleteanzahl.insert(0, '1')
        deletebutton = ttk.Button(deleteframe, text='Basen entfernen', command=self._entfernen)
        deletelabel.pack(side=tk.LEFT, **paddings)
        self.deleteanzahl.pack(side=tk.LEFT, **paddings)
        deletebutton.pack( side=tk.RIGHT, **paddings)

        leerframe.pack(fill=tk.BOTH, **paddings)
        markierungframe.pack(fill=tk.BOTH, **paddings)
        deleteframe.pack(fill=tk.BOTH, **paddings)
        frame.pack(fill=tk.BOTH)

        self.transient(parent)
        self.title("Basen bearbeiten")
        self.grab_set()
        self.resizable(False,False)
        
        self.update()
        h = self.winfo_height()
        w = self.winfo_width()
        hp = parent.winfo_height()
        wp = parent.winfo_width()
        x0 = parent.winfo_rootx()
        y0 = parent.winfo_rooty()
        x = int(x0+wp/2-w/2)
        y = int(y0+hp/2-h/2)
        self.geometry(f'+{x}+{y}')
        self.protocol("WM_DELETE_WINDOW", self._fertig)

    def _leer(self):
        self.highlightobjekt = None
        self.leereinfuegencallback(self.base, int(self.leeranzahl.get()))
        self._fertig()

    def _markiere(self, _):
        self.highlightobjekt = None
        text = self.markierungWahl.get()
        markierung = None
        for m in self.markierungen:
            if text == m.beschreibung:
                markierung = m
                break
        self.markierencallback(self.base, markierung, int(self.markiereAnzahl.get()))
        self._fertig()

    def _entfernen(self):
        self.highlightobjekt = None
        self.entfernencallback(self.base, int(self.deleteanzahl.get()))
        self._fertig()

    def _fertig(self) -> None:
        if self.highlightobjekt:
            self.highlightobjekt.boxRahmen()
        return super().destroy()

class SequenzDialog(tk.Toplevel):
    """Dialog, um Änderungen an einer Sequenz vornehmen zu können"""

    def __init__(self, parent: tk.Widget, sequenz: Sequenz,
            entfernencallback: Callable,
            umbenennencallback: Callable,
            aminosaeurecallback: Callable
        ):
        self.sequenz = sequenz
        if type(self.sequenz) != Sequenz:
            raise TypeError('Das Objekt in Leinwandobjekt muss vom Typ Sequenz sein')
        self.parent = parent
        self.entfernencallback = entfernencallback
        self.umbenennencallback = umbenennencallback
        self.aminosaeurecallback = aminosaeurecallback

        super().__init__(parent)
        frame = ttk.Frame(self)

        renameframe = ttk.LabelFrame(frame, text='Sequenz umbennen')
        self.renameentry = ttk.Entry(renameframe)
        self.renameentry.insert('end', self.sequenz.name)
        renamebutton = ttk.Button(renameframe, text='Sequenz umbennen', command=self._umbenennen)
        self.renameentry.pack(side=tk.LEFT, **paddings)
        renamebutton.pack(side=tk.RIGHT, **paddings)

        aminoframe = ttk.LabelFrame(frame, text='Sequenz in Aminosäure umwandeln')
        aminobutton = ttk.Button(aminoframe, text='Sequenz Aminosäure', command=self._aminosaeure)
        aminobutton.pack( side=tk.RIGHT, **paddings)

        deleteframe = ttk.LabelFrame(frame, text='Sequenz entfernen')
        deletebutton = ttk.Button(deleteframe, text='Sequenz entfernen', command=self._entfernen)
        deletebutton.pack(side=tk.RIGHT, **paddings)

        renameframe.pack( fill=tk.BOTH, **paddings)
        aminoframe.pack(  fill=tk.BOTH, **paddings)
        deleteframe.pack( fill=tk.BOTH, **paddings)
        frame.pack(fill=tk.BOTH)

        self.transient(parent)
        self.title("Sequenz bearbeiten")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.resizable(False,False)

        self.update()
        h = self.winfo_height()
        w = self.winfo_width()
        hp = parent.winfo_height()
        wp = parent.winfo_width()
        x0 = parent.winfo_rootx()
        y0 = parent.winfo_rooty()
        x = int(x0+wp/2-w/2)
        y = int(y0+hp/2-h/2)
        self.geometry(f'+{x}+{y}')


    def _entfernen(self):
        self.entfernencallback(self.sequenz)
        self.destroy()

    def _umbenennen(self):
        self.umbenennencallback(self.sequenz, self.renameentry.get())
        self.destroy()

    def _aminosaeure(self):
        self.aminosaeurecallback(self.sequenz)
        self.destroy()


class LinealDialog(tk.Toplevel):
    "Dieser Dialog wird geöffnet, wenn man auf das Lineal klickt"

    def __init__(self, parent: tk.Widget, highlightobjekt, versteckencallback: Callable, enttarnencallback: Callable):
        super().__init__(parent)

        highlightobjekt.boxRahmen('red')
        self.hightlightobjekt = highlightobjekt
        self.spalte = highlightobjekt.getObjekt()
        if type(self.spalte) != int:
            raise TypeError('Das Objekt in Leinwandobjekt muss vom Typ int sein')
        self.parent = parent
        self.anzahl = 1
        self.versteckencallback = versteckencallback
        self.enttarnencallback = enttarnencallback

        frame = ttk.Frame(self)

        hideframe = ttk.LabelFrame(frame, text='Spalten verstecken')
        hidelabel = ttk.Label(hideframe, text='Anzahl ab hier')
        self.hideentry = ConstrainedEntry(hideframe, width=4)
        self.hideentry.insert('end', self.anzahl)
        hidebutton = ttk.Button(hideframe, text='Spalten verstecken', command=self._verstecken)
        hidelabel.pack(side=tk.LEFT, **paddings)
        self.hideentry.pack(side=tk.LEFT, **paddings)
        hidebutton.pack(side=tk.RIGHT, **paddings)

        enttarnframe = ttk.LabelFrame(frame, text='Versteckte Spalten anzeigen')
        enttarnlabel = ttk.Label(enttarnframe, text='Anzahl ab hier')
        self.enttarnentry = ConstrainedEntry(enttarnframe, width=4)
        self.enttarnentry.insert('end', self.anzahl)
        enttarnbutton = ttk.Button(enttarnframe, text='Spalten enttarnen', command=self._enttarnen)
        enttarnlabel.pack(side=tk.LEFT, **paddings)
        self.enttarnentry.pack(side=tk.LEFT, **paddings)
        enttarnbutton.pack(side=tk.RIGHT, **paddings)

        hideframe.pack(fill=tk.BOTH, **paddings)
        enttarnframe.pack(fill=tk.BOTH, **paddings)
        frame.pack(fill=tk.BOTH)

        self.transient(parent)
        self.title("Linealfunktionen")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._fertig)
        self.resizable(False,False)

        self.update()
        h = self.winfo_height()
        w = self.winfo_width()
        hp = parent.winfo_height()
        wp = parent.winfo_width()
        x0 = parent.winfo_rootx()
        y0 = parent.winfo_rooty()
        x = int(x0+wp/2-w/2)
        y = int(y0+hp/2-h/2)
        self.geometry(f'+{x}+{y}')


    def _verstecken(self):
        # linealtickobjekt muss vernichtet werden, damit die garbage collection
        # das canvas-Element zerstören kann.
        self.hightlightobjekt = None
        self.versteckencallback(self.spalte, int(self.hideentry.get()))
        self._fertig()

    def _enttarnen(self):
        self.hightlightobjekt = None
        self.enttarnencallback(self.spalte, int(self.enttarnentry.get()))
        self._fertig()

    def _fertig(self) -> None:
        if self.hightlightobjekt:
            self.hightlightobjekt.boxRahmen('')
        return super().destroy()


class NeueSequenzDialog(tk.Toplevel):
    """Ein Dialog um neue Sequenzen als Text zu importieren"""

    def __init__(self, parent: tk.Widget, fertigcallback: Callable):
        self.parent = parent
        self.fertigcallback = fertigcallback

        super().__init__(parent)
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH)

        nameframe = ttk.LabelFrame(frame, text='Name')
        nameframe.pack(side=tk.TOP, anchor=tk.W, **paddings)
        self.sequenzname = ttk.Entry(nameframe)
        self.sequenzname.pack(side=tk.TOP, fill=tk.X, **paddings)

        textframe = ttk.LabelFrame(frame, text='Sequenztext')
        textframe.pack(side=tk.TOP, anchor=tk.W, **paddings, ipadx=5, ipady=5)
        f = ttk.Frame(textframe)
        f.pack(fill=tk.BOTH, **paddings)
        self.sequenztext = tk.Text(f)
        vsb = ttk.Scrollbar(f, orient='vertical', command=self.sequenztext.yview)
        self.sequenztext.configure(yscrollcommand=vsb.set)
        self.sequenztext.pack(side=tk.LEFT)
        vsb.pack(side=tk.LEFT, fill=tk.Y)

        button = ttk.Button(frame, text='Fertig!', command=self._fertig)
        button.pack(side=tk.TOP, **paddings)

        self.transient(parent)
        self.title("Neue Sequenz hinzufügen")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.resizable(False,False)

        self.update()
        h = self.winfo_height()
        w = self.winfo_width()
        hp = parent.winfo_height()
        wp = parent.winfo_width()
        x0 = parent.winfo_rootx()
        y0 = parent.winfo_rooty()
        x = int(x0+wp/2-w/2)
        y = int(y0+hp/2-h/2)
        self.geometry(f'+{x}+{y}')

    def _fertig(self):
        self.fertigcallback(self.sequenzname.get(), self.sequenztext.get('1.0', 'end'))
        self.destroy()


class MarkierungenVerwaltenDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, markierungen) -> None:
        super().__init__(parent)
        self.markierungen = markierungen
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH)
        self.frameinner = ttk.Frame(self.frame)
        self.frameinner.pack(fill=tk.BOTH)
        self._markierungenZeichnen()

        self.title("Markierungen verwalten")
        self.minsize(300,30)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.resizable(False,False)

        self.update()
        h = self.winfo_height()
        w = self.winfo_width()
        hp = parent.winfo_height()
        wp = parent.winfo_width()
        x0 = parent.winfo_rootx()
        y0 = parent.winfo_rooty()
        x = int(x0+wp/2-w/2)
        y = int(y0+hp/2-h/2)
        self.geometry(f'+{x}+{y}')
    
    def _markierungenZeichnen(self):
        self.frameinner.destroy()
        self.frameinner = ttk.Frame(self.frame)
        self.frameinner.pack(fill=tk.BOTH, **paddings)
        plusbutton = ttk.Button(self.frameinner, text='+', width=1, command=self._markierungAnhaengen)
        plusbutton.grid(column=0, row=0, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.frameinner, text='Keine gleichen Namen verwenden!', anchor=tk.W).grid(column=1, row=0, sticky=tk.W, **paddings)
        n=1
        for markierung in self.markierungen:
            mw = MarkierungWidget(self.frameinner, markierung, self._markierungEntfernen)
            mw.grid(column=0, row=n, sticky=(tk.W,tk.E), columnspan=2)
            n += 1

    def _markierungAnhaengen(self):
        farbe = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
        self.markierungen.append(Markierung(f'Unbenannt{random.randint(1,99999):0d}',farbe))
        self._markierungenZeichnen()

    def _markierungEntfernen(self, markierung):
        self.markierungen.remove(markierung)


class MarkierungWidget(ttk.Frame):
    def __init__(self, parent, markierung, entfernecallback) -> None:
        super().__init__(parent)
        self.markierung = markierung
        self.entfernecallback = entfernecallback
        self.beschreibung = tk.StringVar(self,value=markierung.beschreibung)
        self.beschreibung.trace('w', self._beschreibungAktualisieren )

        bezeichnungEntry = ttk.Entry(self, textvariable=self.beschreibung)
        farbchooserbutton = ttk.Button(self, text='Farbe wählen', command=self._farbauswahl)
        self.farbquadrat = tk.Frame(self, width=25, height=25, bg=self.markierung.farbe)
        entfernebutton = ttk.Button(self, text='-', width=1, command=self._markierungEntfernen)

        bezeichnungEntry.pack( side=tk.LEFT, fill=tk.Y, **paddings)
        farbchooserbutton.pack(side=tk.LEFT, **paddings)
        self.farbquadrat.pack( side=tk.LEFT, fill=tk.Y, **paddings)
        entfernebutton.pack(   side=tk.LEFT, fill=tk.Y, **paddings)

    def _beschreibungAktualisieren(self, *args):
        self.markierung.beschreibung=self.beschreibung.get()

    def _farbauswahl(self):
        farbe = askcolor(self.markierung.farbe)[1]
        if farbe:
            self.markierung.farbe = farbe
            self.farbquadrat.configure(background=farbe)

    def _markierungEntfernen(self):
        self.entfernecallback(self.markierung)
        self.destroy()

class ConstrainedEntry(ttk.Entry):
    "Kleine Hilfsklasse, um nur numerische Eingaben zuzulassen"

    def __init__(self, *args, **kwargs):
        ttk.Entry.__init__(self, *args, **kwargs)

        vcmd = (self.register(self._validiere),"%P")
        self.configure(validate="key", validatecommand=vcmd)

    def _verbiete(self):
        self.bell()

    def _validiere(self, new_value):
        try:
            if new_value.strip() == "": return True
            value = int(new_value)
            if value < 0 or value > 9999999:
                self._verbiete()
                return False
        except ValueError:
            self._verbiete()
            return False

        return True
