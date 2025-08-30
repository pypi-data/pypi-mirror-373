'''
Created on 6 juin 2016

@author: Jarrige_Pi

  160608 - added 'exts' optional arg to SelectModel, defaults to bin+dat+pic
  160629 - allow import as pi of same sim or th as importer
  160706 - reviewed ganessa.sim/th import
  160820 - SelectFile: exts=None for a selection without extension
  160919 - added select folder
  170228 - added UK dialogs
  170515 - fix parent.inidir not defined
  170618 - SelectFile: title= allow title redefinition
  171207 - fix post= and SelectFile().add_extra_info options
  180306 - added py3 compatibility
  180514 - allow parent._clear_exec not be defined
  180612 - minor changes related to python3 prints (ws, aws)
  181220 - removed 'all' kwarg from ExecStatus.clear
  190107 - handle SelectModel(usedef= False)
  191007 - SelectFile extra info spawns 6 cols
  200604 - Adds chdir before reading a .dat / .pic
  210325 - Add SelectModel.update_info
  200604 - SelectModel: add a chdir to the model folder for potential relative inner read
  210325 - SelectModel: add update_info method
  210610 - Add parent cascading to SelectFile
  210610 - SelectFile: None or blank nonempty title disable frame contour
  210616 - SelectModel: update_info(-1) as alternative to parent.finalise
  210624 - SelectModel: bt_exe_state called from update_info instead of _model_choice
  210723 - SelectModel: add silent=True addl kwarg for reading .dat / .pic
  211004 - SelectModel: do not show button dlg if show_emb=False (default)
  211004 - SelectModel: show_emb kwarg controls button selection in embedded mode
  211004 - SelectFile: use_emb kwarg controls filename / dlg in embedded mode
  211013 - fix chdir error with filename with empty dirname
  211020 - SelectFile: setfilename
  211026 - add fname property to retrieve folder / filename (SelectModel, SelectFile, SelectFolder)
  211028 - add SelectFolder.add_extra_info(fun) and post=fun
  211030 - add typing of aguments and return
  211112 - minor change to update_from (inidir getter); SelectModel usedef requires show_dialog
  211126 - allow extra to append to previous text line if return text starts with backspace \b
  220706 - allow reset file name to '' for SelectFile
  230908 - add .get() as a synonym of .getfilename()
  230112 - catch Exceptions in SelectModel.loadmodel
  240625 - fix SelectFile use when ganessa.sim not imported
  250307 - make parent.v1 StringVar optional
  250313 - make obsolete parent.finalise optional (see update_info)
  250624 - misc adjustments for embedded mode
  250626 - added ask_for_single_input simple dialog

MMI for Piccolo tools
'''
from typing import Tuple, List, Union, Callable, Literal, Type
import os.path as OP
from os import chdir
import sys

from tkinter import W, E, StringVar, simpledialog, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk


from ganessa.util import ws, aws
from ganessa._getdll import _LookupDomainModule

# select which ganessa to import according to caller import
_caller = _LookupDomainModule()
pic = _caller.module
if pic is not None:
    pic.useExceptions()

#****g* ganessa.OpenFileMMI/About
# PURPOSE
#   The module ganessa.OpenFileMMI provides classes for choosing/opening a model,
#   a file, a folder.
# REMARK
#   It should be preceded by 'import ganessa.sim'
#****
#****g* ganessa.OpenFileMMI/iFunctions
#****
#****g* ganessa.OpenFileMMI/iClasses
#****

