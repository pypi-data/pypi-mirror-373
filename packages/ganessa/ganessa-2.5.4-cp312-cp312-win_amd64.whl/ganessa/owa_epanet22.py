"""This file was built from toolkit.py from owa-epanet 2.2.3
in order to create EN_XXX constants and ENxxx functions similar to EpanetTools
Requirement: owa-epanet package 2.2.3 (or above ?)

 2023-08-08: Created by Dr Pierre Antoine Jarrige
 2023-09-19: added ENcreateproject and ENdeleteproject for multiprocessing
 2023-09-21: added default_project for either creating or replacing _default_project
"""

from importlib.metadata import version
__version__ = version("owa-epanet")
del version

from epanet.toolkit import *
from epanet.toolkit import _toolkit

# create aliases for constants
EN_MAXID = MAXID
EN_MAXMSG = MAXMSG
EN_ELEVATION = ELEVATION
EN_BASEDEMAND = BASEDEMAND
EN_PATTERN = PATTERN
EN_EMITTER = EMITTER
EN_INITQUAL = INITQUAL
EN_SOURCEQUAL = SOURCEQUAL
EN_SOURCEPAT = SOURCEPAT
EN_SOURCETYPE = SOURCETYPE
EN_TANKLEVEL = TANKLEVEL
EN_DEMAND = DEMAND
EN_HEAD = HEAD
EN_PRESSURE = PRESSURE
EN_QUALITY = QUALITY
EN_SOURCEMASS = SOURCEMASS
EN_INITVOLUME = INITVOLUME
EN_MIXMODEL = MIXMODEL
EN_MIXZONEVOL = MIXZONEVOL
EN_TANKDIAM = TANKDIAM
EN_MINVOLUME = MINVOLUME
EN_VOLCURVE = VOLCURVE
EN_MINLEVEL = MINLEVEL
EN_MAXLEVEL = MAXLEVEL
EN_MIXFRACTION = MIXFRACTION
EN_TANK_KBULK = TANK_KBULK
EN_TANKVOLUME = TANKVOLUME
EN_MAXVOLUME = MAXVOLUME
EN_CANOVERFLOW = CANOVERFLOW
EN_DEMANDDEFICIT = DEMANDDEFICIT
EN_NODE_INCONTROL = NODE_INCONTROL
EN_DIAMETER = DIAMETER
EN_LENGTH = LENGTH
EN_ROUGHNESS = ROUGHNESS
EN_MINORLOSS = MINORLOSS
EN_INITSTATUS = INITSTATUS
EN_INITSETTING = INITSETTING
EN_KBULK = KBULK
EN_KWALL = KWALL
EN_FLOW = FLOW
EN_VELOCITY = VELOCITY
EN_HEADLOSS = HEADLOSS
EN_STATUS = STATUS
EN_SETTING = SETTING
EN_ENERGY = ENERGY
EN_LINKQUAL = LINKQUAL
EN_LINKPATTERN = LINKPATTERN
EN_PUMP_STATE = PUMP_STATE
EN_PUMP_EFFIC = PUMP_EFFIC
EN_PUMP_POWER = PUMP_POWER
EN_PUMP_HCURVE = PUMP_HCURVE
EN_PUMP_ECURVE = PUMP_ECURVE
EN_PUMP_ECOST = PUMP_ECOST
EN_PUMP_EPAT = PUMP_EPAT
EN_LINK_INCONTROL = LINK_INCONTROL
EN_GPV_CURVE = GPV_CURVE
EN_DURATION = DURATION
EN_HYDSTEP = HYDSTEP
EN_QUALSTEP = QUALSTEP
EN_PATTERNSTEP = PATTERNSTEP
EN_PATTERNSTART = PATTERNSTART
EN_REPORTSTEP = REPORTSTEP
EN_REPORTSTART = REPORTSTART
EN_RULESTEP = RULESTEP
EN_STATISTIC = STATISTIC
EN_PERIODS = PERIODS
EN_STARTTIME = STARTTIME
EN_HTIME = HTIME
EN_QTIME = QTIME
EN_HALTFLAG = HALTFLAG
EN_NEXTEVENT = NEXTEVENT
EN_NEXTEVENTTANK = NEXTEVENTTANK
EN_ITERATIONS = ITERATIONS
EN_RELATIVEERROR = RELATIVEERROR
EN_MAXHEADERROR = MAXHEADERROR
EN_MAXFLOWCHANGE = MAXFLOWCHANGE
EN_MASSBALANCE = MASSBALANCE
EN_DEFICIENTNODES = DEFICIENTNODES
EN_DEMANDREDUCTION = DEMANDREDUCTION
EN_NODE = NODE
EN_LINK = LINK
EN_TIMEPAT = TIMEPAT
EN_CURVE = CURVE
EN_CONTROL = CONTROL
EN_RULE = RULE
EN_NODECOUNT = NODECOUNT
EN_TANKCOUNT = TANKCOUNT
EN_LINKCOUNT = LINKCOUNT
EN_PATCOUNT = PATCOUNT
EN_CURVECOUNT = CURVECOUNT
EN_CONTROLCOUNT = CONTROLCOUNT
EN_RULECOUNT = RULECOUNT
EN_JUNCTION = JUNCTION
EN_RESERVOIR = RESERVOIR
EN_TANK = TANK
EN_CVPIPE = CVPIPE
EN_PIPE = PIPE
EN_PUMP = PUMP
EN_PRV = PRV
EN_PSV = PSV
EN_PBV = PBV
EN_FCV = FCV
EN_TCV = TCV
EN_GPV = GPV
EN_CLOSED = CLOSED
EN_OPEN = OPEN
EN_PUMP_XHEAD = PUMP_XHEAD
EN_PUMP_CLOSED = PUMP_CLOSED
EN_PUMP_OPEN = PUMP_OPEN
EN_PUMP_XFLOW = PUMP_XFLOW
EN_NONE = NONE
EN_CHEM = CHEM
EN_AGE = AGE
EN_TRACE = TRACE
EN_CONCEN = CONCEN
EN_MASS = MASS
EN_SETPOINT = SETPOINT
EN_FLOWPACED = FLOWPACED
EN_HW = HW
EN_DW = DW
EN_CM = CM
EN_CFS = CFS
EN_GPM = GPM
EN_MGD = MGD
EN_IMGD = IMGD
EN_AFD = AFD
EN_LPS = LPS
EN_LPM = LPM
EN_MLD = MLD
EN_CMH = CMH
EN_CMD = CMD
EN_DDA = DDA
EN_PDA = PDA
EN_TRIALS = TRIALS
EN_ACCURACY = ACCURACY
EN_TOLERANCE = TOLERANCE
EN_EMITEXPON = EMITEXPON
EN_DEMANDMULT = DEMANDMULT
EN_HEADERROR = HEADERROR
EN_FLOWCHANGE = FLOWCHANGE
EN_HEADLOSSFORM = HEADLOSSFORM
EN_GLOBALEFFIC = GLOBALEFFIC
EN_GLOBALPRICE = GLOBALPRICE
EN_GLOBALPATTERN = GLOBALPATTERN
EN_DEMANDCHARGE = DEMANDCHARGE
EN_SP_GRAVITY = SP_GRAVITY
EN_SP_VISCOS = SP_VISCOS
EN_UNBALANCED = UNBALANCED
EN_CHECKFREQ = CHECKFREQ
EN_MAXCHECK = MAXCHECK
EN_DAMPLIMIT = DAMPLIMIT
EN_SP_DIFFUS = SP_DIFFUS
EN_BULKORDER = BULKORDER
EN_WALLORDER = WALLORDER
EN_TANKORDER = TANKORDER
EN_CONCENLIMIT = CONCENLIMIT
EN_LOWLEVEL = LOWLEVEL
EN_HILEVEL = HILEVEL
EN_TIMER = TIMER
EN_TIMEOFDAY = TIMEOFDAY
EN_SERIES = SERIES
EN_AVERAGE = AVERAGE
EN_MINIMUM = MINIMUM
EN_MAXIMUM = MAXIMUM
EN_RANGE = RANGE
EN_MIX1 = MIX1
EN_MIX2 = MIX2
EN_FIFO = FIFO
EN_LIFO = LIFO
EN_NOSAVE = NOSAVE
EN_SAVE = SAVE
EN_INITFLOW = INITFLOW
EN_SAVE_AND_INIT = SAVE_AND_INIT
EN_CONST_HP = CONST_HP
EN_POWER_FUNC = POWER_FUNC
EN_CUSTOM = CUSTOM
EN_NOCURVE = NOCURVE
EN_VOLUME_CURVE = VOLUME_CURVE
EN_PUMP_CURVE = PUMP_CURVE
EN_EFFIC_CURVE = EFFIC_CURVE
EN_HLOSS_CURVE = HLOSS_CURVE
EN_GENERIC_CURVE = GENERIC_CURVE
EN_UNCONDITIONAL = UNCONDITIONAL
EN_CONDITIONAL = CONDITIONAL
EN_NO_REPORT = NO_REPORT
EN_NORMAL_REPORT = NORMAL_REPORT
EN_FULL_REPORT = FULL_REPORT
EN_R_NODE = R_NODE
EN_R_LINK = R_LINK
EN_R_SYSTEM = R_SYSTEM
EN_R_DEMAND = R_DEMAND
EN_R_HEAD = R_HEAD
EN_R_GRADE = R_GRADE
EN_R_LEVEL = R_LEVEL
EN_R_PRESSURE = R_PRESSURE
EN_R_FLOW = R_FLOW
EN_R_STATUS = R_STATUS
EN_R_SETTING = R_SETTING
EN_R_POWER = R_POWER
EN_R_TIME = R_TIME
EN_R_CLOCKTIME = R_CLOCKTIME
EN_R_FILLTIME = R_FILLTIME
EN_R_DRAINTIME = R_DRAINTIME
EN_R_EQ = R_EQ
EN_R_NE = R_NE
EN_R_LE = R_LE
EN_R_GE = R_GE
EN_R_LT = R_LT
EN_R_GT = R_GT
EN_R_IS = R_IS
EN_R_NOT = R_NOT
EN_R_BELOW = R_BELOW
EN_R_ABOVE = R_ABOVE
EN_R_IS_OPEN = R_IS_OPEN
EN_R_IS_CLOSED = R_IS_CLOSED
EN_R_IS_ACTIVE = R_IS_ACTIVE
EN_MISSING = MISSING

