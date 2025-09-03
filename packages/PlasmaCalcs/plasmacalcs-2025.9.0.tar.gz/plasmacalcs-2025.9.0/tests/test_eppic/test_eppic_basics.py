"""
File Purpose: basic tests for eppic hookup in PlasmaCalcs.
These tests require an eppic.i file, but don't require any simulation output.
"""
import os
import pytest

import numpy as np

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)


### --------------------- basics --------------------- ###

def get_eppic_calculator(eppic_i='test_eppic_basics.i', **kw_init):
    '''make an eppic calculator'''
    with pc.InDir(HERE):
        ec = pc.EppicCalculator.from_here(eppic_i, **kw_init)
    return ec

def test_make_eppic_calculator():
    '''ensure can make an eppic calculator.'''
    get_eppic_calculator()


### --------------------- dimensions --------------------- ###

def test_dimensions_logic():
    '''ensure dimensions logic is working properly.
    Assumes eppic.i has at least 2 distributions in it.
    '''
    ec = get_eppic_calculator(dist_names={0: 'e'})
    assert len(ec.fluids) == len(ec.input_deck.dists)
    # DimensionValue compared to int or str
    ec.fluid = None  # use all fluids
    assert ec.fluid[0] == 0
    assert ec.fluid[0] == 'e'
    # DimensionValueList indexing
    ec.fluid = None
    assert ec.fluid[(0,1)] == [0,1]
    assert ec.fluid[[0,1]] == [0,1]
    assert ec.fluid[:2] == [0,1]
    assert ec.fluid[:2] == ['e',1]
    assert ec.fluid[[1,0]] == [1,0]
    assert ec.fluid[[0,0,1,1,0]] == [0,0,1,1,0]
    # different ways to set the value of a dimension:
    ec.fluid = None
    assert len(ec.fluid) == len(ec.fluids)
    ec.fluid = 1
    assert ec.fluid == ec.fluids[1]
    ec.fluid = 'e'
    assert ec.fluid == ec.fluids[0]
    ec.fluid = ec.fluids[1]
    assert ec.fluid == ec.fluids[1]
    ec.fluid = slice(None)
    assert len(ec.fluid) == len(ec.fluids)
    assert all(f1==f2 for f1, f2 in zip(ec.fluid, ec.fluids))
    ec.fluid = [0]
    assert len(ec.fluid) == 1
    assert all(f1==f2 for f1, f2 in zip(ec.fluid, ec.fluids))
    ec.fluid = pc.ELECTRON
    assert ec.fluid == ec.fluids[0]
    ec.fluid = pc.IONS
    assert len(ec.fluid) == 2  # there are 2 ions in this input deck.
    ec.fluid = pc.CHARGED
    assert len(ec.fluid) == 3  # 2 ions + 1 electron = 3 charged fluids total.
    with pytest.raises(pc.FluidKeyError):
        ec.fluid = pc.NEUTRAL  # no neutral fluid in ec.fluids
    ec.jfluid = pc.NEUTRAL  # just test to ensure this works :)
    # 'using' block:
    ec.fluid = 1
    with ec.using(fluid=0):
        assert ec.fluid == 0
    assert ec.fluid == 1  # value is restored after exiting the block, normally.
    with pytest.raises(Exception):
        with ec.using(fluid=0):
            assert ec.fluid == 0
            raise Exception('boom - leave ec.using block via crash.')
            assert False, 'should have left block via crash...'
        assert ec.fluid == 1  # value is restored after exiting the block, due to crash.
    # 'iter'
    ec.fluid = 0
    for f in ec.iter_fluid():  # iterate current values only.
        assert f == 0
    ec.fluid = [0,1]
    for i, f in enumerate(ec.iter_fluid()):
        assert f == i
    assert ec.fluid == [0,1]   # original value restored afterwards.
    ec.fluid = 0
    for i, f in enumerate(ec.iter_fluids()):  # iterate all values
        assert f == i
        if i == len(ec.fluids)-1:
            break
    else:  # didn't break
        raise Exception('iter_fluids() never reached reach last fluid.')
    assert ec.fluid == 0   # original value restored afterwards.
    # 'iter' - enumerate
    assert list(enumerate(ec.iter_fluid())) == list(ec.enumerate_fluid())
    assert list(enumerate(ec.iter_fluids())) == list(ec.enumerate_fluids())
    assert list(ec.iter_fluid(enumerate=True)) == list(ec.enumerate_fluid())
    assert list(ec.iter_fluids(enumerate=True)) == list(ec.enumerate_fluids())

