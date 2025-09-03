"""
File Purpose: misc tests for eppic hookup in PlasmaCalcs.
These tests require some simulation output.
Not intended to read lots of different values,
    just to read a few specific/misc. values to check if they work properly.
"""
import os
import pytest

# setting mp start method to fork (instead of 'spawn') prevents leaked semaphore objects. Not sure why.
# it also makes the tests a bit faster, maybe...
import multiprocessing as mp
mp.set_start_method('fork', force=True)

import numpy as np
import xarray as xr

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)


### --------------------- can create eppic calculator --------------------- ###

def get_eppic_calculator(**kw_init):
    '''make an eppic calculator'''
    with pc.InDir(os.path.join(HERE, 'test_eppic_tinybox')):
        ec = pc.EppicCalculator.from_here(**kw_init)
    return ec

def test_make_eppic_calculator():
    '''ensure can make an eppic calculator (with various inputs to __init__).'''
    get_eppic_calculator()
    get_eppic_calculator(snaps_from='timers')
    get_eppic_calculator(kw_units=dict(M=1))

### --------------------- can load moments --------------------- ###

def test_load_moment():
    '''ensure we can load moment related values'''
    ec = get_eppic_calculator()  # defined earlier in this file
    ec('moment1')               # just checking to ensure these don't crash
    ec('moment2')               
    ec('moment3')               
    ec('moment4')

### --------------------- runtimes --------------------- ###

def test_reading_runtimes():
    '''test reading runtimes from eppic timers.dat'''
    ec = get_eppic_calculator()
    with pytest.raises(ValueError):
        ec('runtimes')  # fails because snap 0 file was deleted but timer is known for it.
    ec = get_eppic_calculator(snaps_from='timers')
    arr = ec('runtimes')  # just checking that this doesn't crash!
    arr = ec('calc_timestep_cost')
    assert arr.size == len(ec.snap)

def test_reading_clocktimes():
    '''test reading clock_times from logfile.'''
    ec = get_eppic_calculator(snaps_from='timers')
    # ensure can read clock times
    ec('clock_times')
    # this run took 19 seconds
    # (according to start & stop times. Total job time was actually 23 seconds.
    #   but 4 seconds of that might have been slurm processing stuff.)
    assert ec('total_seconds', item=True) == 19
    # timers.dat units are (experimentally found to be) roughly 1 [timer unit] == 0.01 [seconds].
    assert abs(100 - (ec('run_time').sum() / ec('steps_seconds'))) < 5


### --------------------- multi_slices --------------------- ###

def test_reading_multi_slices():
    '''test reading when using multi_slices.
    Also confirms Dataset.pc.size works properly.
    '''
    ec = get_eppic_calculator()
    with ec.using(multi_slices=dict(ndim=1, ikeep=0)):
        ds = ec('n')
    with ec.using(slices=dict(x=0)):
        arr_x0 = ec('n')
    with ec.using(slices=dict(y=0)):
        arr_y0 = ec('n')
    assert np.all(ds['keep_x'] == arr_y0)  # keep x <--> used y=0 slice
    assert np.all(ds['keep_y'] == arr_x0)  # keep y <--> used x=0 slice
    assert ds.pc.size == arr_x0.pc.size + arr_y0.pc.size


### --------------------- enable_fromfile=False --------------------- ###

def test_enable_fromfile():
    '''test reading when using enable_fromfile=False.'''
    ec = get_eppic_calculator()
    # ensure can load normally
    m0 = ec('m', enable_fromfile=True)
    n0 = ec('n', enable_fromfile=True)
    # when load_direct_fromfile disabled, can load m (doesn't depend on file) but not n.
    m1 = ec('m', enable_fromfile=False)
    assert m1.identical(m0)
    with pytest.raises(pc.QuantCalcError):
        _should_crash = ec('n', enable_fromfile=False)
    # double-check that setting attribute via calculator produces the same behavior
    ec.enable_fromfile = True
    m2 = ec('m')
    assert m2.identical(m0)
    n2 = ec('n')
    assert n2.identical(n0)
    ec.enable_fromfile = False
    m3 = ec('m')
    assert m3.identical(m0)
    with pytest.raises(pc.QuantCalcError):
        _should_crash2 = ec('n')


### --------------------- multiprocessing + parenthesis --------------------- ###

def test_mp_with_parenthesis():
    '''ensure can run multiprocessing with parenthesis.'''
    # it can be tricky because parenthesis_memory is a class variable,
    # and pickling doesn't include changes to class or global variables, by default.
    # this ensures that the __getstate__ & __setstate__ solution works properly
    ec = get_eppic_calculator()
    ec.ncpu = 2
    ec('(n0)')
    ec('(deltafrac_n+1)*7')
    ec('mean_(n)')
    ec('nmean_(u**2)', stats_dimpoint_wise=False)
    ec('nmean_(u**2)', stats_dimpoint_wise=True)

