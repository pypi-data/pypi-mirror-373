'''
Created on 8 sept. 2017

Functions specific to the thermo-hydraulic (Picalor) simulation

@author: Jarrige_Pi
'''
from typing import Callable, List
import numpy as np
from ganessa.th import _dll_api
from ganessa.core import (M, DICT, SIMERR,
            _checkExceptions, _fn_undefined, _ret_errstat)

#****f* tFunctions/solveTH
# PURPOSE
#   Runs the thermo-hydraulic simulation
# SYNTAX
#   istat = solveTH([silent=False [, iverb=-1 [, retry=True]]])
# ARGUMENTS
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). If not set, leaves 'iverb' unchanged.
#   * bool retry: if set to True, the simulation is run again if it fails
#     because of isolated nodes. Optional - defaults to False
# RESULT
#   int istat: error status (0 if OK)
# HISTORY
#   * added 2017.05.15 - version 1.7.5
#   * changed 2019.08.19 - version 2.0.7 - improved error check
#****

def solveTH(silent: bool = False, iverb: int = -1, retry: bool = True) -> int:
    '''Runs a thermo-hydraulic steady-state simulation'''
    # SIM IVERB
    if silent:
        sverb = '-9'
    elif iverb == -1:
        sverb = '-1'
    else: sverb = str(iverb)
    SIM = M.SIM
    _dll_api.gencmd(SIM.ROOT, SIM.IVER, M.NONE, sverb)
    #  EXEC
    _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE)
    istat = _dll_api.commit(0)
    if retry:
        bsimerr, nsimerr = divmod(abs(istat), SIMERR.SIMERR)
        if bsimerr and nsimerr == SIMERR.ISOL:
            _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE)
            istat = _dll_api.commit(0)
    _checkExceptions(32, istat, 'Error running thermo-hydraulic simulation')
    return istat

VectF = List[float]
try:
    setdensity: Callable[[int, VectF, VectF], int] = _dll_api.setdensity
except AttributeError:
    _fn_undefined.append('setdensity')
    setdensity = _ret_errstat

#****g* ganessa.th/tFunctions
# DESCRIPTION
#   Functions available to ganessa.th ONLY
#****
#****f* tFunctions/symmetric_node
# SYNTAX
#   ids = symmetric_node(sid)
# ARGUMENTS
#   string sid: node ID for which the symmetric (counterpart node on
#   the other circuit) is looked for
# RESULT
#   * string sid: id of the counterpart node. '' if not found.
# REMARKS
#   * always returns '' with Piccolo/Ganessa_SIM
#   * the counterpart can be found only if the hot and cold circuits are almost symmetric
#   * symmetric_node requires version 2016B (160511) or higher of Picalor/Ganessa TH dll
# HISTORY
#   new in 1.3.6
#****

try:
    _symmetric_node = _dll_api.symmetric_node
except AttributeError:
    _fn_undefined.append('symmetric_node')
    def symmetric_node(sid: str) -> str:
        return ""
else:
    del _symmetric_node
    def symmetric_node(sid: str) -> str:
        '''Returns node symmetric to the given one, if any'''
        sids, ln = _dll_api.symmetric_node(sid)
        return sids[0:ln]
