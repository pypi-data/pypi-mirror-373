"""

 Epanet compatibility functions with ganessa.sim and other useful methods
    by Dr. Pierre Antoine Jarrige

  1.00 - 2020.06.19 creation
  2.00 - 2023.09.28 extension with (owa-)epanet22: _emu_object = ENmodel() use default project
  2.01 - 2023.10.17 further extensions
  2.02 - 2023.10.25 WQ extension + simulation function renamed (lias kept)
         2023.10.30 add getallminmax raw_stat_duration
  2.03 - 2024.01.12 catch non-ascii .inp file name issue; fix reset calling et.close twice
         2024-01-15 keep comments after section header in ENmodel.save_as
  2.04 - 2025-04-03 add resfile and is_embedded (required when ganessa_sim absent)
"""

__version__ = "2.04"

from typing import Tuple, Union, List, Literal
import os.path as OP
from collections import defaultdict
import atexit
from numbers import Number
import re
from math import pi
import numpy as np
from ganessa import __version__ as _version
from ganessa.util import ws, tostr, hhmmss, strf3, X64, myascii

ElemType = Literal[0, 1, 2, 3]
VectF = List[float]
MatrF = List[VectF]

#****g* ganessa.epanet2/About
# PURPOSE
#   The module ganessa.epanet2 provides epanettools API for epanet 2.00.12.
#   It is a copy of epanettools 0.4.3, with minor fixes.
#****
#****g* ganessa.epanet22/About
# PURPOSE
#   The module ganessa.epanet22 provides epanettools API for epanet 2.2,
#   similar to Epanet 2.0 (legacy API to a single project).
#****
#****g* ganessa.owa_epanet22/About
# PURPOSE
#   The module ganessa.owa_epanet22 provides epanettools compatibility for owa-epanet
#   package, in the sense it hides the Epanet 2.2 project argument by using a
#   default single project, but allow to close / create that project for multiprocessing.
# HISTORY
#   * 2020-09-21: creation
#****
#****g* ganessa.en2emu/About
# PURPOSE
#   The module ganessa.en2emu provides compatibility for a limited set of functions
#   used by Ganessa tools, such as OpenFileMMI.SelectModel. It makes use of owa_epanet22
#   if owa-epanet is installed, otherwise it uses epanet22 legacy, limited API.
#
#   It creates a hidden _emu_object ENmodel object for the current model, caching pipes,
#   tanks, hydaulic EPS results, pressure and flow unit and coefficients etc.
# HISTORY
#   * 2020-06-19: creation / interface with epanettools (epanet 2.0)
#   * 2023-10-17: extension with owa-epanet (epanet 2.2) and epanet22
#   * 2023-10-25: extension with runWQ and changes in epanet project handling
#   * 2023-10-30: add getpipedata, getallminmax, raw_stat_duration
#   * 2024-01-15: minor improvement in ENmodel.save_as: keep comments after section header
#****

def ENretval_skip_retcode(args):
    """remove return errcode for epanet2 and epanet22"""
    return args if isinstance(args, (str, bytes)) else (args[1] if len(args) == 2  else args[1:])

def ENretval_as_is(args):
    """keep as is - owa-epanet"""
    return args

# folder is almost useless
# _emu_object is the current model and is used by flat functions
# It is set with the instance created when calling ENmodel
_emu_folder = None
_emu_object = None
_fresult = ''
_debug = False
is_owa_epanet = False

try:
    from ganessa import owa_epanet22
    owa_epanet_present = True
except ImportError:
    print("owa-epanet not found: using ganessa.epanet implementation")
    owa_epanet_present = False
from ganessa import epanet22
from ganessa import epanet2

et = None
_ENversion = ""
epanet_version = ""
epanet_source = ""
ENretval = ENretval_as_is
_verbose = False

def implementation_selector(mode : str, verbose : bool = True) -> str:
    """Allows to redefine the epanet package to be used ("owa_epanet", "epanet22", "epanet2").
    Verbose arg is meaninful for owa_epanet only.
    CAUTION: change the package before any other calls, or after close, otherwise no effect"""
    global et, ENretval, is_owa_epanet, _ENversion, epanet_version, epanet_source, _verbose
    if _emu_object is not None:
        return
    _verbose = verbose
    if owa_epanet_present and "owa" in mode.lower():
        is_owa_epanet = True
        ENretval = ENretval_as_is
        et = owa_epanet22
        epanet_source = "owa-epanet " + et.__version__
        et.verbose = verbose
    else:
        is_owa_epanet = False
        ENretval = ENretval_skip_retcode
        if "22" in mode:
            et = epanet22
        else:
            et = epanet2
        epanet_source = "ganessa custom epanettools"
    _ENversion = ENretval(et.ENgetversion())
    epanet_version = f"{_ENversion//10000}.{(_ENversion % 10000) // 100}"
    return f"\tEpanet version is: {epanet_version} (from {epanet_source})"

# This instruction sets the owa-epanet engine as default if present, othewise epanet22
ret = implementation_selector("owa_epanet" if owa_epanet_present else "epanet22")
if _verbose:
    print(ret)

LINK = BRANCH = ARC = 1
NODE = NOEUD = 2
TANK = RESERVOIR = RSV = 3

PIC2EPA_LINK_ATTRS = {"Q": et.EN_FLOW,
                      "V": et.EN_VELOCITY,
                      "L": et.EN_LENGTH,
                      "D": et.EN_DIAMETER,
                      "R": et.EN_ROUGHNESS,
                      "C": et.EN_ROUGHNESS,
                      "K": et.EN_MINORLOSS,
                      "PC": et.EN_HEADLOSS,
                      "HL": et.EN_HEADLOSS,
                      }
PIC2EPA_NODE_ATTRS = {"P": et.EN_PRESSURE,
                      "CH": et.EN_HEAD,
                      "HH": et.EN_HEAD,
                      "CS": et.EN_BASEDEMAND,
                      "CC": et.EN_DEMAND,
                      "Z": et.EN_ELEVATION,
                      "C1": et.EN_QUALITY,
                      }

class Setter_v3:
    """setter for UI field"""
    def __init__(self, hnd) -> None:
        self.hnd = hnd
    def set(self, text):
        """set .v3 label"""
        try:
            self.hnd.v3.set(text)
            self.hnd.update()
        except AttributeError:
            pass

