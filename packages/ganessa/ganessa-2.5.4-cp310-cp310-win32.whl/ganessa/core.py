"""Main definitions of constants and functions for Piccolo/Ganessa_SIM API"""
#****g* ganessa.sim&th/Compatibility_
# PURPOSE
#   The installation of ganessa is compatible with several versions of Picwin32.dll
#  (regular Piccolo / Picalor). Missing functions in older versions should NOT be called.
# HISTORY
#   *  2014  -> 141203 Piccolo5 -- release 2014
#   * (2015a -> 151217 Piccolo6 & Picalor6 -- release 2015 (unstable)) - discarded
#   *  2015  -> 160121 Piccolo6 -- release 2015 sp1
#   *  2016  -> 160419 Piccolo6 & Picalor6 -- release 2016
#   *  2016a -> 160930 Piccolo6 release 2016b (incomplete; compatible with 1.4.2)
#   *  2016b -> 161216 Piccolo6 & Picalor6 -- release 2016b (1.5.0 - 1.5.2)
#   *  2017  -> 170627 Piccolo6 & Picalor6 -- release 2017  (1.7.7 - 1.7.8)
#   *  2017b -> 1709xx Piccolo6 & Picalor6 -- release 2017b (1.8.0 - 1.9.6)
#   *  2018  -> 180725 Piccolo6 & Picalor6 -- release 2018  (1.9.7 - )
#   *  2020  -> 200306 Piccolo6 & Picalor6 -- release 2020  (2.1.1 - )
#   *  2021  -> 2103xx Piccolo6 & Picalor6 -- release 2020b (2.1.1 - )
#   *  2022  -> 2209xx Piccolo6 & Picalor6 -- release 2022  (2.3.3 - )
#   *  2023  -> 230320 Piccolo6 & Picalor6 -- release 2023  (2.3.7 - )
#   *  2025  -> 250225 Piccolo6 & Picalor6 -- release 2025  (2.5.0 - )
# REMARK
#   ganessa is compatible with matching or newer versions of Ganessa_SIM/Ganessa_TH.dll only;
#   except a compatibility break on 170117.
#****

from typing import Any, Dict, Sequence, Tuple, Union, Callable, Literal, Mapping, List, Set
from importlib import import_module
import atexit
import numbers
# import re
from sys import modules as sys_modules
from os.path import dirname, exists as op_exists
from operator import itemgetter
from collections import Counter, OrderedDict, defaultdict

from ganessa.util import winstr, tostr, unistr, quotefilename, is_text, ws
from ganessa.util import unicode23, PICFILE_ENCODING
# from ganessa.util import _PTN_WQ_ATTR

from ganessa.util import dist_to_poly
from ganessa import __version__ as _version
from ganessa._getdll import _LookupDomainModule
from ganessa.sort import HeapSortRank

# import the keywords back from the importer module
_caller = _LookupDomainModule().module
_fresult, _lang, _protmode = _caller._fresult, _caller._lang, _caller._protmode
_dll_api = _caller._dll_api
_dll_context = _caller._dll_context
_dll_already_running = _dll_context.embedded
_dll_name = _dll_context.dll

_dll_version = int(_dll_api.getvar('VERSION')[0]) + 2000*10000 if _dll_already_running else 0
_ganessa_raise_exceptions = False
_debug = 0

#****g* ganessa.sim&th/Constants_
# DESCRIPTION
#   Several categories of constants are available:
#   * constants defining a type of element: see BRANCH or LINK, NODE, RESERVOIR or TANK
#   * constants defining a command module: M.COM or M.ROOT, M.GEN, M.SIM etc.
#   * constants defining a command within a module: M.SIM.EXEC
#   * keywords
#
#****
#****g* ganessa.sim&th/Exceptions_
# DESCRIPTION
#   Exceptions available to ganessa.sim and ganessa.th
#****
#****g* ganessa.sim&th/Functions_
# DESCRIPTION
#   Functions available to ganessa.sim and ganessa.th
#****
#****g* ganessa.sim&th/Iterators
# DESCRIPTION
#   Iterators available to ganessa.sim and ganessa.th
#****
#****g* ganessa.sim&th/Classes
# DESCRIPTION
#   Classes available to ganessa.sim and ganessa.th
#****
#****c* Constants/BRANCH, LINK_, NODE_, NOEUD, TANK_, RESERVOIR_, RSV
# DESCRIPTION
#   Those constants allow to select one of the three types of model elements:
#   * LINK or BRANCH: branches elements such as pipes, pumps, valves
#   * NODE or NOEUD
#   * TANK or RESERVOIR or RSV
# REMARK
#   M.LNK, M.NOD and M.RSV are object constants for calling BRANCH, NODE and RESERVOIR modules
#****
LINK = BRANCH = ARC = 1
NODE = NOEUD = 2
TANK = RESERVOIR = RSV = 3

ElemType = Literal[0, 1, 2, 3]
VectF = List[float]
VectI = List[int]

# Class for the dictionary tree for keywords by modules
#****c* Constants/M
# DESCRIPTION
#   The M class provide a dictionnary tree for modules. It provides a
#   hierarchical naming of the commands by modules, for building
#   language-independant commands using  gencmd, gencmdw, _gencmdw functions.
# SYNTAX
#   One of the following:
#   * M.MODULE_SYMBOLIC_NAME
#   * M.MODULE_SYMBOLIC_NAME.COMMAND__SYMBOLIC_NAME or
#   * M.MODULE_SYMBOLIC_NAME..NONE or M.NONE or M.VOID
# CONTENT
#   The available MODULE_SYMBOLIC_NAME are:
#
#   ROOT: modules names: BRA, NOD, RSV, DYN, MOD, SIM, QUA, MES, LAB, FIR, INV, OPT.
#   They can be used in three forms, as first argument for the functions above:
#   * M.ROOT.SIM or M.SIM.ROOT: equals the index of the module name
#   * M.SIM: can be used in gencmd and gencmdw only as first argument
#
#   GEN: general purpose commands:
#   * LOAD: load a binary file
#   * OPEN and CLOSE: open and close an output file
#   * QUIT: the quit command
#   * READ: read a command language or data file
#     |html <br>example: <i>gencmd(M.GEN, M.GEN.OPEN, DICT.EXPORT, 'filename.txt')</i>
#   * EXPORT, SAVE: export or save to a (previously opened) file
#   * IMPORT: import attributes for a type of element from a file
#   * FIND: command for retrieving a given period or instant
#   * MESSAGE: writes a message to the console
#   * DEFPARAM, DEFVAR: define a positional parameter (%1 ... %9) or variable
#   * UNIT: redefine units name and coef
#   * EOF: the end-of-file command
#   LNK: link commands and submodules, including link types (.PIPE .PUMP .NRV .PRV .PSV .FCV .TCV etc.)
#
#   NOD: node commands and submodules:
#   * CONS: demand acquisition submodule
#   * COEF, AREA: demand coefficient by demand type and area
#   * TOPO: topograpy submodule
#   RSV: reservoir command and submodules:
#   * CHAR: characteristics
#   * LEVEL: initial level acquisition submodule
#   MES: measurement commands:
#   * SMOOTH: allow to define the smoothing interval
#   SIM: simulation commands:
#   * FILE: define a result file name
#   * EXEC: runs the simulation
#   QUA: Water quality module commands
#
# REMARK
#   The above codes are not exhaustive. Please refer to the script.
#****
class _CST:
    def __init__(self, cst):
        self.ROOT = cst
        self.NONE = -1

class M:
    '''Module / keywords codes'''
    NONE = VOID = -1
    GEN = _CST(0)
    GEN.CLOSE = 13
    GEN.CMPT = GEN.COMPAT = 65
    GEN.DEFP = GEN.DEFPARAM = 51  # DefParam
    GEN.DEFV = GEN.DEFVAR = 66  # defvar
    GEN.ECHO = 16
    GEN.EOF = 3
    GEN.PIC2EPA = 61
    GEN.EPA2PIC = 62
    GEN.EXPT = GEN.EXPORT = 39  # Export
    GEN.FIND = 18  # Find (instant)
    GEN.FMT = GEN.FORMAT = 10
    GEN.IMPT = GEN.IMPORT = 48
    GEN.INIT = 6
    GEN.LOAD = 17  # Load file.bin
    GEN.MESG = GEN.MESSAGE = 45  # Message
    GEN.OPEN = 12
    GEN.PATH = 23  # Path
    GEN.QUIT = 2
    GEN.READ = 5
    GEN.SAVE = 4
    GEN.STOP = 69 # stop-on error
    GEN.UNIT = 22
    GEN.WORD = GEN.WORDING = 52  # Libelle

    COM = _CST(1)   # COMMAND root level
    ROOT = COM
    BRA = _CST(2)
    ARC = BRA
    LNK = BRA

    BRA.BEND = 28
    BRA.BOOST = 8
    BRA.CUST = 24           # Picalor
    BRA.DENSITY = 18
    BRA.DIAM = 27
    BRA.DIAPH = 4
    BRA.ENVP = 23           # Picalor
    BRA.GPV = BRA.PRBR = 14
    BRA.HLEQ = 9
    BRA.FCV = BRA.FCTV = 7
    BRA.HEAT = 16           # Picalor
    BRA.MANV = 6
    BRA.MAT = 15
    BRA.NRV = BRA.CHECKV = BRA.CV = 3
    BRA.PIPE = 1
    BRA.PRV = 12
    BRA.PSV = 13
    BRA.PUMP = 2
    BRA.SHLT = 32
    BRA.SING = BRA.SHL = 33
    BRA.SST = 19
    BRA.TCV = BRA.THRV = 20
    BRA.VISC = 17

    NOD = _CST(3)
    NOD.AREA = 14 # demand coef by area
    NOD.CONS = 2
    NOD.COEF = 3  # demand coef by code
    NOD.CSMP = 8 # pressure dependant demand
    NOD.INIT = 24
    NOD.P0 = 9
    NOD.P1 = 10
    NOD.TOPO = 1

    RSV = _CST(4)
    TNK = RSV
    RSV.CHAR = 1
    RSV.FEED = 3
    RSV.LEVEL = 2
    RSV.OUT = 4

    DYN = _CST(5)  # dynam
    DYN.CTRL = DYN.REGU = 5
    DYN.CTRL_ENT = 8
    DYN.DATA = 1
    DYN.DSTEP = 3
    DYN.NSTEP = 2

    MOD = _CST(7)  # Modification
    MOD.ADD = 4
    MOD.ALLOC = 15
    MOD.CLOSE = 8
    MOD.DEL = 1
    MOD.DIV = 3
    MOD.INSERT = 13
    MOD.MERGE = 10
    MOD.MULT = 2
    MOD.OPEN = 7
    MOD.PURGE = 17
    MOD.REPLACE = 6
    MOD.REVERSE = 12
    MOD.SPLIT = 11
    MOD.KWMAX = _CST(0)
    MOD.KWMAX.D = 1
    MOD.KWMAX.L = 2
    MOD.KWMAX.LG = 12
    MOD.KWMAX.CS = 3
    MOD.KWMAX.Z = 4
    MOD.KWMAX.R = 8
    MOD.KWCOH = _CST(0)
    MOD.KWCOH.D = 10
    MOD.KWCOH.M = 5
    MOD.KWCOH.R = 6
    MOD.KWCOH.ZN = 11

    SIM = _CST(8)
    SIM.CANCEL = SIM.ANNULER = 13
    SIM.EXEC = 1
    SIM.FILE = 25
    SIM.IVER = SIM.IVERB = 8
    SIM.STOP_DYN = 52
    SIM.STOP_ON = 51

    QUA = _CST(10)      # water quality
    WQ = QUA
    QUA.AGE = 8
    QUA.ALTC = 40
    QUA.CLEAR = QUA.CLEAN = 5
    QUA.CONTINUE = QUA.CONT = QUA.STEP = 13
    QUA.CORROSION = QUA.CORR = 29
    QUA.DECAY = QUA.CONST = 6
    QUA.EXEC = 3
    QUA.FILE = QUA.NODEFILE = 18
    QUA.FILELINK = QUA.LINKFILE = 32
    QUA.INIT = 17
    QUA.INITRSV = 31
    QUA.IVERC = QUA.KOPT = 19
    QUA.KCIN = 28
    QUA.K1 = 20
    QUA.K2 = 21
    QUA.ORDER = QUA.KINEXP = 39
    QUA.POLNOE = QUA.POL = 2
    QUA.POLRSV = 7
    QUA.REGIME = 4
    QUA.RESTIMINI = 43
    QUA.SAVESTATE = 42
    QUA.STORSTEPNODE = 12
    QUA.STORSTEPLINK = 33
    QUA.VISUSTART = 9
    QUA.VISUEND = 24
    QUA.VISUSTEP = 10
    QUA.WALL = 46

    MES = _CST(15)          # measure
    MES.SMOOTH = 6
    LAB = _CST(16)

    FIR = _CST(19)          # fire flow
    FIR.EXEC = 4
    FIR.HYDR = 6
    FIR.INIT = 10
    FIR.PFIX = FIR.Q = 1
    FIR.QFIX = FIR.P = 2
    FIR.TBL = 5
    FIR.WHAT = 3

    INV = _CST(20)          # inverse problem
    INV.BFACT = 11
    INV.CONS = INV.DEMAND = 13
    INV.DTSMOOTH = 7
    INV.EXEC = 8
    INV.FTOL = 32
    INV.INIT = 29
    INV.KMAT = 18
    INV.KWAL = INV.KWALL = 34
    INV.SHL = 26
    INV.NITER = 2
    INV.PARAM = 6
    INV.QUICK = 33
    INV.RMAT = 12
    INV.TSTART = INV.TDEB = INV.TBEG = 4
    INV.TEND = INV.TFIN = 5
    INV.TYPE = INV.METHOD = 1
    INV.WEIGHT = 24
    INV.ZMES = 23
    INV.ZTNK = 28

    OPT = _CST(21)      # options
    OPT.CIL = 1
    OPT.CIN = 2
    OPT.CIT = 3
    OPT.WQINIT = 7