class DialogTexts(dict):
    '''Class for handling locale dialog strings'''
    alldlgtxt = {'file': ('Fichier', 'File'),
                  'folder': ('Dossier', 'Folder'),
                  'infile': ("Fichier d'entrée", 'Input file'),
                  'outfile': ('Fichier de sortie', 'Output file'),
                  'model_file': ('Fichier modèle', 'Model file'),
                  'selfile:':('Fichier choisi :', 'Selected file:'),
                  'selfold:': ('Dossier choisi :', 'Selected folder:'),
                  'selfilfold:': ('Dossier/fichier choisi :', 'Selected folder/file'),
                  'def_file': ('Fichier par défaut', 'Default file'),
                  'spec_file': ('Fichier spécifique', 'Specific file'),
                  'sel_other_model':('Choisir un autre fichier modèle',
                                     'Select another model file'),
                  'sel_other_file':('Choisir un autre fichier', 'Select another file'),
                  'sel_other_fold': ('Choisir un autre dossier', 'Select another folder'),
                  'sel_other_fifold': ('Choisir un autre dossier/fichier',
                                       'Select another folder/file'),
                  'sel_file_proc': ('Choisir le fichier à traiter',
                                    'Select the file to process'),
                  'sel_fifold': ('Choisir le dossier/fichier', 'Select a folder/file'),
                  'sel_fold': ('Choisir le dossier', 'Select a folder'),
                  'infile:': ("Fichier d'entrée :", 'Input file:'),
                  'reading_file': ('Lecture du fichier en cours...', 'Reading file...'),
                  'using_current': ('Utilisation du modèle courant', 'Using current model'),
                  'ganerror:': ('Erreur Ganessa : ', 'Ganessa Error: '),
                  'error:': ('Erreur : ', 'Error: '),
                  'fnf_or_incompat': ('Fichier non trouvé ou incompatible',
                                     'File not found or incompatible file'),
                  'fil_not_load': ('Fichier non chargé', 'File not loaded'),
                  'pipecount:': ('Nombre de tronçons : ', 'Pipe count: '),
                  'nodecount:': ('Nombre de noeuds : ', 'Node count: '),
                  'sim_isol': ('noeuds isolés après simulation',
                               'isolated nodes after simulation'),
                  'exestat': ("Résultat de l'exécution", 'Excution status'),
                  'cancel': ('Annuler', 'Cancel'),
                  "param_input": ("Saisie", "Data entry"),
                  "input_prompt": (" Veuillez entrer une valeur {} : ",
                                   " Please enter {} data:           "),
                  "input_int": ("entière", "integer"),
                  "input_float": ("numérique", "float"),
                  "input_str": ("chaine de caractères", "character string"),
                  "input_defval": ("valeur par défaut", "default value"),
                 }

    def __init__(self, lang):
        '''Sets the string table for the selected language'''
        self.language = lang
        lgidx = 0 if (lang.upper() == 'FR') else 1
        dlgtxt = {k:v[lgidx] for k, v in DialogTexts.alldlgtxt.items()}
        dict.__init__(self, dlgtxt)

dlg = DialogTexts('FR')

#****f* iFunctions/setlanguage
# PURPOSE
#   Sets and/or returns the current UI language.
# SYNTAX
#   val = setlanguage(new_lang=None)
# ARGUMENTS
#   * str new_lang: new language to be used: "FR" for French
#     or any other for English, or None to return current language.
# RESULT
#   * str val: previous/current language
# REMARK
#   language is initialised to "FR" by default.
#****

def setlanguage(lang=None):
    '''Sets the UI language - defaults to FR'''
    global dlg
    previous_lang = dlg.language
    if lang and isinstance(lang, str):
        dlg = DialogTexts(lang)
        if lang != previous_lang:
            print(OP.basename(__file__), 'language set to:', lang)
    return previous_lang

def updatefrom(item, inidir):
    '''Recover inidir from parent if applicable'''
    if not inidir:
        inidir = getattr(item, 'inidir', "")
        # if not inidir and hasattr(item, 'parent'):
        #    inidir = getattr(item.parent, 'inidir', '')
    if not inidir:
        try:
            inidir = OP.dirname(item.fname)
        except AttributeError:
            pass
    return inidir

def clear_exec(parent, *args, **kwargs):
    '''Try to clear the parent execution/status area'''
    try:
        parent.clear_exe(*args, **kwargs)
    except AttributeError:
        try:
            parent._clear_exe(*args, **kwargs)
        except AttributeError:
            pass
    except TypeError:
        parent.clear_exe()

