"""
File Purpose: testing tools from tools.xarray_tools.xarray_grids
"""
import pytest
import numpy as np
import xarray as xr

import PlasmaCalcs as pc


def test_xrrange():
    assert pc.xarray_range is pc.xrrange  # these are aliases for each other.
    xx = xr.DataArray(np.arange(4), coords={'x': np.arange(4)}, name='x')
    assert xx.identical(pc.xrrange(4, 'x'))
    assert xx.identical(pc.xrrange(4, name='x'))  # can supply name as kwarg instead of positional
    xx = xr.DataArray(np.arange(1, 5), coords={'x': np.arange(1, 5)}, name='x')
    assert xx.identical(pc.xrrange((1, 5), 'x'))
    xx = xr.DataArray(np.arange(1, 9, 2), coords={'x': np.arange(1, 9, 2)}, name='x')
    assert xx.identical(pc.xrrange((1, 9, 2), 'x'))
    with pytest.raises(pc.InputError):
        pc.xrrange(1, 5)  # name must be str. E.g., user forgot to put (1,5) as tuple.
    # ensure can create array even without name; uses a default name.
    xx = pc.xrrange(5)
    # ensure can provide coords
    xx = pc.xrrange(5, 'x', coords={'y': 7})
    assert xx.coords['y'] == 7
    assert np.all(xx.coords['x'] == np.arange(5))
    # ensure coords can include name
    xx = pc.xrrange(5, 'x', coords={'x': 10+np.arange(5), 'y': 7})
    assert xx.coords['y'] == 7
    assert np.all(xx.coords['x'] == 10+np.arange(5))

def test_xarray_grid():
    assert np.all(pc.XarrayGrid(1, 100, logstep=1)() == [1,10,100])
    assert np.all(pc.XarrayGrid(1, 10, step=3).grid() == [1,4,7,10])  # grid() is alias for calling
    with pytest.raises(pc.InputConflictError):
        pc.XarrayGrid(pc.xrrange(5, 'x'), 10, step=2)  # can't provide both step and min & max.
    arr = pc.XarrayGrid(pc.xrrange(3, 'x'), span=6, step=2, name='mygrid')()
    assert np.all(arr.isel(x=0) == [0, 2, 4, 6])
    assert np.all(arr.isel(x=1) == [1, 3, 5, 7])
    assert np.all(arr.isel(x=2) == [2, 4, 6, 8])
    assert arr.name == 'mygrid'
    assert set(arr.dims) == set(('x', 'mygrid_dim'))
    assert 'mygrid' in arr.coords
    assert arr['mygrid'].dims == arr.dims
    assert pc.XarrayGrid(1, 100, 50)().identical(pc.xarray_grid(1, 100, 50))
    assert pc.XarrayGrid(1, 100, 50, logspace=True)().identical(pc.xarray_grid(1, 100, 50, logspace=True))
    # step not matching span (or ratio, if logspace) exactly:
    with pytest.raises(pc.InputConflictError):
        pc.xarray_grid(0, 1, step=0.3)  # <-- step doesn't divide evenly into span.
    assert np.allclose(pc.xarray_grid(0, 1, step=0.3, inclusive=(True, False)), [0, 0.3, 0.6, 0.9])
    assert np.allclose(pc.xarray_grid(0, 1, step=0.3, inclusive=(False, True)), [0.1, 0.4, 0.7, 1])
    assert np.allclose(pc.xarray_grid(0, 1, step=0.3, inclusive=(False, False)), [0.3, 0.6, 0.9])
    assert np.all(pc.xarray_grid(10, 17, step=2, inclusive=(True, False)) == [10, 12, 14, 16])
    assert np.all(pc.xarray_grid(10, 17, step=2, inclusive=(False, True)) == [11, 13, 15, 17])
    assert np.all(pc.xarray_grid(10, 17, step=2, inclusive=(False, False)) == [12, 14, 16])
    with pytest.raises(pc.InputConflictError):
        pc.xarray_grid(1, 900, logstep=0.5)  # <-- logstep doesn't divide evenly into span.
    loggrid = np.logspace(0, 3, 7)  # [1, 3.16, 10, 31.6, 100, 316, 1000]
    assert np.allclose(pc.xarray_grid(1, 900, logstep=0.5, inclusive=(True, False)), loggrid[:-1])
    assert np.allclose(pc.xarray_grid(1, 900, logstep=0.5, inclusive=(False, False)), loggrid[1:-1])
    assert np.allclose(pc.xarray_grid(1, 900, logstep=1, inclusive=(True, False)), [1, 10, 100])
    assert np.allclose(pc.xarray_grid(1, 900, logstep=1, inclusive=(False, False)), [10, 100])
    assert np.allclose(pc.xarray_grid(1, 900, logstep=1, inclusive=(False, True)), [9, 90, 900])
    # grid smaller than allowed:
    with pytest.raises(pc.DimensionSizeError):
        pc.xarray_grid(0, 100, N=1)
    with pytest.raises(pc.DimensionSizeError):
        pc.xarray_grid(0, 100, N=0)
    assert np.all(pc.xarray_grid(0, 100, step=100)==[0,100])
    with pytest.raises(pc.DimensionSizeError):
        pc.xarray_grid(0, 100, step=100, inclusive=(True, False))
    with pytest.raises(pc.DimensionSizeError):
        pc.xarray_grid(0, 100, step=100, inclusive=(False, False))
    with pytest.raises(pc.DimensionSizeError):
        pc.xarray_grid(0, 100, step=50, inclusive=(False, False))
    # grid larger than allowed:
    with pytest.raises(pc.DimensionSizeError):  # <-- ensure the N_max limitation works on a small test case
        pc.xarray_grid(0, 1, step=1e-6, N_max=1000)   # (artificially lower N_max)
    with pytest.raises(pc.DimensionSizeError):  # <-- ensure the N_max limitation works on a huge case
        pc.xarray_grid(0, 1, step=1e-10)  # this grid would take up ~80 GB, if N_max didn't cause crash first!