# Build M.ROOT data from M.x.ROOT
for attr, val in M.__dict__.items():
    if attr[0:2] == '__':
        continue
    if attr in  ('ROOT', 'COM', 'NONE', 'VOID'):
        continue
    setattr(M.ROOT, attr, val.ROOT)

# Class for the isolated keywords
#****c* Constants/DICT_
# DESCRIPTION
#   The DICT class provide a dictionnary tree for keywords
# SYNTAX
#   DICT.SYMBOLIC_NAME
# CONTENT
#   * FULLPER: extended simulation (ENCHAINE in French)
#   * EXPORT
#   * INSTANT
#****
class DICT:
    '''Keywords codes'''
    AND = 11
    AUTO = 5
    AVERAGE = AVG = 76
    BINARY = 54
    BY = PAR = 114
    COMMA = VIRGULE = 122
    SEMICOMMA = POINTVIRGULE = CSV = 123
    DATA = 28
    DCF = TCB = 171
    DISTANCE = 155
    DYNAM = 75
    END = 9
    EXPORT = 92
    FILE = 8
    FNODE = TONODE = 168
    FULLPER = 91  # Full-period = enchaine
    INSTANT = 97
    INODE = FROMNODE = 167
    INVERS = REVERSE = 106
    MODEL = 179
    ON = 32
    OFF = 33
    PATH = PARCOURS = 157
    RESULT = 22
    STATIC = PERMANENT = 74
    TEXT = 65
    TO = 10
    TREE = 90

class SIMERR:
    '''Simulation erro codes'''
    SIMERR = 1024
    ISOL = 2
    SLOW_CV = 4
    UNSTABLE = 6
    FCTAPP = 8
    DIVERGE = 10
    DYNSTOP = 11
    STRUCT = 12
    MEMALLOC = 16

#****c* Constants/STR_ATTR_FR, STR_ATTR_EN, STR_ATTR_SP
# DESCRIPTION
#   Sets of attributes whose values are str; other attributes are numeric.
#   * STR_ATTR_FR: French str attributes
#   * STR_ATTR_EN: English str attributes
#   * STR_ATTR_SP: Spanish str attributes
# REMARK
#   see attr_is_str for testing against current language.
#****
STR_ATTR_FR = {"NI", "NF", "CD", "N", "A", "TY", "TF", "NO", "TR", "M", "MR", "PA", "PE", "CL",
               "ZN", "ZP", "CT", "TA", "DN", "DI", "PI", "N1", "N2", "GU", "ST"}
STR_ATTR_EN = {"NI", "NF", "CD", "N", "B", "TY", "TF", "NA", "PE", "M", "FM", "PW", "PC", "CL",
               "ZN", "ZP", "CT", "TA", "ND", "ID", "PI", "N1", "N2", "CE", "ST"}
STR_ATTR_SP = {"NI", "NF", "CD", "N", "A", "TI", "TF", "NO", "GH", "M", "ML", "PA", "PE", "CL",
               "ZN", "ZP", "CT", "TA", "DN", "DI", "PI", "N1", "N2", "UC", "ST"}

#****f* Functions_/attr_is_str
# DESCRIPTION
#   Returns True if the given attribute in the current language is a str value.
# SYNTAX
#   ret = attr_is_str(attrib)
# ARGUMENT
#   str attrib: symbol for the attribute
# RESULT
#   bool ret: True if the attribute value is of type str, False if not
# REMARK
#   Allow to select which function to use
# EXAMPLE
#   linkattrs if attr_is_str(attr) else linkattr
# HISTORY
#   Created 2024-07-18 (2.4.4)
#****
def is_str_attr(attrib : str) -> bool:
    """Tells if an attibute is of type str"""
    lang = getvar("_LANG_")[:2]
    return attrib in {"FR": STR_ATTR_FR, "EN": STR_ATTR_EN, "SP":STR_ATTR_SP}.get(lang, set())

# functions not defined when older dll are used
_fn_undefined = []

#****f* Functions_/implemented_
# SYNTAX
#   ret = implemented(name)
# ARGUMENT
#   str name: name of the function or iterator
# RESULT
#   bool ret: True if implemented, False if not
# HISTORY
#   Created 2022-07-21 (2.3.1)
#****
def implemented(func_name : str) -> bool:
    """Returns True if func_name implemented"""
    return not func_name in _fn_undefined

#****k* Iterators/Elements_
# SYNTAX
#   for id in Elements(typelt):
# ARGUMENT
#   int typelt: type element constants LINK, NODE, TANK, TANK+NODE
# RESULT
#   string id: id of each element of the given type in turn
# HISTORY
#   * From version 1.9.0 (2018/04/05) ids are returned as unicode strings.
#   * From version 2.0.3 (2018/12/03) len compatibility with python3
#   * From version 2.3.5 (2022/11/11) TANK+NODE returns supply nodes
#****
class Elements:
    '''Generic iterator for model elements'''
    def __init__(self, typelt: ElemType):
        if isinstance(typelt, numbers.Number):
            self.type = typelt
            self.nbmax = _dll_api.nbobjects(self.type)
        else:
            self.nbmax = 0
        self.index = 1
    def __iter__(self):
        return self
    def __next__(self) -> str:
        if self.index > self.nbmax:
            raise StopIteration
        (elem, ls) = _dll_api.getid(self.type, self.index)
        self.index += 1
        return tostr(elem[0:ls])
    def __len__(self) -> int:
        return self.nbmax
    next: str = __next__
    len: int = __len__

#****k* Iterators/Links_, Branches_
# SYNTAX
#   * for id in Links():
#   * for id in Branches():
# RESULT
#   string id: returns each branch id in turn
# REMARK
#   Branches and Links are equivalent.
# HISTORY
#   From version 1.9.0 (05/04/2018) ids are returned as unicode strings.
#****
#****k* Iterators/Nodes_
# SYNTAX
#   for id in Nodes():
# RESULT
#   Returns each node id in turn
# HISTORY
#   From version 1.9.0 (05/04/2018) ids are returned as unicode strings.
#****
#****k* Iterators/SupplyNodes
# SYNTAX
#   for id in SupplyNodes():
# RESULT
#   Returns each supply node id of head tanks in turn
# REMARK
#   Tank nodes are not considered as supply nodes.
# HISTORY
#   Created in 2.3.5 (221111)
#****
#****k* Iterators/Tanks_, Reservoirs_
# SYNTAX
#   * for id in Tanks():
#   * for id in Reservoirs():
# RESULT
#   string id: returns each reservoir id in turn
# REMARK
#   Tanks and Reservoirs are equivalent and return both tanks and pressure references.
#   In order to return specifically either, use Selectid with the appropriate selection:
#   (FR) "RESERVOIR (VO > 0) FIN" or "RESERVOIR (VO = 0) FIN" (UK) "RESERVOIR (VO > 0) END"
# HISTORY
#   From version 1.9.0 (05/04/2018) ids are returned as unicode strings.
#****
# Iterators for browsing model elements

class Nodes(Elements):
    '''Node iterator'''
    def __init__(self):
        super(Nodes, self).__init__(NODE)

class Branches(Elements):
    '''Links iterator'''
    def __init__(self):
        super(Branches, self).__init__(BRANCH)

class Links(Elements):
    '''Links iterator'''
    def __init__(self):
        super(Links, self).__init__(LINK)

class Reservoirs(Elements):
    '''Tanks iterator'''
    def __init__(self):
        super(Reservoirs, self).__init__(RESERVOIR)

class Tanks(Elements):
    '''Tanks iterator'''
    def __init__(self):
        super(Tanks, self).__init__(TANK)

class SupplyNodes(Elements):
    '''Node iterator'''
    def __init__(self):
        super(SupplyNodes, self).__init__(TANK+NODE)

def _ret_errstat(*args):
    """default function for not implemented call to API"""
    return -1

def _ret_errstat2(*args):
    """default function for not implemented call to API"""
    return -1, -1

def _check_u(text) -> None:
    if isinstance(text, unicode23):
        return
    print('%WARNING%- unicode string expected here:', ws(text))
    raise UnicodeError
#****f* Functions_/setbatchmode
# SYNTAX
#   oldmode = setbatchmode(mode)
# ARGUMENT
#   int mode: batch mode to activate
# RESULT
#   int oldmode: batch mode that was in effect
# REMARK
#   Defaults to 1 (True)
#****
try:
    setbatchmode: Callable[[int], int] = _dll_api.batchmode
except AttributeError:
    setbatchmode: Callable[[int], int] = _dll_api.setbatchmode

#****f* Functions_/openg, init_
# SYNTAX
#   * init([folder] [, silent=False] [, debug=False])
#   * openg([folder] [, silent=False] [, debug=False])
# ARGUMENT
#   str folder: optional folder name where journal and work files will be created
#   silent: if set to True, most information and warning message will not show
# DESCRIPTION
#   Initialises the ganessa simulation/command language engine.
# REMARKS
#   - Starting with version 1.3.5, a session should be started by calling init() or init(folder).
#     however for compatibility with previous releases where init was called at import time,
#     init is automatically called at 1st call of cmd, cmdfile, execute, load, loadbin
#   - A session should be terminated by calling quit() or typing <Ctrl>+Z
# HISTORY
#   * introduced in 1.3.5
#   * 1.9.6 (180615): fix non-ascii folder str converted to cp1252
#   * 2.3.8 (230419): openg introduced as an alias to init
#****
def init(folder: str = None, silent: bool = False, debug=0) -> None:
    '''Initialisation of the API
    folder: folder for temp files (journal, .bin results)
    silent: if set to True, most information and warning message will not show
    '''
    global _dll_version, _dll_api, _debug
    if debug:
        _debug = debug
        print('Debug mode activated - checking unicode str.')
    if _dll_already_running or _dll_version:
        return
    if not _dll_context.active:
        # reimport afer a previous close
        _dll_context.open()
        _dll_api = _dll_context.get_api()

    # Initialisation of ganessa
    if folder is None or not folder:
        _dll_version = _dll_api.inipic()
    else:
        if _debug:
            _check_u(folder)
        try:
            _dll_version = _dll_api.inipicfld(winstr(folder))
        except AttributeError:
            _dll_version = _dll_api.inipic()
            _fn_undefined.append('init(folder)')
    # context can be closed after init but can cause flexLM issues
    # _dll_context.close()
    # 2 places to check : here and pyGanSim.f90 (inipic)
    if _dll_version < 0:
        jj = -_dll_version
        comment = 'DLL ' + _dll_name
        if jj < 100:
            comment = 'No valid license for ' + comment + '\n'
        else:
            aa, mm, jj = jj//10000, (jj//100) % 100, jj%100
            comment += f' too old: {jj:02d}-{mm:02d}-{aa:02d}\n'
        print(comment)
        raise ImportError(comment)
    print('\t* ganessa:', _version, '-', _dll_name + ':', _dll_version, _lang, '*')
    _precmode = setbatchmode(1)
    if silent:
        _dll_api.gencmd(M.SIM.ROOT, M.SIM.IVER, M.NONE, '-9')
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _istat = _dll_api.commit(0)

openg = init

#****f* Functions_/dll_version, full_version
# SYNTAX
#   * yyyymmdd = dll_version()
#   * text = full_version()
# RESULT
#   * int yyyymmdd = dll version()
#   * str text = full_version()
# REMARK
#   Starting with 2.2.4 (210901), if called before init(), dll_version() will
#   return the version if the .dll is newer than 210831, 0 otherwise.
# HISTORY
#   * dll_version introduced in 1.8.0 (170907)
#   * full_version introduced in 1.8.6 (171201)
#   * returns api.dll_version() if defined (210901)
#****
def dll_version() -> int:
    '''Returns the version of the dll (after init)'''
    try:
        retval = _dll_api.dll_version()
        return retval
    except AttributeError:
        return _dll_version

def full_version() -> str:
    '''Returns the version of the dll (after init)'''
    ret = ' '.join((_dll_name, _lang, _protmode, str((dll_version()))))
    ret += ' / (py)ganessa ' + _version
    return ret

#****f* Functions_/is_embedded
# SYNTAX
#   ret = is_embedded()
# RESULT
#   * bool ret: indicates whether the python the package runs in is embedded in Piccolo.
# REMARKS
#   * It is used by OpenFileMMI.SelectModel and SelectFile in order to hide the model selection.
#   * When python is run in embedded mode, from Piccolo, any modification performed in a python
#     script will occur on the current Piccolo model.
# HISTORY
#   * introduced in 2.2.4 (210823)
#   * python embedding in Piccolo was introduced on 2025-06-23 in 2.5.3 (250630)
#****
def is_embedded() -> bool:
    '''Tells if called from embedded python'''
    return _dll_already_running

#****f* Functions_/quit_, close_
# SYNTAX
#   ret = quit([True])
#   ret = quit([True])
# ARGUMENT
#   optional bool verbose: if set to True, a message is printed.
#   Defaults to False.
# RESULT
#   text ret: text string telling that he module has been unloaded.
#   Terminates the ganessa session and unloads the module ganessa.sim&th
# REMARKS
#   - quit() is automatically called when quitting with <Ctrl>+Z
#   - close() is a synonym for quit()
#   - A session should be terminated by calling quit() or typing <Ctrl>+Z
#   - sys.exit() automatically trigers quit()
# HISTORY
#   - 2.3.0 (220415): do not delete import at close, allowing further init
#****
def close(*args) -> str:
    '''ends the session'''
    global _dll_api, _dll_version
    if _dll_already_running:
        return 'Keeping ' + _dll_name + ' alive.'
    if _dll_version:
        try:
            text = 'Ganessa unloaded.'
            _dll_api.closepic()
            # lib = ctypes.WinDLL(_dll_context.dir + '/' + _dll_context.dll)
            # libHandle = lib._handle
            # _dll_version = 0
            # del sys_modules['ganessa.' + _dll_context.pyd]
            # del _dll_api
            # ctypes.windll.kernel32.FreeLibrary(libHandle)
            _dll_api = None
        except (NameError, KeyError):
            text = 'Ganessa already unloaded...'
        _dll_version = 0
    else:
        text = 'Ganessa was not loaded!'
    _dll_context.close()
    if args and args[0]:
        print(text)
    return text
