"""
File Purpose: tools related to multiprocessing
"""

import multiprocessing as mp
import pickle
import time  # for mptest functions like sleep

import numpy as np

from .arrays import nest_shape
from .docs_tools import format_docstring
from .iterables import (
    is_iterable, is_dictlike,
    Container, ContainerOfList, ContainerOfArray, ContainerOfDict,
)
from .properties import alias, simple_property
from .sentinels import RESULT_MISSING, UNSET, Sentinel
from .timing import TimeLimit, ProgressUpdater
from ..errors import InputError, InputConflictError

from ..defaults import DEFAULTS


_paramdocs_tasks = {
    'kw': '''dict
        kwargs for task will be task.kw, but updated with kw.
        E.g. if task.kw = {'x': 1}, and kw = {'y': 2}, --> task called with x=1, y=2.''',
    'reset': '''bool
        whether to reset self.result to all RESULT_MISSING, before starting this operation.''',
    'skip_done': '''bool
        whether to skip tasks that already have a result (i.e. self.result[idx] != RESULT_MISSING).''',
    'ncpu': '''None or int
        max number of cpus to use for multiprocessing.
        None --> use multiprocessing.cpu_count()
        int --> use this value. if 0 or 1, do not use multiprocessing here.
        Note: will actually use min(ncpu, number of calls to be made);
            e.g. if ncpu=4 but len(arg_kw_tuples)=2, will only use 2 cpus.''',
    'timeout': '''None or int
        max duration, in seconds. Must be None or integer (due to limitations of signal.alarm method)
        None --> no time limit.
        Note: if time_limit is reached, will raise a TimeoutError and save the result so far.
            (in this case, any not-yet-calculated values will each be RESULT_MISSING.)''',
    'f': '''callable
        The function to be called during task evaluation.
        if using ncpu > 1, f must be compatible with multiprocessing, i.e. it must be pickleable,
            e.g. it should be defined at the top level of a module or as a class method.''',
    'ncoarse': '''int
        if >1, group tasks into groups of size ncoarse before performing them.''',
    'print_freq': '''None, or number (possibly negative or 0)
        >0 --> Minimum number of seconds between progress updates.
        =0 --> print every progress update.
        <0 --> never print progress updates.
        None --> use DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ''',
    'assign_task_idx': '''bool
        whether to assign task.i for each task, based on its position in self.''',
    'printable_process_name': '''None or str
        include in progress update printouts. If None, use a reasonable default.''',
    'errors_ok': '''bool, Exception type, or tuple of Exception types
        whether it is okay for some tasks to produce certain errors.
        False --> crash if any task crashes. Equivalent to errors_ok=().
        True --> except Exception (not BaseException, though). Equivalent to errors_ok=Exception.
        Exception type or tuple --> except this type (or these types, if tuple).''',
    'result_missing': '''any object
        result to record for tasks which crash (if errors_ok!=False). Default RESULT_MISSING.''',
}

### --------------------- Helper functions --------------------- ###

def is_task_element(x):
    '''returns whether x is a Task-like element.
    i.e. x is a callable, or len(x)=0, or x iterable but x[0] not iterable nor callable.
    '''
    if callable(x):
        return True
    elif is_iterable(x):
        return len(x)==0 or (not callable(x[0]) and not is_iterable(x[0]))
    else:
        raise TypeError(f'is_task_element(x) expected x to be callable or iterable, but got x={x}')

def check_pickle(x):
    '''checks that x, is pickleable, by pickling then unpickling.
    Returns result of unpickling. Useful for debugging.
    '''
    dump = pickle.dumps(x)
    load = pickle.loads(dump)
    return load

def copy_via_pickle(x):
    '''returns copy of x via pickle.loads(pickle.dumps(x)).'''
    dump = pickle.dumps(x)
    return pickle.loads(dump)


### --------------------- Task --------------------- ###

