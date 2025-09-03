"""
File Purpose: timers, runtime profiling
"""

import cProfile
import pstats
import time
import signal

from ..errors import TimeoutError
from ..defaults import DEFAULTS


### --------------------- Runtime Profiling --------------------- ###

class Profile(cProfile.Profile):
    '''runtime profiler. Usage:
    p = Profile()
    with p:
        >> code to profile goes here <<
    p.print_stats()  # or p.print_stats(key), key='time', 'cumulative', or other key from self.SortKey

    This whole class is a "thin" wrapper around cProfile & pstats
    For a more lightweight form of this class, you can use:
        import cProfile
        p = cProfile.Profile()
        with p:
            >> code to profile goes here <<
        p.print_stats('time')

    sortkey: 'time', 'cumulative', or other key from self.SortKey
        tells default way to sort stats during print_stats.
    clearing: bool, default True
        whether to self.clear() when starting to profile.
        (i.e., when self.enable() is called. Note that self.__enter__() calls self.enable().)
    '''
    def __init__(self, *args, sortkey='time', clearing=True, **kw):
        '''does super().__init__ but also sets self.sortkey.'''
        super().__init__(*args, **kw)
        self.sortkey = sortkey
        self.clearing = clearing

    SortKey = pstats.SortKey  # << for easy reference. See e.g. help(self.SortKey) for details.

    def print_stats(self, sortkey=None):
        '''super().print_stats() using sortkey or self.sortkey if None'''
        if sortkey is None: sortkey = self.sortkey
        super().print_stats(sortkey)

    def enable(self, *args__super, clearing=None, **kw__super):
        '''super().enable(), but first maybe call self.clear().
        clearing: None or bool, default None
            whether to first call self.clear().
            None --> use clearing = self.clearing.
        '''
        if clearing is None: clearing = self.clearing
        if clearing:
            self.clear()
        super().enable(*args__super, **kw__super)

PROFILE = Profile()
def profiling(sortkey=None):
    '''returns default profiler, PROFILE. Sets its sortkey if provided.
    see help(PROFILE.SortKey) for sortkey options.

    Example Usage:
        with profiling():
            >> code to profile goes here <<
        print_profile()
    '''
    if sortkey is not None: PROFILE.sortkey = sortkey
    return PROFILE

def print_profile(sortkey=None):
    '''prints stats from the default profiler (PROFILE).
    see help(PROFILE.SortKey) for sortkey options.

    Example Usage:
        with profiling():
            >> code to profile goes here <<
        print_profile()
    '''
    PROFILE.print_stats(sortkey)

def start_profiling():
    '''equivalent to PROFILE.enable(). Recommended: use profiling() as a context manager instead.
    Example Usage:
        start_profiling()
        >> code to profile goes here <<
        stop_profiling()
    '''
    PROFILE.enable()

def stop_profiling():
    '''equivalent to PROFILE.disable(). Recommended: use profiling() as a context manager instead.
    Example Usage:
        start_profiling()
        >> code to profile goes here <<
        stop_profiling()
    '''
    PROFILE.disable()


### --------------------- Timers --------------------- ###

class Stopwatch():
    '''tracks time since last clear (via self.reset()), or last "marked" time (via self.mark_time()).
    All times are in seconds.

    printing: bool, default True
        whether to print self when exiting context, if self was used as a context manager.

    Can also be used as a context manager, to time a block of code:
        with Stopwatch() as watch:
            >> code to time goes here <<
        print(watch)  # or, if watch.printing=True, this would already be printed, automatically.

    Note that re-using an instance of Stopwatch as a context manager will reset it:
        with Stopwatch() as watch:
            >> code block 1 <<
        watch.time   # time it took to run code block 1
        with watch:  # <-- calls watch.reset() when entering block.
            >> code block 2 <<
        watch.time   # time it took to run code block 2
    '''
    # _t_0: time at "t=0". Set by self.reset()
    # _t_marks: "marked" times (a dict). Default has key=None.
    #             Set by self.mark_time(). Note: self.reset() also removes ALL marked times.
    # _t_create: time when self was created (never changes).
    def __init__(self, printing=True):
        self.reset()
        self._t_create = self._t_0
        self.printing = printing

    # time coordinate setters #
    def reset(self, *, _time=None):
        '''sets "t=0" time to now (or _time, if provided). Also removes all "marked" times.'''
        self._t_0 = self.now() if _time is None else _time
        self._t_marks = dict()  # << reset "marked" times.

    def mark_time(self, key=None, *, _time=None):
        '''sets "marked" time to now (or _time, if provided).
        key: hashable object, default None
            associate marked time with this key. (None --> "default" marked time.)
        '''
        self._t_marks[key] = self.now() if _time is None else _time

    # time getters #
    time = property(lambda self: self.time_since_reset, doc='''alias to self.time_since_reset''')
    time_elapsed = time   # << another alias to time_since_reset

    def time_since_reset(self):
        '''returns time [in seconds] since the "t=0" time on this watch.
        "t=0" set by self.reset(). Also set when created.
        '''
        return self.now() - self._t_0

    def time_since_mark(self, key=None):
        '''returns time [in seconds] since the "mark" time on this watch.
        "mark" set by self.mark_time(). Also set when created or reset().

        key: hashable object, default None
            "marked time" associated with this key.
        '''
        return self.now() - self.get_marked_time(key=key)

    def get_marked_time(self, key=None):
        '''returns marked time associated with this key.'''
        return self._t_marks.get(key, self._t_0)

    def get_marked_times(self):
        '''returns dict of marked times.'''
        return self._t_marks

    @staticmethod
    def now():
        '''returns time.time(). Provided as a static method for convenience.'''
        return time.time()

    # context manager #
    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.printing:
            print(self)

    # display #
    def __repr__(self):
        return f'{type(self).__name__}(time_since_reset = {self.time_since_reset():.2f} seconds)'

    def time_elapsed_string(self, as_string=False):
        '''returns string 'Total time elapsed: {:.2f} seconds.'.format(self.time_since_reset())'''
        return f'Total time elapsed: {self.time_since_reset():.2f} seconds.'