# Register closepic function for proper exit
atexit.register(close)
quit: Callable[[Any], str] = close

#****f* Functions_/cwfold
# SYNTAX
#   ret = cwfold(folder)
# ARGUMENT
#   str folder: folder name where journal (piccolo.jnl) and work files will be created
# RESULT
#   bool ret: True if folder exists; False otherwise
# HISTORY
#   introduced in 1.7.7 (170705)
#   * 1.9.6 (180615): fix non-ascii folder str converted to cp1252
#****
try:
    def cwfold(fold: str) -> bool:
        if _debug:
            _check_u(fold)
        _dll_api.cwfold(winstr(fold))
except AttributeError:
    _fn_undefined.append('cwfold(folder)')
    cwfold: bool = lambda x: False

#****f* Functions_/setlang
# SYNTAX
#   old_lang = setlang([new_lang = "None"])
# ARGUMENT
#   str new_lang: one of 'English', 'French', 'Spanish'. Defaults to 'None'.
# RESULT
#   str old_lang: previous language
# DESCRIPTION
#   Modifiy the current command language to new_lang (console version and macros only).
#   If the language name is misspelled (or 'None'), it will be ignored withour raising an error,
#   so the function will just return the current language.
# HISTORY
#   * introduced in 1.8.0 (170912)
#   * reviewed 2.2.7 (211124) : accepts new_lang with at least 1 letter
#****
def setlang(new_lang: str = "None") -> str:
    '''Sets a language for reading commands'''
    if _dll_version:
        _dll_api.gencmd(M.COM.ROOT, M.NONE)
        _istat = _dll_api.commit(0)
    else:
        init()
    kwl = '_LANG_'
    old_lang = getvar(kwl)
    if new_lang:
        for lng in ('ENGLISH', 'FRENCH', 'SPANISH'):
            if lng.startswith(new_lang.upper()):
                cmd(kwl + ' ' + lng)
                # water_hardness = dict(ENGLISH='HD', FRENCH='TH', SPANISH='DU')[lg]
                # _PTN_WQ_ATTR = re.compile(f'(T|{water_hardness}|C\\d|\\$[0-9A-Z])$')
                break
    return old_lang

# Execution error management
#****e* Exceptions_/useExceptions, GanessaError, SimulationError, IsolatedNodeSimulationError
# SYNTAX
#   * oldstat = useExceptions([status])
#   * try: ... except GanessaError:
#   * try: ... except SimulationError [as exc]:
#   * try: ... except IsolatedNodeSimulationError [as exc]:
# ARGUMENTS
#   bool status: if True, errors will raise exceptions
# RESULT
#   * bool oldstat: previous error handling mode
#   * exception exc: exception object. The attribute exc.reason will provide
#     additional information on the origin of error
# DESCRIPTION
#   SimulationError is a derived class of GanessaError.
#   IsolatedNodeSimulationError is a derived class of SimulationError, thrown when a simulation
#   error originates form isolated nodes.
#
#   The simulation error subtypes (exc.reason) are the following:
#   * SIMERR.ISOL: Isolated nodes
#   * SIMERR.SLOW_CV: Slow convergence (convergence not obtained within max iteration count)
#   * SIMERR.UNSTABLE: Unstability (flip between 2 or more equilibrium points)
#   * SIMERR.FCTAPP: Equipment(s) or storage(s) do not operate properly;
#     they can be retrieved with the Unstable() iterator
#   * SIMERR.DIVERGE: Divergence (convergence criteria increase)
#   * SIMERR.DYNSTOP: The simulation did not complete
#   * SIMERR.STRUCT: Structural inconsistency
#   * SIMERR.MEMALLOC: Memory allocation error (WQ or inverse problem)
# REMARK
#   By default, errors do not raise 'GanessaError' exceptions. If set to True,
#   errors raise exceptions with a string name giving the error message and a int reason
#   giving the type of exception.
# HISTORY
#   * 190715: added SIMERR.DYNSTOP
#   * 210624: added IsolatedNodeSimulationError
#   * 220415: Piccolo 'quit' command terminates
#****
class GanessaError(Exception):
    '''Error class'''
    def __init__(self, number: int, reason: int, text: str):
        if _debug:
            _check_u(text)
        self.number = number
        self.reason = reason
        self.text = tostr(text)
    def __str__(self):
        return _dll_name + f' ERROR : ({self.number:d}) : {self.text:s}'

class SimulationError(GanessaError):
    '''Simulation error subclass'''
    # Build SimulationError constants from SIMERR
    ISOL = SIMERR.ISOL
    SLOW_CV = SIMERR.SLOW_CV
    UNSTABLE = SIMERR.UNSTABLE
    FCTAPP = SIMERR.FCTAPP
    DIVERGE = SIMERR.DIVERGE
    DYNSTOP = SIMERR.DYNSTOP
    STRUCT = SIMERR.STRUCT
    MEMALLOC = SIMERR.MEMALLOC
    def __str__(self) -> str:
        sreason = {SIMERR.ISOL: 'Isolated nodes',
                   SIMERR.SLOW_CV: 'Slow convergence',
                   SIMERR.UNSTABLE: 'Instability',
                   SIMERR.FCTAPP: 'Equipment or storage do not operate properly',
                   SIMERR.DIVERGE: 'Divergence',
                   SIMERR.DYNSTOP: 'Extended Period Simulation ended prematurely',
                   SIMERR.STRUCT: 'Structural inconsistency',
                   SIMERR.MEMALLOC: 'Memory allocation error'}.get(self.reason, 'Unknown')
        detail = 'Hydraulic Simulation Error ({:d}) : {:s}\n{:s}'
        return detail.format(self.reason, sreason, GanessaError.__str__(self))

class IsolatedNodeSimulationError(SimulationError):
    '''Isolated Node Simulation erro subclass'''
    pass


def useExceptions(enable: bool = True) -> None:
    """enable/disable exceptions handling"""
    global _ganessa_raise_exceptions
    _ganessa_raise_exceptions = enable

def _checkExceptions(inum: int, istat: int, text: str = '') -> None:
    """Utility function that will raise exception in case of errors, if enabled"""
    if _debug:
        _check_u(text)
    if _ganessa_raise_exceptions and istat:
        stat = abs(istat)
        SIM_ERR = SIMERR.SIMERR
        if stat & SIM_ERR:     # simulation error code
            sim_reason = stat^SIM_ERR
            exc = IsolatedNodeSimulationError if sim_reason == SIMERR.ISOL else SimulationError
            raise exc(inum, sim_reason, text)
        elif istat > 0:
            raise GanessaError(inum, istat, text)
        else:
            print(f'WARNING: ({inum:d})', text, 'status=', str(istat))
    if istat < 0:
        close()

# Execute a command, a set of commands, a command file
#****f* Functions_/cmd, addcmdw, execute_, cmdfile
# SYNTAX
#   * istat = cmd(scmd)
#   * istat = cmdfile(fname [, args])
#   * istat = addcmdw(scmd)
#   * istat = execute(scmd1 [ ..., scmdn][, dbg= True])
# ARGUMENTS
#   * string scmd: command line to be executed
#   * string fname: data/command file name to be read/executed
#   * string args: optional argument(s) to the command file, as one single string
#   * string scmd1: command line(s) to be executed ('\n' is handled as a command delimiter)
#   * string scmdn: optional command lines(s) to be executed (same as scmd1)
#   * boolean dbg: optional, makes commands to be echoed in the log file.
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - cmd executes the given command
#   - cmdfile reads/executes the commands from the file.
#   - addcmdw pushes the command onto the command stack.
#   - execute pushes the given commands on the stack and executes them.
#   - The stack size (addcmdw, execute) is 64 or 128.
#
#   If an error occurs while reading a file or nested files, the execution stops.
#   If the useException mode is set, the error will raise a GanessaError
# HISTORY
#   * 1.9.6 (180615): convert str to cp1252
#   * 2.1.5 (200915): extend cmdfile to allow cmdfile(file, arg1, arg2, ..)
#   * 2.3.2 (220829): command_logger allows to log activity of cmd, cmdfile and execute
#   * 2.3.3 (220902): add CommandLogger.logs for handling cmdfile multiword command
#****
class CommandLogger:
    """class for loggin cmd, cmdfile and execute commands
    start logging: command_logger.activate = True
    manual entry: command_logger.append(text)
    dump: command_logger.save(filename)"""
    def __init__(self, activate : bool = False) -> None:
        self.commands = [""]
        self.activate = activate

    def log(self, cmd_str : str) -> None:
        """adds a new command"""
        if self.activate:
            self.commands.append(tostr(cmd_str))

    def logs(self, cmd_str : str) -> None:
        """adds a list of keywords as single command"""
        if self.activate:
            self.commands.append(" ".join(map(tostr, cmd_str)))

    def file_content(self, filename : str, merge_lines : int = 80) -> None:
        """Adds the content of the file"""
        if not op_exists(filename):
            return
        with open(filename, "r", encoding=PICFILE_ENCODING) as fin:
            content = ""
            for line in fin:
                line = line.rstrip()
                if len(line) + len(content) > merge_lines:
                    self.commands.append(" * " + content)
                    content = line
                elif content:
                    content += " \t" + line
                else:
                    content = line
            self.commands.append(" * " + content)

    def save(self, filename: str, purge : bool = True) -> None:
        """save the command file"""
        if filename and len(self.commands) > 1:
            with open(filename, "w", encoding=PICFILE_ENCODING) as logfile:
                logfile.write("\n ".join(self.commands))
        if purge:
            self.commands = [""]

command_logger = CommandLogger()


addcmdw: Callable[[str], int] = _dll_api.addcmd
def cmd(scmd: str) -> int:
    '''Execute a single command'''
    if not _dll_version:
        init()
    if _debug:
        _check_u(scmd)
    command_logger.log(scmd)
    istat = _dll_api.cmd(winstr(scmd))
    _checkExceptions(1, istat, 'Syntax error in command: ' + scmd)
    return istat

def cmdfile(fname: str, *args: Tuple[str, ...]) -> int:
    '''Reads (= executes) a command file with optional args'''
    if not _dll_version:
        init()
    if _debug:
        _check_u(fname)
    if args:
        # args = tuple(map(winstr, args))
        if len(args) > 1:
            args = (winstr(' '.join(map(quotefilename, args))), )
        else:
            args = (winstr(args[0]),)
    command_logger.logs([modulekeyword(0, M.GEN.READ), quotefilename(fname), *args])
    istat = _dll_api.cmdfile(winstr(fname), *args)
    _checkExceptions(8, istat, 'Syntax error in file: ' + fname)
    return istat

def execute(*args: Tuple[str, ...], **kwargs: Mapping[str, bool]) -> int:
    '''Executes a tuple of commands in turn
    Handles multiple commands separated with \n as well'''
    if not _dll_version:
        init()
    try:
        dbg = kwargs['dbg']
    except KeyError:
        dbg = False

    if dbg:
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.ECHO, DICT.ON)
    for arg in args:
        if _debug:
            _check_u(arg)
        for cmdline in arg.split('\n'):
            if cmdline:
                command_logger.log(cmdline)
                _dll_api.addcmd(winstr(cmdline))
    if dbg:
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.ECHO, DICT.OFF)
    istat = _dll_api.commit(0)
    _checkExceptions(4, istat, 'Multiple Commands execution error!')
    return istat

# Execute a command, a set of commands, a command file
#****f* Functions_/gencmd, gencmdw, raw_gencmdw, _gencmdw
# PURPOSE
#   Those fuctions allow to generate a language independant command line
#   based upon the keywords id of a module and its commands (see M).
# SYNTAX
#   * istat =  gencmd (module, icmd, [word, scmd, extmode])
#   * istat =  gencmdw(module, icmd, [word, scmd, extmode])
#   * istat = _gencmdw(module, icmd, [word, scmd, extmode])
# ARGUMENTS
#   * module: constant id for the module
#   * icmd:   constant id for the command in the module (or NONE)
#   * word:   constant id for a keyword (or NONE) (optional)
#   * scmd:   additional string (optional)
#   * extmode: if set to 1, the command is appended to the previous one (optional)
#   * string scmd: command line to be executed
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - gencmd builds and executes the given command
#   - gencmdw and _gencmdw build the command and push it onto the command stack
#   - gencmd and gencmdw allow a more flexible entry of the first 2 arguments
#   - If the useException mode is set, an error will raise a GanessaError
#   - raw_gencmdw is an exported version of _gencmdw
# EXAMPLES
#   The following are equivalent:
#   * istat = _gencmdw(M.SIM.ROOT, M.SIM.EXEC, DICT.FULLPER)
#   * istat = gencmdw(M.SIM, "EXEC", DICT.FULLPER)
#   The following are equivalent:
#   * istat = _gencmdw(M.SIM.ROOT, M.SIM.EXEC, scmd="15:30")
#   * istat = gencmdw(M.SIM, "EXEC", scmd="15:30")
# HISTORY
#   1.8.0 (170908): added raw_gencmdw
#****
# Wrapping for 'gencmd': allow the class name as arg1 and if so the attribute name as arg2
_gencmdw = _dll_api.gencmd
raw_gencmdw = _dll_api.gencmd
def gencmdw(module, cmde, *args, **kwargs) -> None:
    '''Generate a command and push on the cmd stack'''
    if not _dll_version:
        init()
    if isinstance(module, numbers.Number):
        modul = module
    else:
        modul = module.ROOT
    if isinstance(cmde, numbers.Number):
        attr = cmde
    else:
        try:
            attr = getattr(modul, cmde.upper())
        except:
            attr = M.NONE
            print('Command or keyword not recognised:', repr(cmde), '\n')
    _dll_api.gencmd(modul, attr, *args, **kwargs)

