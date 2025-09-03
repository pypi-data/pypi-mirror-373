"""
File Purpose: testing tools from tools.xarray_tools.xarray_coords
"""
import pytest
import numpy as np
import xarray as xr

import PlasmaCalcs as pc


def test_xarray_nondim_coords():
    xx = pc.xrrange(5, name='x')
    yy = pc.xrrange(3, 'y')
    arr = xx * yy
    assert len(arr.pc.nondim_coords())==0
    arr = arr.assign_coords(z=7, label='hi')
    ndc = arr.pc.nondim_coords()
    assert ndc['z'] == 7
    assert ndc['label'] == 'hi'
    arr0 = arr.isel(x=0)
    ndc0 = arr0.pc.nondim_coords()
    assert ndc0['x'] == 0
    assert ndc0['z'] == 7
    assert ndc0['label'] == 'hi'
    arr1 = arr.isel(x=0, drop=True)
    assert 'x' not in arr1.pc.nondim_coords()
    # dataset
    ds = xr.Dataset({'xx': xx, 'yy': yy})
    ds = ds.assign_coords(z=7, label='hi')
    ndc = ds.pc.nondim_coords()
    assert ndc['z'] == 7
    assert ndc['label'] == 'hi'
    ds0 = ds.isel(x=0)
    ndc0 = ds0.pc.nondim_coords()
    assert ndc0['x'] == 0
    assert ndc0['z'] == 7
    assert ndc0['label'] == 'hi'

def test_dims_coords():
    xx = pc.xrrange(5, 'x')
    assert xx.pc.dims_coords() == {'x': ['x']}
    yy = pc.xrrange(3, 'y')
    arr = xx * yy
    assert arr.pc.dims_coords() == {'x': ['x'], 'y': ['y']}
    arr = arr.assign_coords(z=xx + yy, testscalar=7)
    dc = arr.pc.dims_coords()
    assert set(dc.keys()) == set(['x', 'y', ()])
    dc_set_vals = {k: set(v) for k,v in dc.items()}
    assert dc_set_vals == {'x': set(['x', 'z']), 'y': set(['y', 'z']), (): set(['testscalar'])}
    yy2 = pc.xrrange(3, 'y').assign_coords(height=lambda arr: arr['y']+10)
    dc = yy2.pc.dims_coords()
    assert set(dc.keys()) == set(['y'])
    assert set(dc['y']) == set(['y', 'height'])

def test_assign_self_as_coord():
    arr = (pc.xrrange(5, 'x') * pc.xrrange(3, 'y')).rename('z')
    arr0 = arr
    arr = arr.pc.assign_self_as_coord()
    assert np.all(arr == arr0)  # assigning new coord doesn't change array values
    assert np.all(arr['z'] == arr)

def test_fill_coords():
    arr = xr.DataArray(np.arange(10)*10, dims=['x'])
    assert 'x' not in arr.coords
    filled = arr.pc.fill_coords()
    assert np.all(filled['x'] == np.arange(10))
    assert 'x' in filled.coords
    arr2 = xr.DataArray(np.arange(24).reshape(2,3,4), dims=['x', 'y', 'z'], coords={'y': [5, 7, 100]})
    filled = arr2.pc.fill_coords()
    assert all(x in filled.coords for x in ['x', 'y', 'z'])
    assert np.all(filled['x'] == np.arange(2))  # existing coords untouched
    assert np.all(filled['y'] == [5, 7, 100])
    assert np.all(filled['z'] == np.arange(4))
    filled = arr2.pc.fill_coords(dim='z')
    assert 'x' not in filled.coords
    assert 'z' in filled.coords
    filled = arr2.pc.fill_coords(dim='y')
    assert filled.identical(arr2)  # no change because y already has coords.

def test_index_coords():
    arr = pc.xrrange(5, 'x') * pc.xrrange(3, 'y', coords={'y': ['a', 'b', 'c']})
    arr = arr.rename('z').pc.assign_self_as_coord()
    assert arr.pc.index_coords().identical(pc.xarray_index_coords(arr))
    ixc = arr.pc.index_coords()
    assert set(ixc.dims) == {'x', 'y'}
    assert set(ixc.coords) == {'x', 'x_index', 'y', 'y_index', 'z', 'z_index'}
    assert all(np.all(ixc[x] == arr[x]) for x in ('x', 'y', 'z'))  # original coords unchanged
    assert np.all(ixc['x_index'] == np.arange(5))
    assert np.all(ixc['y_index'] == np.arange(3))
    for i in range(5):
        for j in range(3):
            assert ixc['z_index'].isel(x=i, y=j).item() == (i, j)
    ixc = arr.pc.index_coords(drop=True)
    assert set(ixc.dims) == {'x', 'y'}
    assert set(ixc.coords) == {'x_index', 'y_index', 'z_index'}
    with pytest.raises(pc.DimensionalityError):
        ixc = arr.pc.index_coords(promote=True)  # can't promote z to dim because z is 2D.
    ixc = arr.pc.index_coords(('x', 'y'))
    assert set(ixc.dims) == {'x', 'y'}
    assert set(ixc.coords) == {'x', 'x_index', 'y', 'y_index', 'z'}
    ixc = arr.pc.index_coords(('x', 'y'), drop=True)
    assert set(ixc.dims) == {'x', 'y'}
    assert set(ixc.coords) == {'x_index', 'y_index', 'z'}
    ixc = arr.pc.index_coords(('x', 'y'), promote=True)
    assert set(ixc.dims) == {'x_index', 'y_index'}
    assert set(ixc.coords) == {'x', 'x_index', 'y', 'y_index', 'z'}
    ixc = arr.pc.index_coords(('x', 'y'), drop=True, promote=True)
    assert set(ixc.dims) == {'x_index', 'y_index'}
    assert set(ixc.coords) == {'x_index', 'y_index', 'z'}
    with pytest.raises(pc.InputError):
        idx = arr.pc.index_coords('x', 'z')  # <-- some new names (i.e., 'z') already exist in array.coords.

