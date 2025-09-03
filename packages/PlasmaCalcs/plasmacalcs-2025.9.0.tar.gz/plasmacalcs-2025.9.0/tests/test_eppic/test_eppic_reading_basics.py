"""
File Purpose: basic tests for eppic hookup in PlasmaCalcs.
These tests require some simulation output.
They also test reading lots of different basic values,
    with lots of different values for dims & slices,
    so it takes a little while to run (~20-30 seconds?).
"""
import os
import pytest

import numpy as np

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)


def get_eppic_calculator(**kw_init):
    '''make an eppic calculator'''
    with pc.InDir(os.path.join(HERE, 'test_eppic_tinybox')):
        ec = pc.EppicCalculator.from_here(**kw_init)
    return ec


### --------------------- basic tests --------------------- ###

def test_dimensions_manip():
    '''ensure can manipulate dimensions properly.'''
    ec = get_eppic_calculator()
    # snaps: there are 10 snaps: 0,1,...,9. Going from it='2560' to it='25600'
    ec.snap = None; assert ec.snap.size == 10
    ec.snap = 0; assert ec.snap.size == 1
    ec.snap = '2560'; assert ec.snap.size == 1
    ec.snap = ['5120', '7680']; assert len(ec.snap) == 2
    ec.snap = 4; assert ec.snap.size == 1
    ec.snap = slice(0, None, 2); assert ec.snap.size == 5
    ec.snap = slice(0, None, 0.4)  # check that "interprets_fractional_indexing" works as expected
    assert ec.snap == ec.snaps[slice(0, None, 4)]
    assert ec.snap.size == 3
    ec.snap = -1; assert ec.snap.size == 1
    # fluids: there are 3 fluids ('e-', 'H+', 'C+')
    ec.fluid = None; assert ec.fluid.size == 3; assert ec.fluid == ['e-', 'H+', 'C+']
    ec.fluid = 0; assert ec.fluid.size == 1; assert ec.fluid == 'e-'
    ec.fluid = -1; assert ec.fluid.size == 1; assert ec.fluid == 'C+'
    ec.fluid = 'H+'; assert ec.fluid.size == 1
    ec.fluid = ['H+', 'C+']; assert len(ec.fluid) == 2
    ec.fluid = ec.fluids.get_electron(); assert ec.fluid.size == 1
    ec.fluid = ec.fluids.charged(); assert ec.fluid.size == 3
    with pytest.raises(pc.FluidKeyError):  # eppic has no neutral fluid, only a constant background.
        ec.fluids.get_neutral()
    # components: there are 3 components ('x', 'y', 'z')
    ec.component = None; assert ec.component.size == 3; assert ec.component == ['x', 'y', 'z']
    ec.component = 0; assert ec.component.size == 1; assert ec.component == 'x'
    ec.component = 'z'; assert ec.component.size == 1
    ec.component = ['x', 'y']; assert len(ec.component) == 2
    ec.component = slice(0, None, 2); assert ec.component.size == 2
    # maindims: there are 2 maindims ('x', 'y')  (it was a 2D run) each with size 16.
    assert len(ec.maindims) == 2
    ec.slices = dict(); assert ec.maindims_shape == (16, 16); assert ec.maindims_size == 16*16
    ec.slices = dict(x=0); assert ec.maindims_shape == (1, 16); assert ec.maindims_size == 16
    ec.slices = dict(x=5); assert ec.maindims_shape == (1, 16); assert ec.maindims_size == 16
    ec.slices = dict(y=-1); assert ec.maindims_shape == (16, 1); assert ec.maindims_size == 16
    ec.slices = dict(x=0, y=0); assert ec.maindims_shape == (1, 1); assert ec.maindims_size == 1
    ec.slices = dict(x=slice(0, None, 2)); assert ec.maindims_shape == (8, 16); assert ec.maindims_size == 8*16
    ec.slices = dict(x=slice(0, 10, 2), y=slice(7, 11)); assert ec.maindims_shape == (5, 4); assert ec.maindims_size == 5*4
    # check that "interprets_fractional_indexing" works as expected
    ec.slices = dict(x=slice(0, 0.5)); assert ec.maindims_shape == (8, 16)
    ec.slices = dict(x=slice(-0.5, None)); assert ec.maindims_shape == (7, 16)
    ec.slices = dict(x=slice(None, None, 0.25), y=slice(None, None, 0.125)); assert ec.maindims_shape == (4, 8)

