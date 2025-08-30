'''
Created on 8 sept. 2017

Functions specific to the hydraulic extended period and WQ simulation (Piccolo)

@author: Jarrige_Pi
'''
import numbers
from typing import Callable, List, Union, Tuple, NamedTuple, Sequence
from numpy import (array as nparray, ndarray, float32, float64, zeros as npzeros,
                   abs as npabs, diff as npdiff, roll as nproll)

from ganessa.util import (winstr, quotefilename, hhmmss, hhmmssd, is_text, tostr,
        is_wq, PY3)
from ganessa.sim import _dll_api
from ganessa.core import (M, DICT, SIMERR, LINK, NODE, TANK, ElemType, GanessaError, VectF,
        _dll_version, selectlen, _select, _ganessa_raise_exceptions, _checkExceptions, getid,
        getindex, getall, _debug, _fn_undefined, dll_version,
        _ret_errstat, _ret_errstat2)

# Run the simulation
try:
    solveh = _dll_api.simulh
except AttributeError:
    solveh = _dll_api.solveh
#****g* ganessa.sim/sFunctions
# DESCRIPTION
#   Functions available to ganessa.sim ONLY.
#****
#****g* ganessa.sim/sIterators
# DESCRIPTION
#   Iterators available to ganessa.sim ONLY
#****
#****f* sFunctions/full_solveH
# PURPOSE
#   Runs the full simulation and loads the result file for browsing results
# SYNTAX
#   istat = full_solveH([resultfile] [, silent] [, iverb] [, retry])
# ARGUMENT
#   * string resultfile: if provided, the results will be written in the file
#     instead of the default 'result.bin'. If the file exists it will be superseded.
#     If not it will be created.
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). The defaults is -1.
#   * bool retry: if set to True, the simulation is run again twice if it fails
#     because of isolated nodes. Optional -  defaults to False
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - Unless explicitely disabled, results are saved to a binary file,
#     which defaults to the file 'result.bin' in the ganessa work directory.
#   - Binary result files also contain all data describing the model.
#   - silent=True overrides iverb setting if provided.
# HISTORY
#   * 1.5.1: optional argument 'retry' added
#   * 2.0.7: improved error check (19/08/19)
#   * 2.2.3: retry=True retries the simulation twice, in case STOP-ON-APP is OFF (26/06/21)
#****
def full_solveH(resultfile: str = None, silent: bool = False,
                iverb: int = -1, retry: bool = False) -> int:
    '''Runs a full hydraulic simulation; optional arguments are:
    Resultfile: (full) name of the .bin resultfile
    silent: if set to True, all messages will be disabled (default False)
    iverb: allow intermediate setting of verbosity (>0) or dumbness (<0)
    retry: if set to True, simulation will restart after an initial 'isolated node' error
    Changed 26.06.21: retry twice - in case STOP-ON-APP is OFF
    '''
    # SIM IVERB
    if silent:
        sverb = '-9'
    elif iverb == -1:
        sverb = '-1'
    else:
        sverb = str(iverb)
    SIM = M.SIM
    _dll_api.gencmd(SIM.ROOT, SIM.IVER, M.NONE, sverb)
    if resultfile:
        # SIM FILE xxx
        _dll_api.gencmd(-SIM.ROOT, SIM.FILE, M.NONE, winstr(quotefilename(resultfile)))
    #  EXEC FULL-PERIOD
    _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, DICT.FULLPER)
    istat = _dll_api.commit(0)
    if retry:
        bsimerr, nsimerr = divmod(abs(istat), SIMERR.SIMERR)
        if bsimerr and nsimerr == SIMERR.ISOL:
            _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, DICT.FULLPER)
            istat = _dll_api.commit(0)
            bsimerr, nsimerr = divmod(abs(istat), SIMERR.SIMERR)
            if bsimerr and nsimerr == SIMERR.ISOL:
                _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, DICT.FULLPER)
                istat = _dll_api.commit(0)
    _checkExceptions(32, istat, 'Error running hydraulic simulation')
    return istat

#****f* sFunctions/solveH
# PURPOSE
#   Runs the simulation at a given instant
# SYNTAX
#   istat = solveH(time [, retry])
# ARGUMENT
#   * int or str time: instant to run the simulation - default to 0.
#     if int: time in seconds; if str: time in the format hh:mm[:ss]
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). If not set, leaves 'iverb' unchanged.
#   * bool retry: if set to True, the simulation is run again if it fails
#     because of isolated nodes. Optional -  defaults to False
# RESULT
#   int istat: error status (0 if OK)
# HISTORY
#   * added 2017.05.15 - version 1.7.5
#   * changed 2019.04.23 - version 2.0.6 - added a third retry
#   * changed 2019.08.19 - version 2.0.7 - improved error check
#****
def solveH(time=0, silent=False, iverb=None, retry=False) -> int:
    '''Runs snapshot hydraulic simulation; optional arguments are:
    time: time at which simulation runs (numeric or hh:mm[:ss])
    silent: if set to True, all messages will be disabled (default False)
    iverb: allow intermediate setting of verbosity (>0) or dumbness (<0)
    retry: if set to True, simulation will restart after an initial 'isolated node' error
    '''
    # SIM
    SIM = M.SIM
    _dll_api.gencmd(SIM.ROOT, SIM.NONE, M.NONE)
    # IVERB
    if silent:
        iverb = -9
    if iverb is not None:
        _dll_api.gencmd(-SIM.ROOT, SIM.IVER, M.NONE, str(iverb))
    # Simulation time
    if isinstance(time, numbers.Number):
        if time == 0:
            stime = '0:0:0'
        else:
            stime = hhmmss(time, rounded=True)
    else:
        stime = time
    #  EXEC
    _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE, stime)
    istat = _dll_api.commit(0)
    if retry:
        bsimerr, nsimerr = divmod(abs(istat), SIMERR.SIMERR)
        if bsimerr and nsimerr == SIMERR.ISOL:
            _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE, stime)
            istat = _dll_api.commit(0)
            # 3rd trial, in case of ON-ISOL-DYN-STOP OFF
            bsimerr, nsimerr = divmod(abs(istat), SIMERR.SIMERR)
            if bsimerr and nsimerr == SIMERR.ISOL:
                _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE, stime)
                istat = _dll_api.commit(0)
    _checkExceptions(32, istat, 'Error running hydraulic simulation')
    return istat

