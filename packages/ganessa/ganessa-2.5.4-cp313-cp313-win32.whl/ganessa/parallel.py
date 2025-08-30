'''
Created on 16 nov. 2017
@author: Jarrige_Pi

modified 2018.02.20 - PA Jarrige - changed TMARK for cpu_count > 1000
modified 2018.04.18 - PA Jarrige - added reduce option and fix seq run
modified 2018.05.14 - PA Jarrige - fix python3 issue
modified 2019.04.11 - PA JARRIGE - fix NotImplementedError in cpu_count
modified 2019.04.16 - PA JARRIGE - added erfun call if fun fails
modified 2023.03.20 - PA JARRIGE - removed imports from __future__
modified 2023.08.07 - PA JARRIGE - use f-string
modified 2024.12.19 - PA JARRIGE - add call to terminate function in sequential reduce mode

'''
import time
from datetime import datetime as DT
from math import log10
from functools import reduce

from multiprocessing import Process, Queue, current_process
from multiprocessing import cpu_count
from ganessa.util import is_text


def snow() -> str:
    '''Returns current date and time as a string dd/mm/yyyy hh:mm:ss'''
    return DT.now().strftime("%d/%m/%Y %H:%M:%S")

# -------------------------------------
# Parallelism handling functions
# -------------------------------------
#
# Function run by worker processes
#
STOP = 'STOP'
TEMPO = 0.125
def mp_worker(inputqueue, outputqueue, init, term, wait, wpnum, wpcount, use):
    '''worker loop for a a parallel process'''
    # rank init and term < 0 for sorting
    if init is not None:
        func, args = init
        rank = -wpnum
        sres, result = mp_calculate(func, args, rank, -1, wpnum, use)
        outputqueue.put((rank, sres, result))
        time.sleep(TEMPO)
    # count is used for logging and temporisation of 1st task
    for count, rankedtask in enumerate(iter(inputqueue.get, STOP)):
        if not count:
            time.sleep(wait)
        rank, (func, args) = rankedtask
        sres, result = mp_calculate(func, args, rank, count, wpnum, use)
        outputqueue.put((rank, sres, result))
    # rank init and term < 0 for sorting
    if term is not None:
        TMARK = (10 if wpcount < 10 else 
                100 if wpcount < 100 else 10 ** (1+ int(log10(wpcount + 0.5))))
        func, args = term
        rank = -wpnum - TMARK
        sres, result = mp_calculate(func, args, rank, -2, wpnum, use)
        outputqueue.put((rank, sres, result))
    outputqueue.close()

#
# Function used to run each task and summarize result
#
def mp_calculate(func, args, rank, count, wpnum, use):
    '''run each task and summarize result'''
    fun, erfun = func if isinstance(func, tuple) else (func, None)
    try:
        result = fun(*args, wpnum=wpnum) if use else fun(*args)
        stat = result if is_text(result) else 'Ok!'
    except Exception as exc:
        # we try erfun as second chance
        try:
            result = erfun(*args, wpnum=wpnum) if use else erfun(*args)
        except Exception:
            result = None
        stat = str(exc)
    sres = f"{ current_process().name} [run {count:2d}] says that {fun.__name__}({rank:2d}): {stat}"
    return sres, result

#****g* ganessa.parallel/About
# PURPOSE
#   The module ganessa.parallel provides a multitasking (parallel) computing
#   capability based on multiprocessing Process and Queue objects.
#****

#****g* ganessa.parallel/Classes_mt
#****
#****g* ganessa.multithread/Functions_mt
#****

#****f* Functions_mt/required_cpu
# SYNTAX
#   ncpu = required_cpu(nb_cpu)
# ARGUMENT
#   int nb_cpu: expected number of parallel processes, up to the hardware core count.
#   A negative or null value indicates the number of hardware cores + nb_cpu.
# RESULT
#   int ncpu: actual number of parallel processes (1 ... max physical core count)
# EXAMPLE
#   * required_cpu(-1) returns the hardware core count but one.
#****
def required_cpu(nb_cpu: int ) -> int:
    '''Returns a number of core to be used, between 1 and available_cpu
    required_cpu(-1) returns core_count - 1'''
    try:
        return 1 + max(0, (nb_cpu - 1) % cpu_count())
    except:
        return 1