def test_manip_coords():
    '''tests scale_coords, shift_coords, and log_coords.'''
    # non-comprehensive (not getting all edge cases) but it's something at least.
    ## syntaxes
    arr = (pc.xrrange(5, 'x') * pc.xrrange(3, 'y')).rename('z')
    assert arr.pc.shift_coords({'x': 2}).identical(arr.pc.shift_coords(x=2))
    assert arr.pc.shift_coords({'x': 2}).identical(pc.xarray_shift_coords(arr, {'x': 2}))
    assert arr.pc.scale_coords({'x': 2}).identical(arr.pc.scale_coords(x=2))
    assert arr.pc.scale_coords({'x': 2}).identical(pc.xarray_scale_coords(arr, {'x': 2}))
    xx = pc.xrrange(5, 'x').pc.shift_coords({'x':1})
    yy = pc.xrrange(3, 'y', coords={'y': [1, 10, np.e]})
    arr = (xx * yy).rename('z')
    assert arr.pc.log_coords().identical(pc.xarray_log_coords(arr))
    assert arr.pc.log_coords().identical(arr.pc.log_coords(drop=True, promote=False))  # <- check defaults
    ## scale coords
    arr = (pc.xrrange(5, 'x') * pc.xrrange(3, 'y')).rename('z')
    x2 = arr.pc.scale_coords({'x': 2})
    assert np.all(x2['x'] == np.arange(5)*2)
    assert x2.identical(arr.pc.scale_coords(x=2))  # alternate syntax
    x2_y10 = arr.pc.scale_coords({'x': 2, 'y': 10})
    assert np.all(x2_y10['x'] == np.arange(5)*2)
    assert np.all(x2_y10['y'] == np.arange(3)*10)

    ## shift coords
    x2 = arr.pc.shift_coords({'x': 2})
    assert np.all(x2['x'] == np.arange(5)+2)
    xm2_y10 = arr.pc.shift_coords({'x': -2, 'y': 10})
    assert np.all(xm2_y10['x'] == np.arange(5)-2)
    assert np.all(xm2_y10['y'] == np.arange(3)+10)

    ## log coords
    xx = pc.xrrange(5, 'x').pc.shift_coords({'x':1})
    yy = pc.xrrange(3, 'y', coords={'y': [1, 10, np.e]})
    arr = (xx * yy).rename('z')
    arr = arr.assign_coords({'testscalar': 1000})
    log = arr.pc.log_coords(drop=True, promote=False)  # <-- this is the default behavior, as checked above.
    assert set(log.dims) == {'x', 'y'}
    assert set(log.coords) == {'log_x', 'log_y', 'log_testscalar'}
    log = arr.pc.log_coords(drop=True, promote=True)
    assert set(log.dims) == {'log_x', 'log_y', 'log_testscalar'}
    assert set(log.coords) == {'log_x', 'log_y', 'log_testscalar'}
    log = arr.pc.log_coords(drop=False, promote=True)
    assert set(log.dims) == {'log_x', 'log_y', 'log_testscalar'}
    assert set(log.coords) == {'log_x', 'log_y', 'log_testscalar', 'x', 'y', 'testscalar'}
    log = arr.pc.log_coords(drop=False, promote=False)
    assert set(log.dims) == {'x', 'y'}
    assert set(log.coords) == {'log_x', 'log_y', 'log_testscalar', 'x', 'y', 'testscalar'}
    assert np.all(log['log_x'] == np.log10(xx['x']))
    assert np.all(log['log_y'] == np.log10(yy['y']))
    assert log['log_y'].isel(y=0) == 0
    assert log['log_y'].isel(y=1) == 1
    # check some more values:
    logyrep = arr.pc.log_coords(['y', 'testscalar'], drop=True, promote=False)
    assert logyrep['log_testscalar'] == 3
    assert logyrep['log_y'].isel(y=1) == 1
    logbasee = arr.pc.log_coords(base='e')
    assert np.allclose(logbasee['log_y'], np.log(yy['y']))
    assert logbasee.attrs['log_base'] == 'e'
    assert logbasee['log_y'].isel(y=2) == 1
    # check what happens if newname is altered:
    log = arr.pc.log_coords(newname='customlog_{coord}')
    assert set(log.dims) == {'x', 'y'}
    assert set(log.coords) == {'customlog_x', 'customlog_y', 'customlog_testscalar'}
    log = arr.pc.log_coords(newname='{coord}')
    assert set(log.dims) == {'x', 'y'}
    assert set(log.coords) == {'x', 'y', 'testscalar'}
    assert np.all(log['x'] == np.log10(xx['x']))
    with pytest.raises(pc.InputError):
        arr.pc.log_coords(newname='same_for_all')  # <-- multiple coords would have same new name --> crash.


# [TODO] tests for: xarray_is_sorted, get_dx_along, differentiate