#****f* sFunctions/setWQresultfile
# PURPOSE
#   Defines the binary result file(s) for WQ simulation.
# SYNTAX
#   setWQresultfile([fnode] , [flink])
# ARGUMENTS
#   * str fnode: name of the node WQ result file
#   * str flink: name of the link WQ result file (optional)
# REMARK
#   * if fnode is omitted, either use None or flink=filename
#   * this command can be used either before running the simulation, for writing
#     the file(s), or afterwards, in order to choose which result file(s) to browse.
#****
def setWQresultfile(fnode: str = None, flink: str = None) -> None:
    '''Added 150914'''
    QUA = M.QUA
    if fnode is not None:
        # QUAL FILE xxx
        _dll_api.gencmd(QUA.ROOT, QUA.NODEFILE, M.NONE, winstr(quotefilename(fnode)))
    if flink is not None:
        # QUAL FILE xxx
        _dll_api.gencmd(QUA.ROOT, QUA.LINKFILE, M.NONE, winstr(quotefilename(flink)))
    _istat = _dll_api.commit(0)

#****f* sFunctions/browseH, browseWQ
# PURPOSE
#   Retrieves and interpolate results from a given time step or instant:
#   * browseH retrieves hydraulic results.
#   * browseWQ retrieves hydraulic
#   |html <b>and</b> water quality results
# SYNTAX
#   * istat = browseH(seconds_or_instant [, wq=False])
#   * istat = browseWQ(time_step_or_instant)
# ARGUMENTS
#   * float seconds: time to load (seconds)
#   * string instant: instant to load, in the form hh:mm:ss[.dd]
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   When called with a numeric value (seconds) is rounded to the nearest second.
#
#   For hydraulic results, two set of results may be available at a given instant:
#   * at boundary of time steps, except beginning and end of the simulation,
#     results ending the previous time step and results starting the next time step.
#   * at internal time steps when a state transition occured (pump start/stop etc.).
#
#   In such a situation the results are those from the end of the previous interval.
#   Use "hresults_block(k) for k in range(tslen())" to get all results in time forward order,
#   including duplicate time.
#****
def browseH(time_or_str: Union[str, float], wq: bool=False) -> int:
    '''Browse .bin result file for hydraulic/WQ results at given time'''
    if isinstance(time_or_str, numbers.Number):
        stime = hhmmss(time_or_str, rounded=True)
    else:
        stime = time_or_str
    GEN = M.GEN
    _dll_api.gencmd(GEN.ROOT, GEN.FIND, DICT.INSTANT, stime)
    if wq:
        _dll_api.gencmd(GEN.ROOT, GEN.FIND)
        _dll_api.gencmd(M.QUA.ROOT, M.NONE, extmode=1)
    istat = _dll_api.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(16*3, istat,
                'Error while retrieving simulation results at: ' + stime)
    return istat

def browseWQ(time_or_str: Union[str, float]):
    '''Browse hydraulic and WQ result file at given time'''
    return browseH(time_or_str, True)

#****f* sFunctions/tsdemand, tsdevice, tsdemandlen, tsdevicelen
# PURPOSE
#   * tsdemandlen: returns the number of values in the profile (demand code)
#   * tsdevicelen: returns the number of values in the device state TS
#   * tsdemand: return the profile time series (demand type)
#   * tsdevice: return the device state time series(boundary conditions)
# SYNTAX
#   * tslen = tsdemandlen(code [, zone])
#   * vec_tim, vec_val, len, mode = tsdemand(code, [,zone])
#   * tslen = tsdevicelen(sid[, attr])
#   * vec_tim, vec_val, len, mode = tsdevice(sid [, attr] [, fixed_interval])
# ARGUMENTS
#   * string code: demand type of element
#   * string zone: area of element
#   * string sid: device element ID
#   * string attr: pump attribute (speed or number of units)
#     or "N" or "NV" or "H" for reservoirs or ""
#   * float fixed_interval (optional): if present and > 0, return values at the give time step
# RESULT
#   * int tslen: number of values for the time serie (0 if none)
#   * float[] vec_tim: vector of instants in seconds
#   * float[] vec_val: vector of demand coefficients (not percentages) or settings
#    (for pumps: 0= off, 1 or higher= open/active)
#   * int mode: type of demand profile (<0 as time series, >0 based on time steps)
# REMARKS
#   * These functions require version 2016 or higher of Piccolo/Ganessa dll
#   * Demand zones require version 2020b or higher
#   * when the demand code or equipment does not exist or has no forcing TS associated,
#     the value (None, None, 0, 0) is returned.
#   * The demand coefficient for the demand type 'code' can be retrieved
#     as float(getvar('coefficient:' + code))
#   * tsdevice("", "T") retrives the user time steps boundaries.
#   * A pump is shut off when the number of units running is 0, even if rotation speed is > 0.
# HISTORY
#   * 25.01.2017: added 'fixed_interval' parameter to tsdevide; changed return value to float
#   * 22.09.2020: added the query of demand profile by zone
#   * 08.08.2022: added the query of pressure reference TS (using N or NV or H)
#
#****
try:
    _tsdemandlen = _dll_api.demand_tslen
except AttributeError:
    _fn_undefined.append('tsdemand')
    tsdemandlen = _ret_errstat
else:
    try:
        _tsczdemandlen = _dll_api.demandcz_tslen
    except AttributeError:
        _tsczdemandlen = _ret_errstat
    def tsdemandlen(code: str, zone: str = '') -> int:
        '''Returns the demand profile TS length for the code / zone'''
        return _tsczdemandlen(code, zone) if zone else _tsdemandlen(code)

def tsdemand(code: str, zone: str = '') -> Tuple[VectF, VectF, int, int]:
    '''Returns the TS demand profile for given code and zone'''
    if zone:
        nbval = _tsczdemandlen(code, zone)
        if nbval > 0:
            return _dll_api.demandcz_ts(code, zone, nbval)
        return (None, None, 0, 0)
    nbval = _tsdemandlen(code)
    if nbval > 0:
        return _dll_api.demand_ts(code, nbval)
    return (None, None, 0, 0)

try:
    tsdevicelen: Callable[[str, str], int] = _dll_api.device_tslen
except AttributeError:
    _fn_undefined.append('tsdevice')
    tsdevicelen = _ret_errstat

def tsdevice(sid: str, attr: str = ' ',
            fixed_interval: float = 0.0) -> Tuple[VectF, VectF, int, int]:
    '''Returns the device boundary condition state TS'''
    if fixed_interval > 0.0:
        tmin, tmax, nbval = _dll_api.tsinterv()
        nbval = int((tmax - tmin)/fixed_interval + 1.499999)
        del tmin, tmax
    else:
        nbval = tsdevicelen(sid, attr)
        fixed_interval = 0.0
    if nbval > 0:
        return _dll_api.device_ts(sid, nbval, fixed_interval, attr)
    return (None, None, 0, 0)