#****f* iClasses/SelectModel, SelectFile, SelectFolder
# PURPOSE
#   Provide ready-to-use frames for display a preselected model/file/folder name; and
#   a button allowing selecting a different model(for reading),
#   file for reading or writing, or folder. SelectModel can load the model,
#   display the link and node counts.
# SYNTAX
#   * frm = SelectModel(parent, file_name, exts=None, usedef=True, silent=True,
#     show_emb=False, inp_core=None)
#   * frm = SelectFile(parent, file_name, exensions, mode, title="", post=None,
#     show_emb=False, allow_reset=False)
#   * frm = SelectFolder(parent, folder_name, title="", post=None)
# ARGUMENTS
#   * frame parent: parent frame
#   * str file_name/folder_name: default value for the model / file / folder.
#     SelectModel will not load the model at frame creation (it can take some time),
#     this has to be done by calling the update_info method.
#   * str or tuple of str exts/extensions: extensions allowed for selecting a file.
#     If a single extension is allowed, it can be provided as a str instead of a singleton.
#   * bool usedef: if True, a radiobutton allow to select between _selected model and
#     default result file.
#   * bool silent: if True, .dat and .pic files are read as silently as possible.
#   * str mode: "r" for reading or "w" for writing. Defaults to "w" if title is set or None.
#   * str title: will appear in the title of the selection dialog box.
#   * callable post: function expecting the file/folder name as single argument, and returning
#     a str that will be displayed below the file/folder name in the frame. It can be defined
#     later with add_extra_info method.
#     It will be called after the selection of the file/folder.
#   * bool show_emb: if False, and the script is run in embedded mode, the selection
#     button is not displayed (the model / file cannot be changed).
#   * module inp_core: alternate core able to read .inp Epanet files and providing a few
#     functions compatible with ganessa.sim (en2emu).
#   * bool allow_reset: if True, a "reset" button is provided to clear the file name.
# RESULT
#   * frame frm: frame or label frame containing the button selection, the
#     model/file/folder name, etc.
# METHODS
#   Those 4 methods return the model/file/folder currently selected:
#   * str name = frm.getfilename()
#   * str name = frm.get()
#   * str name = frm.fname
#   * str name = frm.getfoldername() (SelectFolder only)
#
#   This method appends (SelectModel) or redefines and runs (SelectFile and SelectFolder)
#   the post-processing function with callable post_proc:
#   * frm.add_extra_info(post_proc)
#   * frm.add_extra_model_info(post_proc) (synonym for SelectModel)
#
#   For SelectModel, this method returns the text information computed by the loadmodel
#   (link and node counts) and by additional post-processors added by add_extra_info.
#   For SelectFile and SelectFolder, this method returns the result of post callable:
#   * str text = frm.getinfo()
#
#   This method updates the post processing text displayed in the frame:
#   * frm.update_info()
#
#   These SelectFile methods allow to reset the file name:
#   * frm.setfilename(name)
#   * frm.fname = name
#
#   This SelectFile method allow to modify read / write mode:
#   * frm.set_rw_mode("r" or "w")
# REMARK
#   language is initialised to "FR" by default; see setlanguage.
#****