# takes roughly 20 seconds
def test_reading_basic_values():
    '''ensure can read basic values from eppic.'''
    # checks that output size is correct, for various dimensions.
    # use some of the same dimensions as in test_dimensions_manip, to enable hard-coding the expected results.
    # don't use all of them, because that produces hundreds of input combinations, which takes a while.
    # also compare against the dynamically-calculated expected results.
    ec = get_eppic_calculator()
    snap_inputs = [None, 4, slice(0, None, 2)]
    snap_sizes = [10, 1, 5]
    fluid_inputs = [None, -1, ['H+', 'C+']]
    fluid_sizes = [3, 1, 2]
    component_inputs = [None, 'z', ['x', 'y']]
    component_sizes = [3, 1, 2]
    slice_inputs = [dict(), dict(x=5), dict(x=0, y=0), dict(x=slice(0, 10, 2), y=slice(7, 11))]
    slice_shapes = [(16, 16), (1, 16), (1, 1), (5, 4)]
    slice_sizes = [16*16, 16, 1, 5*4]

    input_attrs = []  # list of dicts of attr values
    input_sizes = []  # list of dicts of attr sizes
    for snap, snap_size in zip(snap_inputs, snap_sizes):
        for fluid, fluid_size in zip(fluid_inputs, fluid_sizes):
            for component, component_size in zip(component_inputs, component_sizes):
                for slices, slice_size in zip(slice_inputs, slice_sizes):
                    input_attrs.append(dict(snap=snap, fluid=fluid, component=component, slices=slices))
                    input_sizes.append(dict(snap=snap_size, fluid=fluid_size, component=component_size, slice=slice_size))
    assert len(input_attrs) == len(input_sizes)
    assert len(input_attrs) == len(snap_sizes) * len(fluid_sizes) * len(component_sizes) * len(slice_sizes)

    for attrs, sizes in zip(input_attrs, input_sizes):
        ec.set_attrs(**attrs)
        # redundant with test_dimensions_manip to check size here, but these are tests so redundancy is fine.
        assert ec.current_n_snap() == sizes['snap']
        assert ec.current_n_fluid()== sizes['fluid']
        assert ec.current_n_component() == sizes['component']
        assert ec.maindims_size == sizes['slice']
        # get some basic values and assert they have the correct size.
        arr = ec('n')  # in its own line for easier debugging in case of crash.
        dynamic_expect_size = ec.match_var_result_size('n')  # dynamically calculate expected size.
        simple_expect_size = sizes['snap'] * sizes['fluid'] * sizes['slice']  # size based on the things 'n' depends on.
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('E')
        dynamic_expect_size = ec.match_var_result_size('E')
        simple_expect_size = sizes['snap'] * sizes['component'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('u')
        dynamic_expect_size = ec.match_var_result_size('u')
        simple_expect_size = sizes['snap'] * sizes['fluid'] * sizes['component'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('Ta')
        dynamic_expect_size = ec.match_var_result_size('Ta')
        simple_expect_size = sizes['snap'] * sizes['fluid'] * sizes['component'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('m')
        dynamic_expect_size = ec.match_var_result_size('m', maindims=False)  # [TODO] infer maindims=False from 'm'
        simple_expect_size = sizes['fluid']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('m_neutral')
        dynamic_expect_size = ec.match_var_result_size('m_neutral', maindims=False) # [TODO] infer maindims=False from 'm'
        simple_expect_size = 1
        assert arr.size == dynamic_expect_size == simple_expect_size
        # get some slightly more complicated values and assert they have the correct size.
        arr = ec('E_x')
        dynamic_expect_size = ec.match_var_result_size('E_x')
        simple_expect_size = sizes['snap'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('u_y')
        dynamic_expect_size = ec.match_var_result_size('u_y')
        simple_expect_size = sizes['snap'] * sizes['fluid'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('T')
        dynamic_expect_size = ec.match_var_result_size('T')
        simple_expect_size = sizes['snap'] * sizes['fluid'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('mod_E')
        dynamic_expect_size = ec.match_var_result_size('mod_E')
        simple_expect_size = sizes['snap'] * sizes['slice']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('mean_n')
        dynamic_expect_size = ec.match_var_result_size('mean_n', maindims=False)  # [TODO] infer maindims=False from 'mean'.
        simple_expect_size = sizes['snap'] * sizes['fluid']
        assert arr.size == dynamic_expect_size == simple_expect_size
        arr = ec('std_u')
        dynamic_expect_size = ec.match_var_result_size('std_u', maindims=False)  # [TODO] infer maindims=False from 'std'.
        simple_expect_size = sizes['snap'] * sizes['fluid'] * sizes['component']
        assert arr.size == dynamic_expect_size == simple_expect_size

def test_reading_fractional_slices():
    '''test reading values when using fractional slices'''
    ec = get_eppic_calculator()
    ec.snap = 7  # choosing a single snap is sufficient for these tests.
    ec.fluid = 0  # choosing a single fluid is sufficient for these tests.
    assert ec.maindims_shape == (16, 16)
    # hard-coded translations below, between fractional & integer slices, assumes maindims_shape==(16,16)
    assert ec('n', slices=dict(x=slice(0, 0.5))).identical(ec('n').isel(x=slice(0, 8)))
    assert ec('n', slices=dict(x=slice(-0.5, None))).identical(ec('n').isel(x=slice(-7, None)))
    assert ec('n', slices=dict(y=slice(0.25, 0.75))).identical(ec('n').isel(y=slice(4, 12)))
    assert ec('n', slices=dict(y=slice(-0.25, None))).identical(ec('n').isel(y=slice(-3, None)))
    assert ec('n', slices=dict(x=slice(None, None, 0.25))).identical(ec('n').isel(x=slice(None, None, 4)))
    # also check that it is possible to use negative step:
    with pytest.raises(NotImplementedError):  # negative step not yet implemented.
        ec('n', slices=dict(x=slice(None, None, -1)))
    # assert ec('n', slices=dict(x=slice(None, None, -1))).identical(ec('n').isel(x=slice(None, None, -1)))
    # assert ec('n', slices=dict(x=slice(None, None, -0.25))).identical(ec('n').isel(x=slice(None, None, -4)))
    # for slice_ in [slice(10, 5, -1), slice(16, 3, -2), slice(0, 5, -1), slice(7, None, -0.25)]:
    #     assert ec('n', slices=dict(x=slice_)).identical(ec('n').isel(x=slice_))

def test_vector_arithmetic():
    '''some tests of vector arithmetic methods'''
    ec = get_eppic_calculator()
    ec.snap = 5  # choosing a single snap is sufficient for these tests.
    # ensure perpmod actually independent of component
    E_perpmod_B = ec('E_perpmod_B')
    assert E_perpmod_B.identical(ec('E_perpmod_B', component='x'))
    assert E_perpmod_B.identical(ec('E_perpmod_B', component=['x', 'y']))
    # ensure perpmod nonzero (not necessarily true in general, but true for this data) & non-nan.
    assert np.all(E_perpmod_B > 0)
    assert np.all(np.isfinite(E_perpmod_B))
    # ensure perpmod identical to perpmag (they are aliases)
    assert E_perpmod_B.equals(ec('E_perpmag_B'))  # can't use "identical" because names are different.
    # ensure for perp, component affects result in the expected way
    E_perp_B = ec('E_perp_B')
    assert E_perp_B.isel(component=0).identical(ec('E_perp_B', component='x'))
    assert np.all(ec('(E_perp_B)_x') > 0)  # not generally true for all data, but true for this data
    assert np.all(ec('E_perp_B', component='y') < 0)  # similarly, should be true for this particular data

def test_deriv_before_slice():
    '''test that deriv_before_slice works as expected.'''
    ec = get_eppic_calculator()
    ec.snap = 3  # choosing a single snap is sufficient for these tests.
    ec.fluid = 0  # choosing a single fluid is sufficient for these tests.
    SLICES_TO_TEST = [
        dict(),
        dict(x=5),
        dict(x=slice(3, 15, 1)),
        dict(x=slice(0, 10, 2)),
        dict(x=slice(0, 10, 2), y=slice(7, 11)),
        dict(x=slice(0, 0.8, 0.25)),
    ]
    for var in ('ddx_n', 'grad_n', 'div_u', 'curl_u'):
        for slices in SLICES_TO_TEST:
            simple_before = ec(var, slices=dict()).pc.isel(slices)  # like deriv_before_slice=True
            deriv_before = ec(var, deriv_before_slice=True, slices=slices)
            deriv_after = ec(var, deriv_before_slice=False, slices=slices)
            assert simple_before.identical(deriv_before)
            if slices:  # i.e. slices != empty dict
                assert not np.allclose(deriv_after, deriv_before)
            else:  # i.e. no slices applied
                assert deriv_after.identical(deriv_before)
        # test mode='step', when step!=1:
        slices = dict(x=slice(5, 13, 2))  # could be any slice with step!=1.
        simple_before = ec(var, slices=dict()).pc.isel(slices)  # like deriv_before_slice=True
        step_after = ec(var, slices=dict(x=slice(5, 13, None))).pc.isel(x=slice(None, None, 2))
        deriv_after = ec(var, deriv_before_slice=False, slices=slices)
        deriv_step = ec(var, deriv_before_slice='step', slices=slices)
        deriv_before = ec(var, deriv_before_slice=True, slices=slices)
        assert simple_before.identical(deriv_before)
        assert not np.allclose(deriv_after, deriv_before)
        assert step_after.identical(deriv_step)
        assert not np.allclose(deriv_step, deriv_before)
        assert not np.allclose(deriv_step, deriv_after)
        # test mode='step', when step==1 (or None):
        slices = dict(x=slice(3, 8, 1))  # could be any slice with step==1.
        simple_before = ec(var, slices=dict()).pc.isel(slices)
        step_after = ec(var, slices=dict(x=slice(3, 8, None))).pc.isel(x=slice(None, None, 1))
        deriv_after = ec(var, deriv_before_slice=False, slices=slices)
        deriv_step = ec(var, deriv_before_slice='step', slices=slices)
        deriv_before = ec(var, deriv_before_slice=True, slices=slices)
        assert simple_before.identical(deriv_before)
        assert not np.allclose(deriv_after, deriv_before)
        assert step_after.identical(deriv_step)
        assert not np.allclose(deriv_step, deriv_before)
        assert deriv_step.identical(deriv_after)  # deriv_step == deriv_after when step==1.
        # test mode='step' when step is fractional
        slices = dict(x=slice(0, 13, 0.25))
        assert ec.maindims_shape == (16, 16)
        step_after = ec(var, slices=dict(x=slice(0, 13, None))).pc.isel(x=slice(None, None, int(0.25*16)))
        deriv_step = ec(var, deriv_before_slice='step', slices=slices)
        assert step_after.identical(deriv_step)
        # test mode='step' when using int or list indexer instead of slice
        xslices = [dict(x=5), dict(x=[0, 7, 10])]
        for slices in xslices:
            assert ec.maindims_shape == (16, 16)
            deriv_step = ec(var, deriv_before_slice='step', slices=slices)
            deriv_before = ec(var, deriv_before_slice=True, slices=slices)
            assert deriv_step.identical(deriv_before)