#****f* sFunctions/hresults_block, hresults_block_xtra
# PURPOSE
#   Retrieves simulation results by block, at exact intermediate time steps,
#   including duplicate dates (ending of previous condition, and stating new)
# SYNTAX
#   * istat = hresults_block(time_step_index, get_incidents)
#   * step, date = hresults_block_xtra()
# ARGUMENTS
#   * int time_step_index: time step index to load, within [0, tslen()[
#   * bool get_incidents: if True, incidents are collected from ending block
# RESULT
#   * int istat: error status (0 if OK, >0 in case of reading error, -1 other error)
#   * int step: user time step the block belongs to (<0 if initial or intermediate
#     simulation step; >0 if user time step right boundary = end of interval)
#   * float date: simulation date
# EXAMPLE
#   for k in range(tslen()):
#       hresults_block(k)
#       step, date = hresults_block_xtra()
#       do something else
# REMARKS
#   * iterating over range(tslen()) allow to browse results by increasing order, including
#     end of previous conditions and start of new conditions happening at the same time.
#   * hresults_block_xtra returns information related to the previous hresults_block call.
# HISTORY
#   * 2025-02-25 (2.5.0) creation
#****
#****f* sFunctions/hstepcount, tslen, mslen, tsval, tsvals, all_ts, msval, tsvalbymts, tsinterv, wqtslen, refdate
# PURPOSE
#   * hstepcount: returns the number of user time steps
#   * tslen, mslen: return number of elements in the time serie
#   * tsval, msval: return the time series of results and measurements
#   * tsvals: returns a list of time series of results
#   * all_ts: returns all time series of a type as a matrix
#   * tsvalbymts: return the time series of results at measurement time steps
#     for a given element type, id and attribute
#   * tsinterv: number and boundaries of user time steps
#   * refdate: return date corresponding to the beginning of simulation
# SYNTAX
#   * hsc = hstepcount()
#   * len = tslen()
#   * len = mslen(typelt, id, attr)
#   * vec_tim, vec_val, len = tsval(typelt, id, attr, [interval])
#   * vec_tim, vec_mes, len = msval(typelt, id, attr, [interval])
#   * vec_tim, vec_val, len = tsvalbymts(typelt, id, attr)
#   * vec_tim, len, [(vec_val, len), ...] = tsvals(typelt, [id_ix, ...], attr, [interval])
#   * vec_tim, len, [(id, vec_val), ...] = tsvals(typelt, [id_ix, ...], attr, [interval], valid_only=True)
#   * matrix_val, vec_tim, vec_tim2 = all_ts(typelt, attr)
#   * tmin, tmax, len = tsinterv()
#   * len, tmax = wqtslen(typelt)
#   * sdate = refdate()
# ARGUMENTS
#   * int typelt: type of element
#   * string id: id of element
#   * list [id_ix, ...]: list of element id or list of element index (starting from 1)
#   * string attr: attribute (data or result) for which value is requested
#   * float interval (optional): if present, requests the time serie
#     at given fixed interval in seconds
# RESULT
#   * int hsc: number of user time steps
#   * int len: number of values for the time serie
#   * float32[] vec_tim: vector of instants in seconds
#   * float32[] vec_val: vector of simulated results at the instants vec_tim
#   * float32[] vec_mes: vector of measurements at the instants vec_tim
#   * float64[] vec_tim2: vector of instants in seconds with distinct values:
#     beginning of time step (identical to end of previous) are incremented by 0.2 s
#   * float32[item_index, time_index] matrix_val: matrix of simulated results
#   * float tmin and tmax: first (vec_tim[0]) and last (vec_tim[-1])
#     instants available in the result time series
#   * string sdate: date time at beginning of the simulation (iso format)
# REMARKS
#   * The time vector is identical for simulation results of all elements of all types,
#     and can be much larger than the number of (user) time steps (hstepcount() <= tslen()).
#   * two consecutive instants in the time vector for simulation results may
#     be identical at time step boundaries, change status instants etc. tsvals and all_ts
#     use and return a modified time vector where second identical value is shifted by 0.2 s.
#   * Each element may have a different measurement time vector form the others
#   * Measurements time series may have different begin and end dates from results
#   * Add 'sdate' in order to get absolute date time
#   * hstepcount requires version 2016 or higher of Piccolo/Ganessa dll
# HISTORY
#   * 12/12/2016 (1.5.1): bug fix when no simulation result available
#   * 15/03/2020 (2.1.1): added wqtslen; fix tsval for WQ ts
#   * 05/02/2023 (2.3.6): added tsvals for efficiently returning multiple ts
#   * 02/05/2023 (2.3.8): revert return values of tsvals (id, ts) allowing to build a dict
#   * 24/02/2025 (2.5.0): fix tsvals by shifting second same time value by 0.2 s;
#                         added all_ts (better results for both with dll version >= 20250225)
#   * 09/07/2025 (2.5.4): fix tsval and tsvals with WQ attribute; fix tsvals typing;
#                         allow tsvals to be called with a list of ids or a list of indices
#****
# Get functions - time series (results and measurements)
try:
    hstepcount = _dll_api.hstepcount
except AttributeError:
    _fn_undefined.append('hstepcount')
    hstepcount = _ret_errstat
tslen: Callable[[], int] = _dll_api.tslen
tsinterv = _dll_api.tsinterv
mslen: Callable[[ElemType, str, str], int] = _dll_api.mslen
ms: Callable[[ElemType, str, str, int, float], Tuple[ndarray, ndarray, int]] = _dll_api.ms
ts: Callable[[ElemType, str, str, int, float], Tuple[ndarray, ndarray, int]] = _dll_api.ts
try:
    wqtslen = _dll_api.wqtsinfo
except AttributeError:
    _fn_undefined.append('wqtslen')
    wqtslen = lambda x: (-1, _dll_api.tsinterv()[1])
try:
    hresults_block: Callable[[int, bool], int] = _dll_api.hresults_block
    hresults_block_xtra: Callable[[], Tuple[int, float]] = _dll_api.hresults_block_xtra
except AttributeError:
    _fn_undefined.extend(['hresults_block', 'hresults_block_xtra'])
    hresults_block = _ret_errstat
    hresults_block_xtra = _ret_errstat2