class SelectModel(ttk.LabelFrame):
    '''Class SelectModel allows to load/read a model:
    frm = SelectModel(parent_frame, model_file, exts=None, usedef=True, silent=True, show_emb=False)
        model_file: file name to be loaded (if exists)
        exts: single extension str or tuple of str extensions. Default None means ('.bin', '.dat', '.pic')
        usedef: if True, a radio button allow to select between default result file and selected model
        silent: if True, .dat and .pic files are read silently
        show_emb: if False, dialog is not shown in embedded mode (current model is used)
        inp_core: alternate core for .inp files (en2emu)
    A label info with links and nodes count is written below the file name

    frm.add_extra_model_info(text_fun)
        add an additional function to be called at refresh, adding an additional info line
        (or append to previous line if returned text starts with backspace \b)

    frm.update_info(start=1)
        updates info label; should be called with start=-1 after every UI item has been created

    frm.fname: file name (getter only)
    '''
    def __init__(self, parent, nfic: str,
                exts: Union[str, Tuple[str, ...], List[str]] = None,
                usedef: bool = True,
                silent: bool = True,
                show_emb: bool = False,
                inp_core = None,
                ):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text=dlg['model_file'], height=95, padding=6)
        self.parent = parent
        self.silent_mode = silent
        self.show_dialog = show_emb or not pic.is_embedded()
        self.usedef = usedef and self.show_dialog
        self.v_ficmodel = StringVar()
        self.v_ficmodelsav = StringVar()
        self.v_model_info = StringVar()
        self.inp_core = inp_core
        self.gan_core = pic
        if exts is None:
            self.exts = ('bin', 'dat', 'pic')
        elif isinstance(exts, (tuple, list)):
            self.exts = [ext.strip('.').lower() for ext in exts]
        else:
            self.exts = (exts.strip('.').lower(), )
        # fr_bin.grid_propagate(0)
        self.s_ficmodel = StringVar()
        if not self.show_dialog:
            nfic = pic.model_filename()
            if OP.splitext(nfic)[1].strip(".").lower() not in self.exts:
                if "bin" in self.exts and (nbin := pic.result_filename()):
                    nfic = nbin
        #     if OP.splitext(nfic)[1].lower() not in exts:
        #         msg = f'Le modèle "{nfic}"\nn\'est pas du type approprié: ' + ' '.join(exts)
        #         messagebox.showwarning(dlg['model_file'], msg)
        if nfic:
            self.v_ficmodelsav.set(nfic)
            self.inidir = OP.dirname(nfic)
            self.s_ficmodel.set('usr')
        else:
            self.inidir = ""
            self.s_ficmodel.set('def')
        self.extra_model_info = [None]
        self.v_model_info.set(' ')
        # create a strinvar for handling msg, if parent has none
        try:
            self.parent.v1.set("")
        except AttributeError:
            self.load_message_var = StringVar()
        else:
            self.load_message_var = self.parent.v1

        # creates lb_info before call to _model_choice
        lb_choice = ttk.Label(self, text=dlg['selfile:'])
        val_choice = ttk.Label(self, textvariable=self.v_ficmodel, style='PS.TLabel')
        lb_info = ttk.Label(self, textvariable=self.v_model_info, style='PS.TLabel')
        self._model_choice(load=False)
        if self.show_dialog:
            if usedef:
                for r, kw, vv in ((0, 'def_file', 'def'), (1, 'spec_file', 'usr')):
                    ttk.Radiobutton(self, text=dlg[kw], variable=self.s_ficmodel,
                        value=vv, command=self._model_choice).grid(row=r, sticky=W)
            else:
                self.s_ficmodel.set('usr')
            bt = ttk.Button(self, text=dlg['sel_other_model'], command=self._sel_fich_model)
            bt.grid(row=1, column=1, sticky=W)
        lb_choice.grid(row=2, column=0, sticky=W)
        val_choice.grid(row=2, column=1, sticky=W+E)
        lb_info.grid(row=3, column=1, sticky=W)

        # propagate model name query
        parent.getmodelname = self.v_ficmodel.get
        # in case parent expects finalise list of actions
        if hasattr(parent, "finalise") and isinstance(parent.finalise, list):
            parent.finalise.append(self._model_choice)

    def _model_choice(self, load=True):
        parent = self.parent
        clear_exec(parent, True)
        nom = self.v_ficmodelsav.get()
        etat = self.s_ficmodel.get()
        if nom and etat == 'usr':
            self.inidir = OP.dirname(nom)
        elif self.usedef:
            self.s_ficmodel.set('def')
            nom = pic.resfile() if pic else 'UnknownDefaultFile.bin'
            self.inidir = ''
        parent.inidir = self.inidir
        self.v_ficmodel.set(nom)
        if load:
            print(aws(dlg['infile:']), ws(nom))
        # updates the model info from the function list
        self.extra_model_info[0] = self.loadmodel if load else self._noloadmodel
        self.update_info(start=0)

    def _sel_fich_model(self):
        clear_exec(self.parent, True)
        ft = [(dlg['file'] + ' ' + ext, '*.' + ext) for ext in self.exts]
        fich = askopenfilename(title=dlg['sel_file_proc'],
                               initialdir=getattr(self.parent, 'inidir', ''),
                               filetypes=ft)
        if fich:
            self.v_ficmodelsav.set(fich)
            self.s_ficmodel.set('usr')
            self._model_choice()

    def getfilename(self) -> str:
        '''Returns the model filename'''
        return self.v_ficmodel.get()

    def get(self) -> str:
        '''Returns the model filename'''
        return self.v_ficmodel.get()

    fname : str = property(getfilename, doc='gets model filename')

    def loadmodel(self) -> str:
        '''Loads the model and returns size inf as a text string'''
        parent = self.parent
        nom = self.v_ficmodel.get()
        if OP.exists(nom) and pic is not None:
            errtxt = ''
            ext = OP.splitext(nom)[1].lower()
            core = self.inp_core if self.inp_core and ext == ".inp" else self.gan_core
            if self.show_dialog:
                self.load_message_var.set(dlg['reading_file'])
                try:
                    if ext == '.bin':
                        pic.loadbin(nom)
                    else:
                        core.reset()
                        if folder := OP.dirname(nom):
                            chdir(folder)
                        if self.silent_mode:
                            core.cmd('SIM IVERB -9')
                        core.cmdfile(nom)
                except pic.IsolatedNodeSimulationError:
                    errtxt =  ' (' + dlg['sim_isol'] + ')'
                except pic.GanessaError as err:
                    errtxt = '\n' + dlg['ganerror:'] + str(err)
                except Exception as err:
                    errtxt = '\n' + dlg['error:'] + str(err)
            else:
                self.load_message_var.set(dlg['using_current'])
            parent.update()
            txt = dlg['pipecount:'] + str(core.nbobjects(core.LINK)) + ' - ' +\
                  dlg['nodecount:'] + str(core.nbobjects(core.NODE)) + errtxt
        else:
            txt = '***' + dlg['fnf_or_incompat'] + '***'
        self.load_message_var.set(txt)
        return txt

    def _noloadmodel(self) -> str:
        '''alternate version of loadmodel to be used before loading'''
        txt = dlg['fil_not_load']
        self.load_message_var.set(txt)
        return txt

    def add_extra_info(self, textfun: Callable[[], str]) -> None:
        '''Register a function that takes no arg
        and returns a text string to be displayed as addl model info'''
        if textfun not in self.extra_model_info:
            self.extra_model_info.append(textfun)

    # compatibility
    add_extra_model_info = add_extra_info

    def update_info(self, start: int = -1) -> None:
        '''Updates model info: run registered funcs and updates label info
            start is the index of the 1st callback to be called
            if start < 0: 1st callback is replaced with loadmodel
        Also try to run parent_frame.bt_exe_state function'''
        if start < 0:
            # alternative to parent.finalise: call update_info(-1)
            self.extra_model_info[0] = self.loadmodel
            # self.extra_model_info[0] = self._model_choice
            start = 0
        model_info = self.v_model_info.get().split('\n')[:start]
        model_info += [f() for f in self.extra_model_info[start:]]
        txt_info = '\n'.join(filter(None, model_info))
        # remove newline if followed with backspace
        txt_info = "".join(txt_info.split('\n\b'))
        self.v_model_info.set(txt_info)
        # Change the button exec state if callback function is defined
        try:
            self.parent.bt_exe_state()
        except AttributeError:
            try:
                self.parent.parent.bt_exe_state()
            except AttributeError:
                try:
                    self.parent._bt_exe_state()
                except AttributeError:
                    pass

    def get_info(self) -> str:
        """Returns extra info text"""
        return self.v_model_info.get()