def gencmd(modul, cmde, *args, **kwargs) -> int:
    '''Generate a command, pushonto the stack and execute the stack as FIFO'''
    gencmdw(modul, cmde, *args, **kwargs)
    istat = _dll_api.commit(0)
    _checkExceptions(3, istat, 'Syntax error in command: ')
    return istat

#****f* Functions_/getkeyword, modulekeyword, attrkeyword, attrname, attrindex
# PURPOSE
#   Get keyword or command name by index  - for building
#   command language independant functions
# SYNTAX
#   * sret = getkeyword(code)
#   * sret = modulekeyword(module, submodule)
#   * sret = attrkeyword(attr)
#   * sret = attrname(attr)
#   * iret = attrindex(sattr)
# ARGUMENTS
#   * int code: code of the keyword (>0) or global command (<0)
#   * int module: code of the module (<0 for the submodule alone)
#   * int submodule: code of the module (0 for the module alone)
#   * int attr: code of the attribute
#   * str sattr: attribute
# RESULT
#   * str sret: trimmed value of the keyword or global command or module submodule
#         (null string if the code or module/submodule is not recognised)
#   * int iret: code for the attribute (0 if undefined)
# HISTORY
#   * getkeyword introduced in 1.4.2 (161010)
#   * modulekeyword and attrkeyword intoduced in 1.7.3 (170313)
#   * From version 1.9.0 (05/04/2018) results are returned as unicode strings.
#   * attrname and attrindex introduced in 2.3.7 (230320) and requires version 2023 (230320) or higher of Piccolo/Ganessa_Sim dll
#****
try:
    _getkeyword = _dll_api.keyword
except AttributeError:
    _getkeyword = lambda code: (0, "")
    _fn_undefined.append('getkeyword')

def getkeyword(code: int) -> str:
    """Returns keyword (code > 0) or global command name (code < 0)"""
    nret, sret = _getkeyword(code)
    return tostr(sret[:nret])

try:
    _modulekeyword = _dll_api.modulekeyword
except AttributeError:
    _modulekeyword = lambda m, sm: (0, "")
    _fn_undefined.append('modulekeyword')

def modulekeyword(module: int, submodule: int) -> str:
    """Returns module and/or submodule keyword(s)"""
    nret, sret = _modulekeyword(module, submodule)
    return tostr(sret[:nret])

try:
    _attrkeyword = _dll_api.attrkeyword
except AttributeError:
    # attrkeyword = lambda code: {5:'NI', 6:'NF', 60:'ZN'}.get(code, '#')
    def attrkeyword(code: int) -> str:
        """Returns symbol (minimal implementation)"""
        return {5:'NI', 6:'NF', 60:'ZN'}.get(code, '#')
    _fn_undefined.append('attrkeyword')
else:
    def attrkeyword(code: int) -> str:
        """Returns symbol"""
        return tostr(_attrkeyword(code))

try:
    _attrname = _dll_api.attrname
    attrindex: Callable[[str], int] = _dll_api.attrindex
except AttributeError:
    # attrname = lambda code: {61:'XX', 83:'YY', 171:'ZZ'}.get(code, '#')
    def attrname(code: int) -> str:
        """Returns symbol long name (minimal implementation)"""
        return {61:'XX', 83:'YY', 171:'ZZ'}.get(code, '#')
    attrindex = _ret_errstat
    _fn_undefined.extend(["attrname", "attrindex"])
else:
    def attrname(code: int) -> str:
        """Returns symbol long name - Piccolo returns cp850 encoded bytes"""
        sz, name = _attrname(code)
        return str(name[:sz], "cp850")

#****f* Functions_/commit
# PURPOSE
#   Executes all the commands available on the stack (first in, first executed)
# SYNTAX
#   istat = commit()
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   If an error occurs, the remaining part of the stack is cleared
#****
def commit(*args) -> int:
    '''Execute the command stack'''
    istat = _dll_api.commit(*args)
    _checkExceptions(2, istat, 'Command language execution error!')
    return istat

#****f* Functions_/reset_
# PURPOSE
#   Clears (removes) all model objects
# SYNTAX
#   istat = reset()
# RESULT
#   int istat: error status (0 if OK)
#****
def reset() -> int:
    '''Clears (removes) all model objects'''
    if not _dll_version:
        init()
    nbn = _dll_api.nbobjects(NODE)
    _dll_api.addcmd(' /* before system reset: nb of nodes: ' + str(nbn))
    # COMM INIT
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.INIT, extmode=True)
    return _dll_api.commit(0)

#****f* Functions_/loadbin
# PURPOSE
#   Clears (removes) all model objects and loads a binary file
# SYNTAX
#   istat = loadbin(fname)
# ARGUMENT
#   string fname: binary data/result file name to be loaded
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - The current model is discarded before the new one is loaded.
#   - If the file content is not a Piccolo binary file an error occurs.
#   - Binary result files also contain all data describing the model.
#   - The filename is quoted if necessary
#****
def loadbin(fname: str) -> str:
    """Removes all model objects and loads a binary file"""
    if not _dll_version:
        init()
    if _debug:
        _check_u(fname)
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.LOAD, scmd=winstr(quotefilename(fname)))
    istat = _dll_api.commit(0)
    _checkExceptions(16, istat, 'Error loading binfile: ')
    return istat

#****f* Functions_/loadres
# PURPOSE
#   Loads the default binary result file.
# SYNTAX
#   istat = loadres()
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   The current model is discarded before the data corresponding to
#   the last simulation making use of the default result file is loaded.
#****
def loadres() -> int:
    """Loads the default binary result file"""
    if _fresult:
        return loadbin(_fresult)
    else:
        print(' *** Result file not found !')
        return 1

#****f* Functions_/resfile, res_filename, model_filename, result_filename, emb_model_folder
# PURPOSE
#   Returns the name of the default binary result file; the model filename;
#   the actual result file name if defined.
# SYNTAX
#   * name = resfile()
#   * name = res_filename()
#   * name = result_filename()
#   * name = model_filename()
#   * folder = emb_model_folder()
# RESULT
#   str name: file name or "" if undefined
#   str folder: folder if called from embedded python or "" if not
# HISTORY
#   * 170919 (1.8.0) Introduced resfile (default binary result file)
#   * 210929 (2.2.5) Added model_filename and res_filename (= resfile)
#   * 211112 (2.2.6) Added emb_model_folder
#   * 250619 (2.5.3) Added result_filename (current binary result file)
#****
def resfile() -> str:
    '''Returns the default binary result file'''
    return _fresult
def res_filename() -> str:
    '''Returns the default binary result file'''
    return _fresult
def model_filename() -> str:
    '''Return the unquoted model fullname'''
    return getvar(getkeyword(DICT.MODEL)).strip('"')
def emb_model_folder() -> str:
    '''Returns the model folder name if embedded, else None'''
    return dirname(model_filename()) if is_embedded() else ""
def result_filename() -> str:
    """Returns the name of the hydraulic simulation results bin file"""
    name = getvar(getkeyword(DICT.BINARY)).strip('"')
    return name if name else _fresult
    

#****f* Functions_/nbobjects
# PURPOSE
#   Returns the number of model elements in the given type
# SYNTAX
#   nb = nbobjects(typelt)
# ARGUMENT
#   int typelt: type of element (LINK, NODE, TANK) or NODE+TANK for supply nodes
# RESULT
#   int nb: number of element in that type
# REMARK
#   Call for tank supply nodes count (NODE+TANK) requires 2022-11-11 or higher version
#   of Piccolo/Ganessa_SIM dll.
#****
nbobjects: Callable[[ElemType], int] = _dll_api.nbobjects

#****f* Functions_/selectlen, select_
# PURPOSE
#   * selectlen returns the number and type of model elements in the given selection
#   * select: returns the index vector, number and type of elements in the selection
# SYNTAX
#   * nb, typelt = selectlen(sname)
#   * vect_idx, nb, typelt = select(sname)
# ARGUMENT
#   string sname: name of selection
# RESULT
#   * int nb: number of element in that selection
#   * int typelt: type of element of that selection
#   * int vect_idx[]: index vector of elements in the selection
#****
try:
    _selectlen: Tuple[int, ElemType] = _dll_api.getselectlen
    _select: VectI = _dll_api.getselect
except AttributeError:
    _selectlen: Tuple[int, ElemType] = _dll_api.selectlen
    _select: VectI = _dll_api.select
def select(sname: str) -> Tuple[VectI, int, ElemType]:
    '''Returns the index vector, number and type of elements'''
    if _debug:
        _check_u(sname)
    nb, typelt = _selectlen(winstr(sname))
    return (_select(nb), nb, typelt)
selectlen: Callable[[str], Tuple[int, ElemType]] = _selectlen

#****f* Functions_/nbvertices
# PURPOSE
#   Returns the number of links with vertices (bends)
# SYNTAX
#   nb = nbvertices()
# RESULT
#   int nb: number of links with vertices
#****
def nbvertices() -> int:
    '''Returns the number of links with vertices'''
    sel_bends = modulekeyword(M.LNK.ROOT, 0) + ' (XY > 0) ' + getkeyword(DICT.END)
    nb, _ = selectlen(sel_bends)
    return nb

#****k* Iterators/Selectid, Selected
# SYNTAX
#   for id in Selectid(select_name):
#
#   for id, typelt in Selected(select_name [, return_type=True]):
# ARGUMENT
#   string select_name: selection definition or selection name
#   bool return_type: if False, the type is not returned (default True)
# RESULT
#   Returns the id [and type] of each element in the selection in turn:
#   * string id: id of the next element in the selection
#   * int type: element type (the same for all ids), if return_type is True
# HISTORY
#   * 2.0.3 (2018/12/03) len compatibility with python3
#   * 2.1.1 (2020/03/20) add return_type optional keyword argument
#   * 2.2.9 (2022/02/11) convert string to ansi for Piccolo cmd language
#   * 2.3.0 (2022/04/20) add Selectid(sname) - same behaviour as Selected(sname, False)
#   * 2.3.7 (2023/03/30) empty selection returns empty iterator
#   * 2.4.4 (2024/07/17) added numelt field
#****
# Iterators for browsing model elements
class Selectid:
    '''Command language Selection iterator with no return type'''
    def __init__(self, select_name: str):
        self.definition = select_name
        self.return_type = False
        self.index = 0
        self.numelt = 0
        if _debug:
            _check_u(select_name)
        if not select_name.strip():
            self.nbmax = 0
        else:
            self.nbmax, self.type = _selectlen(winstr(select_name))
            if self.nbmax > 0:
                self.select = _select(self.nbmax)

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.select
                self.nbmax = 0
            raise StopIteration
        self.numelt = self.select[self.index]
        elem, ls = _dll_api.getid(self.type, self.numelt)
        self.index += 1
        return tostr(elem[0:ls])

    def __len__(self) -> int:
        return self.nbmax

    next = __next__

    len = __len__

class Selected(Selectid):
    '''Command language Selection iterator - optional return type'''
    def __init__(self, select_name: str, return_type: bool = True):
        super().__init__(select_name)
        self.return_type = return_type

    def __next__(self) -> Union[str, Tuple[str, ElemType]]:
        ret_val = super().__next__()
        if self.return_type:
            return (ret_val, self.type)
        return ret_val

#****k* Iterators/Pipes
# PURPOSE
#   Returns pipe IDs otionnaly with one or more attributes.
# SYNTAX
#   for id in Pipes():
#
#   for id, *retvals in Pipes(*attrs):
# ARGUMENT
#   optional str attrs: attributes values to be returned
# RESULT
#   Returns the id [and attributes values if one or more "attr" given] of each pipe element in turn:
#   * string id: id of the next pipe element
#   * tuple of float or str retvals: values of the attributes for the pipe (as many as attributes in attrs)
# HISTORY
#   * 2.4.4 (2024/07/17) created
#****
class Pipes(Selectid):
    """Pipes iterator returning an optional attribute"""
    def __init__(self, *attr_sequence: Sequence[str]):
        # get "PIPE"
        super().__init__(modulekeyword(-2, 1))
        self.attrs = tuple(attr for attr in attr_sequence if attr)
        if not self.attrs:
            return
        lang = getvar("_LANG_")[:2]
        str_attrs = {"FR": STR_ATTR_FR, "EN": STR_ATTR_EN, "SP":STR_ATTR_SP}[lang]
        self.attr_getter1 = tuple((lambda x, y=attr: nlinkattrs(x, y)) if attr in str_attrs else
                                  (lambda x, y=attr: nlinkattr(x, y))
                                  for attr in self.attrs)
        self.attr_getter2 = tuple((nlinkattrs if attr in str_attrs else nlinkattr)
                                  for attr in self.attrs)

    def __next__(self) -> Union[str, Tuple[str, float]]:
        ret_val = super().__next__()
        if self.attrs:
            # attr_getter1 is 2% faster than attr_getter2 with 3 attributes
            return ret_val, *(getter(self.numelt) for getter in self.attr_getter1)
            # return ret_val, *(getter(self.numelt, attr)
            #        for getter, attr in zip(self.attr_getter2, self.attrs))
        return ret_val