# default project for compatibility with epanettools
_default_project = None
verbose = True

def default_project(project=None):
    global _default_project
    if _default_project is None:
        if project is None:
            _default_project = _toolkit.createproject()
            text = "Default epanet project created:"
        else:
            _default_project = project
            text = "Using this project as default:"
        if verbose:
            print(text, hex(id(_default_project)))
    return _default_project

def ENcreateproject():
    return _toolkit.createproject()

# Create ENxxx functions using the default project as 1st arg to epanet22 API
def ENdeleteproject(project=None):
    global _default_project
    text = "Project"
    if project is None:
        text = "Default project"
        project = _default_project
        _default_project = None
    if project is not None:
        if verbose:
            print(text, hex(id(project)), "is being deleted")
        iret = _toolkit.deleteproject(project)
        return iret
    return -1

def ENrunproject(inpFile, rptFile, outFile, pviewprog):
    default_project()
    return _toolkit.runproject(_default_project, inpFile, rptFile, outFile, pviewprog)

def ENinit(rptFile, outFile, unitsType, headLossType):
    default_project()
    return _toolkit.init(_default_project, rptFile, outFile, unitsType, headLossType)

def ENopen(inpFile, rptFile, outFile):
    default_project()
    return _toolkit.open(_default_project, inpFile, rptFile, outFile)