def tsval(typelt: ElemType, sid: str, sattr: str,
        fixed_interval: float = 0.0) -> Tuple[ndarray, ndarray, int]:
    '''Returns a simulated result TS at given element'''
    is_wq_attr = is_wq(sattr)
    if fixed_interval > 0.0:
        if is_wq_attr:
            tmin = 0.0
            _nbval, tmax = wqtslen(typelt)
        else:
            tmin, tmax, _nbval = _dll_api.tsinterv()
        nbval = int((tmax - tmin)/fixed_interval + 1.499999)
        del tmin, tmax
    else:
        fixed_interval = 0.0
        if is_wq_attr:
            nbval, tmax = wqtslen(typelt)
            if nbval < 0:
                fixed_interval = 60.
                nbval = int(tmax/fixed_interval + 1.499999)
        else:
            nbval = _dll_api.tslen()
    if nbval > 0:
        vt, vv, nb_returned = _dll_api.ts(typelt, sid, sattr, nbval, fixed_interval)
        if is_wq_attr and len(vt) > nb_returned:
            vt, vv = vt[:nb_returned], vv[:nb_returned]
        return vt, vv, nb_returned
    return (None, None, nbval)

def tsvals(typelt: ElemType, id_seq: Union[Sequence[str], Sequence[int]], sattr: str,
        fixed_interval: float = 0.0, valid_only: bool = False) -> Tuple[ndarray, int, List[Union[Tuple[ndarray, int], Tuple[str, ndarray]]]]:
    """Returns a list of simulated result TS at given elements - fetch by date for efficiency
    return value depends on "valid_only"
    """
    if not id_seq:
        return (None, None, 0)
    if isinstance(id_seq[0], str):
        # get item indices
        idx_item = nparray([getindex(typelt, kid) for kid in id_seq])
    elif isinstance(id_seq[0], int):
        # get item IDs
        idx_item = nparray(id_seq)
        id_seq = [getid(typelt, idx) for idx in id_seq]
    # get time vector from first item - nonzero returns a tuple
    if len(first_existing_idx := idx_item.nonzero()[0]) == 0:
        return None, 0, [(None, 0) for _ in id_seq]
    # force fixed interval when asking for WQ items
    if (is_wq_attr := is_wq(sattr)) and fixed_interval <= 0:
        fixed_interval = 300
    # better use tsval to get tvect and nbt since it depends on fixed_interval
    tvect, _vv, nbt = tsval(typelt, id_seq[first_existing_idx[0]], sattr, fixed_interval)
    tvect64 = nparray(tvect, dtype=float64)
    # Prepare result matrix
    all_val = npzeros((len(id_seq), nbt))
    # Piccolo / Ganessa_SIM index starts at 1
    idx_item -= 1
    browse_by_time = -1
    if fixed_interval == 0:
        browse_by_time = hresults_block(0, False)
        if not browse_by_time:
            # retrieve results block by block
            for kt in range(nbt):
                hresults_block(kt, False)
                all_flows = getall(typelt, sattr)
                all_val[:, kt] = all_flows[idx_item]
        else:
            # remove 0.01 and add 0.21 seconds to the pair of same time step value,
            #  in order to catch simulated value after potential discontinuity
            right_side = npdiff(tvect64, prepend=tvect64[1] - 1) == 0
            tvect64[right_side] += 0.21
            tvect64[nproll(right_side, -1)] -= 0.01
            tvect = nparray(tvect64, dtype=float32)
    if browse_by_time:
        # Iterate over time
        for kt, instant in enumerate(tvect64):
            browseH(hhmmssd(instant), is_wq_attr)
            all_flows = getall(typelt, sattr)
            all_val[:, kt] = all_flows[idx_item]

    idx_item += 1
    # get TS by element (the other dimension)
    # Return TS, length (None, 0 for nonexistent items) or (ID, TS) in valid_only mode
    if valid_only:
        ret_vals = [(sid, all_val[k, :]) for k, (idx, sid) in enumerate(zip(idx_item, id_seq)) if idx]
    else:
        ret_vals = [((all_val[k, :], nbt) if idx else (None, 0)) for k, idx in enumerate(idx_item)]
    return tvect, nbt, ret_vals

def all_ts(typelt: ElemType, sattr: str) -> Tuple[ndarray, ndarray, ndarray]:
    """Returns all simulated hydraulic TS for attribute 'sattr' at all elements. 
    fetch by date for efficiency; return as a (float32) matrix [<elements>, <time_steps>];
    other return parameters are original (float32) and modified (float64) time vector.
    try getting results by browsing result blocks if possible, otherwise browse by date
    """
    nb_items = _dll_api.nbobjects(typelt)
    nb_time = _dll_api.tslen()
    # convert time vect to float64 / float imprecision
    ts_matrix = npzeros((nb_items, nb_time), dtype=float32)
    if hresults_block(0, False) == 0:
        # retrieve results block by block
        status, tvect = set(), []
        for kt in range(nb_time):
            stat = hresults_block(kt, False)
            tvect.append(hresults_block_xtra()[1])
            status.add(stat)
            if stat == 0:
                ts_matrix[:, kt] = getall(typelt, sattr)
        if len(status) == 1 and status.pop() == 0:
            tvect = nparray(tvect, dtype=float32)
            return ts_matrix, tvect, nparray(tvect, dtype=float64)

    # Piccolo / Ganessa_SIM index starts at 1
    tvect = tsval(typelt, getid(typelt, 1), sattr)[0]
    tvect64 = nparray(tvect, dtype=float64)
    # browsing by block not available: browse by time
    # add 0.21 seconds to the next identical time step and remove 0.01 to the 1st identical
    right_side = npdiff(tvect64, prepend=tvect64[1] - 1) == 0
    tvect64[right_side] += 0.21
    tvect64[nproll(right_side, -1)] -= 0.01
    for kt, instant in enumerate(tvect64):
        # hhmmssd preserves the time increment 0.2, hhmmsss dont.
        browseH(hhmmssd(instant))
        ts_matrix[:, kt] = getall(typelt, sattr)
    return ts_matrix, tvect, tvect64

def msval(typelt: ElemType, sid: str, sattr: str,
        fixed_interval: float = 0.0) -> Tuple[ndarray, ndarray, int]:
    '''Returns a measurement TS at given element'''
    nbval = _dll_api.mslen(typelt, sid, sattr)
    if nbval <= 0:
        return (None, None, nbval)
    if fixed_interval > 0.0:
        t, v, nb = _dll_api.ms(typelt, sid, sattr, nbval)
        nbval = int((t[-1] - t[0])/fixed_interval + 1.499999)
        del t, v, nb
    else:
        fixed_interval = 0.0
    return _dll_api.ms(typelt, sid, sattr, nbval, fixed_interval)