#****f* Functions_/linkattr, nodeattr, tankattr, linkattrs, nodeattrs, tankattrs, attr_, attrs_, meanattr, linkattrv, tankattrv
# PURPOSE
#   * linkattr, nodeattr, rsvattr, attr: return numerical attributes
#     of a given element by id
#   * linkattrs, nodeattrs, attrs: return text attributes of a
#     given element by id
#   * meanattr: return mean attribute of from and to nodes given by branch id
# SYNTAX
#   * val = linkattr(id, attr)
#   * val = nodeattr(id, attr)
#   * val = tankattr(id, attr)
#   * txt = linkattrs(id, attr)
#   * txt = nodeattrs(id, attr)
#   * txt = tankattrs(id, attr)
#   * val = attr[typelt](id, attr)
#   * btxt, sz = attrs(typelt, id, attr)
#   * val = meanattr(id, attr)
#   * valx, valy, count = linkattrv(id, attr)
#   * valx, valy, count = tankattrv(id, attr)
# ARGUMENTS
#   * string id: id of element
#   * string attr: attribute (data or result) for which value is requested
#   * int typelt: type of element
# RESULT
#   * float val: value of the numerical attribute (0. if not available)
#   * string txt: value of the text attribute (empty string '' if
#     undefined or not available)
#   * byte btxt: value of the text attribute, as a byte (python3) or str(python2)
#   * int sz: length of the returned string
#   * valx, valy: array of float for the curve
#   * count: #points for the returned curve (0 if none)
# REMARKS
#   * Numerical attributes are returned converted in the actual unit system.
#   * Reservoir text attributes are identical to the underlying node id
#   * meanattr requires version 2016 or higher of Piccolo/Ganessa dll
#   * branchattr, rsvattr and branchattrs are synonyms for linkattr, tankattr and linkattrs
#   * linkattrv, tankattrv requires version 2022 (220804) or higher of Piccolo/Ganessa dll
#   * tankattrs(rsv_id, "TY") returns fill mode keyword, while "TF" (FR, esp) / "FT" (UK)
#     returns drain mode (requires version 240416 or higher of Piccolo/Ganessa dll)
#   * tankattr(rsv_id, "TY") returns 2*fill + drain mode = 0 .. 3 -
#     (requires version 240418 or higher of Piccolo/Ganessa dll)
# HISTORY
#   * version 1.9.0 (05/04/2018) ids and attributes are returned as unicode strings.
#   * version 2.3.2 (04/08/2022) added linkattrv and tankattrv
#****
nodeattr: Callable[[str, str], float] = _dll_api.nodeattr
linkattr: Callable[[str, str], float] = _dll_api.branchattr
tankattr: Callable[[str, str], float] = _dll_api.rsvattr
branchattr: Callable[[str, str], float] = _dll_api.branchattr
rsvattr: Callable[[str, str], float] = _dll_api.rsvattr

attr: float = {LINK: _dll_api.branchattr,
        NODE: _dll_api.nodeattr,
        TANK: _dll_api.rsvattr}
attrs: str = _dll_api.strattr

def linkattrs(eid: str, sattr: str) -> str:
    """Returns the value of str attribute 'sattr' for link 'eid'"""
    sval, n = _dll_api.strattr(LINK, eid, sattr)
    return tostr(sval[0:n]) if n > 0 else ''
branchattrs = linkattrs

def nodeattrs(eid: str, sattr: str) -> str:
    """Returns the value of str attribute 'sattr' for node 'eid'"""
    sval, n = _dll_api.strattr(NODE, eid, sattr)
    return tostr(sval[0:n]) if n > 0 else ''

def tankattrs(eid: str, sattr: str) -> str:
    """Returns the value of str attribute 'sattr' for tank 'eid'"""
    sval, n = _dll_api.strattr(TANK, eid, sattr)
    return tostr(sval[0:n]) if n > 0 else ''

try:
    meanattr: Callable[[str, str], float] = _dll_api.nodemeanattr
except AttributeError:
    meanattr = lambda sid, sattr: 0.0
    _fn_undefined.append('meanattr')

try:
    linkattrvlen: Callable[[str, str], int] = _dll_api.linkattr_arrcount
    tankattrvlen: Callable[[str, str], int] = _dll_api.tankattr_arrcount
except AttributeError:
    linkattrvlen = _ret_errstat
    tankattrvlen = _ret_errstat
    _fn_undefined.extend(['linkattrvlen', 'tankattrvlen', 'linkattrv', 'tankattrv'])

def linkattrv(eid: str, sattr: str) -> Tuple[VectF, VectF, int]:
    """Returns the Q, HH pump or GPV curve (attr CO), or Q, efficiency curve (attr RT) """
    nbval = linkattrvlen(eid, sattr)
    if nbval > 0:
        return _dll_api.linkattr_arr(nbval)
    return None, None, 0

def tankattrv(eid: str, sattr: str) -> Tuple[VectF, VectF, int]:
    """attr: CO or VO: returns the height/volume
             SC: returns the height/section
             RH: returns the hydraulic resistance (pass N2 eid to get the 2nd)"""
    nbval = tankattrvlen(eid, sattr)
    if nbval > 0:
        return _dll_api.tankattr_arr(nbval)
    return None, None, 0


#****f* Functions_/shearstr
# PURPOSE
#   Returns the shear stress associated with a velocity for the given pipe
# SYNTAX
#   val, grad = shearstr(id, v)
# ARGUMENTS
#   * string id: id of element
#   * float v: velocity for which value is requested
# RESULT
#   * float val: value of the shear stress
#   * float grad: value of ds/dv
# REMARKS
#   * val is not defined if id is not a pipe
#   * requires Piccolo 2017
# HISTORY
#   * 31.03.2017: function created (1.7.3)
#****
try:
    shearstr = _dll_api.shearstr
except AttributeError:
    shearstr = lambda sid, val: (0.0, 0.0)
    _fn_undefined.append('shearstr')

#****f* Functions_/nlinkattr, nnodeattr, ntankattr, nlinkattrs, nnodeattrs, ntankattrs, nattr, nattrs
# PURPOSE
#   * nlinkattr, nnodeattr, nrsvattr, nattr: return numerical attributes
#     of a given element by index
#   * nlinkattrs, nnodeattrs, nattrs: return text attributes of a
#     given element by index
# SYNTAX
#   * val = nlinkattr(num, attr)
#   * val = nnodeattr(num, attr)
#   * val = ntankattr(num, attr)
#   * txt = nlinkattrs(num, attr)
#   * txt = nnodeattrs(num, attr)
#   * txt = ntankattrs(num, attr)
#   * val = nattr[typelt](num, attr)
#   * btxt, sz = nattrs(typelt, num, attr)
# ARGUMENTS
#   * int num: index of element (stating at 1)
#   * string id_or_num: id or index of element
#   * string attr: attribute (data or result) for which value is requested
#   * int typelt: type of element
# RESULT
#   * float val: value of the numerical attribute (0. if not available)
#   * string txt: value of the text attribute (empty string '' if
#     undefined or not available)
#   * int sz: length of the returned string
#   * byte btxt: value of the text attribute, as a byte (python3) or str(python2)
# REMARKS
#   * Numerical attributes are returned converted in the actual unit system.
#   * Tank text attributes are identical to the underlying node id
# HISTORY
#   From version 1.9.0 (05/04/2018) ids and attributes are returned as unicode strings.
#****
try:
    nnodeattr: float = _dll_api.nnodeattr
    nlinkattr: float = _dll_api.nlinkattr
    ntankattr: float = _dll_api.ntankattr
    nattrs: str = _dll_api.nstrattr
except AttributeError:
    _fn_undefined.extend(['nnodeattr', 'nlinkattr', 'ntankattr', 'nattr',
            'nattrs', 'nnodeattrs', 'nlinkattrs', 'ntankattrs',])
    ntankattr = nlinkattr = nnodeattr = lambda num, attr: 0.0
    nattrs = lambda typ, num, attr: ""

nattr: float = {LINK: nlinkattr,
                NODE: nnodeattr,
                TANK: ntankattr}

def nlinkattrs(num: int, sattr: str) -> str:
    """Returns the str link attribute at index num"""
    sval, n = nattrs(LINK, num, sattr)
    return tostr(sval[0:n]) if n > 0 else ""
branchattrs = linkattrs

def nnodeattrs(num: int, sattr: str) -> str:
    """Returns the str node attribute at index num"""
    sval, n = nattrs(NODE, num, sattr)
    return tostr(sval[0:n]) if n > 0 else ""

def ntankattrs(num: int, sattr: str) -> str:
    """Returns the str tank attribute at index num"""
    sval, n = nattrs(TANK, num, sattr)
    return tostr(sval[0:n]) if n > 0 else ""


#****f* Functions_/getdemandbycode, getcodedemandinit, nextcodedemand
# PURPOSE
#   * getdemandbycode: returns demand for a given node and consumer code by id
#   * getcodedemandinit: initialises and returns the number of pairs
# SYNTAX
#   * demand, istat = getdemandbycode(nid, code)
#   * nbpairs = getcodedemandinit(nid)
#   * code, demand, codelen = nextcodedemand()
# ARGUMENTS
#   * string nid: id of node
#   * string code: code for which demand value is requested
#   * int nbpairs: number of demand, csm pairs for the node
# RESULT
#   * float demand: value of the demand (0 if not available)
#   * int istat: return code (0= 0K -1= unknown code 1= unknown node 3= dll too old)
#   * int nbpairs: number of code, demand pairs for the node
#   * string code: demand code
#   * int codelen: length of code string
# REMARKS
#   * these functions require version 2016 or higher of the Piccolo/Ganessa dll
#   * If the GanSim Dll is too old those function will not return data
#   * See also the Demands(nid) iterator
# HISTORY
#   From version 1.9.0 (05/04/2018) codes are returned as unicode strings.
#****
try:
    getdemandbycode: Callable[[str, str], Tuple[float, int]] = _dll_api.getdemandnodebycode
    getcodedemandinit: Callable[[str], Tuple[int, int]] = _dll_api.getcodedemandinit
    nextcodedemand: Callable[[], Tuple[str, float, int]] = _dll_api.nextcodedemand
except AttributeError:
    getcodedemandinit = _ret_errstat
    _fn_undefined.append('Demands')
    _fn_undefined.append('demand by node getter')

#getcodedemandall = _dll_api.getcodedemandall
#****k* Iterators/Demands
# SYNTAX
#   for code, csm in Demands(node_id):
# ARGUMENT
#   string node_id: id of node
# RESULT
#   Returns each demand code and nominal value for the node in turn:
#   * string code: demand code
#   * float csm: demand value for this code
# REMARK
#   * requires version 2016 or higher of Piccolo/Ganessa dll
# HISTORY
#   From version 1.9.0 (05/04/2018) codes are returned as unicode strings.
#****
# Iterators for browsing demand codes and values for a given node
class Demands:
    '''Iterator over demand code, damand value at a given node'''
    def __init__(self, node_id: str):
        self.nb, self.szcod = getcodedemandinit(node_id)
        if self.nb < 0:
            raise GanessaError(8, 0, 'The version of ' + _dll_name +
                                ' does not support this feature')
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, float]:
        if self.nb == 0:
            raise StopIteration
        self.nb -= 1
        code, csm, n = _dll_api.nextcodedemand()
        return (tostr(code[0:n]), csm) if n > 0 else ('', 0.0)
    next = __next__

#****f* Functions_/getcodescount, nextcode
# PURPOSE
#   * getcodescount: returns count of used demand codes
#   * nextcode: returns the list of used codes with node count
# SYNTAX
#   * ncodes = getcodescount(used_only)
#   * code, demand, count, nbchar  = nextcode()
# ARGUMENTS
#   * bool used_only: if True, only codes associated with at least
#     one node will be returned
# RESULT
#   * int ncodes: number of codes to be returned
#   * str code: demand codes
#   * float demand: total nominal demand for the code
#   * int count: node count
#   * int nbchar: nb of chars in the demand code string
# REMARKS
#   * these functions require version 2016 or higher of Piccolo/Ganessa dll
#   * If the GanSim Dll is too old those function will not return data
#   * See also the Demands(id) iterator
# HISTORY
#   From version 1.9.0 (05/04/2018) codes are returned as unicode strings.
#****
try:
    getcodescount: Callable[[bool], int] = _dll_api.getcodescount
    nextcode: Callable[[], Tuple[str, float, int, int]] = _dll_api.nextcodecsmnodecount
except AttributeError:
    _fn_undefined.append('DemandCodes')
    _fn_undefined.append('demand codes table getter')
    getcodescount = _ret_errstat

#****k* Iterators/DemandCodes
# SYNTAX
#   for code, demand, nodecount in DemandCodes():
# RESULT
#   Returns each demand code and node count in turn:
#   * string code: demand code
#   * float demand: total demand value for the code
#   * int count: node count associated with the code
# REMARK
#   * DemandCodes requires version 2016 or higher of Piccolo/Ganessa dll
# HISTORY
#   Added 11/09/2015
#****
# Iterators for browsing demand codes and values for a given node
class DemandCodes:
    '''Iterator for demand codes, total nominal demand and node count
    Added 150911'''
    def __init__(self, used_only: bool = False):
        self.used_only = used_only
        self.nbc = getcodescount(used_only)
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, float, int]:
        if self.nbc <= 0:
            raise StopIteration
        self.nbc -= 1
        code, csm, nbn, lnc = _dll_api.nextcodecsmnodecount()
        return (tostr(code[0:lnc]), csm, nbn) if lnc > 0 else ('', 0.0, 0)
    next = __next__

#****k* Iterators/Table_
# SYNTAX
#   for item, objcount in Table(table, typelt=LINK):
# ARGUMENTS
#   * string table: requested table (2 char symbol or table name)
#   * int typelt: optional type of element (LINK or NODE), if table is ZN or ZP.
#     Defaults to LINK.
# RESULT
#   Returns each table entry and associated object count in turn:
#   * string item: table entry (possibly empty string)
#   * int objcount: node or link count associated with the code
# REMARKS
#   * Table requires version 2015/12 or higher of Piccolo/Ganessa dll
#   * see TableValues for getting values associated with entries
#   * in order to get demand counts per zone, use "COEFFICIENT-ZONE" table name.
#   * empty entry may be reported as "(DEFLT)" or "(DEFAUT)"
# HISTORY
#   * From version 1.9.0 (05/04/2018) items are returned as unicode strings.
#   * Modified 2023/03/27 (version 2.3.7): added demand codes and zones - requires version 2023 (230327) or higher of Piccolo/Ganessa_Sim dll
#****
try:
    tablecount: Callable[[str, int], int] = _dll_api.tablecount
except AttributeError:
    _fn_undefined.append('Table')
    _fn_undefined.append('table entries getter')
    tablecount = _ret_errstat

class Table:
    '''Iterator for area, area2, material, nominal diameter etc. tables'''
    def __init__(self, table: str, typelt: ElemType = LINK):
        self.table = table
        self.nbitems = tablecount(table, typelt)
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, int]:
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, objcount, ln = _dll_api.nexttableentry()
        return tostr(item[0:ln]) if ln > 0 else "", objcount
    next = __next__