def ENgettitle():
    return _toolkit.gettitle(_default_project)

def ENsettitle(line1, line2, line3):
    return _toolkit.settitle(_default_project, line1, line2, line3)

def ENgetcomment(object, index):
    return _toolkit.getcomment(_default_project, object, index)

def ENsetcomment(object, index, comment):
    return _toolkit.setcomment(_default_project, object, index, comment)

def ENgetcount(object):
    return _toolkit.getcount(_default_project, object)

def ENsaveinpfile(filename):
    return _toolkit.saveinpfile(_default_project, filename)

def ENclose():
    if _default_project is not None:
        return _toolkit.close(_default_project)
    return 0

def ENsolveH():
    return _toolkit.solveH(_default_project)

def ENusehydfile(filename):
    return _toolkit.usehydfile(_default_project, filename)

def ENopenH():
    return _toolkit.openH(_default_project)

def ENinitH(initFlag):
    return _toolkit.initH(_default_project, initFlag)

def ENrunH():
    return _toolkit.runH(_default_project)

def ENnextH():
    return _toolkit.nextH(_default_project)

def ENsaveH():
    return _toolkit.saveH(_default_project)

def ENsavehydfile(filename):
    return _toolkit.savehydfile(_default_project, filename)

def ENcloseH():
    return _toolkit.closeH(_default_project)