class TickingWatch(Stopwatch):
    '''Stopwatch that also "ticks" every N seconds.
    No active background process; just checks time, when queried. See self.tick().
    
    self.tick() returns whether at least N seconds have passed since the "marked" time,
        AND if the result is True, sets the "marked" time to now.
    self.nticks tracks the number of times self.tick() ever returned True.
        note: self.nticks resets to 0 when self.reset() is called.

    interval: int (possibly negative or 0)
        N. Number of seconds between ticks.
        >0 --> minimum time between calls to self.tick() returning True.
        =0  --> self.tick() will always return True.
        <0 --> self.tick() will always return False.
    wait: bool, default True
        whether the first True tick() may require waiting.
        False --> the first call to self.tick() will always give True.
        True --> the first call to self.tick() will only give True if self.interval seconds have passed.
    _t_mark_key: hashable object, default 'tick'
        key associated with the "marked" time for ticking.
        note: if None, ticks are stored in the "default marked time" key; see Stopwatch for details.
    '''
    def __init__(self, interval, *, wait=True, _t_mark_key='tick'):
        super().__init__()
        self.interval = interval
        self.wait = wait
        self.waiting = wait  # << whether we are waiting for tick.
        self._t_mark_key = _t_mark_key

    def reset(self, **kw):
        '''resets the "t=0" time, also set self.nticks=0.'''
        super().reset(**kw)
        self.nticks = 0

    def time_since_tick(self):
        '''get time since last tick. Note: does not edit the "marked" time.'''
        return self.time_since_mark(key=self._t_mark_key)

    def _mark_tick_time(self, *, _time=None):
        '''mark time of this tick. Intended for internal use, only.'''
        self.mark_time(key=self._t_mark_key, _time=_time)

    def tick(self):
        '''returns True if enough time has passed for the next tick.
        If True, also "marks" the current time, as the previous tick time.
        "Enough time" usually means at least self.interval seconds.
        Exceptions:
            if not self.waiting, return True (and set self.waiting = False)
            if interval < 0, return False.
        '''
        if self.interval < 0:
            result = False
        elif not self.waiting:
            result = True
            self.waiting = True
        else:
            result = (self.time_since_tick() >= self.interval)
        if result:
            self.nticks += 1
            self._mark_tick_time()
        return result


### --------------------- Progress updates --------------------- ###