class SelectFile(ttk.Frame):
    '''Label Frame dialog for selection an input ou output file
    frm = SelectFile(parent_frame, filename, extensions, mode, title='', post=None, use_emb=False)
        extensions: extension or tuple of extensions to look for
        mode: 'r' for reading and 'w' for writing
        title: custom frame title
        post: callable returning a string to be displayed in the info label, below the file name
        use_emb: if True, and embedded mode, and extensions are provided, use model file name with 1st extension
        allow_reset: if True, add a 'Cancel' button that clears the file name when pressed (2.3.1)
    frm.add_extra_info(post)
        records and calls 'post' with file name as single arg. See post above.
    frm.fname: file name (getter and setter)
    '''
    def __init__(self, parent, nfic: str,
                 extensions: Union[None, str, Tuple[str, ...]],
                 mode: Literal['r', 'w'],
                 title: str = "",
                 post: Callable[[str], str] = None,
                 use_emb: bool = False,
                 allow_reset: bool = False):
        self.mode = ""
        self.allow_reset = allow_reset
        self.naturefic = dlg['outfile'] if mode == 'w' else dlg['infile']
        if title is None or (title and not title.strip()):
            ttk.Frame.__init__(self, parent)
            if not mode:
                mode = 'w'
            self.naturefic = ""
        else:
            ttk.LabelFrame.__init__(self, parent)
            if title:
                self.naturefic = title
        self.set_rw_mode(mode)
        self.parent = parent.parent if hasattr(parent, 'parent') else parent
        self.post = post
        self.v_fich = StringVar()
        self.v_post = StringVar()
        self.use_emb = use_emb and pic and pic.is_embedded()
        if extensions is None or not extensions:
            self.exts = None
        elif isinstance(extensions, tuple):
            self.exts = [ext.strip('.').lower() for ext in extensions]
        else:
            self.exts = (extensions.strip('.').lower(), )
        # fr_out.grid_propagate(0)
        if self.exts is not None and self.use_emb:
            model_name = OP.splitext(pic.model_filename())[0]
            for ext in self.exts:
                if OP.exists(nfic := (model_name + "." + ext)):
                    break
            else:
                nfic = model_name + "." + self.exts[0]
        if nfic:
            self.v_fich.set(nfic)
        ttk.Label(self, text=dlg['selfilfold:']).grid(row=2, column=0, sticky=W)
        if not self.use_emb:
            ttk.Button(self, text=dlg['sel_other_fifold'],
                         command=self._sel_fich).grid(row=1, column=1, columnspan=3, sticky=W)
        if allow_reset:
            ttk.Label(self, text="    ").grid(row=1, column=5, sticky=W)
            self.clr_btn = ttk.Button(self, text=dlg['cancel'], command=self.clearfilename)
            self.clr_btn.grid(row=1, column=6, sticky=E)
            self.clr_btn.state([("!" if nfic else "") + "disabled"])
        ttk.Label(self, textvariable=self.v_fich, style='PS.TLabel'
            ).grid(row=2, column=1, columnspan=6, sticky=W+E)
        self.extra = ttk.Label(self, textvariable=self.v_post, style='PS.TLabel')
        self.add_extra_info(post)

    # Choix du dossier et racine de fichier de sortie
    def _sel_fich(self):
        clear_exec(self.parent)
        nom = self.v_fich.get()
        inidir = OP.dirname(nom)
        inidir = updatefrom(self.parent, inidir)
        inifil = OP.splitext(OP.basename(nom))[0]

        if self.exts is None:
            kwft = dict()
        else:
            kwft = {'filetypes': [(dlg['file'] + ' ' + ext, '*.' + ext) for ext in self.exts]}
        fich = self.ask(title=dlg['sel_fifold'] + ' ' + self.naturefic,
                        initialdir=inidir, initialfile=inifil, **kwft)
        self.setfilename(fich)

    def getfilename(self) -> str:
        '''Returns the filename'''
        return self.v_fich.get()

    def get(self) -> str:
        '''Returns the filename'''
        return self.v_fich.get()

    def setfilename(self, name: str) -> None:
        '''Resets the filename'''
        if name:
            if not OP.splitext(name)[1] and self.exts is not None:
                name += '.' + self.exts[0]
            self.v_fich.set(name)
            self.update_info()
            if self.allow_reset:
                self.clr_btn.state(["!disabled"])

    # getter and setter as properties
    fname: str = property(getfilename, setfilename, doc='Get/set file name')

    def update_info(self, *args) -> None:
        '''Runs post analysis'''
        if self.post is not None:
            nom = self.v_fich.get()
            txt = self.post(nom)
            self.v_post.set(txt)
            if txt:
                self.extra.grid(row=3, column=1, columnspan=6, sticky=W)
                return
        self.extra.forget()

    def add_extra_info(self, post : Callable[[str], str]) -> None:
        '''Define post analysis'''
        self.post = post
        self.update_info()

    def set_rw_mode(self, mode: Literal['r', 'w']) -> None:
        """Change R/W mode"""
        if mode == self.mode:
            return
        if self.naturefic in (dlg['infile'], dlg['outfile'], ):
            self.naturefic = dlg['outfile'] if mode == 'w' else dlg['infile']
        self.ask = askopenfilename if mode == 'r' else asksaveasfilename
        if self.naturefic.strip():
            self.configure(text=self.naturefic, height=80, padding=6)

    def clearfilename(self) -> None:
        """clears the filename"""
        self.v_fich.set("")
        self.update_info()
        if self.allow_reset:
            self.clr_btn.state(["disabled"])

    def get_info(self) -> str:
        """Returns extra info text"""
        return self.v_post.get()