def ENsolveQ():
    return _toolkit.solveQ(_default_project)

def ENopenQ():
    return _toolkit.openQ(_default_project)

def ENinitQ(saveFlag):
    return _toolkit.initQ(_default_project, saveFlag)

def ENrunQ():
    return _toolkit.runQ(_default_project)

def ENnextQ():
    return _toolkit.nextQ(_default_project)

def ENstepQ():
    return _toolkit.stepQ(_default_project)

def ENcloseQ():
    return _toolkit.closeQ(_default_project)

def ENwriteline(line):
    return _toolkit.writeline(_default_project, line)

def ENreport():
    return _toolkit.report(_default_project)

def ENcopyreport(filename):
    return _toolkit.copyreport(_default_project, filename)

def ENclearreport():
    return _toolkit.clearreport(_default_project)

def ENresetreport():
    return _toolkit.resetreport(_default_project)

def ENsetreport(format):
    return _toolkit.setreport(_default_project, format)

def ENsetstatusreport(level):
    return _toolkit.setstatusreport(_default_project, level)

def ENgetversion():
    return _toolkit.getversion()

def ENgeterror(errcode, maxLen):
    return _toolkit.geterror(errcode, maxLen)

def ENgetstatistic(type):
    return _toolkit.getstatistic(_default_project, type)

def ENgetresultindex(type, index):
    return _toolkit.getresultindex(_default_project, type, index)

def ENgetoption(option):
    return _toolkit.getoption(_default_project, option)

def ENsetoption(option, value):
    return _toolkit.setoption(_default_project, option, value)

def ENgetflowunits():
    return _toolkit.getflowunits(_default_project)

def ENsetflowunits(units):
    return _toolkit.setflowunits(_default_project, units)

def ENgettimeparam(param):
    return _toolkit.gettimeparam(_default_project, param)

def ENsettimeparam(param, value):
    return _toolkit.settimeparam(_default_project, param, value)

def ENgetqualinfo():
    return _toolkit.getqualinfo(_default_project)

def ENgetqualtype():
    return _toolkit.getqualtype(_default_project)

def ENsetqualtype(qualType, chemName, chemUnits, traceNode):
    return _toolkit.setqualtype(_default_project, qualType, chemName, chemUnits, traceNode)

def ENaddnode(id, nodeType):
    return _toolkit.addnode(_default_project, id, nodeType)

def ENdeletenode(index, actionCode):
    return _toolkit.deletenode(_default_project, index, actionCode)

def ENgetnodeindex(id):
    return _toolkit.getnodeindex(_default_project, id)

def ENgetnodeid(index):
    return _toolkit.getnodeid(_default_project, index)

def ENsetnodeid(index, newid):
    return _toolkit.setnodeid(_default_project, index, newid)

def ENgetnodetype(index):
    return _toolkit.getnodetype(_default_project, index)

def ENgetnodevalue(index, property):
    return _toolkit.getnodevalue(_default_project, index, property)

def ENsetnodevalue(index, property, value):
    return _toolkit.setnodevalue(_default_project, index, property, value)

def ENsetjuncdata(index, elev, dmnd, dmndpat):
    return _toolkit.setjuncdata(_default_project, index, elev, dmnd, dmndpat)

def ENsettankdata(index, elev, initlvl, minlvl, maxlvl, diam, minvol, volcurve):
    return _toolkit.settankdata(_default_project, index, elev, initlvl, minlvl, maxlvl, diam, minvol, volcurve)

def ENgetcoord(index):
    return _toolkit.getcoord(_default_project, index)

def ENsetcoord(index, x, y):
    return _toolkit.setcoord(_default_project, index, x, y)

def ENgetdemandmodel():
    return _toolkit.getdemandmodel(_default_project)

def ENsetdemandmodel(type, pmin, preq, pexp):
    return _toolkit.setdemandmodel(_default_project, type, pmin, preq, pexp)

def ENadddemand(nodeIndex, baseDemand, demandPattern, demandName):
    return _toolkit.adddemand(_default_project, nodeIndex, baseDemand, demandPattern, demandName)

