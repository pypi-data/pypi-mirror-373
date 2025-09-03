"""
File Purpose: test xarray save & xarray load.
"""
import os
import pytest

import numpy as np
import xarray as xr

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)
TESTS_DIR = os.path.dirname(HERE)
ARTIFACTS = os.path.join(TESTS_DIR, '_test_artifacts', 'xarray_io')
if os.path.exists(ARTIFACTS):  # remove any xarray_io artifacts before running tests.
    import shutil; shutil.rmtree(ARTIFACTS)
# <-- don't makedirs here; xarray_save should makedirs as needed.

### --------------------- can create eppic calculator --------------------- ###

def get_eppic_calculator(**kw_init):
    '''make an eppic calculator'''
    with pc.InDir(os.path.join(HERE, 'test_eppic_tinybox')):
        ec = pc.EppicCalculator.from_here(**kw_init)
    return ec


### --------------------- load / save / load some basic stuff! --------------------- ###

@pytest.mark.filterwarnings('ignore:`product`.*NumPy.*:DeprecationWarning')
def test_eppic_xarray_io():
    '''test saving & loading xarray with DimensionValue coords.'''
    ec = get_eppic_calculator()

    # array without ANY DimensionValue coordinates.
    arr = ec('7')  # just the number 7, as a DataArray!
    dst = arr.pc.save(os.path.join(ARTIFACTS, 'just_7'))
    arr_loaded = pc.xarray_load(dst)
    assert np.all(arr == arr_loaded)

    # very small array
    n0 = ec('n0')
    dst = n0.pc.save(os.path.join(ARTIFACTS, 'n0'))
    n0_loaded = pc.xarray_load(dst)
    assert np.all(n0 == n0_loaded)

    # array with spatial extent
    n = ec('n')
    dst = n.pc.save(os.path.join(ARTIFACTS, 'n'))
    n_loaded = pc.xarray_load(dst)
    assert np.all(n == n_loaded)
    # check naming scheme:
    assert os.path.basename(dst) == 'n.pcxarr'
    assert dst == os.path.abspath(os.path.join(ARTIFACTS, 'n.pcxarr'))

    # crash if would overwrite but not exist_ok:
    with pytest.raises(FileExistsError):
        n.pc.save(os.path.join(ARTIFACTS, 'n'))
    # don't crash if exist_ok:
    n.pc.save(os.path.join(ARTIFACTS, 'n'), exist_ok=True)
    n_loaded = pc.xarray_load(dst)
    assert np.all(n == n_loaded)

    # array at only 1 snap.
    n = ec('n', snap=7)
    dst = n.pc.save(os.path.join(ARTIFACTS, 'n_at_snap=7'))
    n_loaded = pc.xarray_load(dst)
    assert np.all(n == n_loaded)

    # array with only 1 fluid. Also with multiple components
    u = ec('u', fluid=0)
    dst = u.pc.save(os.path.join(ARTIFACTS, 'u_at_fluid=0'))
    u_loaded = pc.xarray_load(dst)
    assert np.all(u == u_loaded)

    # array with only 1 fluid and only 1 component.
    u = ec('u', fluid=1, component='z')
    dst = u.pc.save(os.path.join(ARTIFACTS, 'u_at_fluid=1_component=z'))
    u_loaded = pc.xarray_load(dst)
    assert np.all(u == u_loaded)

    # dataset
    n_at_box_edges = ec('n', multi_slices=dict(ndim=1))
    assert isinstance(n_at_box_edges, xr.Dataset)
    dst = n_at_box_edges.pc.save(os.path.join(ARTIFACTS, 'n_at_box_edges'))
    n_at_box_edges_loaded = pc.xarray_load(dst)
    assert n_at_box_edges.equals(n_at_box_edges_loaded)

    # array with bool-valued attrs
    arr = ec('7')  # just the number 7, as a DataArray!
    arr.attrs['attr0'] = True
    arr.attrs['attr1'] = False
    dst = arr.pc.save(os.path.join(ARTIFACTS, 'array_with_bool_attrs'))
    arr_loaded = pc.xarray_load(dst)
    assert np.all(arr == arr_loaded)

    # dataset with bool-valued attrs
    ds = ec(['0', '7'])
    ds.attrs['attr0'] = True
    ds.attrs['attr1'] = False
    dst = ds.pc.save(os.path.join(ARTIFACTS, 'dataset_with_bool_attrs'))
    ds_loaded = pc.xarray_load(dst)
    assert ds.equals(ds_loaded)

    # dataset with data_vars that have bool-valued attrs
    ds = ec(['0', '7'])
    ds['0'].attrs['attr0'] = True
    ds['7'].attrs['attr1'] = False
    dst = ds.pc.save(os.path.join(ARTIFACTS, 'dataset_with_bool_attrs_in_data_vars'))
    ds_loaded = pc.xarray_load(dst)
    assert ds.equals(ds_loaded)

    # toplevel_scale_coords (and, saving array with simple dict-valued attr)
    arr = ec('moment1', toplevel_scale_coords={'t': 1000}, assign_behavior_attrs=True)
    assert np.isclose(arr['t'].isel(snap=3), ec.snaps[3].t * ec.u('t') * 1000)
    assert arr.attrs['toplevel_scale_coords'] == {'t': 1000}
    dst = arr.pc.save(os.path.join(ARTIFACTS, 'moment1_with_toplevel_scale_coords_t_1000'))
    arr_loaded = pc.xarray_load(dst)
    assert np.all(arr == arr_loaded)
    assert arr_loaded.attrs['toplevel_scale_coords'] == {'t': 1000}

    # saving & loading UniqueDimensionValue (here: snap is INPUT_SNAP)
    ec.set_vars_from_inputs()
    assert ec.snap is pc.INPUT_SNAP
    arr = ec('n')
    dst = arr.pc.save(os.path.join(ARTIFACTS, 'n_at_INPUT_SNAP'))
    arr_loaded = pc.xarray_load(dst)
    assert np.all(arr == arr_loaded)
    assert arr_loaded['snap'].item() is pc.INPUT_SNAP