class SelectFolder(ttk.LabelFrame):
    '''Folder selector
    frm = SelectFolder(parent_frame, foldername, title='', post=None)
        title: custom frame title
        post: callable returning a strig to be displayed in the info label, below the file name
    frm.add_extra_info(post)
        records and calls 'post' with file name as single arg. See post above.
    frm.fname: file name (getter and setter)
    '''
    # folder selector frame - 160919
    def __init__(self, parent, nfold: str,
                 title: str = "",
                 post: Callable[[str], str] = None):
        ttk.LabelFrame.__init__(self, parent)
        self.naturefold = title if title else dlg['folder'] + " "
        self.configure(text=self.naturefold, height=80, padding=6)
        self.parent = parent
        self.v_fold = StringVar()
        self.post = post
        self.v_post = StringVar()
        if nfold:
            self.v_fold.set(nfold)
        ttk.Label(self, text=dlg['selfold:']).grid(row=2, column=0, sticky=W)
        ttk.Button(self, text=dlg['sel_other_fold'],
                         command=self._sel_fold).grid(row=1, column=1, columnspan=3, sticky=W)
        ttk.Label(self, textvariable=self.v_fold, style='PS.TLabel').grid(row=2, column=1, columnspan=6, sticky=W+E)
        self.extra = ttk.Label(self, textvariable=self.v_post, style='PS.TLabel')
        self.add_extra_info(post)

    # Choix du dossier et racine de fichier de sortie
    def _sel_fold(self):
        clear_exec(self.parent)
        inidir = self.v_fold.get()
        inidir = updatefrom(self.parent, inidir)
        fold = askdirectory(title=dlg['sel_fold'],
                            initialdir=inidir, mustexist=True)
        if fold:
            self.v_fold.set(fold)
            self.update_info()

    def getfoldername(self) -> str:
        '''Returns the folder'''
        return self.v_fold.get()

    def getfilename(self) -> str:
        '''Returns the folder'''
        return self.v_fold.get()

    def get(self) -> str:
        '''Returns the folder'''
        return self.v_fold.get()

    fname: str = property(getfoldername, doc='get folder name')

    def update_info(self, *args) -> None:
        '''Runs post analysis and updates info label'''
        if self.post is not None:
            nom = self.v_fold.get()
            txt = self.post(nom)
            self.v_post.set(txt)
            if txt:
                self.extra.grid(row=3, column=1, columnspan=6, sticky=W)
                return
        self.extra.forget()

    def add_extra_info(self, post: Callable[[str], str]) -> None:
        '''Define post analysis and runs it to update info label'''
        self.post = post
        self.update_info()

    def get_info(self) -> str:
        """Returns extra info text"""
        return self.v_post.get()