class ENmodel:
    """Functions to be called while epanet is active i.e. between init and close
    init calls open that call et.ENopen that creates owa-epanet project if needed
    close deletes it"""
    FILE_ENCODING = "utf-8"
    MEM_X32 = 500
    MEM_X64 = 2000
    def __init__(self, fname : str, hnd, debug=False):
        global _emu_object
        self.err = []
        self.hnd = Setter_v3(hnd) if hnd and hasattr(hnd, "v3") else hnd
        self.debug = debug
        self.filename = fname
        self.tank_index = []
        self.pipe_index = []
        self.errcode = 0
        self.coords = {}
        self.vertices = {}
        self.labels = []
        self.backdrop = []
        self.vertices = defaultdict(list)
        self.hyd_step = 0
        self.duration = 0
        self.hydraulic_results = None
        self.hyd_sim_for_wq = False
        self.extra_text = []
        warntxt = "" if fname == myascii(fname) else  "non-ascii .inp file name"
        if warntxt:
            if _verbose:
                print(" * Warning:", warntxt, "*")
            if self.hnd:
                self.hnd.set(warntxt)
        _emu_object = self
        try:
            self.open(fname)
        except Exception as exc:
            self.errcode = 1
            self.err.append(str(exc))
            # do not keep model name to avoid reset() reopens it
            self.filename = ""
            raise Exception(str(exc) + f" ({warntxt})") from exc
        # self.get_coords()
        # stores the instance in _emu_object global, for flat functions

    def open(self, fname: str):
        """Opens Epanet model - clears errcode"""
        self.errcode = 0
        self.err = []
        base, _ext = OP.splitext(fname)
        self.inp = ws(base + '.inp')
        self.rpt = ws(base + '.rpt')
        self.ENerr(et.ENopen(self.inp, self.rpt, ws("")), True)
        self.update_indexes()
        if not self.errcode:
            self.hyd_step = self.ENerr(et.ENgettimeparam(et.EN_HYDSTEP))
        if not self.errcode:
            self.duration = self.ENerr(et.ENgettimeparam(et.EN_DURATION))

    def update_indexes(self):
        """Update tank_index and pipe_index"""
        if not self.errcode:
            self.tank_index = [ix for ix in range(1, self.nodecount+1)
                               if ENretval(et.ENgetnodetype(ix)) == et.EN_TANK]
            self.pipe_index = [ix for ix in range(1, self.linkcount+1)
                               if ENretval(et.ENgetlinktype(ix)) == et.EN_PIPE]

    def close(self):
        ''''Terminate'''
        global _emu_object
        self.tank_index = []
        self.pipe_index = []
        self.hydraulic_results = None
        self.hyd_sim_for_wq = False
        et.ENclose()
        self.errcode = -1
        if self == _emu_object:
            _emu_object = None
        if is_owa_epanet:
            return et.ENdeleteproject()
        else:
            return 0

    def reopen(self):
        """reloads the model"""
        global _emu_object
        et.ENclose()
        self.open(self.filename)
        if _emu_object is None:
            _emu_object = self

    def save(self, fname : str, append : List[str] = None) -> bool:
        """Save Epanet model; optionnally appends a section before [END]"""
        et.ENsaveinpfile(ws(fname))
        if append is None or not append:
            return True
        # insert "append" before "[END]"
        with open(fname, "r", encoding=self.FILE_ENCODING) as ef:
            content = ef.readlines()
        for k, line in enumerate(content[::-1]):
            if re.search("[END]", line, re.IGNORECASE):
                break
        else:
            return False
        pos = -1 - k
        content[pos:pos] = [line + "\n" for line in append]
        with open(fname, "w", encoding=self.FILE_ENCODING) as ef:
            ef.writelines(content)
        return True

    def save_as(self, fname):
        '''Copy the file with current coords / vertices / labels (Epanet2)'''
        # with tempfile.NamedTemporaryFile(delete=False, suffix='.inp') as f:
        #     pass
        # self.save(f.name)
        sections = ('[COORD', '[VERTI', '[LABEL', '[BACKD')
        fcopy, new_section = True, ""
        kw = dict(encoding=self.FILE_ENCODING)
        with open(self.filename, "r", **kw) as enfile, open(fname, "w", **kw) as fout:
            for text in self.extra_text:
                fout.write('; ' + text + '\n')
            for unstripped_line in enfile:
                line = unstripped_line.strip()
                if not line:
                    fout.write(unstripped_line)
                    continue
                if line[0] == ';':
                    fout.write(unstripped_line)
                    continue
                if line[0] != '[':
                    # interior of sections - replace selected content
                    if new_section:
                        for ks, section in enumerate(sections):
                            if new_section.startswith(section):
                                fcopy = False
                                if ks == 0:      # coords
                                    for node, coords in self.coords.items():
                                        x, y = coords
                                        fout.write(f' {node} \t{strf3(x)} \t{strf3(y)}\n')
                                if ks == 1:      # vertices
                                    for link, points in self.vertices.items():
                                        for x, y in points:
                                            fout.write(f' {link} \t{strf3(x)} \t{strf3(y)}\n')
                                if ks == 2:      # labels
                                    for x, y, label in self.labels:
                                        fout.write(f' {strf3(x)} \t{strf3(y)} \t{label}\n')
                                if ks == 3:      # backdrop
                                    for scmd in self.backdrop:
                                        skip = '; ' if scmd.startswith('DIMEN') else ' '
                                        fout.write(f'{skip}{scmd}\n')
                        new_section = False
                    if fcopy:
                        fout.write(unstripped_line)
                    continue
                # section change
                fout.write(unstripped_line)
                fcopy = True
                new_section = line.upper()
        # os.remove(f.name)

    @property
    def folder(self) -> str:
        """Returns model folder"""
        fld = OP.dirname(self.filename)
        if not fld and _emu_folder:
            fld = _emu_folder
        return fld

    def ENerr(self, ret, showerr: bool = False, info : str = ""):
        "Error handler"
        val = 0
        if isinstance(ret, (list, tuple)):
            ret, val = ret
        elif ret is None:
            ret = 0
        else:
            val, ret = ret, 0
        if self.errcode == 0:
            self.errcode = ret
        if ret > 0:
            _r, error = et.ENgeterror(ret, 80)
            print(ret, error)
            if info:
                error += " " + info
            self.err.append(error)
            if self.debug:
                for msg in self.get_rpt_errors():
                    self.err.append(msg)
                    if showerr:
                        print(msg)
        return val

    def get_rpt_errors(self) -> List[str]:
        '''Gets errors from RPT file'''
        rpt = self.rpt
        res = []
        if not OP.exists(rpt):
            return res
        with open(rpt, "r", encoding="utf-8") as frpt:
            lasterr = False
            for rdata in frpt:
                data = tostr(rdata)
                if lasterr:
                    data = data.strip()
                    if data:
                        lasterr += '\n\t\t' + data
                    else:
                        res.append(lasterr)
                        lasterr = False
                elif re.search(r'(?i)Error \d+:.*', data) is not None:
                    lasterr = data.strip()
            if lasterr:
                res.append(lasterr)
        return res

    @property
    def linkcount(self) -> int:
        """link count"""
        return 0 if self.errcode else ENretval(et.ENgetcount(et.EN_LINKCOUNT))

    @property
    def nodecount(self) -> int:
        """node count"""
        return 0 if self.errcode else ENretval(et.ENgetcount(et.EN_NODECOUNT))

    @property
    def tankcount(self) -> int:
        """tank count"""
        return 0 if self.errcode else len(self.tank_index)

    @property
    def wq_step(self) -> int:
        """WQ step"""
        return 0 if self.errcode else ENretval(et.ENgettimeparam(et.EN_QUALSTEP))

    @staticmethod
    def linknodes(link: Union[str, int], qavg:float = 0) -> Tuple[str, str]:
        """Return initial and final node ID in flow direction if given"""
        ix = link if isinstance(link, Number) else ENretval(et.ENgetlinkindex(link))
        if ix <= 0:
            return "", ""
        nix, nfx = ENretval(et.ENgetlinknodes(ix))
        ni = ENretval(et.ENgetnodeid(nix))
        nf = ENretval(et.ENgetnodeid(nfx))
        return (nf, ni) if qavg < 0 else (ni, nf)

    def pexists(self, p: str) -> bool:
        '''Returns the existence of pipe in the model'''
        if self.errcode:
            return 0
        ix = ENretval(et.ENgetlinkindex(p))
        return ix > 0

    def get_coords(self):
        '''Retrieve coords from .inp file (Epanet2) - used by ChangeProj'''
        fcoords = fvertices = flabels = fbackdrop = False
        with open(self.filename, 'r', encoding=self.FILE_ENCODING) as enfile:
            for line in enfile:
                line = line.strip()
                if not line:
                    continue
                if line[0] == ';':
                    continue
                if line[0] == '[':
                    fcoords = line.startswith('[COORD')
                    fvertices = line.startswith('[VERTI')
                    flabels = line.startswith('[LABEL')
                    fbackdrop = line.startswith('[BACKD')
                    continue
                if fcoords or fvertices:
                    data = line.split()
                    if len(data) < 3:
                        continue
                    coords = float(data[1]), float(data[2])
                    if fcoords:
                        self.coords[data[0]] = coords
                    else:
                        self.vertices[data[0]].append(coords)
                if flabels:
                    data = line.split(maxsplit=2)
                    self.labels.append((float(data[0]), float(data[1]), data[2]))
                if fbackdrop:
                    self.backdrop.append(line)

    def getENerrmsg(self):
        """Returns error"""
        return self.err

    def flowunitfactor(self) -> float:
        '''Returns a coefficient with respect to m3/s'''
        if self.err:
            return 1.0
        ix = self.ENerr(et.ENgetflowunits())
        qepa = {et.EN_CFS: 0.3048**3,
                et.EN_GPM: 0.003785411784/60.,
                et.EN_MGD: 3785.411784/86400., et.EN_IMGD: 4546.09/86400.,
                et.EN_AFD: 4046.86*0.3048/86400.,
                et.EN_LPS: 0.001, et.EN_LPM: 0.001/60., et.EN_MLD: 1000./86400.,
                et.EN_CMH: 1./3600., et.EN_CMD: 1./86400.}[ix]
        # qpic = float(pic.getvar('unite.Q'))
        return qepa

    def flowunitname(self) -> str:
        '''Returns a coefficient with respect to m3/s'''
        if self.err:
            return "?"
        ix = self.ENerr(et.ENgetflowunits())
        qepa = {et.EN_CFS: "cf/s",
                et.EN_GPM: "gpm",
                et.EN_MGD: "Mg/d", et.EN_IMGD: "iMg/d",
                et.EN_AFD: "afd",
                et.EN_LPS: "l/s", et.EN_LPM: "l/min", et.EN_MLD: "Ml/d",
                et.EN_CMH: "m3/h", et.EN_CMD: "m3/d"}[ix]
        # qpic = float(pic.getvar('unite.Q'))
        return qepa

    def pressureunitfactor(self) -> float:
        """returns a coefficient with respect to mcw"""
        if self.err:
            return 1.0
        ix = self.ENerr(et.ENgetflowunits())
        if ix in (et.EN_CFS, et.EN_GPM, et.EN_AFD, et.EN_MGD, et.EN_IMGD):
            # PSI
            return 0.7031
        return 1

    def pressureunitname(self) -> str:
        """returns a name with respect to mcw"""
        if self.err:
            return 1.0
        ix = self.ENerr(et.ENgetflowunits())
        if ix in (et.EN_CFS, et.EN_GPM, et.EN_AFD, et.EN_MGD, et.EN_IMGD):
            # PSI
            return "psi"
        return "m"

    def headunitfactor(self) -> float:
        """returns a coefficient with respect to mcw"""
        if self.err:
            return 1.0
        ix = self.ENerr(et.ENgetflowunits())
        if ix in (et.EN_CFS, et.EN_GPM, et.EN_AFD, et.EN_MGD, et.EN_IMGD):
            # feet
            return 0.3048
        return 1

    def headunitname(self) -> str:
        """returns a name with respect to mcw"""
        if self.err:
            return 1.0
        ix = self.ENerr(et.ENgetflowunits())
        if ix in (et.EN_CFS, et.EN_GPM, et.EN_AFD, et.EN_MGD, et.EN_IMGD):
            # feet
            return "ft"
        return "m"

    def runH_results_asdict(self):
        '''Runs the simulation and collects all links and nodes results
        as dicts of ID -> np.array. No unit conversion'''
        if self.err:
            return None, None, None, None, [], 0
        linkcount, nodecount = self.linkcount, self.nodecount
        if _verbose:
            print('Model has', linkcount, 'links and', nodecount, 'nodes.')

        duration = self.ENerr(et.ENgettimeparam(et.EN_DURATION))
        # 8 * nbts * (duration / dt) < 0.5*10**9 -- double avec la transposition !
        dtmin = 8 * (1 + self.nodecount + self.linkcount) * duration / (5*10**8)
        maxsteps = 5*10**8 // (8 * (1 + self.nodecount + self.linkcount))
        if _verbose:
            print(f'Running simulation over {duration} s and collecting results')
            print(f'Avg sampling interval > {int(dtmin)} s')
        self.ENerr(et.ENopenH(), True)
        # qfact = self.EN2Picunitfactor()
        qfact = 1.0
        tank_index = self.tank_index
        tankcount = len(tank_index)
        mapresults = []
        tstep = 1
        show, stepcount, stepskips, step = 0, 0, 0, duration / 24
        self.ENerr(et.ENinitH(0), True)
        while tstep > 0:
            ret, t = et.ENrunH()
            if ret:
                self.err.append(et.ENgeterror(ret, 80)[1] + ' t=' + hhmmss(t))
            if t >= show:
                txt = f'\t{int(100*show/duration):3d}% - t= {hhmmss(t)}'
                if self.hnd:
                    self.hnd.set(txt)
                elif self.debug:
                    print(txt)
                show += step
            # stepcount < t * maxsteps/duration
            if duration*stepcount <= t*maxsteps:
                stepcount += 1
                # Retrieve hydraulic results for time t
                flow = np.zeros(linkcount+1)
                pres = np.zeros(nodecount+1)
                levl = np.zeros(tankcount)
                for ix in range(1, nodecount+1):
                    _ret, v = et.ENgetnodevalue(ix, et.EN_PRESSURE)
                    pres[ix] = v
                for ix in range(1, linkcount+1):
                    _ret, v = et.ENgetlinkvalue(ix, et.EN_FLOW)
                    flow[ix] = v
                for k, ix in enumerate(tank_index):
                    _ret, v = et.ENgetnodevalue(ix, et.EN_HEAD)
                    levl[k] = v
                mapresults.append((t, flow*qfact, pres, levl))
            else:
                stepskips += 1
            _ret, tstep = et.ENnextH()
        _ret = et.ENcloseH()
        if self.err:
            print('\n'.join(self.err))

        # Transpose results by type and object
        steps = np.array([r[0] for r in mapresults])
        tmp = np.array([r[1] for r in mapresults])
        flows = {et.ENgetlinkid(ix)[1]: tmp[:, ix] for ix in range(1, linkcount+1)}
        tmp = np.array([r[2] for r in mapresults])
        press = {et.ENgetnodeid(ix)[1]: tmp[:, ix] for ix in range(1, nodecount+1)}
        tmp = np.array([r[3] for r in mapresults])
        levls = {et.ENgetnodeid(ix)[1]: tmp[:, k] for k, ix in enumerate(tank_index)}
        #
        tf = steps[-1]
        txt = 'Simulation hydraulique '
        txt += 'terminée' if tf >= duration else 'interrompue à ' + hhmmss(tf)
        if self.hnd:
            self.hnd.set(txt)
        if self.debug:
            print(f'Stored {stepcount} - skipped {stepskips} steps')
            print(txt)
        sr = stepcount/float(stepcount + stepskips)
        return (steps, flows, press, levls, mapresults, sr)

    def runH_results_part(self, links, nodes, tanks):
        '''Runs the simulation and collects results for elements given as parameters
        This function is not intended to be used for all model objects
        flows are converted in m3/s, pressure in mcw, head in mcw
        '''
        time = []
        pres = {k:[] for k in nodes}
        flow = {k:[] for k in links}
        levl = {k:[] for k in tanks}
        ixnodes = [(ENretval(et.ENgetnodeindex(ws(k))), k) for k in nodes]
        ixlinks = [(ENretval(et.ENgetlinkindex(ws(k))), k) for k in links]
        if self.err:
            return time, flow, pres, levl

        linkcount, nodecount = self.linkcount, self.nodecount
        duration = self.ENerr(et.ENgettimeparam(et.EN_DURATION))
        if _verbose:
            print('Model has', linkcount, 'links and', nodecount, 'nodes.')
            print(f'Running simulation over {duration} s and collecting results')
            print(f' links={len(links)} nodes={len(nodes)} tanks={len(tanks)}')
        self.ENerr(et.ENopenH(), True)
        qfact = self.flowunitfactor()
        pfact = self.pressureunitfactor()
        hfact = self.headunitfactor()
        show, step = 0, duration / 10
        self.ENerr(et.ENinitH(0), True)

        tstep = 0 if self.err else 1
        while tstep > 0:
            t = self.ENerr(et.ENrunH(), info="tprev=" + hhmmss(tstep))
            if t >= show:
                if _verbose:
                    print(f'\t{int(100*show/duration):3d}% - t= {t}')
                show += step
            time.append(t)
            # Retrieve hydraulic results for time t
            for ix, node in ixnodes:
                # _ret, ix = et.ENgetnodeindex(node)
                v = ENretval(et.ENgetnodevalue(ix, et.EN_PRESSURE))
                pres[node].append(v*pfact)
            for ix, link in ixlinks:
                # _ret, ix = et.ENgetlinkindex(link)
                v = ENretval(et.ENgetlinkvalue(ix, et.EN_FLOW))
                flow[link].append(v*qfact)
            for tank in tanks:
                ix = ENretval(et.ENgetnodeindex(tank))
                v = ENretval(et.ENgetnodevalue(ix, et.EN_HEAD))
                levl[tank].append(v*hfact)
            tstep = ENretval(et.ENnextH())
        if not self.errcode:
            self.ENerr(et.ENcloseH(), True)
        if self.err:
            print('\n'.join(self.err))
        # if False:
        #     time = np.array(time)
        #     for d in flow, pres, levl:
        #         for k, v in d.items():
        #             d[k] = np.array(v, dtype=np.float32)
        return time, flow, pres, levl

    def runH_snapshot(self, time: int = 0) -> None:
        """Runs a steady-state (snapshot) simulation at given time
        Results are not collected - they can be accessed using regular epanet functions
        ENgetlinkvalue / ENgetnodevalue"""
        et.ENsettimeparam(et.EN_DURATION, 0)
        et.ENsettimeparam(et.EN_PATTERNSTART, time)
        self.ENerr(et.ENopenH(), True)
        self.ENerr(et.ENinitH(0), True)
        et.ENrunH()
        et.ENcloseH()

    def runH_eps(self, mem_max=None) -> Tuple[VectF, MatrF, MatrF, MatrF]:
        '''Runs the simulation and collects all links and nodes results
        Returns a tuple of np.arrays: times[t], flows[t, ix], press[t, ix], levl[t, ix]
        flows are converted in m3/s, pressure in mcw, head in mcw'''
        self.hyd_sim_for_wq = False
        if self.err or self.errcode:
            self.hydraulic_results = None
            return None, None, None, None
        linkcount, nodecount, tankcount = self.linkcount, self.nodecount, self.tankcount
        if self.debug:
            print('Model has', linkcount, 'links and', nodecount, 'nodes.')

        duration = self.duration
        # 8 * nbts * (duration / dt) < 0.5*10**9 -- double avec la transposition !
        if mem_max is None:
            mem_max = self.MEM_X64 if X64 else self.MEM_X32
        mem_max *= 10**6
        dtmin = 8 * (1 + self.nodecount + self.linkcount) * duration / mem_max
        maxsteps = mem_max // (8 * (1 + self.nodecount + self.linkcount))
        if self.debug:
            print(f'Running simulation over {duration} s ({duration//3600} h) and collecting results')
            print(f'Avg sampling interval > {int(dtmin)} s')
        qfact = self.flowunitfactor()
        pfact = self.pressureunitfactor()
        hfact = self.headunitfactor()
         # rule_step = self.ENerr(et.ENgettimeparam(et.EN_RULESTEP))
        steps = []
        tstep = 1
        # preallocate matrix for handling results by time step
        sz_steps = 3 * (duration // self.hyd_step) // 2
        if self.debug:
            print(f"Allocating {sz_steps} for expected {duration // self.hyd_step} hydraulic steps")
        flow = np.zeros((sz_steps, linkcount+1), dtype=np.float32)
        pres = np.zeros((sz_steps, nodecount+1), dtype=np.float32)
        levl = np.zeros((sz_steps, tankcount), dtype=np.float32)
        steps = np.zeros(sz_steps, dtype = np.float32)
        # Prepare and run simulation
        show, stepcount, stepskips, step = 0, 0, 0, duration / (50 if duration > 24 else 24)
        self.ENerr(et.ENopenH(), True)
        self.ENerr(et.ENinitH(0), True)
        while tstep > 0:
            t = et.ENrunH()
            if isinstance(t, (tuple, list)):
                ret, t = t
                if ret:
                    self.err.append(ENretval(et.ENgeterror(ret, 80)) + ' t=' + hhmmss(t))
            if t >= show:
                txt = f'\t{int(100*show/duration):3d}% - t= {hhmmss(t)}'
                if self.hnd:
                    self.hnd.set(txt)
                elif self.debug:
                    print(txt)
                show += step
            if stepcount >= sz_steps:
                # resize if too small
                sz_steps = 5 * int(sz_steps * duration / t) // 4
                if self.debug:
                    print("Resizing result matrix to", sz_steps, "steps at", hhmmss(t))
                flow.resize((sz_steps, linkcount+1), refcheck=False)
                pres.resize((sz_steps, nodecount+1), refcheck=False)
                levl.resize((sz_steps, tankcount), refcheck=False)
                steps.resize(sz_steps, refcheck=False)
            # stepcount < t * maxsteps/duration
            if duration*stepcount <= t*maxsteps:
                # Retrieve hydraulic results for time t
                for ix in range(1, nodecount+1):
                    v = ENretval(et.ENgetnodevalue(ix, et.EN_PRESSURE))
                    pres[stepcount, ix] = v
                for ix in range(1, linkcount+1):
                    v = ENretval(et.ENgetlinkvalue(ix, et.EN_FLOW))
                    flow[stepcount, ix] = v
                for k, ix in enumerate(self.tank_index):
                    v = ENretval(et.ENgetnodevalue(ix, et.EN_HEAD))
                    levl[stepcount, k] = v
                steps[stepcount] = t
                stepcount += 1
            else:
                stepskips += 1
            tstep = ENretval(et.ENnextH())
        #
        et.ENcloseH()
        if self.err:
            if len(self.err) < 128:
                print('\n'.join(self.err))
            else:
                print('\n'.join(self.err[:64]))
                print('\t...')
                print('\n'.join(self.err[-64:]))

        # Transpose results by type and object
        if self.debug:
            print(f"Epanet simulation done ({stepcount} steps - skipped {stepskips})")
        steps.resize(stepcount, refcheck=False)
        flow.resize((stepcount, linkcount+1), refcheck=False)
        pres.resize((stepcount, nodecount+1), refcheck=False)
        levl.resize((stepcount, tankcount), refcheck=False)
        # Results in m3/s and mcw
        flow *= qfact
        pres *= pfact
        levl *= hfact
        # flows =  {ENretval(et.ENgetlinkid(ix)): flow[:, ix] for ix in range(1, linkcount+1)}
        # press = {ENretval(et.ENgetnodeid(ix)): pres[:, ix] for ix in range(1, nodecount+1)}
        # levls = {ENretval(et.ENgetnodeid(ix)): levl[:, k] for k, ix in enumerate(self.tank_index)}
        tf = steps[-1]
        txt = 'complete' if tf >= duration else 'halted at ' + hhmmss(tf)
        txt = 'Hydraulic simulation ' + txt
        if self.hnd:
            self.hnd.set(txt)
        if self.debug:
            print(txt)
        # Close and reopen to allow further use of ENsolveH
        # self.ENerr(et.ENclose())
        # self.ENerr(et.ENopen(ws(self.inp), ws(self.rpt), ws("")), True)
        self.hydraulic_results = steps, flow, pres, levl
        return steps, flow, pres, levl

    def runH_for_WQ(self):
        """Runs hydraulic for WQ"""
        if not self.hyd_sim_for_wq:
            # if self.verbose:
            if _verbose:
                print("Running SolveH for:", self.filename)
            self.ENerr(et.ENsolveH(), True)
            self.hyd_sim_for_wq = not self.errcode

    def runWQ(self, wqargs: Tuple[int, str, str, str],
              wq_cycles: int = 1,
              mem_max = None,
              comp_name: str = "") -> Tuple[VectF, MatrF, MatrF]:
        '''Runs the WQ simulation and collects all links and nodes results
        wqargs: ENsetqualtype args (wq type, chem name, unit, trace node)
        wq_cycle: multiplier for the simulation duration - only last duration will be used
        Returns a tuple of np.arrays: times[t], node_wq_results[t, ix], flows[t, ix]
        Flows are converted to m3/s'''
        if self.err or self.errcode:
            return None, None, None
        nodecount = self.nodecount
        linkcount = self.linkcount
        if wq_cycles > 0:
            # extend hydraulic horizon by wq_cycles
            # if duration=24h and wq_cycle=3: run 3*24h but keep last 24h for WQ results
            total_duration = int(self.duration * wq_cycles)
            start_collection_time = max(0, total_duration - self.duration)
            et.ENsettimeparam(et.EN_DURATION, total_duration)
        elif wq_cycles <= -1:
            # use 1 / abs(wq_cycles) last portion for WQ data
            # if duration=72h and wq_cycle=-3: run 72h and keep last 72/3= 24h for WQ results
            wq_cycles *= -1
            total_duration = self.duration
            start_collection_time = total_duration * (wq_cycles - 1) / wq_cycles
        else:
            # values in [0, 1[ are not allowed
            raise ValueError
        duration = int(round(self.duration))
        # 8 * nbts * (duration / dt) < 0.5*10**9 -- double avec la transposition !
        if mem_max is None:
            mem_max = self.MEM_X64 if X64 else self.MEM_X32
        mem_max *= 10**6
        dtmin = 8 * (1 + self.nodecount) * duration / mem_max
        maxsteps = mem_max // (8 * (1 + self.nodecount))
        if self.debug:
            print(f'Running simulation over {total_duration} s ({total_duration//3600} h)',
                f'and collecting last period ({duration // 3600} h) results')
            print(f'Avg sampling interval > {int(dtmin)} s')
        steps = []
        tstep = duration
        # preallocate matrix for handling results by time step
        sz_steps = 5 * (duration // self.wq_step) // 4
        if self.debug:
            print(f"Allocating {sz_steps} for expected {duration // self.wq_step} WQ steps")
        vect = np.zeros((sz_steps, nodecount+1), dtype=np.float32)
        flow = np.zeros((sz_steps, linkcount+1), dtype=np.float32)
        steps = np.zeros(sz_steps, dtype = np.float32)
        # Prepare and run simulation
        show, stepcount, stepskips = 0, 0, 0
        step = total_duration / (50 if total_duration > 24 else 24)
        self.runH_for_WQ()
        self.ENerr(et.ENsetqualtype(*wqargs), True)
        self.ENerr(et.ENopenQ(), True)
        self.ENerr(et.ENinitQ(0), True)
        while tstep > 0:
            t = ENretval(et.ENrunQ())
            if t >= show:
                txt = f'\t{int(100*show/total_duration):3d}% - t= {hhmmss(t)}'
                if self.hnd:
                    self.hnd.set(txt)
                if self.debug:
                    print(txt)
                show += step
            t_rel = t - start_collection_time
            if stepcount >= sz_steps:
                # resize if too small
                sz_steps = 5 * int(sz_steps * duration / t_rel) // 4
                if self.debug:
                    print("Resizing result matrix to", sz_steps, "steps at", hhmmss(t))
                vect.resize((sz_steps, nodecount+1), refcheck=False)
                flow.resize((sz_steps, linkcount+1), refcheck=False)
                steps.resize(sz_steps, refcheck=False)
            # stepcount < t * maxsteps/duration
            if duration*stepcount <= t_rel*maxsteps:
                # Retrieve water quality results for time t
                for ix in range(1, nodecount+1):
                    v = ENretval(et.ENgetnodevalue(ix, et.EN_QUALITY))
                    vect[stepcount, ix] = v
                for ix in range(1, linkcount+1):
                    v = ENretval(et.ENgetlinkvalue(ix, et.EN_FLOW))
                    flow[stepcount, ix] = v
                steps[stepcount] = t
                stepcount += 1
            else:
                stepskips += 1
            tstep = ENretval(et.ENstepQ())
        #
        et.ENcloseQ()
        if self.err:
            if len(self.err) < 128:
                print('\n'.join(self.err))
            else:
                print('\n'.join(self.err[:64]))
                print('\t...')
                print('\n'.join(self.err[-64:]))

        # Transpose results by type and object
        if self.debug:
            print(f"Epanet simulation done ({stepcount} steps)")
        steps.resize(stepcount, refcheck=False)
        vect.resize((stepcount, nodecount+1), refcheck=False)
        flow.resize((stepcount, linkcount+1), refcheck=False)
        # flows in m3/s
        flow *= self.flowunitfactor()
        # print(f'Stored {stepcount} - skipped {stepskips} steps')
        if self.hnd:
            tf = steps[-1]
            txt = 'complete' if tf >= total_duration - self.wq_step else 'halted at ' + hhmmss(tf)
            if comp_name:
                txt += " for " + comp_name
            txt = f'WQ simulation {txt}'
            if self.debug:
                print(txt)
            self.hnd.set(txt)
        return steps, vect, flow

    run_hydraulic_snapshot = runH_snapshot
    run_hydraulic_eps = runH_eps

    def getallminmax(self, typelt: ElemType, attr: str) -> Tuple[VectF, VectF, VectF]:
        """Returns min, max and avg values of elements of given type for attr
        from results stored during last 'runH_eps'
        attributes allowed: Q, V (links), P, CH, HH (nodes)"""
        # select result table
        try:
            results = self.hydraulic_results[typelt]
        except (AttributeError, KeyError):
            return [], [], []
        # could have the transformation on min, max, avg but requires 3 to be treated
        if typelt == LINK and attr == "V":
            # copy res array
            results = results.copy()
            # divide by pipe section
            for k in range(1, self.linkcount + 1):
                inv_area = 1 / area if (area := link_section(k)) > 0 else 0
                results[:, k] *= inv_area
        elif typelt == NODE and attr in ("CH", "HH"):
            # copy res array
            results = results.copy()
            # add elevation
            for k in range(1, self.nodecount + 1):
                z = et.ENgetnodevalue(k, et.EN_ELEVATION)
                results[:, k] += z
        elif not (typelt == LINK and attr == "Q" or typelt == NODE and attr == "P"):
            raise ValueError
        return results.min(axis=0), results.max(axis=0), results.mean(axis=0)

    def raw_stat_duration(self, typelt: ElemType, attr: str,
                        str_op : str, treshold : float,
                        indexes : List[int], count : int) -> VectF:
        """Returns cumulated time interval where results for attr is op vlim
        from results stored during last 'runH_eps'
        attributes allowed: Q, V (links), P, CH, HH (nodes)"""
        if count < len(indexes):
            raise ValueError
        # select result table
        try:
            values = self.hydraulic_results[typelt]
            steps = self.hydraulic_results[0]
        except (AttributeError, KeyError):
            return []
        # convert to the required attribute
        if typelt == LINK and attr == "V":
            # copy res array
            values = values.copy()
            for k in indexes:
                inv_area = 1 / area if (area := link_section(k)) > 0 else 0
                values[:, k] *= inv_area
        elif typelt == NODE and attr in ("CH", "HH"):
            # copy res array
            values = values.copy()
            for k in indexes:
                z = et.ENgetnodevalue(int(k), et.EN_ELEVATION)
                values[:, k] += z
        elif not (typelt == LINK and attr == "Q" or typelt == NODE and attr == "P"):
            raise ValueError
        # compute cumulated time
        dt = [steps[1:] - steps[:-1]]
        comp_func = {">": np.greater, ">=": np.greater_equal, "=": np.equal,
                    "<": np.less, "<=": np.less_equal, "==": np.equal}[str_op]
        cumt = [np.sum(dt, where=comp_func(values[:-1, k], treshold)) for k in indexes]
        return np.array(cumt)


class Elements:
    '''Generic iterator for model elements'''
    def __init__(self, typelt):
        if isinstance(typelt, Number):
            self.type = typelt
            self.nbmax = nbobjects(self.type)
            self.get_id = {LINK: et.ENgetlinkid,
                           NODE: et.ENgetnodeid,
                           TANK: get_tank_id}[typelt]
        self.index = 1
    def __iter__(self):
        return self
    def __next__(self):
        if self.index > self.nbmax:
            raise StopIteration
        elem = ENretval(self.get_id(self.index))
        self.index += 1
        return tostr(elem)
    def __len__(self):
        return self.nbmax
    next = __next__
    len = __len__

class Nodes(Elements):
    '''Node iterator'''
    def __init__(self):
        super(Nodes, self).__init__(NODE)

class Links(Elements):
    '''Links iterator'''
    def __init__(self):
        super(Links, self).__init__(LINK)

class Tanks(Elements):
    '''Tanks iterator'''
    def __init__(self):
        super(Tanks, self).__init__(TANK)

class Pipes:
    '''Pipe iterator for model elements - Returns ID or ID, value'''
    def __init__(self, attr: str = None):
        if _emu_object is None:
            self.nbmax = 0
        else:
            self.nbmax = len(_emu_object.pipe_index)
            self.pipe_index = np.array(_emu_object.pipe_index, dtype=np.int32)
        self.index = 0
        self.en_attr = None
        if attr is None:
            return
        self.en_attr = PIC2EPA_LINK_ATTRS.get(attr.upper(), et.EN_FLOW)
    def __iter__(self):
        return self
    def __next__(self) -> Union[str, Tuple[str, float]]:
        if self.index >= self.nbmax:
            raise StopIteration
        idx = int(self.pipe_index[self.index])
        elem = ENretval(et.ENgetlinkid(idx))
        self.index += 1
        if self.en_attr is None:
            return tostr(elem)
        elif self.en_attr == "SC":
            return tostr(elem), link_section(idx)
        return tostr(elem), ENretval(et.ENgetlinkvalue(idx, self.en_attr))
    def __len__(self):
        return self.nbmax
    next = __next__
    len = __len__

class GanessaError(Exception):
    '''Error class - may be useless here'''
    def __init__(self, number, reason, text):
        self.number = number
        self.reason = reason
        self.text = tostr(text)
    def __str__(self):
        return __file__ + f' ERROR : ({self.number}) : {self.text}'

def epanet_model():
    """Returns the Epanet model (ENmodel) instance"""
    return _emu_object

def epanet_folder():
    """Returns the Epanet folder as ddefined with init"""
    return _emu_folder

def init(folder: str = None, _silent: bool = False, debug: bool = False):
    """Emulate Piccolo/Ganessa_SIM init method"""
    global _emu_folder, _debug
    _emu_folder = folder
    _debug = debug
    # this is equivalent to close() - terminate default owa-epanet
    close()

def dll_version() -> str:
    """Returns epanet version as str: "2.0" or "2.2" """
    return epanet_version

def full_version() -> str:
    '''Returns the version of the dll (after init)'''
    ret = f"Epanet {epanet_version} (from {epanet_source}) / (py)ganessa {_version}"
    return ret

def close(*_args):
    """Ends Epanet model - kill owa-epanet project"""
    global _emu_object
    if _emu_object:
        _emu_object.close()
    _emu_object = None

atexit.register(close)

def setlang(_new_lang) -> str:
    """Fake for Piccolo setlang"""
    return 'en'

def useExceptions(enable=True):
    """fake for Piccolo useExceptions"""
    import inspect
    fname = inspect.currentframe().f_code.co_name
    if _verbose:
        print("Ignoring call to", fname, "with arg:", enable)

def reset():
    """fake for Piccolo reset - close/reopen epanet project"""
    try:
        model_file = _emu_object.filename
    except AttributeError:
        model_file = ""
    if model_file:
        cmdfile(model_file)
    elif is_owa_epanet or _emu_object:
        et.ENclose()

def is_embedded() -> bool:
    """Fake for Piccolo is_embedded """
    return False

def cmdfile(fname: str, *_args):
    """fake for piccolo cmdfile - Opens Epanet model"""
    # close()
    if is_owa_epanet or _emu_object:
        et.ENclose()
    temp = ENmodel(fname, None, _debug)
    assert temp == _emu_object

def loadbin(fname: str):
    """fake for piccolo loadbin - Opens Epanet model"""
    # close()
    if is_owa_epanet or _emu_object:
        et.ENclose()
    temp = ENmodel(fname, None, _debug)
    assert temp == _emu_object

def loadres():
    """fake for piccolo loadres - simulate ?"""
    if _emu_object and _emu_object.hydraulic_results is None:
        _emu_object.runH_eps()
        return 0
    return 1

def resfile() -> str:
    """Fake for Piccolo resfile"""
    try:
        model_file = _emu_object.filename
    except AttributeError:
        model_file = "To_be_defined.inp"
    return model_file

def runH(time: int = 0) -> int:
    """fake for piccolo solveH - snapshot simulation (Epanet: runH)"""
    if _emu_object:
        _emu_object.runH_snapshot(time)
        return 0
    return 1

def clear_err(full=False):
    """Clear errors if any"""
    if _emu_object:
        _emu_object.errcode = 0
        if full:
            _emu_object.err = []
        return 0
    return 1

def cmd(arg):
    """fake for piccolo cmd"""
    if _verbose:
        print("Ignoring:", arg)
    return 0

def execute(*args):
    """fake for piccolo execute"""
    if _verbose:
        print("Ignoring execute", len(args), "commands")
    return 0

def save(fname: str):
    """save model as (epanet2 with coords / vertices / labels)"""
    if _emu_object:
        _emu_object.save_as(fname)

def savemodel(fname: str, append_section : List[str] = None):
    """save model; optionally append a section"""
    if _emu_object:
        _emu_object.save(fname, append_section)

def nbobjects(objtyp: int) -> int:
    """fake for piccolo nbobjects"""
    try:
        return {LINK: _emu_object.linkcount,
                NODE: _emu_object.nodecount,
                TANK: _emu_object.tankcount,
                }[objtyp]
    except AttributeError:
        return 0

def nbvertices() -> int:
    """Returns the number of vertices found in the .inp"""
    return len(_emu_object.vertices) if _emu_object else 0

def selectlen(text: str) -> Tuple[int, int]:
    """Return a count - valid for pipes only"""
    if text.upper() in ("TUYAU", "PIPE"):
        return len(_emu_object.pipe_index), LINK
    if text.upper() in ("TANK", "RESERVOIR") or "RESERVOIR".startswith(text.upper()):
        return len(_emu_object.tank_index), TANK
    return 0, LINK

def get_tank_id(idx: int) -> str:
    """Return a tank ID for the current model (index starting at 1)"""
    try:
        return ENretval(et.ENgetnodeid(_emu_object.tank_index[idx-1]))
    except AttributeError:
        return ""

def getid(typelt: int, idx: int) -> str:
    """Return object ID by type (index starting at 1)"""
    if typelt == LINK:
        sid = et.ENgetlinkid(idx)
    elif typelt == NODE:
        sid = et.ENgetnodeid(idx)
    elif _emu_object:
        sid = et.ENgetnodeid(_emu_object.tank_index[idx-1])
    else:
        return ""
    return tostr(ENretval(sid))

def linknodes(link: Union[int, str], flow: float = 0) -> Tuple[str, str]:
    """Return from and to node IDs - link is either an ID or an index"""
    if _emu_object:
        return _emu_object.linknodes(link, flow)
    return "", ""

def nlinkattr(idx: int, attr: str) -> float:
    """fake for piccolo nlinkattr - implemented for a limited set of attributes"""
    et_attr = PIC2EPA_LINK_ATTRS[attr]
    v = ENretval(et.ENgetlinkvalue(idx, et_attr))
    return v

def linkattr(sid: str, attr: str) -> float:
    """fake for piccolo linkattr - implemented for a limited set of attributes"""
    ix = ENretval(et.ENgetlinkindex(sid))
    return nlinkattr(ix, attr) if ix else 0

def getindex(typelt: int, sid: str) -> int:
    """Return object index"""
    try:
        if typelt == LINK:
            idx = ENretval(et.ENgetlinkindex(sid))
        elif typelt == NODE:
            idx = ENretval(et.ENgetnodeindex(sid))
        elif _emu_object:
            idxn = ENretval(et.ENgetnodeindex(sid))
            idx = _emu_object.tank_index.index(idxn) + 1
    except ValueError:
        idx = 0
    return idx

def exists(typelt: int, sid: str) -> bool:
    """Returns true if object exists, false otherwise"""
    return getindex(typelt, sid) > 0

def nnodeattr(idx: int, attr: str) -> float:
    """fake for piccolo nnodeattr - implemented for a limited set of attributes"""
    if attr in ('X', 'Y'):
        nid = ENretval(et.ENgetnodeid(idx))
        try:
            return _emu_object.coords[nid]
        except (AttributeError, KeyError):
            return 0
    et_attr = PIC2EPA_NODE_ATTRS[attr]
    v = ENretval(et.ENgetnodevalue(idx, et_attr))
    return v

def nodeattr(nid: str, attr: str) -> float:
    """fake for piccolo nodeattr - implemented for a limited set of attributes"""
    if attr in ('X', 'Y'):
        try:
            return _emu_object.coords[nid][0 if attr == 'X' else 1]
        except (AttributeError, KeyError):
            return 0
    et_attr = PIC2EPA_NODE_ATTRS[attr]
    idx = ENretval(et.ENgetnodeindex(nid))
    v = ENretval(et.ENgetnodevalue(idx, et_attr))
    return v

def link_section(link: int) -> float:
    """Returns section of a link - 0 if diameter is undefined (pumps)"""
    try:
        diam = et.ENgetlinkvalue(link, et.EN_DIAMETER)
        return pi * (0.0005 * diam) ** 2
    except:
        return 0

def linkXYZV(sid: str, include_nodes: bool = True) -> Tuple[VectF, VectF, VectF, VectF, int]:
    """fake for piccolo linkXYZV"""
    x, y, z, v, nbp = [], [], [], [], 0
    if not _emu_object:
        return x, y, z, v, nbp
    ix = ENretval(et.ENgetlinkindex(sid))
    xni, xnf = ENretval(et.ENgetlinknodes(ix))
    zi = ENretval(et.ENgetnodevalue(xni, et.EN_ELEVATION))
    zf = ENretval(et.ENgetnodevalue(xnf, et.EN_ELEVATION))
    try:
        vertices = _emu_object.vertices[sid]
    except KeyError:
        if not include_nodes:
            return x, y, z, v, nbp
    else:
        x, y = zip(*vertices) if vertices else ([], [])
        nbp = len(x)
    if include_nodes:
        nbp += 2
    # faux mais bon...
    z = np.linspace(zi, zf, num=nbp)
    v = np.zeros(nbp)
    if include_nodes:
        x[0:0] = nnodeattr(xni, 'X')
        x.append(nnodeattr(xnf, 'X'))
        y[0:0] = nnodeattr(xni, 'Y')
        y.append(nnodeattr(xnf, 'Y'))
    return x, y, z, v, nbp

def getpipedate(link : int) -> Tuple[float, float, float, float]:
    """Returns pipe parameters as set by setpipedata:
    length, diam, rough, mloss"""
    length = et.ENgetlinkvalue(link, et.EN_LENGTH)
    diam = et.ENgetlinkvalue(link, et.EN_DIAMETER)
    rough = et.ENgetlinkvalue(link, et.EN_ROUGHNESS)
    mloss = et.ENgetlinkvalue(link, et.EN_MINORLOSS)
    return length, diam, rough, mloss

def getunitcoef(attr : str) -> float:
    """Returns the unit relative to Piccolo reference unit"""
    try:
        if attr.upper()[0] == "Q":
            return _emu_object.flowunitfactor()
        if attr.upper()[0] == "P":
            return _emu_object.pressureunitfactor()
    except AttributeError:
        return 1

def getunitname(attr : str) -> str:
    """Returns the unit name"""
    try:
        if attr.upper()[0] == "Q":
            return _emu_object.flowunitname()
        if attr.upper()[0] == "P":
            return _emu_object.pressureunitname()
    except AttributeError:
        return "Unknown"

def getvar(command : str) -> str:
    """fake for piccolo getvar"""
    command = command.upper()
    if m := re.match(r"Q(\d\d):NOEUD\.[XY]", command):
        if not _emu_object.coords:
            _emu_object.get_coords()
        xy = np.array(list(_emu_object.coords.values()))
        percentile = int(m[1])
        values = np.percentile(xy, percentile, axis=0)
        return strf3(values[0 if command[-1] == "X" else 1])
    return "#NAN#"

def get_labels():
    '''Returns the list of (x, y, labels) if any'''
    try:
        return _emu_object.labels
    except AttributeError:
        return []

def set_coordinates(node, x, y):
    '''Resets the node coordinates'''
    try:
        _emu_object.coords[node] = (x, y)
    except (AttributeError, KeyError):
        pass

def set_vertices(link, x, y):
    '''Resets the link vertices'''
    try:
        _emu_object.vertices[link] = list(zip(x, y))
    except (AttributeError, KeyError):
        pass

def clear_labels():
    '''Add a new label'''
    if  _emu_object:
        _emu_object.labels = []

def add_label(x, y, label):
    '''Add a new label'''
    if _emu_object:
        _emu_object.labels.append((x, y, label))

def add_extra_text(text):
    '''Add a new comment'''
    if _emu_object:
        if not text.startswith(';'):
            text = ';' + text
        _emu_object.extra_text.append(text)

def total_demand() -> Tuple[float, float]:
    """Return total demand and deficit at current time"""
    nodecount = nbobjects(NODE)
    demand = deficit = 0
    for ix in range(1, nodecount+1):
        if ENretval(et.ENgetnodetype(ix)) == et.EN_JUNCTION:
            demand += ENretval(et.ENgetnodevalue(ix, et.EN_DEMAND))
            deficit += ENretval(et.ENgetnodevalue(ix, et.EN_DEMANDDEFICIT))
            # reduction += ENretval(et.ENgetnodevalue(ix, et.EN_DEMANDREDUCTION))
    return demand, deficit

def getallminmax(typelt: ElemType, attr: str) -> Tuple[VectF, VectF, VectF]:
    """Returns min, max and avg values of elements of given type for attr"""
    return _emu_object.getallminmax(typelt, attr)

def raw_stat_duration(typelt: ElemType, attr: str,
                      str_op : str, treshold : float,
                      indexes : List[int], count : int) -> VectF:
    """Returns cumulated time interval where results for attr is op vlim"""
    return _emu_object.raw_stat_duration(typelt, attr, str_op, treshold, indexes, count)
