"""
File Purpose: basic tests for bifrost hookup in PlasmaCalcs.
These tests require some simulation output.
"""
import os

import numpy as np

import PlasmaCalcs as pc

HERE = os.path.dirname(__file__)


### --------------------- can create bifrost calculator --------------------- ###

def get_bifrost_calculator(**kw_init):
    '''make a bifrost calculator'''
    with pc.InDir(os.path.join(HERE, 'test_bifrost_tinybox')):
        bc = pc.BifrostCalculator(**kw_init)
    return bc

def get_bifrost_multifluid_calculator(**kw_init):
    '''make a multifluid bifrost calculator (for multifluid analysis of bifrost outputs)'''
    with pc.InDir(os.path.join(HERE, 'test_bifrost_tinybox')):
        bm = pc.BifrostMultifluidCalculator(**kw_init)
    return bm

def test_make_bifrost_calculator():
    '''ensure can make bifrost calculator and bifrost multifluid calculator'''
    get_bifrost_calculator()
    get_bifrost_multifluid_calculator()


### --------------------- misc tests --------------------- ###

def test_bifrost_calculator_misc():
    '''load some values. Mostly trying to ensure things don't crash.'''
    bc = get_bifrost_calculator()
    ## check: can load all simple MHD vars:
    bc('e')
    bc('r')
    bc('B')
    ## check: can load derived vars:
    assert bc.eos_mode == 'neq'
    bc('T')  # <-- comes directly from aux outputs.
    bc('P')  # <-- plugs e & r into lookup tables.
    bc.tabin['P']  # <-- ensure P table actually exists...
    ## check: misc. dimensionality things:
    assert bc('B').sizes['component'] == 3
    assert set(bc.maindims) == set(['x', 'z'])  # this is a 2D sim without y extent.
    assert bc('r').sizes['x'] == bc.maindims_sizes['x'] == 50
    assert bc('r').sizes['z'] == bc.maindims_sizes['z'] == 50
    ## check: misc. things related to "single fluid"
    assert bc('r').equals(bc('SF_r'))
    assert np.allclose(bc('m') * bc('n') / bc('r'), 1)

def test_bifrost_multifluid_calculator_misc():
    '''load some values. Mostly trying to ensure things don't crash.'''
    bm = get_bifrost_multifluid_calculator()
    assert len(bm.elements) == 16
    assert len(bm.fluids) == 19  # 16 once-ionized, plus e, H_I, and He_III.
    n = bm('n')
    assert n.sizes['fluid'] == 19
    assert bm('SF_n')['fluid'].item() is pc.SINGLE_FLUID
    # nusn = bm('nusn')  # TODO: currently, crashes; see issue #21.
    bm.snap  = 0  # using non-iterable bm.snap is the workaround for now.
    nusn = bm('nusn')
    assert nusn.sizes['fluid'] == 19
    assert nusn['jfluid'] == 'H_I'
    assert np.all(nusn.pc.sel(fluid='H_I') == 0)  # 0 self-self collisions
    assert nusn.max() > 1e5  # sometimes collisions are significant;
    assert 1e-4 < nusn.pc.sel(fluid=pc.CHARGED).min() < 1e-2  # sometimes they aren't.
    # [TODO] more misc. checks...


### --------------------- stagger tests --------------------- ###

def test_bifrost_stagger():
    '''test some things related to stagger operations'''
    bc = get_bifrost_calculator()
    ## check: stagger mesh interpolation operations for B.
    staggered = bc('B')
    raw = bc('B', stagger_direct=False)
    # (By (centered) = shift(By, yup), but can't do yup for 2D without y)
    assert staggered.pc.sel(component='y').equals(raw.pc.sel(component='y'))
    # (Bx (centered) = shift(Bx, xup), which has some impact on results.
    #  similar for Bz. Tested impact on results once when code is working for sure,
    #  and hard-coded answers below. If deviation changes significantly,
    #  due to changes in stagger algorithm itself, this will crash.
    #  putting a small margin of error here in case of tiny numerical rounding errors.)
    ratx = staggered.pc.sel(component='x') / raw.pc.sel(component='x')
    ratz = staggered.pc.sel(component='z') / raw.pc.sel(component='z')
    assert 0.005 < ratx.std()  < 0.020
    assert 0.900 < ratx.min()  < 0.930
    assert 0.990 < ratx.mean() < 1.010
    assert 1.000 < ratx.max()  < 1.030
    assert 0.0005 < ratz.std()  < 0.0009
    assert 0.9950 < ratz.min()  < 0.9970
    assert 1.0005 < ratz.mean() < 1.0020
    assert 1.0060 < ratz.max()  < 1.0090
    ## check: stagger mesh interpolation and derivative operations for J.
    # bc('J')  # TODO: currently, crashes; see issue #21.
    bc.snap = 0  # using non-iterable bc.snap is the workaround for now.
    J = bc('J')
    rawJ = bc('J', J_stagger=False)
    Jdiff = J - rawJ
    # (similarly to above: stagger has some impact on results.
    #  hard-coded; test will crash if updates ever significantly change results.
    #  using values directly also helps to check that units are correct.)
    assert 0.002 < Jdiff.std() < 0.003
    assert -0.007 < Jdiff.min() < -0.006
    assert 0.000 < Jdiff.mean() < 0.001
    assert 0.025 < Jdiff.max() < 0.031
    ## check: using stagger interface separately.
    bc = get_bifrost_calculator()
    # (stagger interface expects: raw units and 3D numpy arrays.)
    bc.snap = 0
    bc.units = 'raw'
    bc.squeeze_direct = False
    J_z_from_interface = bc.stagger(bc('B_y').values, 'ddxdn xup yup')
    assert np.allclose(1, J_z_from_interface / bc('J_z'))
    ## check: bc.stagger_minimal_slicing = True doesn't cause crash.
    # (TODO: check values for correctness as well...)
    bc = get_bifrost_calculator(snap=0)
    bc.stagger_minimal_slicing = True
    bc('B')
    bc('J')


# [TODO] more bifrost tests...