class ExecStatus(ttk.LabelFrame):
    '''1-5 lines status frame'''
    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent)
        self.parent = parent
        self.configure(text=dlg['exestat'], height=80, padding=6)
        self.vars = []
        for k in range(1, 5):
            attr = 'v' + str(k)
            if not hasattr(parent, attr):
                break
            v = getattr(parent, attr)
            ttk.Label(self, textvariable=v).grid(row=len(self.vars), column=0, sticky=W)
            self.vars.append(v)

    def clear(self, *args, **kwargs) -> None:
        ''' clears status variables'''
        parent = self.parent
        try:
            count = kwargs.popitem()
        except KeyError:
            count = args[0] if args else -1
        if count < 0:
            count = 2**len(self.vars)-1
        for v in self.vars:
            count, reset = divmod(count, 2)
            if reset:
                getattr(parent, v).set('')

#****f* iFunctions/ask_for_single_input
# PURPOSE
#   Display a dialog box for a single data entry
# SYNTAX
#   val = ask_for_single_input(reason, defval=None)
# ARGUMENTS
#   * string reason: main prompt displayed in the dialog box
#   * defval: default value or type of expected value (int, float or str)
#     (default to None for str input)
# RESULT
#   * (int or float or str) val: value provided by the user, or defval.
# REMARKS
#   * if defval is a type (int, float, str) then user MUST enter a value of
#     this type and validate with OK. Null string is not allowed.
#   * if defval is a value (int, float, str) then it is retured if user
#     cancels the dialog.
# HISTORY
#   * 2025-06-26: function created (2.5.3)
#****

