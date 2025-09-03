"""
File Purpose: misc tests for eppic hookup in PlasmaCalcs.
"""

import os
import pickle
import pytest

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)


### --------------------- basics --------------------- ###

def get_eppic_calculator(eppic_i='test_eppic_basics.i', **kw_init):
    '''make an eppic calculator'''
    with pc.InDir(HERE):
        ec = pc.EppicCalculator.from_here(eppic_i, **kw_init)
    return ec


### --------------------- help --------------------- ###

def test_eppic_calculator_help():
    '''ensure that eppic calculator help doesn't crash.'''
    print('\n\n')
    print('--------------------- [test_eppic_calculator_help] START ---------------------')
    print('\n\n')
    # as classmethod
    pc.EppicCalculator.cls_help()  # allow to print this; it's not huge output
    pc.EppicCalculator.cls_help(print=False)
    pc.EppicCalculator.cls_help('', print=False)
    pc.EppicCalculator.cls_help('deltafrac_n', print=True)  # allow to print this; it's not huge output
    pc.EppicCalculator.cls_help('mod', print=False)
    pc.EppicCalculator.cls_help('q', print=False)
    pc.EppicCalculator.cls_help('', modules=True, print=False)
    pc.EppicCalculator.cls_help('', modules=True, dense=False, print=False)
    pc.EppicCalculator.cls_help('1+2', print=False)
    pc.EppicCalculator.cls_help('1+(2+3)', print=False)
    pc.EppicCalculator.cls_help('var_that_isnt_defined_anywhere')  # allow to print this; it's not huge output
    # as instance method
    ec = get_eppic_calculator()
    ec.help(print=False)  # could print this but decided not to.
    ec.help('', print=False)
    ec.help('deltafrac_n', print=True)  # allow to print this; it's not huge output
    ec.help('mod', print=False)
    ec.help('q', print=False)
    ec.help('', modules=True, print=False)
    ec.help('', modules=True, dense=False, print=False)
    ec.help('1+2', print=False)
    ec.help('1+(2+3)', print=False)
    ec.help('var_that_isnt_defined_anywhere')    # allow to print this; it's not huge output

    # calling help as classmethod by accident should crash:
    with pytest.raises(pc.InputError):
        pc.EppicCalculator.help()
    # calling class help for var depending on instance values should crash:
    with pytest.raises(pc.InputError):
        pc.EppicCalculator.cls_help('nusj')  # nusj needs to know ec.fluid...
    # calling help from instance should not crash:
    ec.help('nusj', print=False)
    # even if fluids change, still shouldn't crash:
    ec.fluid = 0
    ec.help('nusj', print=False)
    ec.fluid = [0,1]
    ec.help('nusj', print=False)
    print('\n\n')
    print('--------------------- [test_eppic_calculator_help] FINISH ---------------------')
    print('\n\n')


### --------------------- units --------------------- ###

def test_eppic_coords_units():
    '''ensure coords_units works as intended.
    See also: issue #4
    '''
    ec = get_eppic_calculator()
    assert ec.units == 'si'
    assert ec.coords_units is None  # i.e. "always match ec.units"
    assert ec.coords_units_explicit == 'si'
    ec.units = 'raw'
    assert ec.coords_units_explicit == 'raw'  # matches ec.units
    # ensure coords_units still matches ec.units even ec.using(...)
    ec.units = 'si'
    with ec.using(coords_units='raw'):
        pass
    assert ec.coords_units_explicit == 'si'
    ec.units = 'raw'
    assert ec.coords_units_explicit == 'raw'  # still matches ec.units
    ec.coords_units = 'raw'
    ec.units = 'si'
    assert ec.coords_units == 'raw'
    assert ec.coords_units_explicit == 'raw'  # no longer matches ec.units


### --------------------- timescales --------------------- ###

def test_eppic_timescales():
    '''ensure the EppicCalculator.timescales() method is working properly.'''
    # [TODO] actually test the values. (currently, just testing that it doesn't crash.)
    ec = get_eppic_calculator()
    ec.set_vars_from_inputs()
    ec.timescales()

def test_eppic_choose_params():
    '''ensure the EppicCalculator.choose_params() method is working properly.'''
    # [TODO] actually test the values... (currently, just testing that it doesn't crash.)
    ec = get_eppic_calculator()
    ec.set_vars_from_inputs()
    ec.choose_params()


### --------------------- fft_keep --------------------- ###

def test_fft_keep():
    '''ensure that the fft_keep property works as intended.'''
    ec = get_eppic_calculator()
    ec.fft_keep = None
    slices0 = ec.fft_slices.copy()
    ec.fft_keep = 0.1
    slices1 = ec.fft_slices.copy()
    assert slices1 != slices0  # setting keep adjusts fft_slices.
    with ec.using(fft_keep=None):
        assert ec.fft_slices == slices0  # setting keep adjusts fft_slices.
    # exiting a "using" block resets keep to old value, adjusting fft_slices.
    assert ec.fft_slices == slices1
    ec.fft_keep = 0.2
    for x in ec.maindims:
        assert ec.fft_slices.get_slice(f'freq_{x}') == slice(0.4, 0.6, None)
    ec.fft_keep = 0.3
    for x in ec.maindims:
        assert ec.fft_slices.get_slice(f'freq_{x}') == slice(0.35, 0.65, None)
    assert len(ec.maindims)>0  # i.e., that loop iterated over a non-empty list^
    # test that using half works too.
    x = ec.maindims[0]
    ec.fft_keep = 0.3
    ec.fft_half = x
    assert ec.fft_slices.get_slice(f'freq_{x}') == slice(0.5, 0.65, None)
    for y in ec.maindims[1:]:
        assert ec.fft_slices.get_slice(f'freq_{y}') == slice(0.35, 0.65, None)


### --------------------- multiprocessing --------------------- ###

def test_eppic_pickling():
    '''ensure that EppicCalculator can be pickled & unpickled.'''
    ec = get_eppic_calculator()
    # immediately after initializing:
    dump = pickle.dumps(ec)
    _tmp = pickle.loads(dump)
    # after running a calculation (which doesn't depend on any vars):
    ec('0')
    dump = pickle.dumps(ec)
    _tmp = pickle.loads(dump)
    # after setting vars:
    ec.set_vars_from_inputs()
    dump = pickle.dumps(ec)
    _tmp = pickle.loads(dump)
    # after getting a set var
    ec('n')
    dump = pickle.dumps(ec)
    _tmp = pickle.loads(dump)

def test_eppic_simple_mp_compatible():
    '''ensure that multiprocessing doesn't cause crashes when doing simple things.
    Not guaranteed to test that multiprocessing is actually occurring...
    but guaranteed to ensure that multiprocessing isn't interfering with simple things.
    '''
    ec = get_eppic_calculator()
    ec.ncpu = 2
    # immediately after initializing
    ec('0')
    # from input deck
    ec('n0')  # should get n0 for multiple fluids
    # when setting vars
    ec.set_vars_from_inputs()
    # after setting vars
    ec('n')
