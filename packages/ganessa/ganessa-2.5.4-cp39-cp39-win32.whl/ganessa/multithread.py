'''
Created on 14 déc. 2016

171116: machinery moved to 'parallel'; mp_run left here for legacy

@author: Jarrige_Pi
'''
from ganessa.parallel import MultiProc
# for legacy
from ganessa.parallel import required_cpu


#****f* Functions_mt/mp_run
# DESCRIPTION
#   This function is provided for legacy compatibility.
#   parallel.MultiProc should be used instead.
# SYNTAX
#   mp_run(logprint, tasks [, nb_cpu= -1] [, wait= 0.0] [, use_wpnum= False])
# ARGUMENT
#   see MultiProc and run
# RESULT
#   this function is implemented as:
#   * MultiProc(logprint, nb_cpu, wait, use_wpnum).run(tasks)
# HISTORY
#   * Created 2016.12.14
#   * Updated 2017.11.14: class interface and optional wpnum argument.
#   * Updated 2017.11.16: machinery moved to parallel
#****

def mp_run(logprint, tasks, nb_cpu=-1, wait=0.15, use_wpnum=False):
    '''Runs tasks in parallel'''
    MultiProc(logprint, nb_cpu, wait, use_wpnum).run(tasks)