#****k* Iterators/TableValues
# SYNTAX
#   for item, objcount, vect in TableValues(table):
# ARGUMENTS
#   string table: requested table (2 char symbol or table name)
# RESULT
#   Returns each table entry and associated object count and values in turn:
#   * string item: table entry (possibly empty string for ZN)
#   * int objcount: link/node count associated with the entry
#   * float vect: vector of values for the entry.
#
#   The vector size depends on the table:
#   * (D) diameter (1): internal diameter
#   * (M) material (3): roughness, HW factor C, wave celerity
#   * (PA/PW) pipewall (7): WQ characteristics
#   * (FH/PI) hydrants (5): nominal flow, nominal pressure, height, diameter, friction coef K
#   * (CD) demand codes (2): coefficient and total demand
#   * (ZN) demand zones (2): coefficient and total demand
# REMARKS
#   * TableValues requires version 2022/07/20 or higher of Piccolo/Ganessa dll
#   * empty entry may be reported as "(DEFLT)" or "(DEFAUT)"
#   * Table("CD") does not return indicator of pressure dependant demand for demand codes; 
#     this indicator can be obtained with function: code_pressure(code).
# HISTORY
#   * Created 2022/07/20 (version 2.3.1).
#   * Modified 2023/03/27 (version 2.3.7): added demand codes and zones - requires version 2023 (230327) or higher of Piccolo/Ganessa_Sim dll
#****
try:
    tablevalcount: Callable[[str], Tuple[int, int]] = _dll_api.tablevalcount
except AttributeError:
    _fn_undefined.append('TableValues')
    _fn_undefined.append('table entries & values getter')
    tablevalcount = _ret_errstat2

class TableValues:
    '''Iterator for material, nominal diameter, hydrants etc. tables'''
    def __init__(self, table: str):
        self.table = table
        self.nbitems, value_sz = tablevalcount(table)
        self.value_size = value_sz
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, int, VectF]:
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, objcount, ln, values = _dll_api.nexttablevalentry(self.value_size)
        return tostr(item[0:ln]) if ln > 0 else "", objcount, values
    next = __next__

#****f* Functions_/areas
# PURPOSE
#   return areas associated with nodes/links
# SYNTAX
#   area = areas(typelt, attr)
# ARGUMENTS
#   * int typelt: type of object (NODE or LINK)
#   * str attr (optional): area attribute to be returned (ZN or ZP). Default to 'ZN'
# RESULT
#   * counter area: dictionary of node/link counts by area
# HISTORY
#   From version 1.9.0 (05/04/2018) area are returned as unicode strings.
#****
def areas(typelt: ElemType, sattr: str = '') -> Counter:
    '''Returns a counter for areas of given element type'''
    c_areas = Counter()
    if typelt not in (NODE, LINK):
        return c_areas
    if not sattr:
        sattr = attrkeyword(60)      # ZN
    for i in range(1, _dll_api.nbobjects(typelt) + 1):
        item, n = _dll_api.nstrattr(typelt, i, sattr)
        if n > 0:
            c_areas[tostr(item[0:n])] += 1
    return c_areas

#****f* Functions_/getid
# PURPOSE
#   Returns the id of an element by type and index
# SYNTAX
#   id = getid(typelt, numelt)
# ARGUMENTS
#   * int typelt: type of element
#   * int numelt: index of element
# RESULT
#   unicode string id: id of the element
# REMARKS
#   * Internal index starts with 1
#   * Internal index of an element may change after a simulation or
#     a modification of the model.
# HISTORY
#   From version 1.9.0 (05/04/2018) ids are returned as unicode strings.
#****
def getid(typelt: ElemType, numelt: int) -> str:
    '''Returns the ID of element of type and index'''
    eid, n = _dll_api.getid(typelt, numelt)
    return tostr(eid[0:n]) if n > 0 else ''

#****f* Functions_/getindex, exists_
# SYNTAX
#   * num = getindex(typelt, sid)
#   * bret = exists(typelt, sid)
# ARGUMENT
#   * int typelt: type of element
#   * string sid: ID of element
# RESULT
#   * int num: index of element ID (starting at pos 1)
#   * bool bret: indicates if the element exists in the model
# HISTORY
#   * getindex new in 1.3.3 but not working !
#   * getindex fixed in 1.9.4 (180604)
#   * exists created in 1.9.4 (180604)
#****
try:
    getindex: Callable[[ElemType, str], int] = _dll_api.geteltindex
except AttributeError:
    _fn_undefined.append('getindex')
    _fn_undefined.append('exists')
    getindex = _ret_errstat
    exists = _ret_errstat
else:
    def exists(typelt: ElemType, sid: str) -> bool:
        """Returns True if the element of given type exists in the model"""
        return _dll_api.geteltindex(typelt, sid) > 0

#****f* Functions_/extrnodes
# PURPOSE
#   Returns the from and to node (indexes) form link index
# SYNTAX
#   i_from, i_to = extrnodes(i_link)
# ARGUMENTS
#   * int i_link: index of the link
# RESULT
#   * int i_from: index of from node
#   * int i_to:   index of to node
# REMARKS
#   * Internal indexes start with 1
#   * Internal index of an element may change after a simulation
#     or a modification of the model.
#   * see linknodes to get from and to node IDs
#****
extrnodes: Callable[[int], Tuple[int, int]] = _dll_api.extrnodes

#****f* Functions_/linknodes
# PURPOSE
#   Return from and to nodes, in the direction of flow if given
# SYNTAX
#   * from, to = linknodes(id_or_num [, flow=0])
# ARGUMENTS
#   * str or int id_or_num: id or index of link element
#   * float flow: optional direction of flow to be considered
# RESULT
#   * str from: from (initial) node
#   * str to: to (final) node
# REMARK
#   * If flow is given and negative, topological from and to nodes are swapped.
#   * see extrnodes to get from and to node indexes from link index.
# HISTORY
#   2.4.7 (2025-01-07): creation
#****
def linknodes(link : Union[int, str], flow : float = 0) -> Tuple[str, str]:
    """Returns from and to nodes, in the direction of flow if flow is given"""
    if isinstance(link, numbers.Number):
        nn1, nn2 = extrnodes(link)
        n1, n2 = getid(NODE, nn1), getid(NODE, nn2)
    else:
        attr1, attr2 = attrkeyword(5), attrkeyword(6)
        n1, n2 = linkattrs(link, attr1), linkattrs(link, attr2)
    return (n2, n1) if flow < 0 else (n1, n2)

#****f* Functions_/linkXYZV, branchXYZV
# PURPOSE
#   Returns the XYZ polyline representing a link, and eventually
#   an additional node attribute
# SYNTAX
#   vec_x, vec_y, vec_z, vec_v, len = linkXYZV(id, [attr], [include_depth])
# ARGUMENTS
#   * string id: id of element
#   * string attr: optional attribute for which value is requested
#   * bool include_depth: optional attribute, defaults to False
# RESULT
#   * int len: number of points for the polyline
#   * double[] vec_x, vec_y: vector of coordinates
#   * float[] vec_z: vector of interpolated elevations (minus depth if include_depth= True)
#   * float[] vec_v: vector of interpolated attribute
# HISTORY
#   optional argument include_depth introduced in 1.4.2 (160908)
# REMARKS
#   * Z and V are interpolated from initial and final nodes
#   * if attribute is missing or not recognised vec_v is null.
#   * if the link has no vertice, len=2 and the function returns values
#     from ending nodes
#   * if the id does not exists the return value is (None, None, None, None, 0)
#   * branchXYZV is a synonym of linkXYZV.
#****
try:
    _linkxyzdv = _dll_api.branchxyzdv
except AttributeError:
    _linkxyzdv = _dll_api.branchxyzv
    _fn_undefined.append('linkXYZV(include_depth=True)')

def linkXYZV(sid: str, sattr: str = '--', include_depth: bool = False):
    """Returns the polyline X, Y, Z, V, len for link sid and attribute sattr"""
    nbval = _dll_api.branchxylen(sid)
    if nbval > 0:
        _func = _linkxyzdv if include_depth else _dll_api.branchxyzv
        return _func(sid, sattr, nbval)
    else:
        return (None, None, None, None, 0)
branchXYZV = linkXYZV

#****f* Functions_/linkbbox
# PURPOSE
#   Returns the link bounding box
# SYNTAX
#   xmin, xmax, ymin, ymax, num = linkbbox(id)
# ARGUMENTS
#   * string id: id of element
# RESULT
#   * int num: link internal number (0 if not found)
#   * double xmin, xmax, ymin, ymax: bounding box
# HISTORY
#   Created in 1.8.5 (171128)
#****
try:
    linkbbox = _dll_api.bbox
except AttributeError:
    def linkbbox(sid: str) -> Tuple[float, float, float, float, int]:
        '''Returns the link bounding box and index'''
        nbval = _dll_api.branchxylen(sid)
        if nbval > 0:
            x, y, _z, _v, np = _dll_api.branchxyzv(sid, '--', nbval)
            return np.amin(x), np. amax(x), np.amin(y), np. amax(y), np
        else:
            return (0., 0., 0., 0., 0)

#****f* Functions_/nodeXYZ
# PURPOSE
#   Returns the XYZ coordinates and depth of a node
# SYNTAX
#   x, y, z, dz = nodeXYZ(id)
# ARGUMENTS
#   * string id: id of element
# RESULT
#   * double x, y: coordinates
#   * float z, dz: elevation and depth
# REMARKS
#   * nodeXYZ requires version 2016 or higher of Piccolo/Ganessa dll
#   * if the id does not exists the return value is (None, None, None, None)
#   * In most cases dz is 0.0
#****
try:
    nodeXYZ: Callable[[str], Tuple[float, float, float, float]] = _dll_api.nodexyz
except AttributeError:
    _fn_undefined.append('nodeXYZ')
    nodeXYZ = lambda sid: (0.0, 0.0, 0.0, 0.0)

#****f* Functions_/dist2link
# PURPOSE
#   Returns the distance and curvilinear abcissae of a point from the given link
# SYNTAX
#   d, s1, s2 = dist2link(id, x, y)
# ARGUMENTS
#   * string id: id of link element
#   * double x, y: coordinates of the point
# RESULT
#   * double d: distance of the point to the link polyline
#   * double s1, s2: curvilinear distance of the projection from each extremity
# HISTORY
#   introduced in 1.3.7 (160706)
# REMARKS
#   * dist2link requires version 2016b or higher of Piccolo/Ganessa dll;
#     if not a pure python calculation is made using linkXYZV
#   * the polyline length is s1 + s2;
#     s1= 0 or s2= 0 when the point projection is outside the polyline
#   * if the id does not exists the return value is (-1, -1, -1)
#****
try:
    dist2link: Callable[[str, float, float], Tuple[float, float, float]] = _dll_api.distlink
except AttributeError:
    # _fn_undefined.append('dist2link')
    def dist2link(sid, x, y):
        xs, ys, _zs, _vs, nseg = linkXYZV(sid)
        if nseg:
            return dist_to_poly(x, y, nseg, xs, ys)
        else:
            return -1, -1, -1

#****f* Functions_/getvar, getunitname, getunitcoef
# PURPOSE
#   Returns the value of a Piccolo expression or variable
# SYNTAX
#   * str_val = getvar(expression)
#   * str_val = getunitname(attr)
#   * coef = getunitcoef(attr)
# ARGUMENTS
#   * string expression: the expression or user variable to be returned.
#     See the Piccolo Reference Manual (chap. 2.3) for the predefined variables and
#     allowed expressions.
#   * string attr: symbol associated to an attribute
# RESULT
#   * string str_val: a string containing the expected value. If the expression
#     or variable is not defined or implemented, the value '#NAN#' is returned.
#   * float coef: a float giving the unit coefficient / internal units
# REMARKS
#   * User variable and simple expressions (system variables) can be abbreviated; e.g.
#     getvar("WORK") and getvar("WORKDIR") will return the work folder.
#   * Older Piccolo/Ganessa_SIM may return "#NAN#"" for some predefined variables.
#   * Unit coefficient of a given attribute can also be returned with
#     the adequate getvar('unite.'+attr).
#   * The unit coefficient is the number of internal units per user units:
#     1 (user unit) = coef (internal unit).
#   Internal units are SI units excepted:
#   * diameter and roughness:  mm
#   * pressure: mwc
#   * concentrations: mg/l (or ppm)
#   * consumed mass (D1): g
# EXAMPLE
#    If the user flow unit is 'l/s', since internal flow unit is 'm3/s',
#    getunitcoef("Q") returns 0.001
# HISTORY
#   From version 1.9.0 (05/04/2018) info returned as unicode strings.
#****
def getvar(varname: str) -> str:
    '''Returns the str value of expression or variable varname'''
    sval, slen = _dll_api.getvar(varname)
    return tostr(sval[:slen])

def getunitname(sattr: str) -> str:
    '''Returns the unit name for attribute sattr'''
    sval, slen = _dll_api.getunit(sattr)
    return unistr(sval[:slen])

try:
    getunitcoef: Callable[[str], float] = _dll_api.getunitval
except AttributeError:
    def getunitcoef(sattr: str) -> float:
        '''Returns coef to internal unit for unit sattr'''
        sunit = modulekeyword(M.GEN.ROOT, M.GEN.UNIT)
        scoef = getvar(sunit + '.' + sattr)
        return float(scoef)

#****f* Functions_/getall
# PURPOSE
#   getall returns the value for all objects of the given type
# SYNTAX
#   vect = getall(typelt, attr)
# ARGUMENTS
#   * int typelt: type of element (LINK, NODE, TANK)
#   * string attr: attribute (result) for which value is requested
# RESULT
#   * float[] vect: vector of values
# REMARKS
#   getall(typelt, attr): when typelt =1 (links), attr can be either a regular attribute
#   ('Q', 'V', 'D', etc.) or a node-based attribute such as 'P:M' for mean pressure,
#   'P:G' for geometric mean, 'P:N' for min and 'p:X' for max.
#****
def getall(typelt: ElemType, sattr) -> Union[VectF, None]:
    ''' returns the value for all objects of the given type'''
    nbval = _dll_api.nbobjects(typelt)
    if nbval > 0:
        return _dll_api.getall(typelt, sattr, nbval)
    else:
        return None