def tsvalbymts(typelt: ElemType, sid: str, sattr: str) -> Tuple[ndarray, ndarray, int]:
    '''Returns a simulated result TS at given element at the same
    time as the measurement TS if any'''
    nbval = _dll_api.mslen(typelt if _dll_version < 20141205 else -typelt, sid, sattr)
    if nbval > 0:
        return _dll_api.ts(-typelt, sid, sattr, nbval, 0.0)
    return (None, None, nbval)

def refdate() -> str:
    '''Returns Reference date for the simulation'''
    sdate, slen = _dll_api.refdate()
    return tostr(sdate[0:slen]) if slen > 0 else ''

#****f* sFunctions/msmooth
# PURPOSE
#   Defines the smoothing time width for time series of measurements
# SYNTAX
#   msmooth(twidth)
# ARGUMENTS
#   twidth: characteristic time window for smoothing, in seconds
# REMARKS
#   * The smoothing algorithm is a convolution with exp(-(t/twidth)^2).
#   * Best results are expected when twidth is in the order of magnitude
#     or larger than the sampling interval.
#   * call msmooth(0.0) in order to cancel smoothing.
#****
def msmooth(twidth: float) -> None:
    '''Sets the smoothing time width for measurement TS'''
    # MESURE DT-LISSAGE xxx
    sval = str(twidth) if isinstance(twidth, numbers.Number) else twidth
    MES = M.MES
    _dll_api.gencmd(MES.ROOT, MES.SMOOTH, M.NONE, sval)
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _dll_api.commit(0)

#****f* sFunctions/defcalind, getcalind
# PURPOSE
#   Compute and return calibration indicators
# SYNTAX
#   * defcalind(lnk_threshold, nod_threshold, rsv_threshold)
#   * val, ival = getcalind(typelt, id_elt[, rank])
# ARGUMENTS
#   * xxx_threshold : thresholds for computing indicators
#   * int typelt: type of element
#   * string id_elt: id of element
#   * int rank: rank of the calibration indicator
# RESULT
#   val:  percentage of values below threshold
#   ival: indicator rank, from 1 (best) to 4 (worse) (-1 if not defined)
# REMARK
#   * defcalind actually compute all indicators; getcalind returns them.
#   * 2.3.3 (220909) optional argument rank added - return default indicator if not set;
#     older dlls return 0, -1 when rank > 1
#   * 2.5.2 (250407) fix _dll_api.dll_version() undefined with dll jan-2022
#****
def defcalind(br_threshold=0.1, no_threshold=0.2, rsv_threshold=0.5):
    '''Define calibration parameters'''
    _dll_api.defcalind(br_threshold, no_threshold, rsv_threshold)

def getcalind(typelt : ElemType, id_elt : str, rank=1) -> Tuple[float, int]:
    """Returns calibration indicator"""
    if dll_version() < 20220908:
        if rank != 1:
            return (0.0, -1)
        getter = {LINK: _dll_api.branchattr, NODE: _dll_api.nodeattr, TANK: _dll_api.rsvattr}
        cal = getter[typelt](id_elt, "RC")
        ind = int(0.01 + getter[typelt](id_elt, "IC"))
    else:
        try:
            cal, ind = _dll_api.getcalind(typelt, id_elt, rank)
        except Exception:
            cal, ind =  _dll_api.getcalind(typelt, id_elt) if rank == 1 else (0, -1)
    return cal, ind

#****f* sFunctions/getallminmax
# PURPOSE
#   * getallminmax returns the min, max, average and mindate, maxdate
#     for all objects of the given type
# SYNTAX
#   * vec_min, vec_max, vec_avg, vec_tmin, vec_tmax = getallminmax(typelt, attr)
# ARGUMENTS
#   * int typelt: type of element (LINK, NODE, TANK)
#   * string attr: attribute (result) for which value is requested
# RESULT
#   * float[] vec_min, vec_max, vec_avg: min, max and avg values for all elements
#   * float[] vec_tmin, vec_tmax: vector of instants where the min, max value is reached
#****
def getallminmax(typelt: ElemType, sattr: str) -> Tuple[VectF, VectF, VectF, VectF, VectF]:
    '''Returns min/max/avg results for given attribute for all elements at once'''
    nbval = _dll_api.nbobjects(typelt)
    if nbval > 0:
        return _dll_api.getallminmax(typelt, sattr, nbval)
    return (None, None, None, None, None)

#****k* sIterators/getMinMax
# PURPOSE
#   Returns the id, min, max, avg value reached by the attribute for each object
#   of the given type or selection in turn
# SYNTAX
#   for id, vmin, vmax, vavg in getMinMax(typelt or selection, sattr):
# ARGUMENT
#   * int typelt: type element constants LINK, NODE, TANK
#   * string selection: name of a selection
#   * string attr: attribute (result) for which value is requested
# RESULT
#   id, vmin, vmax, vavg: str element id, minimum, maximum and average values
#   for the attribute over the simulation
# HISTORY
#  * 181220: added len method
#****
class getMinMax:
    '''Iterator returning min/max/avg for elements of the selection
    for a given attribute'''
    def __init__(self, typelt_sel: Union[ElemType, str], sattr: str):
        self.attr = sattr
        if isinstance(typelt_sel, numbers.Number):
            self.type = typelt_sel
            self.nbmax = _dll_api.nbobjects(self.type)
            items = range(1, self.nbmax + 1)
            self.select = list(items) if PY3 else items
        elif is_text(typelt_sel):
            self.nbmax, self.type = selectlen(typelt_sel)
            if self.nbmax > 0:
                self.select = _select(self.nbmax)
        else:
            raise TypeError
        nbelem = _dll_api.nbobjects(self.type)
        if self.nbmax > 0:
            self.vmin, self.vmax, self.avg, tmin, tmax = _dll_api.getallminmax(self.type, sattr, nbelem)
            del tmin, tmax
        self.index = 0
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, float, float, float]:
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.vmin, self.vmax, self.avg, self.select
                self.nbmax = 0
            raise StopIteration
        # returns fortran index (from 1)
        numelt = self.select[self.index]
        (elem, ls) = _dll_api.getid(self.type, numelt)
        # np.array index
        numelt -= 1
        vmin, vmax, vmoy = self.vmin[numelt], self.vmax[numelt], self.avg[numelt]
        self.index += 1
        return (tostr(elem[0:ls]), vmin, vmax, vmoy)
    def __len__(self) -> int:
        return self.nbmax
    next = __next__
    len = __len__