def ask_for_single_input(reason : str,
                defval : Union[int, float, str, Type[int], Type[float], Type[str]] = None):
    """Ask user to enter a value, whose type is determined as follows:
    - if defval is a type (int, float, str) ask for a value of this type - entry is mandatory
    - if defval is a value (of type int, float, str) ask for this type of entry; Cancel will
      use it as default value.
    - if defval is None, then a str is expected.

Reason is the main prompt text; expected type and default value are shown.
"""
    root = Tk()
    # Hide main window
    root.withdraw()
    # determine type of input based on default and nature
    KINT, KFLOAT, KSTR = 1, 2, 3
    default_value = None
    itype = KSTR
    if defval is not None:
        if isinstance(defval, type(int)):
            itype = KINT
        elif isinstance(defval, type(float)):
            itype = KFLOAT
        elif isinstance(defval, type(str)):
            itype = KSTR
        else:
            default_value = defval
            if isinstance(defval, int):
                itype = KINT
            elif isinstance(defval, float):
                itype = KFLOAT
            elif isinstance(defval, str):
                itype = KSTR
            else:
                default_value = None

    # create dialog texts
    title = dlg["param_input"]
    if itype == KINT:
        stype = "input_int"
        func = simpledialog.askinteger
    elif itype == KFLOAT:
        stype = "input_float"
        func = simpledialog.askfloat
    else:
        stype = "input_str"
        func = simpledialog.askstring
    prompt = dlg["input_prompt"].format(dlg[stype])
    if reason and isinstance(reason, str):
        prompt = reason + "\n\n" + prompt
    # Ask user for the value
    if default_value is None:
        user_input = None
        while user_input is None:
            user_input = func(title, prompt)
            if func == simpledialog.askstring and not user_input:
                user_input = None
    else:
        s_input_defval = dlg["input_defval"]
        prompt += f"\n[ x ] or [ Cancel ] => {s_input_defval} : {default_value}"
        user_input = func(title, prompt)
        if func == simpledialog.askstring and not user_input:
            user_input = None
        if user_input is None:
            user_input = default_value
            
    if user_input is not None:
        print(f"Valeur saisie : {user_input}")
    else:
        print("Aucune valeur saisie.")
    root.destroy()
    return user_input

if __name__ == "__main__":
    xx = ask_for_single_input("Réponse universelle ?", defval=42)
    xx = ask_for_single_input(defval=42.0)
    xx = ask_for_single_input(defval="42")