def ENdeletedemand(nodeIndex, demandIndex):
    return _toolkit.deletedemand(_default_project, nodeIndex, demandIndex)

def ENgetdemandindex(nodeIndex, demandName):
    return _toolkit.getdemandindex(_default_project, nodeIndex, demandName)

def ENgetnumdemands(nodeIndex):
    return _toolkit.getnumdemands(_default_project, nodeIndex)

def ENgetbasedemand(nodeIndex, demandIndex):
    return _toolkit.getbasedemand(_default_project, nodeIndex, demandIndex)

def ENsetbasedemand(nodeIndex, demandIndex, baseDemand):
    return _toolkit.setbasedemand(_default_project, nodeIndex, demandIndex, baseDemand)

def ENgetdemandpattern(nodeIndex, demandIndex):
    return _toolkit.getdemandpattern(_default_project, nodeIndex, demandIndex)

def ENsetdemandpattern(nodeIndex, demandIndex, patIndex):
    return _toolkit.setdemandpattern(_default_project, nodeIndex, demandIndex, patIndex)

def ENgetdemandname(nodeIndex, demandIndex):
    return _toolkit.getdemandname(_default_project, nodeIndex, demandIndex)

def ENsetdemandname(nodeIndex, demandIdx, demandName):
    return _toolkit.setdemandname(_default_project, nodeIndex, demandIdx, demandName)

def ENaddlink(id, linkType, fromNode, toNode):
    return _toolkit.addlink(_default_project, id, linkType, fromNode, toNode)

def ENdeletelink(index, actionCode):
    return _toolkit.deletelink(_default_project, index, actionCode)

def ENgetlinkindex(id):
    return _toolkit.getlinkindex(_default_project, id)

def ENgetlinkid(index):
    return _toolkit.getlinkid(_default_project, index)

def ENsetlinkid(index, newid):
    return _toolkit.setlinkid(_default_project, index, newid)

def ENgetlinktype(index):
    return _toolkit.getlinktype(_default_project, index)

def ENsetlinktype(inout_index, linkType, actionCode):
    return _toolkit.setlinktype(_default_project, inout_index, linkType, actionCode)

def ENgetlinknodes(index):
    return _toolkit.getlinknodes(_default_project, index)

def ENsetlinknodes(index, node1, node2):
    return _toolkit.setlinknodes(_default_project, index, node1, node2)

def ENgetlinkvalue(index, property):
    return _toolkit.getlinkvalue(_default_project, index, property)

def ENsetlinkvalue(index, property, value):
    return _toolkit.setlinkvalue(_default_project, index, property, value)

def ENsetpipedata(index, length, diam, rough, mloss):
    return _toolkit.setpipedata(_default_project, index, length, diam, rough, mloss)

def ENgetvertexcount(index):
    return _toolkit.getvertexcount(_default_project, index)

def ENgetvertex(index, vertex):
    return _toolkit.getvertex(_default_project, index, vertex)

def ENsetvertex(index, vertex, x, y):
    return _toolkit.setvertex(_default_project, index, vertex, x, y)

def ENsetvertices(index, x, y, count):
    return _toolkit.setvertices(_default_project, index, x, y, count)

def ENgetpumptype(linkIndex):
    return _toolkit.getpumptype(_default_project, linkIndex)

def ENgetheadcurveindex(linkIndex):
    return _toolkit.getheadcurveindex(_default_project, linkIndex)

def ENsetheadcurveindex(linkIndex, curveIndex):
    return _toolkit.setheadcurveindex(_default_project, linkIndex, curveIndex)

def ENaddpattern(id):
    return _toolkit.addpattern(_default_project, id)

def ENdeletepattern(index):
    return _toolkit.deletepattern(_default_project, index)

def ENgetpatternindex(id):
    return _toolkit.getpatternindex(_default_project, id)

def ENgetpatternid(index):
    return _toolkit.getpatternid(_default_project, index)

def ENsetpatternid(index, id):
    return _toolkit.setpatternid(_default_project, index, id)

def ENgetpatternlen(index):
    return _toolkit.getpatternlen(_default_project, index)

def ENgetpatternvalue(index, period):
    return _toolkit.getpatternvalue(_default_project, index, period)

def ENsetpatternvalue(index, period, value):
    return _toolkit.setpatternvalue(_default_project, index, period, value)