#****f* sFunctions/inv_summary, inv_varcount, inv_variable
# SYNTAX
#   * iter, iter100, fobjmin, fobj100, fobj0, flambda = inv_summary()
#   * vcount = inv_varcount(stype)
#   * num, val, delta = inv_variable(stype, idx)
# ARGUMENTS
#   * str stype: type of variable (ZN, PR, K, CS)
#   * int idx: index of variable
# RESULT
#   * int iter: number of iterations
#   * int iter100: number of iterations required to get 1.01 * min
#   * float fobjmin: minimum value of misfit function
#   * float fobj100: misfit function at iteration iter100
#   * float fobj0: misfit function before fitting
#   * float flambda: Levenberg-Marquardt multiplier
#   * int vcount: number of variables of the type
#   * int num: element (link or node or tank) index, starting at 1
#   * float val: value of variable of type stype and rank idx
#   * float delta: variation of variable (final - initial value)
# REMARK
#   * inv_summary requires version 2016 (160309) or higher of Piccolo/Ganessa dll
#   * inv_varcount and inv_variable require version 2022 (220924) or higher
# HISTORY
#   * new in 1.3.4
#   * 2.3.3: added inv_varcount and inv_variable
#****
try:
    inv_summary: Callable[[], Tuple[int, int, float, float, float, float]] = _dll_api.inv_summary
except AttributeError:
    _fn_undefined.append('inv_summary')
    inv_summary = _ret_errstat

try:
    inv_varcount: Callable[[str], int] = _dll_api.inv_var_type_count
    inv_variable: Callable[[str, int], Tuple[int, float, float]] = _dll_api.inv_variable
except AttributeError:
    _fn_undefined.append('inv_varcount')
    _fn_undefined.append('inv_variable')
    inv_varcount = _ret_errstat
    inv_variable = lambda x, y: -1, 0, 0

#****f* sFunctions/stat_quantiles, stat_duration
# PURPOSE
#   stat_quantiles and stat_duration returns stat info associated with result TS
#   of a given attribute for all elements in a selection.
#   raw_stat_quantiles and raw_stat_duration are pass_thru versions where
#   the selection is provided as its type, buffer and length
# SYNTAX
#   * quantiles = stat_quantiles(sel, attr, qtl)
#   * duration = stat_duration(sel, attr, sop, threshold)
#   * quantiles = raw_stat_quantiles(typelt, attr, qtl, bufsel, nb)
#   * duration = raw_stat_duration(typelt, attr, sop, threshold, bufsel, nb)
# ARGUMENTS
#   * string sel: selection of elements for which stats are expected
#   * string attr: attribute over which the stat is computed
#   * float iterable qtl: quantiles to be computed (0 <= qtl[i] <= 1)
#   * string sop: comparison operator '<' or '>'
#   * float threshold: comparison threshold (expressed in attribute unit)
#   * int typelt: selection object type
#   * int nb: selection count
#   * int[] bufsel: selection vector of indices
# RESULT
#   * float[:,:] quantiles: 2-dim array of quantiles - shape (#sel, #qtl).
#     quantiles[i] is the array of quantiles for the element in position i;
#     quantiles[:, k] is the array of quantile qtl[k] for all elements
#   * float[:] duration: array of cumulated duration (att sop threshold) - shape (#sel, ).
#   The functions return an empty list if the selection or qtl is empty .
# EXAMPLE
#   * cd = stat_duration('branch (d > 500) end', 'V', '>', 0.7)
#   * qtl = stat_quantiles('branch (d > 500) end', 'V', [0.5, 0.95, 1.0])
#     will return median, 95% quantile and maximum for velocity.
# REMARK
#   Allowed attributes are:
#   * links: flow (Q), velocity (V), head loss (PC / HL), gradient (GR)
#   * nodes: Head (HH / CH), pressure (P) and pipe pressure (PP)
#   * tanks: level (NC / CL), height (H), volume (CV / VC), volume percentage (V%),
#     flow (Q), filling flow (IQ / QR), draught flow (OQ / QV),
#   * all: water quality attributes T, C0 ... C9.
#   See also: getallminmax, getMinMax, Dynamic_stats
# HISTORY
#   * new in 1.5.0 (161124) - should be compatible with 2016b kernel.
#   * 1.8.0 (170908): added raw_stat_quantiles and raw_stat_duration
#****

try:
    _tmp_ = _dll_api.stat_quantiles
except AttributeError:
    _fn_undefined.append('stat_quantiles')
    _fn_undefined.append('stat_duration')
    stat_quantiles = _ret_errstat
    stat_duration = _ret_errstat
else:
    del _tmp_
    def stat_squantiles(sel, attr, qtl):
        '''Returns quantiles results for given selection, attribute'''
        if len(qtl) > 0:
            nb, _typelt = selectlen(sel)
            # vqtl = numpy.array(qtl).astype(numpy.float32, order='F')
            if nb > 0:
                ret = _dll_api.stat_squantiles(sel, attr, nb, qtl)
                return ret
        return []

    def stat_quantiles(sel, attr, qtl):
        '''Returns quantiles results for given selection, attribute'''
        if len(qtl) > 0:
            nb, typelt = selectlen(sel)
            if nb > 0:
                bufsel = _select(nb)
                ret = _dll_api.stat_quantiles(typelt, attr, qtl, bufsel, nb)
                # vqtl = numpy.array(qtl).astype(numpy.float32, order='F')
                return ret
        return []

    def stat_sduration(sel, attr, sop, threshold):
        '''Returns duration for which attribute op thereshod for given selection'''
        nb, _typelt = selectlen(sel)
        ret = _dll_api.stat_sduration(sel, attr, sop, threshold, nb) if nb > 0 else []
        return ret

    def stat_duration(sel, attr, sop, threshold):
        '''Returns duration for which attribute op thereshod for given selection'''
        nb, typelt = selectlen(sel)
        if nb > 0:
            bufsel = _select(nb)
            ret = _dll_api.stat_duration(typelt, attr, sop, threshold, bufsel, nb)
            return ret
        return []

    raw_stat_duration = _dll_api.stat_duration

