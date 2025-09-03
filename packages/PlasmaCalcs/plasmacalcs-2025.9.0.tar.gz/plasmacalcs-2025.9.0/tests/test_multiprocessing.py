"""
File Purpose: testing multiprocessing
"""

import pickle

import numpy as np
import pytest

import PlasmaCalcs as pc

MAX_TIMEOUT = 15  # timeout after this many seconds for each test below;
# in case something goes horribly wrong! (don't want to waste gitlab CI time for no reason...)

### --------------------- multiprocessing generic --------------------- ###

def test_multiprocessing_basics():
    '''test that basic multiprocessing works.'''
    for ncpu in [1,2]:  # (when ncpu=1, will not use multiprocessing. When ncpu=2, will use it.)
        # ensure that timeout works:
        with pytest.raises(pc.TimeoutError):
            tasks = pc.TaskList((pc.mptest_sleep, 2), (pc.mptest_sleep, 2))
            tasks(ncpu=ncpu, timeout=1)

        # ensure that results are correct:
        tasks = pc.TaskList([pc.mptest_add100, 1], [pc.mptest_add100, 2], [pc.mptest_add100, 3])
        results = tasks(ncpu=ncpu, timeout=MAX_TIMEOUT)
        assert results == [101, 102, 103]

        # ensure that it works even with lots of tasks:
        tasks = pc.TaskList(*[(pc.mptest_add100, i) for i in range(100)])
        results = tasks(ncpu=ncpu, timeout=MAX_TIMEOUT)
        assert results == [i+100 for i in range(100)]

 # [TODO] test TaskArray

def test_multiprocessing_being_used():
    '''test that multiprocessing is ACTUALLY being used.'''
    # if the tasks are not actually being run with multiprocessing, this test will fail;
    # sleeping for 4 seconds, twice in a row, in less than 6 seconds total, is impossible!!!
    # but if the sleeps are run in parallel, then it will be possible :)
    #
    # (this test assumes that the multiprocessing overhead here will take less than 2 seconds;
    #  if the overhead takes longer than 2 seconds, this test will fail erroneously.)
    with pc.TimeLimit(6):
        tasks = pc.TaskList([pc.mptest_sleep, 4], [pc.mptest_sleep, 4])
        # ensure that multiprocessing is ACTUALLY being used:
        results = tasks(ncpu=2, timeout=MAX_TIMEOUT)


### --------------------- multiprocessing + sentinels --------------------- ###

def assert_is_unset(unset):
    '''asserts that unset is pc.UNSET.
    Defined as a top-level function so it can be compatible with multiprocessing.
    '''
    assert unset is pc.UNSET

def test_basic_sentinels():
    '''test that basic sentinels work with multiprocessing.'''
    timeout = 10  # timeout after 10 seconds. In case something goes horribly wrong.
    tasks = pc.TaskList((assert_is_unset, pc.UNSET), (assert_is_unset, pc.UNSET))
    tasks(ncpu=2, timeout=timeout)

    tasks_many = pc.TaskList(*[(assert_is_unset, pc.UNSET) for _ in range(100)])
    tasks_many(ncpu=2, timeout=timeout)

def assert_is_missing_snap(missing_snap):
    '''asserts that missing_snap is pc.MISSING_SNAP.
    Defined as a top-level function so it can be compatible with multiprocessing.
    '''
    assert missing_snap is pc.MISSING_SNAP

def test_dimension_value_sentinels():
    '''test that UniqueDimensionValue objects work with multiprocessing.'''
    timeout = 10  # timeout after 10 seconds. In case something goes horribly wrong.
    tasks = pc.TaskList((assert_is_missing_snap, pc.MISSING_SNAP), (assert_is_missing_snap, pc.MISSING_SNAP))
    tasks(ncpu=2, timeout=timeout)


### --------------------- picklable PlasmaCalculator --------------------- ###

def test_picklable_plasma_calculator():
    '''test that PlasmaCalculator instance can be pickled (i.e. is compatible with multiprocessing)'''
    p = pc.PlasmaCalculator()
    # immediately after initialization
    dump = pickle.dumps(p)
    _tmp = pickle.loads(dump)
    # after getting a var
    p('0')
    dump = pickle.dumps(p)
    _tmp = pickle.loads(dump)