def ENgetaveragepatternvalue(index):
    return _toolkit.getaveragepatternvalue(_default_project, index)

def ENsetpattern(index, values, len):
    return _toolkit.setpattern(_default_project, index, values, len)

def ENaddcurve(id):
    return _toolkit.addcurve(_default_project, id)

def ENdeletecurve(index):
    return _toolkit.deletecurve(_default_project, index)

def ENgetcurveindex(id):
    return _toolkit.getcurveindex(_default_project, id)

def ENgetcurveid(index):
    return _toolkit.getcurveid(_default_project, index)

def ENsetcurveid(index, id):
    return _toolkit.setcurveid(_default_project, index, id)

def ENgetcurvelen(index):
    return _toolkit.getcurvelen(_default_project, index)

def ENgetcurvetype(index):
    return _toolkit.getcurvetype(_default_project, index)

def ENsetcurvetype(index, type):
    return _toolkit.setcurvetype(_default_project, index, type)

def ENgetcurvevalue(curveIndex, pointIndex):
    return _toolkit.getcurvevalue(_default_project, curveIndex, pointIndex)

def ENsetcurvevalue(curveIndex, pointIndex, x, y):
    return _toolkit.setcurvevalue(_default_project, curveIndex, pointIndex, x, y)

def ENgetcurve(index, out_xValues, out_yValues):
    return _toolkit.getcurve(_default_project, index, out_xValues, out_yValues)

def ENsetcurve(index, xValues, yValues, nPoints):
    return _toolkit.setcurve(_default_project, index, xValues, yValues, nPoints)

def ENaddcontrol(type, linkIndex, setting, nodeIndex, level):
    return _toolkit.addcontrol(_default_project, type, linkIndex, setting, nodeIndex, level)

def ENdeletecontrol(index):
    return _toolkit.deletecontrol(_default_project, index)

def ENgetcontrol(index):
    return _toolkit.getcontrol(_default_project, index)

def ENsetcontrol(index, type, linkIndex, setting, nodeIndex, level):
    return _toolkit.setcontrol(_default_project, index, type, linkIndex, setting, nodeIndex, level)

def ENaddrule(rule):
    return _toolkit.addrule(_default_project, rule)

def ENdeleterule(index):
    return _toolkit.deleterule(_default_project, index)

def ENgetrule(index):
    return _toolkit.getrule(_default_project, index)

def ENgetruleID(index):
    r"""
    getruleID(ph, index) -> int

    Parameters
    ----------
    ph: EN_Project
    index: int

    """
    return _toolkit.getruleID(_default_project, index)

def ENgetpremise(ruleIndex, premiseIndex):
    return _toolkit.getpremise(_default_project, ruleIndex, premiseIndex)

def ENsetpremise(ruleIndex, premiseIndex, logop, object, objIndex, variable, relop, status, value):
    return _toolkit.setpremise(_default_project, ruleIndex, premiseIndex, logop, object, objIndex, variable, relop, status, value)

def ENsetpremiseindex(ruleIndex, premiseIndex, objIndex):
    return _toolkit.setpremiseindex(_default_project, ruleIndex, premiseIndex, objIndex)

def ENsetpremisestatus(ruleIndex, premiseIndex, status):
    return _toolkit.setpremisestatus(_default_project, ruleIndex, premiseIndex, status)

def ENsetpremisevalue(ruleIndex, premiseIndex, value):
    return _toolkit.setpremisevalue(_default_project, ruleIndex, premiseIndex, value)

def ENgetthenaction(ruleIndex, actionIndex):
    return _toolkit.getthenaction(_default_project, ruleIndex, actionIndex)

def ENsetthenaction(ruleIndex, actionIndex, linkIndex, status, setting):
    return _toolkit.setthenaction(_default_project, ruleIndex, actionIndex, linkIndex, status, setting)

def ENgetelseaction(ruleIndex, actionIndex):
    return _toolkit.getelseaction(_default_project, ruleIndex, actionIndex)

def ENsetelseaction(ruleIndex, actionIndex, linkIndex, status, setting):
    return _toolkit.setelseaction(_default_project, ruleIndex, actionIndex, linkIndex, status, setting)

def ENsetrulepriority(index, priority):
    return _toolkit.setrulepriority(_default_project, index, priority)