#****k* sIterators/Dynamic_Stats
# PURPOSE
#   Iterator which returns stat info associated with result TS
#   of a given attribute for all elements in a selection in turn.
# SYNTAX
#   for id, retval in Dynamic_Stats(sel, attr [, quantile= qtl] [, duration= (sop, threshold)]):
# ARGUMENT
#   * string sel: selection
#   * string attr: attribute
#   * float iterable qtl: quantiles to be computed (0 <= qtl[i] <= 1)
#   * string sop: comparison operator '<' or '>'
#   * float threshold: comparison threshold (expressed in attribute unit)
# RESULT
#   Returns the id and type of each element in the selection in turn:
#   * string id: id of the next element in the selection
#   * retval: result of the requested stat.
#   The return value depends on the input parameters:
#   * if duration= (sop, threshold) is present, returns the cumulated duration for which attribute (sop) threshold.
#   * if not, if quantile= qtl is present, returns a numpy array of the quantiles for the element id.
#   * without duration and quantile keywords, the return value is [minval, maxval, avg] over the result TS.
# REMARK
#   See also getallminmax, stat_quantiles, stat_duration, getMinMax
# HISTORY
#   * new in 1.5.0 (161124) - should be compatible with 2016b kernel.
#   * 181220: added __len__
#****
# Iterators for browsing model elements
class Dynamic_Stats:
    '''Iterator which returns stat info associated with result TS'''
    def __init__(self, sel, attr, quantiles=None, duration=None):
        nb, typ = selectlen(sel)
        self.nbmax, self.type = nb, typ
        if self.nbmax > 0:
            sbuf = _select(self.nbmax)
            self.select = sbuf
            if duration is not None:
                sop, threshold = duration
                self.values = _dll_api.stat_duration(typ, attr, sop, threshold, sbuf, nb)
            elif quantiles is not None:
                self.values = _dll_api.stat_quantiles(typ, attr, quantiles, sbuf, nb)
            else:
                nobj = _dll_api.nbobjects(typ)
                vmin, vmax, avg, tmin, tmax = _dll_api.getallminmax(typ, attr, nobj)
                del tmin, tmax
                vbuf = sbuf - 1
                self.values = nparray([vmin[vbuf], vmax[vbuf], avg[vbuf]]).transpose()
        self.index = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.select
                del self.values
                self.nbmax = 0
            raise StopIteration
        numelt = self.select[self.index]
        elem, ls = _dll_api.getid(self.type, numelt)
        value = self.values[self.index]
        self.index += 1
        return (tostr(elem[0:ls]), value)
    def __len__(self):
        return self.nbmax
    next = __next__
    len = __len__

#****k* sIterators/WQSources
# PURPOSE
#   Provide access to the sequence of source items
# SYNTAX
#   for node, code, attr, tvec, cvec, nvec in WQSources(node=None):
# ARGUMENTS
#   string node: specific node to look for, or '' for all nodes.
# RESULT
#   Returns each source boundary condition in turn:
#   * string node: node ID
#   * string code: code associated to the source (or '' if forcing)
#   * string attr: WQ attribute (T, C0 ... C9, $0 ... $9, $A ...$ Z)
#   * float tvec[], cvec[]: time and quantity vector (time serie)
#   * int nvec : TS size
#   If node is given (non blank string):
#   * if it exists, data will be returned for this node only
#   * if the node does not exists, the return sequence is empty
#   If the node is not given, all WQ data will be returned
# REMARK
#   * WQSources requires version 2020 (200306) or higher of Piccolo/Ganessa_Sim dll
# HISTORY
#   * new in 2.1.1
#****
try:
    _wq_source_data_init = _dll_api.wqdatainit
except AttributeError:
    _fn_undefined.append('WQSources')
    _wq_source_data_init = _ret_errstat

class WQSources:
    '''Iterator returning WQ source data'''
    def __init__(self, node=None):
        '''inits the iterator and returns the longest TS'''
        node = node if node and is_text(node) else ''
        self.max_ts_size = _wq_source_data_init(winstr(node))
        self.exhausted = self.max_ts_size <= 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.exhausted:
            raise StopIteration
        iret, nvec, tvec, cvec, node, code, attr, ln, lc = _dll_api.wqdata(self.max_ts_size)
        if nvec <= 0:
            raise StopIteration
        self.exhausted = iret < 0
        return tostr(node[:ln]), tostr(code[:lc]), tostr(attr), tvec[:nvec], cvec[:nvec], nvec
    next = __next__

#****k* sIterators/Controls_
# PURPOSE
#   Provide access to the controls on pumps and manual valves
# SYNTAX
#   for control_id, control_data in Controls([which]):
# ARGUMENTS
#   str which: "GU" or "GROUPE-CONTROLE" for getting control entities;
#   leave blank for valves and pumps
# RESULT
#   Returns each control information in turn - control_id is a ControlId NamedTuple:
#   * int mtype: type of master (controller element) as one of LINK, NODE or TANK.
#   * str master: master ID
#   * str slave: controlled link ID (pump or manual valve or control entity)
#   * int priority: priority of the control
#   * int initial_state: initial slave state when controller position is between start and stop threshold
#   control_data = ControlData NamedTuple:
#   * str period: name of the time period on which the control operates; possibly ""
#   * bool active: True if the control is active for the given period
#   * array start: array of start thresholds
#   * array stop: array of stop thresholds
#   * int nbval: number of threshold values
#   * float delay: delay after the condition is met for changing
# REMARKS
#   * Controls requires version 2022 (220821) or higher of Piccolo/Ganessa_Sim dll
#   * nbval is 1 for valves and pumps with a single unit; otherwise it is equal to the number of pump units.
#     With control entities, it is the number of combination minus one.
#   * multiple controls can be set for a given ControlId (pair of master and slave), on several periods
#     (time intervals); null period is the default value
# HISTORY
#   * new in 2.3.2 (220820)
#****
try:
    _control_init = _dll_api.control_init
except AttributeError:
    _fn_undefined.append('Controls')
    _control_init = _ret_errstat

class ControlId(NamedTuple):
    """Entity for describing Controls"""
    mtype: ElemType
    master: str
    slave: str
    priority: int
    initial_state: int

class ControlData(NamedTuple):
    """Data associated with a ControlId"""
    period: str
    active: bool
    start: VectF
    stop: VectF
    nbval: int
    delay: float

class Controls:
    """Iterator for returning controls"""
    def __init__(self, item_type : str = ""):
        """Inits the controls API"""
        self.controls_count = _control_init(item_type)
        self.type = item_type
        self.index = 0
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[ElemType, str, str, int, int, str, bool, VectF, VectF, int, float, bool]:
        if self.index >= self.controls_count:
            raise StopIteration
        master, mtype, slave, szm, szs, state0, delay, prio, nbs = _dll_api.control_idx(self.index)
        self.index += 1
        if nbs <= 0:
            raise StopIteration
        master, slave = tostr(master[:szm]), tostr(slave[:szs])
        period, szp, active, nbval, vstart, vstop = _dll_api.control_data(nbs)
        return (ControlId(mtype, master, slave, prio, state0),
                ControlData(tostr(period[:szp]), active, vstart.astype(float64).round(4),
                            vstop.astype(float64).round(4), nbval, delay))
    def __len__(self) -> int:
        return self.controls_count