@format_docstring(**_paramdocs_tasks)
class Task():
    '''a single task, i.e. a function, args, & kwargs.
    Calling self will perform the task, i.e. self.result=f(*args, **kw), and return result.

    Alternatively, calling self.apply_async(pool) enables to perform task in parallel,
        using the muliprocessing module.

    f: {f}
    args: iterable of args or non-iterable object.
        if iterable, will be interpreted as the list of args.
        if non-iterable, will use args = [args].
    i: any object
        optionally, index for this task.
        Useful when task appears inside a TaskContainer.
    '''
    # [TODO] is there any non-negligible time cost to making Task objects instead of passing tuples?
    def __init__(self, f, args=None, kw=None, *, i=None):
        self.f = f
        self.args = () if args is None else (args if is_iterable(args) else [args])
        self.kw = dict() if kw is None else kw
        self.i = i
        if not is_dictlike(self.kw):
            errmsg = f'{type(self).__name__}(...) expected kw to be dict-like, but got kw={kw}'
            raise TypeError(errmsg)

    def new_with(self, f=UNSET, args=UNSET, kw=UNSET, i=UNSET):
        '''return a new Task, with the given inputs. Use value from self for UNSET inputs.
        E.g. Task(f, [5,6]).new_with(f=g, kw=dict(y=7)) --> Task(g, [5,6], dict(y=7))
        '''
        cls = type(self)
        f = self.f if f is UNSET else f
        args = self.args if args is UNSET else args
        kw = self.kw if kw is UNSET else kw
        i = self.i if i is UNSET else i
        return cls(f, args, kw, i=i)

    @classmethod
    def implied(cls, task_info, *, force_kw=True, **kw_init):
        '''return the Task implied from task_info.
        task_info: Task, iterable, or callable.
            Task --> return task_info, unchanged (unless force_kw and len(kw_init)>0).
                     if task_info is not an instance of cls but it is a Task, raise TypeError.
            iterable --> return Task(*task_info).
            callable --> return Task(task_info).
        force_kw: bool
            applies if kw_init provided and task_info is a Task...
                True --> return task_info.new_with(**kw_init)
                False --> return task_info, unchanged.
        kw_init: pass to Task(..., **kw_init) if task_info is not already a Task.
        '''
        if isinstance(task_info, Task):
            if isinstance(task_info, cls):
                if force_kw and len(kw_init)>0:
                    return task_info.new_with(**kw_init)
                else:
                    return task_info
            else:
                raise TypeError(f'{cls.__name__}.implied(t) expected t subtype of {cls.__name__}, but got t={task_info}.')
        elif is_iterable(task_info):
            return cls(*task_info, **kw_init)
        elif callable(task_info):
            return cls(task_info, **kw_init)
        else:
            errmsg = f'{cls.__name__}.implied(t) expected {cls.__name__}, iterable, or callable, but got t={task_info}.'
            raise TypeError(errmsg)

    # # # PERFORM THE TASK # # #
    @format_docstring(**_paramdocs_tasks, sub_ntab=1)
    def __call__(self, **kw):
        '''perform the task, i.e. return f(*args, **kw).

        kw: {kw}
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.result = self.f(*self.args, **self.get_kw(kw=kw))
        return self.result

    @format_docstring(**_paramdocs_tasks, sub_ntab=1)
    def apply_async(self, pool, *, kw=dict()):
        '''perform the task asynchronously, i.e. pool.apply_async(...)
        Equivalent to pool.apply_async(self.f, args=self.args, kwds=self.kw)

        kw: {kw}
        '''
        return pool.apply_async(self.f, args=self.args, kwds=self.get_kw(kw=kw))

    # # # UPDATE KWARGS # # #
    def get_kw(self, kw=dict()):
        '''gets self.kw, but updated with values from kw. (doesn't alter self.kw)
        [EFF] if kw is empty, return self.kw instead of making a copy.
        '''
        return {**self.kw, **kw} if kw else self.kw

    # # # DISPLAY # # #
    def _repr_contents(self):
        result = [f'f={self.f.__name__}']
        if len(self.args)>0:
            result.append(f'args={self.args}')
        if len(self.kw)>0:
            result.append(f'kw={self.kw}')
        if self.i is not None:
            result.append(f'i={self.i}')
        return result

    def __repr__(self):
        str_contents = ', '.join(self._repr_contents())
        return f'{self.__class__.__name__}({str_contents})'


### --------------------- unique tasks --------------------- ###

class CrashIfCalled():
    '''callable which is not intended to be called. Crashes when called.
    Crashes with error message provided in __init__, if any.
    '''
    def __init__(self, errmsg=None):
        self.errmsg = errmsg

    def __call__(self, *args, **kw):
        if self.errmsg is not None:
            raise ValueError(self.errmsg)
        else:
            raise ValueError('CrashIfCalled was called!')


class UniqueTask(Sentinel, Task):
    '''a unique task. f, args, and kwargs, should be defined at the class level, not inside __init__.'''
    def __init__(self, *args__None, **kw__None):
        pass  # do nothing (instead of super().__init__)

    f = CrashIfCalled('UniqueTask.f was called, but not provided')
    args = ()
    kw = dict()

    def new_with(self, *args, **kw):
        '''return self. If args or kwargs provided, crash with InputError instead.'''
        if args or kw:
            raise InputError('UniqueTask.new_with(...) cannot take any arguments.')
        return self

    @classmethod
    def implied(cls, *args, **kw):
        '''return self. If args or kwargs provided, crash with InputError instead.'''
        if args or kw:
            raise InputError('UniqueTask.implied(...) cannot take any arguments.')
        return cls()


UNSET_TASK = UniqueTask('UNSET_TASK')
UNSET_TASK.f = CrashIfCalled('called UNSET_TASK! This is not supposed to happen. Probably forgot to set a task.')


### --------------------- identity task --------------------- ###

def identity(x):
    '''returns x. Provided for convenience with Task API.'''
    return x

class IdentityTask(Task):
    '''task which returns its (single) input. Useful for TaskArray, etc.'''
    def __init__(self, x, i=None):
        super().__init__(identity, x, i=i)


### --------------------- Task Containers --------------------- ###

@format_docstring(**_paramdocs_tasks)
class TaskContainer(Container):
    '''a container for multiple tasks; each Task is a function, args, & kwargs.
    Calling self will perform all tasks, returning the result (and updating self.result as well).

    tasks: iterable of Task objects
        Tasks to perform. Expected type depends on subclass, see e.g. TaskList or TaskArray.
    assign_task_idx: {assign_task_idx}
    printable_process_name: {printable_process_name}
    errors_ok: {errors_ok}
    result_missing: {result_missing}
    '''
    task_cls = Task  # class for any Tasks made by this TaskContainer
    tasks = alias('data')

    def __init__(self, tasks, *args_super, assign_task_idx=True, printable_process_name=None,
                 errors_ok=False, result_missing=RESULT_MISSING, **kw_super):
        super().__init__(tasks, *args_super, **kw_super)
        if assign_task_idx:
            self.assign_task_idx()
        self.printable_process_name = printable_process_name
        self.errors_ok = errors_ok
        self.result_missing = result_missing

    def assign_task_idx(self):
        '''assign task.i for tasks in self, based on their positions in self.'''
        for i, task in self.enumerate():
            task.i = i

    # # # PROPERTIES # # #
    @property
    def printable_process_name(self):
        '''return the name to be used for progress updates, if any.
        If None, use the default: "[type(self)].__call__".
        '''
        result = getattr(self, '_printable_process_name', None)
        if result is None:
            result = f'{type(self).__name__}.__call__'
        return result
    @printable_process_name.setter
    def printable_process_name(self, value):
        '''set the name to be used for progress updates.'''
        self._printable_process_name = value

    @property
    def errors_ok(self):
        '''tuple of Exception types which are okay for tasks to raise.
        setting self.errors_ok = False --> use empty tuple, i.e. no errors are okay.
        setting self.errors_ok = errtype --> use errors_ok = (errtype,).
        
        setting errors_ok will crash if it includes any parent class of KeyboardInterrupt,
            e.g. errors_ok=BaseException will crash, but errors_ok=Exception will be fine.

        See also: self.errors_ok_tuple
        '''
        return self._errors_ok
    @errors_ok.setter
    def errors_ok(self, value):
        '''set self.errors_ok to value, converting to tuple if needed. See also: self.errors_ok_tuple'''
        self._errors_ok = self.errors_ok_tuple(value)

    def errors_ok_tuple(self, value=UNSET):
        '''returns tuple of okay errors. UNSET --> self.errors_ok.
        False --> (). errtype --> (errtype,).
        if result includes any parent class of KeyboardInterrupt, raises InputError.
        e.g. errors_ok_tuple(BaseException) will crash, but errors_ok_tuple(Exception) will be fine.
        '''
        if value is UNSET:
            return self.errors_ok
        if value is False:
            value = ()
        elif isinstance(value, type):
            value = (value,)
        value = tuple(value)
        for errtype in value:
            if issubclass(errtype, KeyboardInterrupt):
                raise InputError('errors_ok cannot include KeyboardInterrupt or its parent classes.')
        return value

    # # # CALLING # # #
    def init_result(self):
        '''set self.result = container with similar shape as self, filled with RESULT_MISSING.
        Then, return self.result.
        The idea is that self.result[idx] will correspond to the result of self[idx].
        '''
        self.result = self.new_empty(fill=RESULT_MISSING)
        return self.result

    @format_docstring(**_paramdocs_tasks, sub_ntab=2)
    def __call__(self, *, kw=dict(), idx=None, reset=False, skip_done=False,
                 ncpu=None, timeout=None, ncoarse=1,
                 print_freq=None, errors_ok=UNSET, result_missing=UNSET):
        ''''perform all tasks in self, returning the results.

        OPTIONS (AFFECTS ALL TASKS)
            kw: {kw}

        OPTIONS (AFFECTS WHICH TASKS ARE PERFORMED)
            idx: None or iterable of indices
                None --> perform all tasks in self.
                iterable of indices --> perform only these tasks.
            reset: {reset}
            skip_done: {skip_done}

        OPTIONS (AFFECTS MULTIPROCESSING STRATEGY)
            ncpu: {ncpu}
            timeout: {timeout}
            ncoarse: {ncoarse}

        OPTIONS (MISC)
            print_freq: {print_freq}
            errors_ok: UNSET or {errors_ok}
                UNSET --> use self.errors_ok.
            result_missing: UNSET or {result_missing}
                UNSET --> use self.result_missing.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if reset or not hasattr(self, 'result'):
            self.init_result()  # creates self.result.
        idx_todo = [i for i, task in self.enumerate(idx) if (not skip_done) or (result[i] is RESULT_MISSING)]
        if len(idx_todo)==0:  # nothing left to calculate!
            return self.result
        if ncpu is None:
            ncpu = mp.cpu_count()
        if ncoarse > 1:
            coarsened = self.coarsen(ncoarse=ncoarse, idx=idx_todo)
            return coarsened(kw=kw, ncpu=ncpu, print_freq=print_freq, timeout=timeout)

        errors_ok = self.errors_ok_tuple(errors_ok)
        if result_missing is UNSET: result_missing = self.result_missing
        _updater = ProgressUpdater(print_freq, wait=True)  # wait=True --> wait print_freq seconds before first print.
        _N_todo = self.size(idx_todo)  # for updates - number of tasks total in self at these idx.
        _idx_done = set()  # helps with debugging - track which tasks were done this time.
        with TimeLimit(timeout):
            if ncpu > 1:  # multiprocessing
                getters = dict()
                with mp.Pool(processes=ncpu) as pool:
                    for _n, (i, task) in enumerate(self.enumerate(idx_todo)):
                        _updater.print(f'assigning task {_n} of {_N_todo}.')
                        getters[i] = task.apply_async(pool, kw=kw)
                    for _n, (i, getter) in enumerate(getters.items()):
                        _updater.print(f'waiting for results from task {_n} of {_N_todo}.')
                        try:
                            self.result[i] = getters[i].get()
                        except errors_ok:
                            self.result[i] = result_missing
                        _idx_done.add(i)
            else:  # single processor
                for _n, (i, task) in enumerate(self.enumerate(idx_todo)):
                    _updater.print(f'performing task {_n} of {_N_todo}.')
                    try:
                        self.result[i] = task(**kw)
                    except errors_ok:
                        self.result[i] = result_missing
                    _idx_done.add(i)
        _updater.finalize(self.printable_process_name, end='\n')
        return self.result
    
    def coarsen(self, ncoarse=5, *, idx=None):
        '''return a TaskPartition containing TaskGroups of size ncoarse.
        Useful for coarsening a TaskContainer for more efficient multiprocessing;
            grouping tasks together can reduce the overhead of multiprocessing,
            while still allowing for parallel processing as the groups are run in parallel.

        if idx is provided, only group the tasks with those indices.
        '''
        return TaskPartition.from_task_container(self, ncoarse=ncoarse, idx=idx)


@format_docstring(**_paramdocs_tasks)
class TaskList(TaskContainer, ContainerOfList):
    '''a container for multiple tasks; each Task is a function, args, & kwargs.
    Calling self will perform all tasks, returning the result (and updating self.result as well).

    tasks: Tasks, iterables, or callables.
        the Tasks to be performed.
        any non-Task input will be used to create a Task.
        E.g. TaskList(f1, (f2, args2), Task(f3, args3, kwargs3))
            --> [Task(f1), Task(f2, args2), Task(f3, args3, kwargs3)]
    from_list: None or iterable
        optionally, can provide all tasks as a single list, instead of as args.
        if provided, *tasks must be empty.
    assign_task_idx: {assign_task_idx}
    printable_process_name: {printable_process_name}
    errors_ok: {errors_ok}
    result_missing: {result_missing}
    '''
    def __init__(self, *tasks, from_list=None, **kw_super):
        if from_list is not None:
            if len(tasks)>0:
                raise InputConflictError('TaskList(...) expects *tasks or from_list, but not both.')
            tasks = from_list
        result = []
        for i, task in enumerate(tasks):
            result.append(self.task_cls.implied(task))
        super().__init__(result, **kw_super)


class TaskArray(TaskContainer, ContainerOfArray):
    '''a container for multiple tasks; each Task is a function, args, & kwargs.
    Calling self will perform all tasks, returning the result (and updating self.result as well).

    tasks: array-like of Tasks, iterables, or callables.
        the Tasks to be performed.
        any non-Task input will be used to create a Task.
        E.g. TaskArray([f1, (f2, args2), Task(f3, args3, kwargs3)])
            --> [Task(f1), Task(f2, args2), Task(f3, args3, kwargs3)]
    shape: None or tuple
        shape that the array of tasks should have.
        if None, infer tasks shape using self.task_nest_shape(tasks).
        if provided, use the specified shape instead of trying to infer it.
    checks: bool
        whether to perform checks on the inputs, and possibly convert inputs if needed.
        if False, assumes that tasks is already a numpy array of Task objects.
    assign_task_idx: {assign_task_idx}
    printable_process_name: {printable_process_name}
    errors_ok: {errors_ok}
    result_missing: {result_missing}
    '''
    def __init__(self, tasks, *, shape=None, checks=True, **kw_super):
        if checks:
            if shape is None:
                shape = self.task_nest_shape(tasks)
            tarr = np.empty(shape, dtype=object)
            for idx in np.ndindex(*shape):  # idx is a tuple of indices.
                # Assign tarr[idx] = tasks[idx], for all idx.
                # But, tasks might not be a numpy array, so we need to do multi-indexing.
                ti = tasks
                if len(idx)==0:
                    ti = ti[()]
                else:
                    for j in idx:
                        ti = ti[j]
                tarr[idx] = ti
            # convert each element of array into a Task
            for idx, task in np.ndenumerate(tarr):
                tarr[idx] = self.task_cls.implied(task)
            tasks = tarr
        super().__init__(tasks, **kw_super)

    @staticmethod
    def task_nest_shape(nested_list):
        '''returns the implied shape for numpy object array of tasks from nested_list.
        This will be the most natural shape to use if each element of nested_list
        is an iterable (e.g. tuple) or callable (e.g. function or Task),
        and there is no desire to iter(f) for any callable f in the nested_list.
        '''
        return nest_shape(nested_list, is_element=is_task_element)

    @classmethod
    def empty(cls, shape):
        '''return a TaskArray of shape shape, filled with UNSET_TASK.'''
        return cls(np.full(shape, UNSET_TASK, dtype=object), checks=False, assign_task_idx=False)


class TaskContainerCallKwargsAttrHaver():
    '''object with attrs corresponding to the main kwargs for TaskContainer.__call__.
    This includes ncpu, timeout, and ncoarse.
    It does not include kw, idx, reset, or skip_done.
    '''
    ncpu = simple_property('_ncpu', setdefaultvia='_default_ncpu',
        doc=_paramdocs_tasks['ncpu'] + '''
        see also: self.get_ncpu() to read actual number of cpus when self.ncpu is None.''')
    def _default_ncpu(self):
        '''returns default for ncpu. Here, returns None; i.e., use multiprocessing.cpu_count().'''
        return None

    def get_ncpu(self):
        '''returns ncpu, but if None, return multiprocessing.cpu_count() instead.
        (This is for convenience; using None will also work with any methods defined here.)
        '''
        return mp.cpu_count() if self.ncpu is None else self.ncpu

    timeout = simple_property('_timeout', setdefaultvia='_default_timeout', doc=_paramdocs_tasks['timeout'])
    def _default_timeout(self):
        '''returns default for timeout. Here, returns None; i.e., no time limit.'''
        return None

    ncoarse = simple_property('_ncoarse', setdefaultvia='_default_ncoarse', doc=_paramdocs_tasks['ncoarse'])
    def _default_ncoarse(self):
        '''returns default for ncoarse. Here, returns 1; i.e., do not group tasks.'''
        return 1

    print_freq = simple_property('_print_freq', setdefaultvia='_default_print_freq', doc=_paramdocs_tasks['print_freq'])
    def _default_print_freq(self):
        '''returns default for print_freq. Here, returns UNSET; i.e., infer from self.verbose.
        (See self.print_freq_explicit to get the actual value of print_freq.)
        '''
        return UNSET

    print_freq_explicit = alias('print_freq',
        doc='''like self.print_freq, but converts UNSET to value based on self.verbose,
        UNSET --> result depends on self.verbose:
            False or <=0 --> -1
            True or (>=1 and <5) --> None
            >=5 --> 0  (i.e. print every progress update)
            if self.verbose doesn't exist --> None
        if result would be None, instead give DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ.''')
    @print_freq_explicit.getter
    def print_freq_explicit(self):
        '''returns the actual value of print_freq, maybe inferred from self.verbose,
        and if None then convert to DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ.
        '''
        result = self.print_freq
        if result is UNSET:  # infer from self.verbose
            if hasattr(self, 'verbose'):
                if (not self.verbose) or (self.verbose <= 0):
                    result = -1
                elif self.verbose >= 5:
                    result = 0
                elif self.verbose:
                    result = None
            else:
                result = None
        if result is None:
            result = DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ
        return result

    def check_pickle(self, x=None):
        '''checks that self (or, x, if provided) is pickleable, by pickling then unpickling.
        Returns result of unpickling. Useful for debugging.
        '''
        obj = self if x is None else x
        dump = pickle.dumps(obj)
        load = pickle.loads(dump)
        return load


### --------------------- TaskGroup (helps with coarsen) --------------------- ###

@format_docstring(**_paramdocs_tasks)
class TaskGroup(Task, ContainerOfDict):
    '''treats a dict of Tasks as if it was a single Task.

    Helps with coarsen. Users probably don't need to think about TaskGroup directly.

    tasks: dict of Tasks
    errors_ok: tuple of Exception types
        the exception types for which to return result_missing instead of crashing, in case of error.
    result_missing: {result_missing}
    '''
    args = ()   # behave like a Task with no args
    kw = dict() # behave like a Task with no kwargs

    tasks = alias('data')

    def __init__(self, tasks, *, i=None, errors_ok=(), result_missing=RESULT_MISSING):
        self.tasks = dict(tasks)
        self.i = i
        self.errors_ok = errors_ok
        self.result_missing = result_missing

    def f(self, *args__None, **kw):
        '''perform all tasks in self, returning the results (as a dict)'''
        result = dict()
        errors_ok = self.errors_ok
        for i, task in self.enumerate():
            try:
                result[i] = task(**kw)
            except errors_ok:
                result[i] = self.result_missing
        return result


@format_docstring(**_paramdocs_tasks)
class TaskPartition(TaskList):
    '''a container for a list of TaskGroups, each with Tasks from the same TaskContainer.
    Knows to call each TaskGroup in parallel,
        but call in series the individual tasks within each TaskGroup.

    Helps with TaskContainer.coarsen.

    assign_task_idx: {assign_task_idx}
    printable_process_name: {printable_process_name}
    '''
    group_cls = TaskGroup  # class for any TaskGroups made by this TaskPartition
    groups = alias('tasks')

    def __init__(self, original, groups, **kw_super):
        self.original = original
        super().__init__(from_list=list(groups), **kw_super)

    @classmethod
    @format_docstring(**_paramdocs_tasks, sub_ntab=1)
    def from_task_container(cls, original, ncoarse=5, *, idx=None, errors_ok=UNSET, result_missing=UNSET):
        '''return a TaskPartition containing TaskGroups of size ncoarse.
        Useful for coarsening a TaskContainer for more efficient multiprocessing;
            grouping tasks together can reduce the overhead of multiprocessing,
            while still allowing for parallel processing as the groups are run in parallel.

        if idx is provided, only group the tasks with those indices.

        errors_ok: UNSET or {errors_ok}
            UNSET --> use original.errors_ok.
        result_missing: {result_missing}
            UNSET --> use original.result_missing.
        '''
        idxs0 = [i for i, task in original.enumerate(idx=idx)]
        idxs = [idxs0[i:i+ncoarse] for i in range(0, len(idxs0), ncoarse)]
        task_mappings = [{i:task for i,task in original.enumerate(idx=jdx)} for jdx in idxs]
        if errors_ok is UNSET: errors_ok = original.errors_ok
        if result_missing is UNSET: result_missing = original.result_missing
        kw_group = dict(errors_ok=errors_ok, result_missing=result_missing)
        printable_process_name = f'{cls.__name__}({original.printable_process_name}, ncoarse={ncoarse})'
        return cls(original, [cls.group_cls(tasks, **kw_group) for tasks in task_mappings],
                   printable_process_name=printable_process_name)

    def _assign_result_i(self, result_i, i):
        '''assign result_i to self.result[i], and also self.original.result[j] for all relevant j.'''
        self.result[i] = result_i
        for j, task in self[i].enumerate():
            self.original._assign_result_i(result_i[j], j)

    @format_docstring(**_paramdocs_tasks, sub_ntab=1)
    def __call__(self, *, kw=dict(), ncpu=None, timeout=None, print_freq=None):
        '''perform all tasks in all groups of self. return results formatted to original shape.

        kw: {kw}
        ncpu: {ncpu}
        timeout: {timeout}

        The following kwargs are acceptable for TaskContainer but NOT here:
            idx, reset, skip_done, ncoarse, errors_ok, result_missing.
        That is because idx, reset, skip_done, and ncoarse are not relevant,
        while errors_ok and result_missing are handled by the TaskGroups.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        call_result = super().__call__(kw=kw, ncpu=ncpu, timeout=timeout, print_freq=print_freq,
                                       errors_ok=False, # result_missing doesn't matter because errors_ok=False
                                       )
        for i, group in self.enumerate():
            result_i = call_result[i]
            for j, task in group.enumerate():
                self.original.result[j] = result_i[j]
        return self.original.result


### --------------------- Test Functions --------------------- ###

# test functions to help test/develop/debug multiprocessing codes^
def mptest_add100(x):
    '''adds 100 to x'''
    return x + 100

def mptest_sleep(t):
    '''sleeps for t seconds, then returns t'''
    time.sleep(t)
    return t

def mptest_sleep_add100(t):
    '''sleeps for t seconds, then returns t+100'''
    time.sleep(t)
    return t + 100

def mptest_echo(*args, **kw):
    '''print inputs then return (args, kw)'''
    print('args:', args)
    print('kw:', kw)
    return args, kw

class MPTestClass():
    '''empty class useful for multiprocessing testing.'''
    mem = dict()

    # def __init__(self):
    #     self.mem = dict()

    def update_mem(self, key, value):
        '''update self.mem with key, value. Print mem after.'''
        self.mem[key] = value
        print('after update_mem:', self.mem)

    def get_mem(self, key):
        '''return self.mem[key]. print mem before.'''
        print('before get_mem:', self.mem)
        return self.mem[key]