def test_ds_from_input_deck():
    '''ensure ec('ds') gets the right values, accounting for nout_avg.'''
    # this test exists because the original ec('ds') used input_deck['dx'] instead,
    #    which fails to account for nout_avg.
    ec = get_eppic_calculator()
    assert ec('ds_x') == ec.input_deck.Dx == ec.input_deck.get_dspace('x')
    assert ec('ds_y') == ec.input_deck.Dy == ec.input_deck.get_dspace('x')
    assert ec('ds_z') == ec.input_deck.Dz == ec.input_deck.get_dspace('x')


### --------------------- loading vars --------------------- ###

def test_unknown_var():
    '''ensure crash with DimensionError or QuantCalcError when trying to get an unknown_var.'''
    ec = get_eppic_calculator()
    with pytest.raises((pc.DimensionError, pc.QuantCalcError)):
        ec('this_var_is_definitely_not_known_by_plasma_calcs')

def test_match_var():
    '''test match_var framework.'''
    ec = get_eppic_calculator()
    assert isinstance(ec.match_var('q'), pc.MatchedVar)
    assert isinstance(ec.match_var('q/m'), pc.MatchedPattern)
    q_over_m = ec.match_var('q/m')
    assert list(q_over_m.groups()) == ['q', 'm']
    assert list(q_over_m.deps) == [0,1]  # depends on groups()[0] and [1].
    assert isinstance(ec.match_var('(q*mod_B)/(m*nusn)'), pc.MatchedPattern)  # more complicated var
    # loading dims
    assert set(ec.match_var_loading_dims('q')) == {'fluid'}
    assert set(ec.match_var_loading_dims('q/m')) == {'fluid'}
    assert set(ec.match_var_loading_dims('B')) == {'component'}
    assert set(ec.match_var_loading_dims('mod_B')) == set()
    assert set(ec.match_var_loading_dims('q*B')) == {'fluid', 'component'}
    assert set(ec.match_var_loading_dims('q*mod_B')) == {'fluid'}
    assert set(ec.match_var_loading_dims('skappa')) == {'fluid'}

def test_nodata_vars():
    '''ensure can get some vars (which don't require any simulation data).'''
    ec = get_eppic_calculator()
    ec('q')
    ec('m')
    ec('B')
    ec('nusn')
    # info about neutrals is fully encoded in input deck too:
    ec('m_neutral')
    assert np.all(ec('m_n') == ec('m_neutral'))  # <-- ensures that aliases work
    ec('T_neutral')
    ec('u_neutral')
    with pytest.raises(pc.FormulaMissingError):
        ec('n_neutral')  # neutral density not known for eppic so this should crash.

def test_nodata_calcs():
    '''ensure can do some calculations (which don't require any simulation data).'''
    ec = get_eppic_calculator()
    ec.fluid = None
    assert np.all(ec('q/q')==1)
    assert np.all(ec('m-m')==0)
    assert np.all(ec('B_z')==ec('B', component='z')==ec('B', component=2))
    # more complicated calcs:
    skappa = ec('skappa')  # q |B| / (m nusn), depends only on fluids.
    assert skappa.size == len(ec.fluids)
    assert np.allclose(skappa, ec('q')*ec('mod_B')/(ec('m')*ec('nusn')))
    assert np.allclose(skappa, ec('q*mod_B/(m*nusn)'))        # parenthesis works
    assert np.allclose(skappa, ec('q*mod_B/m/nusn'))          # dividing by multiple things also works.
    assert np.allclose(skappa, ec('(q*(mod_B))/(m*(nusn))'))  # adding extra parentheses is fine
    assert np.allclose(1, ec('skappa/(q*mod_B/(m*nusn))'))    # dividing by complicated var is fine