#****f* Functions_/wqtracevectsize
# PURPOSE
#   wqtracevectsize returns the max count of water quality concentrations allowed,
#   including chlorine (C1).
# SYNTAX
#   n = wqtracevectsize()
# RESULT
#   * int n: max count
# REMARK
#   One may expect a return value of either 9 (C1 .. C9)
#   or 45 (C1 .. C9 + $0 .. $9 + $A .. $Z).
# HISTORY
#   introduced 2.0.0 (180820)
#****
try:
    wqtracevectsize: Callable[[], int] = _dll_api.wqcompmaxcount
except AttributeError:
    def wqtracevectsize():
        return 9

#****k* Iterators/Unstable
# PURPOSE
#   Provide access to the list of elements which status cannot be determined
#   thus causing a simulation not converge.
# SYNTAX
#   for item, typelt in Unstable():
# ARGUMENTS
#   none
# RESULT
#   Returns each unstable element in turn:
#   * string item: element ID
#   * int typelt: element type
# REMARK
#   * Unstable requires version 2016 (160118) or higher of Piccolo/Ganessa dll
# HISTORY
#   * new in 1.3.2
#   * From version 1.9.0 (05/04/2018) items are returned as unicode strings.
#****
try:
    unstablecount = _dll_api.unstablecount
except AttributeError:
    _fn_undefined.append('Unstable')
    _fn_undefined.append('unstable getter')
    unstablecount = _ret_errstat

class Unstable:
    '''Iterator ustable items during a simulation'''
    def __init__(self):
        self.nbitems = unstablecount()
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, ElemType]:
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, typelt, ln = _dll_api.nextunstableentry()
        return (tostr(item[0:ln]), typelt) if ln > 0 else ('', 0)
    next = __next__

#****f* Functions_/save_, savemodel
# SYNTAX
#   * istat = save(fname [, version])
#   * istat = savemodel(fname [, version] [, extra_data])
# ARGUMENTS
#   * string fname: file name to save to
#   * string version: optional version string "x.yz" for writing compatible file format,
#     for text file only.
#   * list extra_data: list of (selection, attribute_keyword) to be saved.
#     Selection is a string describing a valid selection at save time; attribute_keyword
#     is a string name of a valid attribute for import, such as XX, YY, ZZ, K (links), Z (nodes).
#     Multiple attributes can be provided separated by blanks.
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   * 'save' uses the same procedure as Piccolo MMI.
#   * 'savemodel' is pure python and produces the same hydraulic content;
#     exotic options and cost data are not saved.
#   * If filename ends with '.bin' then data is saved as binary. Otherwise data is
#     saved as text (.dat mode) file.
#   * If the useException mode is set, any error will raise GanessaError exception.
# EXAMPLE
#   savemodel('myModel.dat', version='3.95', extra_data=[('NOEUD', 'YY ZZ')])
# HISTORY
#   * 190617: added extra_data keyword parameter to savemodel (2.0.7)
#****
def _save_kw_command():
    # SAVE TEXT COMM
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.TEXT)
    _dll_api.gencmd(M.COM.ROOT, M.NONE, extmode=1)

def save(fname: str, version: str = '') -> int:
    '''Save model the same way as Piccolo 'File > save' '''
    return _dll_api.savefile(winstr(fname), version)

def savemodel(fname: str, version: str = None,
              extra_data: Sequence[Tuple[str, str]] = None) -> int:
    '''Save model, possibily adding extra data to import when opening'''
    # First close opened file if any
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.CLOSE)

    fwq = winstr(quotefilename(fname))
    if fname.lower().strip('"\'').endswith('.bin'):
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.OPEN, DICT.BINARY, fwq)
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.DATA)
        if extra_data is not None:
            print('Additional data not supported for .bin files')
    else:
        if version:
            _dll_api.gencmd(M.GEN.ROOT, M.GEN.COMPAT, M.NONE, version)
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.OPEN, DICT.DATA, fwq)
        for module in ('NOD', 'BRA', 'RSV', 'DYN', 'LAB', 'MES', 'SIM'):
            _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
            _dll_api.gencmd(getattr(M.ROOT, module), M.NONE, extmode=1)
        # singularities and wording
        _save_kw_command()
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _dll_api.gencmd(-M.BRA.ROOT, M.BRA.SING, extmode=1)
        _save_kw_command()
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.WORDING, extmode=1)
        _save_kw_command()
        # Quality at the end, in case option not available
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _dll_api.gencmd(M.QUA.ROOT, M.NONE, extmode=1)
        if extra_data is not None:
            _save_kw_command()
            # SAVE TEXT IMPORT attr <type_elem> "@<"
            # SAVE EXPORT <selection> ID attr   /* ID <value>
            # SAVE TEXT  "@<"
            for sel, attr in extra_data:
                nb, seltype = selectlen(winstr(sel))
                if nb == 0:
                    continue
                aid = attrkeyword(24 if seltype == LINK else 23)
                _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.TEXT)
                _dll_api.gencmd(M.GEN.ROOT, M.GEN.IMPORT, M.NONE, attr, extmode=1)
                _dll_api.gencmd(-M.COM.ROOT, seltype+1, M.NONE, '"@<"', extmode=1)
                _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
                _dll_api.gencmd(M.GEN.ROOT, M.GEN.EXPORT, M.NONE, winstr(sel), extmode=1)
                _dll_api.gencmd(M.GEN.ROOT, M.GEN.FORMAT, M.NONE, aid + ' ' + attr, extmode=1)
                _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.TEXT, '"@<"')
        # _dll_api.gencmd(M.GEN.ROOT, M.GEN.EOF, extmode= 1)
    # Close and commit
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.CLOSE)
    istat = _dll_api.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(9, istat, 'Error while saving model')
    return istat

#****f* Functions_/importEpanet, exportEpanet
# SYNTAX
#   * istat = importEpanet(fname)
#   * istat = exportEpanet(fname)
# ARGUMENTS
#   string fname: file name to import from / export to (should be an .inp)
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   At import, .inp file is first converted to a .inp_cvt.dat Piccolo file,
#   then this file is read. Syntax error if any will refer to the converted .dat file.
#****

def importEpanet(fname: str) -> int:
    '''Imports an .inp Epanet file'''
    reset()
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.EPA2PIC, scmd=winstr(quotefilename(fname)))
    istat = _dll_api.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(10, istat, 'Error while importing Epanet file')
    return istat

def exportEpanet(fname: str) -> int:
    '''Exports the current model as an .inp Epanet file'''
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.PIC2EPA, scmd=winstr(quotefilename(fname)))
    istat = _dll_api.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(10, istat, 'Error while exporting Epanet file')
    return istat

def get_labels():
    '''Compatibility with epanet emulator'''
    return []
#****f* Functions_/addSHLtype, addSHL, updateSHL, delSHL
# PURPOSE
#   * addSHLtype: Add / modify a single head losses (SHL) from the SHL table
#   * addSHL, updateSHL, delSHL: Add / modify / delete single head losses (SHL)
#     objects for a given pipe
# SYNTAX
#   * istat = addSHLtype(shltype, values [, comment])
#   * istat = addSHL(id, shltype, nb)
#   * istat = updateSHL(id, shltype, nb)
#   * istat = delSHL(id [, shltype])
# ARGUMENTS
#   * string shltype: type of shl to be added/modified
#   * float values: direct and reverse SHL coefficients
#   * string comment: long name of the SHL type
#   * string id: id of pipe
#   * int nb: number of SHL of type shltype to be added / updated with
# RESULT
#   int istat: error status (0 if OK)
# COMMENTS
#   If shltype is not given or is '' for delSHL then all SHL are removed from pipe.
# REMARK
#   * these functions require version 2015/12 or higher of Piccolo/Ganessa dll
#****
try:
    def addSHLtype(shltype, values, comment=' '):
        _dll_api.addshlentry(shltype, values, comment)
    addSHL = _dll_api.addsingleshl
    updateSHL = _dll_api.updatesingleshl
    def delSHL(sid, shlid=''):
        _dll_api.removeshl(sid, shlid)
except AttributeError:
    _fn_undefined.append('SHL getter and setter')
    addSHLtype = _ret_errstat
    updateSHL = _ret_errstat
    delSHL = _ret_errstat

#****f* Functions_/setlinkattr, setbranchattr, setnodeattr
# SYNTAX
#   * istat = setlinkattr(id, attr, val)
#   * istat = setnodeattr(id, attr, val)
#   * istat = setbranchattr(id, attr, val)
# ARGUMENTS
#   * string id: id of element
#   * string attr: attribute (data or result) to be set to val
#   * float val: new value for attr
# RESULT
#   int istat: error status:
#   * 0 if OK
#   * 1 if the attribute is not defined for the type of link/node
#   * -1 if the attribute is not recognised
#   * -2 if the link/node does not exist
# REMARKS
#   * setbranchattr requires version 2015/12 or higher of Piccolo/Ganessa dll
# HISTORY
#   * setlinkattr is a synonym that has been introduced as 22/09/2016
#   * setnodeattr has been introduced on 22/06/2020 (2.1.3)
#****
try:
    setbranchattr: Callable[[str, str, float], int] = _dll_api.setbranchattrbyid
except AttributeError:
    _fn_undefined.append('setbranchattr')
    setbranchattr = _ret_errstat
setlinkattr = setbranchattr
try:
    setnodeattr: Callable[[str, str, float], int] = _dll_api.setnodeattrbyid
except AttributeError:
    _fn_undefined.append('setnodeattr')
    setnodeattr = _ret_errstat