#****o* Classes_mt/MultiProc, run_, run_sequential
# DESCRIPTION
#   The MultiProc class allows to define and run tasks in parallel. A number
#   of N processing instances (nb_cpu provided, default all cores but one)
#   are created; then tasks from the tasks list are dispatched to the processing
#   instances.
#
#   An init task (resp. a term task) may be provided; if so it is called by
#   each processing instance before the 1st task (resp. after the last one).
#   If init is not provided,
#   first N tasks are guaranteed to be run on distinct instances and
#   can also be used for initialisation purposes. Then each task in the list is
#   associated to the next processing instance available in turn. The execution
#   order is not guaranteed (except the first N tasks if init is not provided).
#
#   run executes the tasks list in parallel processing instances; run_sequential
#   executes the tasks list sequentially, i.e. init, tasks in order, term.
#
# SYNTAX
#   * mp = MultiProc(logprint [, nb_cpu= -1] [, wait= 0.0] [, use_wpnum= False] [, reduce= None]
#     [, progress= None])
#   * results, resinit, resterm = mp.run(tasks [, init=None] [, term= None])
#   * results, resinit, resterm = mp.run_sequential(tasks [, init=None] [, term= None] [, wpnum= None])
#   * comb_results = mp.run(tasks [, init=None] [, term= None])
#   * comb_results = mp.run_sequential(tasks [, init=None] [, term= None] [, wpnum= None])
#   * ncpu = mp.nmaxcpu
# ARGUMENT
#   * function logprint: called by mp.run with a single str arg for logging
#   * int nb_cpu: optional number of parallel processes, up to the hardware core count.
#     A negative value indicates the number of hardware cores + nb_cpu (defaults to -1).
#   * float wait: wait time (s) before the first task of each processing instance.
#   * bool use_wpnum: if True, the function called in task list must accept an
#     integer keyword argument wpnum, being equal to the process number (1 ... nb_cpu)
#     in charge of its execution.
#   * callable progress: function for displaying the overall progression.
#     It is called after every task completion with the completion rank (starting at 0)
#     and the total task count, i.e. progress(i, ntasks) where i in range(ntasks).
#   * callable reduce: function for reducing the simulation results.
#     the first call to 'init' is used to initialise comb_results;
#     then every incoming result is merged in turn (in random order):
#     comb_result = reduce(comb_results, result)
#   * tasks: list of (func, args) tuples defining the tasks to be run as
#     result = func(*args) if use_wpnum is False or not set; or
#     result = func(*args, wpnum= proc_num) otherwise.
#     if func returns a str or unicode, it will be inserted in the log string.
#   * optionally, func can be a tuple (fun, erfun); erfun(*args) will be called
#     for a return value if fun(*args) raise an exception (added 190416).
#   * init (optional) tuple (func, args) to be called by every processing instance
#     before any tasks.
#   * term (optional) tuple (func, args) to be called by every processing instance
#     after all tasks.
# RESULT
#   * int ncpu: number of processing instances.
#   When reduce function is not provided:
#   * results: list of result = func(args), in the original tasks list order.
#   * resinit: list of results for init calls (empty if init is None).
#     Its length is the processing instances count.
#   * resterm: list of results for term calls (empty if term is None).
#     Its length is the processing instances count.
#   When reduce function is provided:
#   * comb_results: reduced results. Roughly reduce(reduce, results, init_result)
# REMARKS
#   * tasks are run in parallel by the set of parallel processes: when a process
#     ends up a task, it starts executing the next task available in the list.
#   * the number of processing instances is available as mp.nmaxcpu
#   * run_sequential is provided for debugging, it loops and execute tasks in turn.
#   * if the tasks count is smaller than the number of requested cpus, the number
#     of processing instances is reduced to the task count.
# HISTORY
#   * Created 2016.12.14
#   * Updated 2017.11.14: class interface and optional wpnum argument.
#   * Updated 2017.11.17: renamed to parallel; added results return list.
#     added init and term options
#   * Updated 2017.11.20: return values as a tuple of 3 lists for tasks, init, term
#   * Updated 2017.11.30: added progress method
#   * Updated 2018.04.18: added reduce method; fix init seq run issue.
#   * Updated 2018.05.14: fix python3 issue
#   * Updated 2019.04.11: NotImplementedError handling in cpu_count
#   * Updated 2019.04.16: added erfun handling for return value when fun raises an exception
#   * Updated 2023.08.07: use f-strings
#   * Updated 2024.12.19: fix missing 'term' call by run_sequential
#****