def test_set_vars_from_input():
    '''ensure can set vars from input deck.'''
    ec = get_eppic_calculator()
    ec.set_vars_from_inputs()

def test_get_vars_from_input():
    '''ensure can get vars after setting them from input deck.'''
    ec = get_eppic_calculator()
    with pytest.raises((pc.DimensionError, pc.QuantCalcError)):
        ec('n')  # can't get 'n' before setting vars from input
    with pytest.raises((pc.DimensionError, pc.QuantCalcError)):
        ec('u')  # can't get 'u' before setting vars from input
    with pytest.raises((pc.DimensionError, pc.QuantCalcError)):
        ec('T')  # can't get 'T' before setting vars from input
    ec.set_vars_from_inputs()
    n = ec('n')   # can get 'n' after setting vars from input
    u = ec('u')   # can get 'u' after setting vars from input
    T = ec('T')   # can get 'T' after setting vars from input
    # size test for n (T is similar; not tested here)
    assert ec('n').size == len(ec.fluids)
    assert np.all(ec('n') == [fluid['n0d'] for fluid in ec.iter_fluid()])
    assert np.all(ec('n').isel(fluid=[1,0]) == [ec.fluid[1]['n0d'], ec.fluid[0]['n0d']])
    with ec.using(fluid=0):
        assert ec('n') == ec.fluid['n0d']
    # size test for u
    with ec.using(fluid=None, component=None):
        assert ec('u').size == ec.current_n_fluid() * ec.current_n_component()
        assert ec('u').size == ec.current_n_dimpoints(['fluid', 'component'])
    with ec.using(fluid=[0,1], component='y'):
        assert ec('u').size == ec.current_n_dimpoints(['fluid', 'component'])
    with ec.using(fluid=[0,1], component=None):
        assert ec('u').size == ec.current_n_dimpoints(['fluid', 'component'])
    with ec.using(fluid=0, component=('x', 'y')):
        assert ec('u').size == ec.current_n_dimpoints(['fluid', 'component'])
    # calcs with u. Also Ta (Ta nontrivial; u sometimes trivial, i.e. all 0)
    assert np.all(ec('mod_u') == np.sqrt(ec('u_x')**2 + ec('u_y')**2 + ec('u_z')**2))
    assert np.all(ec('mod_Ta') == np.sqrt(ec('Ta_x')**2 + ec('Ta_y')**2 + ec('Ta_z')**2))


### --------------------- misc vars or aspects of EppicCalculator --------------------- ###

def test_get_string_valued_var():
    '''ensure can get collision_type (a string-valued var).'''
    ec = get_eppic_calculator()
    arr = ec('collision_type', fluid=0, jfluid=0)
    assert arr.size == 1
    arr = ec('collision_type', fluid=None, jfluid=0)
    assert arr.size == len(ec.fluids)
    arr = ec('collision_type', fluid=None, jfluid=None)
    assert arr.size == len(ec.fluids) * len(ec.jfluids)
    # grid of collision types (jfluid was probably just an EppicNeutral before)
    ec.jfluids = ec.fluids
    ec.jfluid = None
    arr = ec('collision_type', fluid=None, jfluid=None)
    assert arr.size == len(ec.fluids) * len(ec.jfluids)
    assert arr[0,0] == '0'  # no collisions between fluid and itself.
    assert ec.fluids[0].is_electron()
    assert ec.fluids[1].is_ion()
    assert arr[0,1] == 'coulomb'  # electron-ion collisions are coulomb collisions
    assert ec.fluids[2].is_ion()
    assert arr[1,2] == 'coulomb'  # ion-ion collisions are coulomb collisions.
