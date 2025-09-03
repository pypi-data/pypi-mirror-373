"""
File Purpose: basic test for bifrost hookup in PlasmaCalcs.
These tests require the snapname_NNN.idl file(s), but not any simulation output data.
"""
import os
import pytest

import numpy as np

import PlasmaCalcs as pc

HERE = os.path.dirname(__file__)
RUNDIR = os.path.join(HERE, 'test_bifrost_nodata')
SNAPNAME = 'l2d90x40r_it'  # snapname for the tests here.


### --------------------- basics --------------------- ###

def get_bifrost_calculator(snapname=None, **kw_init):
    '''make a bifrost calculator'''
    with pc.InDir(RUNDIR):
        bc = pc.BifrostCalculator(snapname=snapname, **kw_init)
    return bc

def test_make_bifrost_calculator():
    '''ensure can make a bifrost calculator, when snapname is known.'''
    get_bifrost_calculator(snapname=SNAPNAME)


### --------------------- inferring snapname --------------------- ###

def test_bifrost_infer_snapname():
    '''ensure can infer snapname from directory, when snapname is not provided.'''
    with pc.InDir(RUNDIR):
        snapname = pc.bifrost.bifrost_infer_snapname_here()
    assert snapname == SNAPNAME
    snapname = pc.bifrost.bifrost_infer_snapname_here(dir=RUNDIR)
    assert snapname == SNAPNAME
    # making bifrost calculator without supplying snapname only possible if snapname can be inferred.
    bc = get_bifrost_calculator(snapname=None)  # <-- just trying to ensure no crash.
    # ensure crash if snapname can't be inferred.
    #   (Ambiguity especially important to test, to avoid anyone accidentally reading the wrong data!)
    SNAPNAME_MISSING_DIR = os.path.join(HERE, 'test_infer_snapname', 'missing_crash')
    assert os.path.isdir(SNAPNAME_MISSING_DIR)
    with pytest.raises(FileNotFoundError):
        snapname = pc.bifrost.bifrost_infer_snapname_here(dir=SNAPNAME_MISSING_DIR)
    SNAPNAME_AMBIGUOUS_DIR = os.path.join(HERE, 'test_infer_snapname', 'ambiguous_crash')
    assert os.path.isdir(SNAPNAME_AMBIGUOUS_DIR)
    with pytest.raises(pc.FileAmbiguityError):
        snapname = pc.bifrost.bifrost_infer_snapname_here(dir=SNAPNAME_AMBIGUOUS_DIR)


### --------------------- Units --------------------- ###