#****o* Classes/Graph_, extrnodes, adjlinks, adjnodes, propagate, dtree, wtree, antennas, segment_other_end, path
# PURPOSE
#   Builds a simple graph from the current model topology.
# SYNTAX
#   graph = Graph([orientation])
# METHODS
#   * from_n, to_n = graph.extrnodes(alink): returns the from and to nodes of alink
#   * linkset = graph.adjlinks(anode): returns links adjacent to anode as a set
#   * nodeset = graph.adjnodes(anode): returns nodes adjacent to anode as a set
#   * plist = graph.oriented_links(anode): returns a list of (link, index) tuples
#   * pairs = graph.adj_links_nodes(node): return a set of (link, nodes) tuples
#   * link, from_n, to_n = graph.poplink(): remove a link and returns it with from and to nodes
#   * slinks, snodes = graph.propagate(anode [, maxlen= -1]):
#     returns the sets of links and nodes connected to 'anode' by a path of max link count 'maxlen'
#   * tree, slinks = graph.dtree(anode [, maxlen= -1]): returns a tree as an ordered dict,
#     of minimum link count.
#   * tree = graph.wtree(anode [, weight="L"]): returns a tree as an ordered dict,
#     of minimum weight (weight for a link is linkattr(alink, weight)).
#   * linkset, nodeset = graph.downstream(anode [, update='Q'] [, maxlen=-1]):
#     returns downstream elements with respect to 'update' attribute direction (default Q)
#   * linkset, nodeset = graph.upstream(anode [, update='Q'] [, maxlen=-1]):
#     returns upstream elements with respect to 'update' attribute direction (default Q)
#   * linkset = graph.extended_segment(alink [, addl_boundary_nodes=None]):
#     returns the set of links on the same segment as alink
#   * blink, bnode, count = segment_other_end(alink, anode):
#     returns the other end and link count of segment starting at node anode with link alink
#   * plist [, unlooped] = graph.antennas([keep_nodes=None][, strict=True]):
#     returns a list of (link, nodes) tuples of element in antennas. kept_nodes allow to mark
#     a sequence of nodes to be considered not belonging to antenna.
#     If strict=False, allow 2 or more parallel segments to be handled as a single segment;
#     the list of links removed for unlooping is also returned.
#   * nlist, klist, wlist = graph.path(from_n, to_n [, weight=""]):
#     returns a minimal path between 'from_n' and 'to_n' nodes. Minimal means cumulated weight when
#     weight is present, link count otherwise.
# ARGUMENTS
#   * str orientation: the attribute sign will be used for orienting the graph.
#     (default None, orientation from -> to)
#   * str alink, anode, node: link, node ID
#   * int maxlen: compute graph propagation up to maxlen steps (<0 if not limited)
#   * str weight: attribute to be used as weight
#   * str update: attribute to be used as link direction (defaut 'Q'; use '' or None to
#     disable direction update)
#   * sequence addl_boundary_nodes: sequence of nodes to consider as additional segment boundaries
# RESULT
#   The graph is built from the current model links and nodes:
#   * set linkset: set of adjacent links ID
#   * set nodeset: set of adjacent nodes ID
#   * plist: list of tuples (ID alink, int idx) where idx is the index
#     of the other node in graph.edges[alink] (graph.edges[alink][1-idx] == anode).
#   * sets slinks, snodes: sets of links and nodes ID.
#   * OrderedDict tree: ordered dict where key are node IDs, values are a link ID
#     and a depth integer value (dtree) or cumulated weight (wtree).
#     The link allows to connect the node at minimum weight.
#   * list nlist: list of nodes forming the path (nlist[0] is from_n, nlist[-1] is to_n)
#   * list klist: list of links connecting node to the next (klist[-1] is "")
#   * list wlist: list of decreasing cumulated weights to 'to_n' (wlist[-1] is 0).
#     [wlist[0] - x for x in wlist] is the increasing cumulated weights from 'from_n'.
# REMARK
#   * first key, value returned by dtree/wtree is the root node, and ("", 0)
#   * dtree may be incorrect up to 2.5.0.
# HISTORY
#   * new in 1.3.7 (160706)
#   * 1.7.6 (170620): use attrkeyword() for IN and FN
#   * 1.8.2 (171103): added graph.dtree
#   * 1.8.5 (171128): updated dtree, added graph.adjnodes
#   * 2.0.8 (200106): added revert, upstream, downstream
#                     discard degenerated links (same from and to node)
#                     changed internal representation
#   * 2.1.8 (210325): added pop and __len__
#   * 2.3.4 (221010): added extended_segment
#           (221110): added antennas
#   * 2.4.8 (250210): added segment_other_end; keyword antennas(strict)
#   * 2.5.1 (250305): added path and wtree; fix HeapSort use for dtree
#   * 2.5.3 (250424): graph inherit from (link) dict; remove self._edges;
#                     replace pop with pop_link
#****
class Graph(dict):
    '''Dual node/link representation for in depth propagation'''
    def __init__(self, orientation: Literal['Q', 'V'] = None):
        KWNI = attrkeyword(5)   # initial node
        KWNF = attrkeyword(6)   # final node
        # self._nodes = {n:set() for n in Nodes()}
        self._nodes = defaultdict(set)
        # self._edges = {}
        self._reverted_links = set()
        self._orientation = orientation
        if orientation is not None and is_text(orientation):
            swap = lambda a: linkattr(a, orientation) < 0
        else:
            swap = lambda a: False
        for a in Links():
            fm_node, to_node = linkattrs(a, KWNI), linkattrs(a, KWNF)
            if fm_node != to_node:
                if swap(a):
                    fm_node, to_node = to_node, fm_node
                    self._reverted_links.add(a)
                self[a] = (fm_node, to_node)
                # self._addtonodes(a, fm_node, to_node)
        self.optional_arg_dependant_results = None

    # def __len__(self) -> int:
    #     '''Length of the graph = edge count'''
    #     return len(self)
    
    # def __contains__(self, alink: str) -> bool:
    #     """link in or not in"""
    #     return alink in self

    def extrnodes(self, alink: str) -> Tuple[str, str]:
        '''Returns from and to nodes as a tuple'''
        return self[alink]

    def adjlinks(self, anode: str) -> Set[str]:
        '''Returns adjacent links as a set'''
        return {a for a, _ in self._nodes[anode]}

    def adjnodes(self, anode: str) -> Set[str]:
        '''Returns the other nodes of the links connected to anode as a set'''
        return {n for _, n in self._nodes[anode]}

    def oriented_links(self, anode: str) -> List[Tuple[str, Literal[0, 1]]]:
        '''Returns the links and the indice for the other node as a list of tuples'''
        return [(a, 1 if anode == self[a][0] else 0)
                        for a, _ in self._nodes[anode]]

    def adj_links_nodes(self, anode: str) -> List[Tuple[str, str]]:
        '''Returns the links and the other node as a list of tuples'''
        return self._nodes[anode].copy()

    def _addtonodes(self, a, n1, n2):
        self._nodes[n1].add((a, n2))
        self._nodes[n2].add((a, n1))

    def _addtonodes_old(self, a, n1, n2):
        self._addtonode_old(n1, a, n2)
        self._addtonode_old(n2, a, n1)

    def _addtonode_old(self, n1, a, n2):
        try:
            self._nodes[n1].add((a, n2))
        except KeyError:
            self._nodes[n1] = {(a, n2)}

    def add(self, link: str, nodes: Tuple[str, str]) -> None:
        '''Add a link between nodes'''
        if is_text(link) and isinstance(nodes, tuple):
            fm_node, to_node = nodes
            if fm_node != to_node:
                retval = super().__setitem__(link, nodes)
                self._addtonodes(link, fm_node, to_node)
                return retval

    def __setitem__(self, key, value):
        """setter for link: self[link] = nod1, node2"""
        return self.add(key, value)

    def remove(self, link: str) -> None:
        '''Removes the link from the graph'''
        fm_node, to_node = self.pop(link)
        self._remove_link_deps(link, fm_node, to_node)

    def __delitem__(self, key):
        """remove link using del self[link]"""
        return self.remove(key)

    def pop_link(self) -> Tuple[str, str, str]:
        '''Removes a link and returns it with fm_node and to_node'''
        try:
            link, (fm_node, to_node) = self.popitem()
        except KeyError:
            return None, None, None
        self._remove_link_deps(link, fm_node, to_node)
        return link, fm_node, to_node

    def _remove_link_deps(self, link, fm_node, to_node):
        """Complete link removal on dependancies"""
        # use discard for error tolerance
        self._nodes[fm_node].remove((link, to_node))
        self._nodes[to_node].remove((link, fm_node))
        # del self[link]
        self._reverted_links.discard(link)

    def revert(self, link: str) -> None:
        '''Reverts the link: exchange from and to nodes'''
        from_node, to_node = self[link]
        # self[link] = (to_node, from_node)
        super().__setitem__(link, (to_node, from_node))

    def propagate(self, rootnode: str, maxlen: int = -1) -> Tuple[Set[str], Set[str]]:
        '''Finds links / nodes connected to the root up to the given depth'''
        edges = set()
        nodes = {rootnode}
        border_nodes = {rootnode}
        while maxlen and border_nodes:
            maxlen -= 1
            border_edges = set()
            for n in border_nodes:
                border_edges.update(self.adjlinks(n))
            edges.update(border_edges)
            border_nodes = {n for a in border_edges for n in self[a]
                                                    if n not in border_nodes}
            nodes.update(border_nodes)
        return edges, nodes

    def dtree(self, rootnode: str, maxlen: int = -1) -> Tuple[Dict[str, Tuple[str, float]], Set[str]]:
        '''Build a tree from rootnode as an OrderedDict'''
        border_nodes = HeapSortRank(index_key=itemgetter(0))
        border_nodes.push((rootnode, ""), 0)
        nodes = OrderedDict()
        edges = set()
        while len(border_nodes):
            (n, an), cumlen = border_nodes.pop()
            nodes[n] = an, cumlen
            if cumlen == maxlen:
                continue
            for a, nk in self.adj_links_nodes(n):
                edges.add(a)
                if nk not in nodes:
                    border_nodes.update_if_lower((nk, a), cumlen + 1)
        return nodes, edges

    def wtree(self, rootnode: str, weight: str = "L") -> Tuple[Dict[str, Tuple[str, float]]]:
        '''Build a minimum weigth tree from rootnode as an OrderedDict
        weight is the value of "weight" attribute, defaults to "L"'''
        border_nodes = HeapSortRank(index_key=itemgetter(0))
        border_nodes.push((rootnode, ""), 0)
        nodes = OrderedDict()
        # edges = set()
        while len(border_nodes):
            (n, an), cumlen = border_nodes.pop()
            nodes[n] = an, cumlen
            for a, nk in self.adj_links_nodes(n):
                # edges.add(a)
                if nk not in nodes:
                    w = linkattr(a, weight)
                    border_nodes.update_if_lower((nk, a), cumlen + w)
        return nodes

    def path(self, node1: str, node2: str, weight: str = "") -> Tuple[List[str], List[float], List[str]]:
        """Find path between node1 and node2 using dtree (minimal count) or wtree (minimal weight)
        returns a list of successive nodes from node1 to node2, the list of cumulated weights,
        and the list of links connecting each node with the next (last is "")."""
        tree = self.wtree(node2, weight) if weight else self.dtree(node2)[0]
        path_nodes, path_links, path_weights = [], [], []
        nn = node1
        while True:
            link, w = tree[nn]
            path_nodes.append(nn)
            path_links.append(link)
            path_weights.append(w)
            if not link:
                break
            # replace with other node
            n1, n2 = self.extrnodes(link)
            nn = n2 if nn == n1 else n1
        return path_nodes, path_links, path_weights

    def downstream(self, rootnode, update='Q', maxlen=-1):
        '''Returns sets of downstream nodes and links'''
        return self.oriented_propagation(rootnode, 1, update, maxlen)

    def upstream(self, rootnode, update='Q', maxlen=-1):
        '''Returns sets of upstream nodes and links'''
        return self.oriented_propagation(rootnode, 0, update, maxlen)

    def oriented_propagation(self, rootnode: str,
                direction: Literal[0, 1],
                update: Literal['Q', 'V', ''],
                maxlen: int) -> Tuple[Set[str], Set[str]]:
        '''Oriented propagation - returns sets of nodes and links
            rootnode: starting node
            direction: 1 for downstream, 0 for upstream
            update: Attribute giving link orientation (or '' or False)
            maxlen: propagate up to maxlen deepness'''
        # _reverted_links tracks revert operation for successive calls
        if update:
            upd_attr = update if is_text(update) else 'Q'
            for k in Links():
                if linkattr(k, upd_attr) < 0:
                    if k not in self._reverted_links:
                        self.revert(k)
                        self._reverted_links.add(k)
                elif k in self._reverted_links:
                    self.revert(k)
                    self._reverted_links.remove(k)
            self._orientation = upd_attr

        edges = set()
        nodes = {rootnode}
        border_nodes = {rootnode}
        while maxlen and border_nodes:
            maxlen -= 1
            border_edges = {k for b in border_nodes for k, s in self.oriented_links(b)
                                                    if s == direction}
            edges.update(border_edges)
            border_nodes = {self[a][direction] for a in border_edges} - nodes
            nodes.update(border_nodes)
        return edges, nodes

    def extended_segment(self, alink: str, addl_boundary_nodes: Sequence[str] = None) -> Set[str]:
        """Returns a set of links connected to the given link by simple nodes
        addl_boundary_nodes is an optional set of boundary nodes to stop search"""
        segment = {alink}
        border_nodes = set(self.extrnodes(alink))
        boundary_nodes = set() if addl_boundary_nodes is None else set(addl_boundary_nodes)
        while border_nodes:
            node = border_nodes.pop()
            if node in boundary_nodes:
                continue
            adj_links_nodes = self.adj_links_nodes(node)
            if len(adj_links_nodes) == 2:
                for a, n in adj_links_nodes:
                    if a not in segment:
                        segment.add(a)
                        border_nodes.add(n)
                        break
        return segment

    def segment_other_end(self, anode: str, alink: str) -> Tuple[str, str, int]:
        """Returns the other ending (link, node, count) of segment starting with
        'anode' end of 'alink' (count is the link count)"""
        nodes = self.extrnodes(alink)
        if anode not in nodes:
            raise ValueError
        other_node = nodes[1] if anode == nodes[0] else nodes[0]
        count = 1
        while True:
            if len(adj := self.adj_links_nodes(other_node)) != 2:
                return alink, other_node, count
            adj.remove((alink, anode))
            anode = other_node
            alink, other_node = adj.pop()
            count += 1

    def antennas(self, keep_nodes: Sequence[str] = None, strict: bool = True) -> List[Tuple[str, str]]:
        """Returns a list of (link, node) in antennas - graph not modified.
        If strict=False, the list of links whose removal allows unlooping of parallel paths
        is available from extra_result as well"""
        kept = set(keep_nodes) if keep_nodes else set()
        # Add 2 fictive adjacent links to kept_nodes for marking as non antenna
        adjacents =  HeapSortRank()
        results, removed_links, hit_nodes, unloops = [], set(), set(), []
        for n, adj in self._nodes.items():
            adj_count = len(adj)
            if adj_count:
                rank = (adj_count + (2 if n in kept else 0))
                adjacents.push(n, rank)
        # iterate over current ending nodes (connected links == 1)
        while adjacents:
            node, rank = adjacents.pop()
            if not rank:
                # isolated node
                continue
            if rank > 1:
                hit_nodes -= kept
                if strict or not hit_nodes:
                    # all true antenna have been processed
                    break
                # last chance with hit nodes
                adjacents.push(node, rank)
                for hnode in hit_nodes:
                    target = set()
                    for alink, anode in self.adj_links_nodes(hnode):
                        if alink in removed_links:
                            continue
                        xlink, xnode = alink, anode
                        _blink, bnode, _count = self.segment_other_end(hnode, alink)
                        target.add(bnode)
                    if len(target) == 1 and bnode != hnode:
                        # discard xlink to break the loop, leaving hnode and xnode terminal
                        removed_links.add(xlink)
                        unloops.append(xlink)
                        adjacents.modify(hnode, -1)
                        adjacents.modify(xnode, -1)
                hit_nodes.clear()
                continue
            hit_nodes.discard(node)
            for link, other_node in self.adj_links_nodes(node):
                if link in removed_links:
                    continue
                removed_links.add(link)
                hit_nodes.add(other_node)
                results.append((link, other_node))
                adjacents.modify(other_node, -1)
        if not strict:
            self.optional_arg_dependant_results = unloops
        return results

### Print functions not available due to obsolete version of dll ###

if _fn_undefined:
    print('Warning: the following functions and iterators are not compatible with this version of', _dll_name, ':')
    nuf, duf = len(_fn_undefined), 5
    for k in range(0, nuf, duf):
        print('   ', ', '.join(_fn_undefined[k:min(k+duf, nuf)]))
    del nuf, duf

#**#**f* Functions_/getcluster
# PURPOSE
#   Computes and returns the index of the nearest node in the selection,
#   as cumulated path relative to the given attribute.
# SYNTAX
#   vec_idx = getcluster(sname [, attr] [, copybuf])
# ARGUMENTS
#   * string sname: name of selection
#   * string attr (optional): attribute used for weighing links (expected L, XX, YY, ZZ, RH/HD).
#     Defaults to RH/HD
#   * string copybuf (optional): the result is also copied on node attribute copybuf.
#     Valid arguments are '', 'XX', 'YY' or 'ZZ'.
# RESULT
#   int vec_idx[]: vector of the nearest root node. 0 means that the node is not
#   connected to the root selection.
# HISTORY
#   introduced and aborted in 1.3.3
# REMARK
#   if sname is a link or tank selection, it is converted to a node selection.
#****
#try:
#    _tmp = _dll_api.getcluster
#except AttributeError:
#    print('getcluster function not defined in this version of', _dll_name)
#    getcluster = _ret_errstat
#else:
#    def getcluster(sname, attr= ' ', copybuf= ' '):
#        return _dll_api.getcluster(sname, attr, copybuf.upper(), _dll_api.nbobjects(NODE))