class ProgressUpdater(TickingWatch):
    '''class for printing messages but only when enough time has passed.
    "Enough" is defined by the input parameter print_freq (in seconds).

    print_freq: None or int (possibly negative or 0)
        Number of seconds between progress updates.
        None --> use DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ
        >0 --> minimum time between calls to self.tick() returning True.
        =0  --> self.tick() will always return True.
        <0 --> self.tick() will always return False.
    wait: bool, default False
        whether to wait until print_freq seconds has passed before doing the first printout.
    print_time: bool, default False
        whether to print time by default
    clearline: bool, default True
        whether to clear the current line before printing.
    clearN: int, default 100
        number of characters to clear if clearing a line.

    Example:
        updater = ProgressUpdater(print_freq=2, wait=True)
        updater.print('This will not be printed')   # not printed because 2 seconds have not passed yet.
        time.sleep(2.5)  # << wait 2.5 seconds. (Or, put code here which takes >= 2 seconds)
        updater.print('This WILL be printed!')      # prints, then timer is reset,
        updater.print('This will not be printed')   # so it won't print again until 2 more seconds have passed.
    '''
    def __init__(self, print_freq=None, *, wait=False, print_time=True, clearline=True, clearN=100,):
        if print_freq is None:
            print_freq = DEFAULTS.PROGRESS_UPDATES_PRINT_FREQ
        super().__init__(interval=print_freq, wait=wait)
        self.print_time = print_time
        self.clearline  = clearline
        self.clearN     = clearN
    
    print_freq = property(lambda self: getattr(self, 'interval'),
                          lambda self, value: setattr(self, 'interval', value),
                          doc='''alias for self.interval''')

    def print_clear(self, N=None, force=False):
        r'''clears current printed line, and moves cursor to beginning of the line.
        only if self.clearline AND self has printed at least 1 message. OR if force.

        troubleshooting: did you use end='', e.g. print(..., end='')?
            (If not, your print statement may go to the next line.)

        N: None or int
            number of characters to clear.
            None --> use self.clearN instead.
        force: bool, default False
            whether to force print, even if not self.clearline.
            False --> require self.clearline, else don't print.

        Equivalent to:
            print('\r'+ ' '*N +'\r', end='')
        '''
        if force or (self.clearline and self.nticks > 0):
            if N is None: N = self.clearN
            print('\r'+ ' '*N +'\r', end='')

    def message_to_print(self, *args_message, sep=' '):
        '''returns message that would be printed, including info about time elapsed.
        Equivalent to message printed by self.print(...), if it's time to print an update.
        '''
        return sep.join((*args_message, self.time_elapsed_string()))

    def force_print(self, *args_message, end='', print_time=None, **kw__print):
        '''prints, without first checking whether to print.
        Clear the line first, if self.clearline.
        print_time: None or bool
            whether to print f'Total time elapsed: {format(t):.2f} seconds.'
            None --> use self.print_time (default: True)
        '''
        self.print_clear()
        if print_time or ((print_time is None) and self.print_time):
            args_message = (*args_message, self.time_elapsed_string())
        print(*args_message, end=end, **kw__print)

    def print(self, *args_message, end='', print_time=None, **kw__print):
        '''prints message given by *args_message, if it is time to print.
        Clear the line first, if self.clearline.
        print_time: None or bool
            whether to print f'Total time elapsed: {format(t):.2f} seconds.'
            None --> use self.print_time (default: True)
        '''
        if self.tick():
            self.force_print(*args_message, end=end, print_time=print_time, **kw__print)

    def printf(self, f=lambda: '', *, end='', print_time=None, **kw__print):
        '''prints message given by calling f() (which must return a single string).
        [EFF] note: only calls f() if actually printing!
            Can use this instead of self.print() if computing the print message might be expensive.

        Clear the line first, if self.clearline.
        print_time: None or bool
            whether to print f'Total time elapsed: {format(t):.2f} seconds.'
            None --> use self.print_time (default: True)

        Example:
            updater = ProgressUpdater(print_freq=2)
            updater.printf(lambda: '{} '.format(object_whose_string_is_expensive_to_calculate))
        '''
        if self.tick():
            message = f()
            self.force_print(message, end=end, print_time=print_time, **kw__print)

    def finalize(self, process_name=None, *, always=False, **kw__print):
        '''prints 'Completed process in 0.00 seconds!', filling in the process name and time elapsed as appropriate.
        Also, clear the line first, if self.clearline.

        process_name: None (default) or string
            None --> don't print any info about the process which completed.
            string --> include this name in the finalize message.
        always: False (default) or True
            False --> ignore this kwarg.
            True --> always print the finalize message.
        '''
        time_elapsed = self.time()
        if (always) or (self.nticks > 0):
            process_name = '' if process_name is None else repr(process_name) + ' '
            message = f'Completed {process_name}in {time_elapsed:.2f} seconds!'
            self.force_print(message, print_time=False, **kw__print)


### --------------------- Execution time limiter --------------------- ###

class TimeLimit():
    '''context manager which imposes a time limit, exiting with TimeoutError if internal code takes too long.
    Usage example:
        with TimeLimit(10):
            # any code in this block must complete within 10 seconds, else will crash with TimeoutError.

    seconds: None or int
        timeout after this many seconds (unless code completes before then).
        Must be an integer, due to limitations of signal.alarm method.
        None, or <=0 --> no time limit
    '''
    def __init__(self, seconds):
        if seconds is None:
            seconds = 0
        self.seconds = seconds

    now = staticmethod(time.time)  # << for easy reference.

    def time_elapsed(self):
        '''returns time elapsed since entering the context.'''
        return self.now() - self.start_time

    def signal_handler(self, _signum, _frame):
        '''raise TimeoutError.'''
        raise TimeoutError(f"Timed out after {self.time_elapsed():.2g} seconds.")

    def __enter__(self):
        self.start_time = time.time()
        if self.seconds > 0:
            signal.signal(signal.SIGALRM, self.signal_handler)
            signal.alarm(self.seconds)  # raise signal.SIGALRM in this many seconds from now.
            self.set_alarm = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if getattr(self, 'set_alarm', False):
            signal.alarm(0)  # cancel any remaining alarms.