def test_bifrost_units():
    '''test bifrost units, also tests some of the cgs unit conversions code'''
    bc = get_bifrost_calculator()
    assert bc.u is not None
    assert isinstance(bc.u, pc.bifrost.BifrostUnitsManager)
    # ensure units kwarg is working
    bc = get_bifrost_calculator(units='raw')
    assert bc.u.units == bc.units == 'raw'
    bc = get_bifrost_calculator(units='si')
    assert bc.u.units == bc.units == 'si'
    bc = get_bifrost_calculator(units='cgs')  # ensure units='cgs' works too
    assert bc.u.units == bc.units == 'cgs'
    bc.units = 'si'
    assert bc.u.units == bc.units == 'si'
    # ensure default output is SI when .units == 'si'
    assert bc.u('l') == bc.u('l', 'si')
    assert bc.u('r') == bc.u('r', 'si')
    # try to get some other units just to ensure it's possible:
    for ustr in ('acceleration', 'current_density', 'temperature', 'pressure',
                 'flux', 'momentum_density', 'permittivity', 'capacitance',
                 'e_field', 'ef', 'b_field', 'b', 'force', 'power', 'volume',
                 'speed', 'q', 'charge', 'dimensionless', 'time', 'mass'):
        bc.u(ustr)
    # units test -- ensure can get conversion factors for all KNOWN:
    for key, ustr in bc.u.KNOWN.items():
        bc.u(ustr)
    # check units math works out properly:
    assert bc.u('l')**2 == bc.u('l2') == bc.u('area')
    assert bc.u('l')**-3 == bc.u('l-3') == bc.u('number_density') == bc.u('volume-1')
    assert bc.u('r')**-0.25 * bc.u('b')**3.7 == bc.u('r-0.25 b3.7')
    # checking units from params (bc.params tell conversions in cgs)
    assert bc.params is bc.params  # <-- ensure not recalculating params each time
    assert bc.u('l') * 1e2  == bc.params['u_l'] == bc.u('l', 'cgs')
    assert bc.u('t')        == bc.params['u_t'] == bc.u('t', 'cgs')
    assert bc.u('r') * 1e-3 == bc.params['u_r'] == bc.u('r', 'cgs')
    # check unit conversions:
    assert bc.u('l', 'si', convert_from='cgs') == 1e-2
    assert bc.u('l', 'cgs', 'si') == 1e2
    assert bc.u('M', 'cgs', 'si') == 1e3 == 1 / bc.u('M', 'si', 'cgs')
    assert bc.u('r', 'cgs', 'si') == 1e3 / (1e2)**3
    # check physical parameters:
    assert np.isclose(bc.u('amu', 'si'), bc.u.PHYSICAL_CONSTANTS_SI['amu'][0])
    assert np.isclose(bc.u('amu', 'cgs'), bc.u.PHYSICAL_CONSTANTS_SI['amu'][0] * 1e3)
    assert np.isclose(bc.u('c', 'si'), 2.99792E8)
    for pconst, (val, unit) in bc.u.PHYSICAL_CONSTANTS_SI.items():
        assert np.isclose(bc.u(pconst, 'si'), val)
    for pconst in ('amu', 'c', 'kB', 'me', 'h', 'eV', 'eV kB-1'):
        val, unit = bc.u.PHYSICAL_CONSTANTS_SI[pconst]
        assert np.isclose(bc.u(pconst, 'cgs'), val * bc.u(unit, 'cgs', 'si'))
    # for cgs, E & M quantities raise UnitsUnknownError:
    u = pc.UnitsManager()
    ucgs = u.CGS_UNITS
    for quant in ('q', 'b', 'ef', 'permittivity', 'permeability'):  # misc E & M conversion factors
        with pytest.raises(pc.UnitsUnknownError):
            ucgs(quant, 'si')  # converting from cgs to SI is impossible
        with pytest.raises(pc.UnitsUnknownError):
            u(quant, 'cgs')  # converting from raw to cgs is impossible
    for quant in ('eps0', 'mu0'):  # misc E & M physical constants
        with pytest.raises(pc.UnitsUnknownError):
            ucgs(quant, 'raw')  # converting to cgs is impossible
        with pytest.raises(pc.UnitsUnknownError):
            u(quant, 'cgs')  # converting to cgs is impossible


### --------------------- Coords / Maindims / Meshfile --------------------- ###

def test_bifrost_load_meshfile():
    '''tests that we can load the meshfile coordinates!'''
    bc = get_bifrost_calculator()
    bc.load_mesh_coords()  # just checking that this doesn't crash
    bc.get_maindims_coords()  # just checking that this doesn't crash

def test_bifrost_squeeze_direct():
    '''tests that squeeze direct is working properly'''
    bc = get_bifrost_calculator()
    assert bc.params['mx'] > 1
    assert bc.params['my'] == 1  # in the input decks here, my=1.
    assert bc.params['mz'] > 1
    assert bc.maindims_size == bc.params['mx'] * bc.params['mz']
    # with squeezing:
    bc.squeeze_direct = True
    assert bc.maindims == ('x', 'z')
    assert bc.maindims_shape == (bc.params['mx'], bc.params['mz'])
    coords = bc.get_maindims_coords()
    assert 'y' not in coords
    assert 'x' in coords and 'z' in coords
    assert len(coords['x']) == bc.params['mx']
    assert len(coords['z']) == bc.params['mz']
    # without squeezing:
    bc.squeeze_direct = False
    assert bc.maindims == ('x', 'y', 'z')
    assert bc.maindims_shape == (bc.params['mx'], bc.params['my'], bc.params['mz'])
    coords = bc.get_maindims_coords()
    assert 'x' in coords and 'y' in coords and 'z' in coords
    assert len(coords['x']) == bc.params['mx']
    assert len(coords['y']) == bc.params['my']
    assert len(coords['z']) == bc.params['mz']

# [TODO] could test stagger methods here if desired.