# class for encapsulating the thing
class MultiProc:
    '''Class for running tasks in parallel and merge or reduce results'''
    def __init__(self, logprint, nb_cpu=-1, wait=0.0, use_wpnum=False,
                 progress=None, freduce=None):
        self.logfun = logprint
        self._nmaxcpu = required_cpu(nb_cpu)
        # first tasks must be taken by workers before any one ends up.
        self.wait = wait
        self.use_wpnum = use_wpnum
        self.progress = progress
        self.reduce = freduce
        self.ncpu = 0

    @property
    def nmaxcpu(self):
        '''Get the max used CPU count'''
        return self._nmaxcpu

    def run(self, tasks, init=None, term=None):
        '''Runs tasks list in parallel'''
        # set the threads
        mpf = '  >>> '
        ntasks = len(tasks)
        self.ncpu = min(self._nmaxcpu, ntasks)
        if not tasks:
            return
        if self._nmaxcpu == 1:
            return self.run_sequential(tasks, init, term)

        # Create queues
        task_queue = Queue()
        done_queue = Queue()

        logprint = self.logfun
        # Submit tasks and remember initial rank
        logprint(mpf + snow())
        for rank, task in enumerate(tasks):
            task_queue.put((rank, task))
        logprint(mpf + f'Task queue built: {ntasks} tasks to run')

        # Tell child processes to stop at the end
        for _i in range(self.ncpu):
            task_queue.put(STOP)

        # Create worker processes
        logprint(mpf + f'Creating {self.ncpu} threads...')
        # introduce delay for 1st task of wp if no explicit init
        wait = max(self.wait, TEMPO) if init is None else self.wait
        processes = [Process(target=mp_worker,
                             args=(task_queue, done_queue, init, term,
                                   wait, pn+1, self.ncpu, self.use_wpnum))
                             for pn in range(self.ncpu)]
        # Start worker processes
        for p in processes:
            p.start()
        logprint('\n' + mpf + f'{self.ncpu} threads started.\n')

        # Get and print results asap
        if init is not None:
            ntasks += self.ncpu
        if term is not None:
            ntasks += self.ncpu
        results = []

        if self.progress is not None:
            self.progress(0, ntasks)
        for i in range(ntasks):
            output_rank, retlog, retval = done_queue.get()
            logprint(mpf + retlog + '\t ' + snow())
            if self.reduce is None:
                results.append((output_rank, retval))
            elif output_rank < 0:
                if not results:
                    results = retval
            else:
                results = self.reduce(results, retval)
            if self.progress is not None:
                self.progress(i, ntasks)

        # Wait for worker processes to stop
        for p in processes:
            p.join()
            p.terminate()
        del task_queue, done_queue
        logprint(mpf + 'Threads stopped.')

        if self.reduce is None:
            # sort results by initial task rank (term, init, tasklist)
            results.sort()
            logprint(mpf + snow())
            # returns results only, not rank
            results = list(zip(*results))[1]
            # extract init and term results
            nt = 0 if term is None else self.ncpu
            ni = nt if init is None else nt + self.ncpu
            return results[ni:], results[nt:ni], results[:nt]
        return results

    def run_sequential(self, tasks, init=None, term=None, wpnum=0):
        '''Run tasks list sequentially'''
        ntasks = len(tasks)
        # define calculation function
        def seq_calculate(k, func, args):
            # fun, erfun = func if isinstance(func, tuple) else (func, None)
            fun = func[0] if isinstance(func, tuple) else func
            if self.use_wpnum:
                result = fun(*args, wpnum=wpnum)
            else:
                result = fun(*args)
            #===================================================================
            # use = self.use_wpnum
            # try:
            #     result = fun(*args, wpnum=wpnum) if use else fun(*args)
            # except Exception:
            #     try:
            #         result = erfun(*args, wpnum=wpnum) if use else erfun(*args)
            #     except Exception:
            #         result = None
            #===================================================================

            stat = result if is_text(result) else 'Ok!'
            self.logfun(fun.__name__ + ' ' + stat)
            if self.progress is not None:
                self.progress((ntasks if k < 0 else k), ntasks)
            return result

        if self.reduce is None:
            resinit, resterm = [], []
            if init is not None:
                resinit = [seq_calculate(0, *init)]
            results = [seq_calculate(i, *task) for i, task in enumerate(tasks)]
            if term is not None:
                resterm = [seq_calculate(-1, *term)]
            return results, resinit, resterm

        results = reduce(self.reduce,
                            (seq_calculate(i, *task) for i, task in enumerate(tasks)),
                            [] if init is None else seq_calculate(0, *init))
        if term is not None:
            resterm = [seq_calculate(-1, *term)]
        return results

# the call 'freeze_support()' should appear just after line
# 'if __name__ == "__main__":'
# if the script has to be bound to an executable.