## [TODO] DISABLED TEST_MP_TIMEOUT UNTIL FURTHER NOTICE
## I'm tired of gitlab runner failing this test inconsistently;
## it seems like sometimes gitlab CI can handle it but other times it can't.
## last time it crashed, the logs looked like:
# tests/test_eppic/test_eppic_reading_misc.py::test_mp_with_parenthesis PASSED
# tests/test_eppic/test_eppic_reading_misc.py::test_mp_timeout [test_mp_timeout] started
# [test_mp_timeout] got eppic calculator
# [test_mp_timeout] about to check ec(longvar, ncpu=1) for 10 snaps
# [test_mp_timeout] ec(longvar, ncpu=1) for 10 snaps took 1.46e-01 seconds
# [test_mp_timeout] setting NSNAP=684 to make computations take "a long time" (approx 10 seconds).
# [test_mp_timeout] starting ec(longvar, ncpu=1, timeout=1) for 684 snaps
# Terminated
# WARNING: step_script could not run to completion because the timeout was exceeded.
## I gave step_script 5 mins total to run, so 10 seconds should have completed.
## Most likely the timeout code itself is causing the error;
## maybe sometimes gitlab doesn't like SIGALRM??
## Can re-enable if you want to debug. Probably do it in a separate branch though.

# takes roughly 2 seconds, but run after test_mp_with_parenthesis,
#   so that we don't run this until we know ncpu>1 actually works on this machine.
# def test_mp_timeout():
#     '''ensure eppic calculator will timeout properly.'''
#     # this test has print statements because pytest will print them if the test fails,
#     #   and this test seems to fail inconsistently on some of the gitlab runners.
#     #   the prints will hopefully help debug why it fails on some runners but not others.
#     print(f'[test_mp_timeout] started', flush=True)  # flush=True --> print ASAP.
#     ec = get_eppic_calculator()
#     print(f'[test_mp_timeout] got eppic calculator', flush=True)
#     longvar = 'stats_lowpass_(u_drift**2)'  # something that takes a while to calculate
#     # check time it takes to calculate:
#     ec.snap = slice(10)
#     assert len(ec.snap) == 10  # there are at least 10 snaps in eppic_tinybox.
#     print(f'[test_mp_timeout] about to check ec(longvar, ncpu=1) for 10 snaps', flush=True)
#     with pc.Stopwatch(printing=False) as watch:
#         ec(longvar, ncpu=1, snap=ec.snap[:10])
#     time10 = watch.time_elapsed()
#     print(f'[test_mp_timeout] ec(longvar, ncpu=1) for 10 snaps took {time10:.2e} seconds', flush=True)
#     time_per_snap = time10 / 10
#     safety = 10
#     timeout = 1
#     NSNAP = int(safety * timeout / time_per_snap)  # should take roughly [safety * timeout] seconds.
#     print(f'[test_mp_timeout] setting NSNAP={NSNAP} to make computations take "a long time" (approx 10 seconds).', flush=True)
#     ec.snap = [i%10 for i in range(NSNAP)]
#     assert time10 * NSNAP/10 > 1.1  # ensure longvar actually takes > 1s to calculate, when doing NSNAP snaps.
#     # check timeout when ncpu=1 (i.e., single processing)
#     with pc.Stopwatch(printing=False) as watch:
#         print(f'[test_mp_timeout] starting ec(longvar, ncpu=1, timeout=1) for {NSNAP} snaps', flush=True)
#         with pytest.raises(pc.TimeoutError):
#             ec(longvar, ncpu=1, timeout=1)   # ensure timeout works when ncpu=1
#     print(f'[test_mp_timeout] ec(longvar, ncpu=1, timeout=1) for {NSNAP} snaps, timeout after {watch.time_elapsed():.2e} seconds', flush=True)
#     assert len(ec.snap) == NSNAP  # ensure original snaps restored even after TimeoutError.
#     # check timeout when ncpu=2 (i.e., multiprocessing)
#     with pc.Stopwatch(printing=False) as watch:
#         print(f'[test_mp_timeout] starting ec(longvar, ncpu=2, timeout=1) for {NSNAP} snaps', flush=True)
#         with pytest.raises(pc.TimeoutError):
#             ec(longvar, ncpu=2, timeout=1)   # ensure timeout works when ncpu>1
#     print(f'[test_mp_timeout] ec(longvar, ncpu=2, timeout=1) for {NSNAP} snaps, timeout after {watch.time_elapsed():.2e} seconds', flush=True)


### --------------------- misc small multiprocessing --------------------- ###
# e.g., ensure https://gitlab.com/Sevans7/plasmacalcs/-/issues/2 does not appear again;
# that issue was: Can't pickle local object 'EppicBasesLoader._get_T_neutral.<locals>.Tn_loader'

def test_mp_small_misc():
    '''ensure small misc vars do not crash when ncpu > 1.'''
    ec = get_eppic_calculator()
    ec.ncpu = 2
    ec('T_n')
    ec('moment1')
    ec('moment2')
    ec('moment3')
    ec('moment4')
    # ec('vdist', fluid=0)  # would be nice to check, but vdist is not saved in tinybox.