#****k* sIterators/ControlEntities
# PURPOSE
#   Provide access to the control entities
# SYNTAX
#   for name, item_names, descr_combs, pump_count, combis in ControlEntities():
# ARGUMENTS
#   none
# RESULT
#   Returns each control entity information in turn:
#   * str name: name of the control entity (can be used for dynamic data or controls)
#   * List[str] item_names: names of the links forming the control entity. Pumps are at the end.
#   * List[str] descr_combs: optional description of the combinations
#   * int pump_count: number of pumps in the control entity
#   * ndarray combis[comb_count, fitting_count + pump_count]: fitting settings per combination
# REMARKS
#   * ControlEntities requires version 2022 (220824) or higher of Piccolo/Ganessa_Sim dll
#   * #items in the control entity is len(item_names); #combinations is len(descr_combs)
#   * Pumps have 2 settings: number of pumps running and speed, all other have one.
#   * The setting for any fitting and combination is combis[cmb_idx, fitting_idx]. For pumps this
#     returns the status of the pump; the speed is at combis[cmb_idx, fitting_count + pump_idx]
#   * Pump speed is returned as -1 for fixed speed pumps
# EXAMPLE
#   For a control entity comprising 1 valve and 2 pumps and 4 combinations, the iterator will return
#   ('ENTITY_NAME', ['VALVE_NAME', 'PUMP1', 'PUMP2'], ['Descr1', 'Descr2', 'Descr3', 'Descr4'], 2, combis)
#   where shape(combis) is (4, 5):
#   * combis(x, 0): status (0 / 1) for the valve
#   * combis(x, 1): status (0 / 1) for pump#1
#   * combis(x, 2): status (0 / 1) for pump#2
#   * combis(x, 3): speed for pump#1
#   * combis(x, 4): speed for pump#2
#
# HISTORY
#   * 2.3.2  (220824) creation
#   * 2.3.11 (231114) added __len__
#****
try:
    _control_entity_init = _dll_api.control_entity_init
except AttributeError:
    _fn_undefined.append('ControlEntities')
    _control_entity_init = _ret_errstat

class ControlEntities:
    """Iterator for returning control entities"""
    def __init__(self):
        """Inits the controls API"""
        self.control_entities_count = _control_entity_init()
        self.index = 0
    def __iter__(self):
        return self
    def __next__(self) -> Tuple[str, List[str], List[str], int, ndarray]:
        if self.index >= self.control_entities_count:
            raise StopIteration
        # get name of control entity and counts
        name, szname, nbapps, pump_count, nbcomb = _dll_api.control_entity_idx(self.index)
        self.index += 1
        if nbapps <= 0:
            raise StopIteration
        name = tostr(name[:szname])
        # get names of combinations
        descr_combs = [_dll_api.control_entity_desc(k) for k in range(nbcomb)]
        descr_combs = [tostr(desc[:sz]).strip() for desc, sz in descr_combs]
        # get link indices and combination settings
        kid_apps, combis = _dll_api.control_entity_data(nbapps, nbcomb, nbapps + pump_count)
        item_names = [getid(LINK, k) for k in kid_apps]
        return name, item_names, descr_combs, pump_count, combis
    next = __next__

#****k* sIterators/IPSVariable
# PURPOSE
#   Provide access to the fitted values after IPS
# SYNTAX
#   for sid, val, delta in IPSVariable(stype):
# 
#   str stype: IPS variable category (ZN, PR, K, CS)
# RESULTARGUMENTS
#   Returns each variable identifier and value:
#   * str sid: node (ZN, CS) or link (K) or tank (PR) ID
#   * float val: value
#   * float delta: variation of variable after IPS
# REMARK
#   * IPSVariable requires version 2022 (220924) or higher of Piccolo/Ganessa_Sim dll
# HISTORY
#   * new in 2.3.3
#****
class IPSVariable:
    '''Iterator returning IPS results'''
    vartype = dict(K=LINK, PR=TANK, ZR=TANK)
    def __init__(self, stype="PR"):
        '''inits the iterator '''
        self.stype = stype.upper()
        self.var_count = inv_varcount(self.stype)
        self.ptype = self.vartype.get(self.stype, NODE)
        self.index = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.index >= self.var_count:
            raise StopIteration
        num, val, delta = inv_variable(self.stype, self.index)
        self.index += 1
        if num <= 0:
            raise StopIteration
        sid, ls = _dll_api.getid(self.ptype, num)
        return tostr(sid[:ls]), val, delta
    next = __next__

#****f* sFunctions/demand_pressure, code_pressure
# PURPOSE
#   * demand_pressure returns current demand-dependant parameters
#   * code_pressure returns code dependance when pressure dependant demand is active
# SYNTAX
#   * state, law_index, exponent, p0, p1, babove, bdepth, law_name = demand_pressure()
#   * active = code_pressure(code)
# ARGUMENTS
#   * str code: code to be examined
# RESULT
#   * int state: 0 if not active / 1 active for all demand codes / -1 active for some
#   * int law_index: 1 .. 5 (1=EXP, 2=ELL, 3=SQRT, 4=LIN, 5=POW)
#   * float exponent: exponent if law is of power type (3 .. 5)
#   * float p0, p1: cancellation and fixed pressure thresholds
#   * bool babove: if true, demand / pression equation holds when P > p1
#   * bool bdepth: if True, node depth is taken into account (pipe pressure is used)
#   * str law_name: equation demnd = f(P)
#     (EXPONENTIELLE, ELLOPTIQUE, RACINE-CARREE, LINEAIRE, PUISSANCE)
#     (EXPONENTIAL, ELLPTIC, SQUARE-ROOT, LINEAR, POWER)
#   * bool active: True if demand associated with code is pressure dependant when pdd active
# HISTORY
#   2025.02.27 (2.5.0): creation
#****
try:
    def demand_pressure() -> Tuple[int, int, float, float, float, bool, bool, str]:
        """returns state, law_index, exponent, p0, p1, babove, bdepth, law_name"""
        ret =  _dll_api.demand_pressure()
        return *ret[0:-1], tostr(ret[-1])
    code_pressure: Callable[[str], bool] = _dll_api.code_pressure
except AttributeError:
    _fn_undefined.append("demand_pressure")
    def demand_pressure():
        """dummy function for missing API"""
        return 0, 0, 1.0, 0.0, 10.0, False, False, ""
    code_pressure = _ret_errstat
