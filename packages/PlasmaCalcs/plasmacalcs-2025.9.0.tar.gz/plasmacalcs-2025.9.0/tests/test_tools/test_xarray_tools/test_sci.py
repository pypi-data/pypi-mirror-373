"""
File Purpose: testing tools from tools.xarray_tools.xarray_sci
"""
import pytest
import numpy as np
import xarray as xr

import PlasmaCalcs as pc


def test_xarray_interp_inverse():
    # silly little example, to make it easy to understand & follow:
    # arr looks like: [[0, 10, ..., 40], [1, 11, ..., 41], ..., [9, 19, ..., 49]].
    tt = pc.xrrange(5, 'tens')
    oo = pc.xrrange(10, 'ones')
    arr = (10 * tt + oo).rename('n')
    assert pc.xarray_interp_inverse(arr, tens=1, n=17) == 7  # n=17, tens=1 --> ones=7
    assert arr.pc.interp_inverse(tens=1, n=17) == 7  # more convenient syntax works too.
    # more exact matches:
    assert arr.pc.interp_inverse(tens=2, n=23) == 3  # n=23, tens=2 --> ones=3
    assert arr.pc.interp_inverse(n=20, tens=2) == 0  # n=20, tens=2 --> ones=0
    assert arr.pc.interp_inverse(n=18, ones=8) == 1  # n=18, ones=8 --> tens=1
    assert arr.pc.interp_inverse(n=29, ones=9) == 2  # n=29, ones=9 --> tens=2
    # inexact matches:
    assert arr.pc.interp_inverse(n=15, ones=0) == 1.5  # ones=0 --> tens needs 0.5
    assert arr.pc.interp_inverse(n=27, ones=3) == 2.4
    assert arr.pc.interp_inverse(n=23.5, tens=2) == 3.5
    assert arr.pc.interp_inverse(n=27, tens=2.5) == 2
    # unreachable array values (n) gives nan
    assert np.isnan(arr.pc.interp_inverse(n=27, tens=3))  # ones can't compensate
    # out of bounds input coords (ones or tens) raises DimensionValueError (regardless of n)
    with pytest.raises(pc.DimensionValueError):
        arr.pc.interp_inverse(n=27, ones=10)
    with pytest.raises(pc.DimensionValueError):
        arr.pc.interp_inverse(n=27.5, ones=-1)
    with pytest.raises(pc.DimensionValueError):
        arr.pc.interp_inverse(n=None, ones=-1)
    with pytest.raises(pc.DimensionValueError):
        arr.pc.interp_inverse(n=-1000, tens=5)
    with pytest.raises(pc.DimensionValueError):
        arr.pc.interp_inverse(n=10000, tens=-1)
    with pytest.raises(pc.DimensionValueError):
        arr.pc.interp_inverse(n=None, tens=-1)
    # coords as arrays:
    assert np.all(arr.pc.interp_inverse(ones=[7, 2], n=27) == [2.0, 2.5])
    vals = arr.pc.interp_inverse(tens=[2,3], n=27)
    assert vals[0] == 7
    assert np.isnan(vals[1])
    # array.name var as array:
    assert np.all(arr.pc.interp_inverse(ones=5, n=[20, 25, 30, 36]) == [1.5, 2, 2.5, 3.1])
    # both as array:
    vals = arr.pc.interp_inverse(ones=[0, 7, 9], n=[27, 29])
    assert np.all(vals.isel(n=0) == [2.7, 2. , 1.8])
    assert np.all(vals.isel(n=1) == [2.9, 2.2, 2. ])
    # interp_inverse + interp --> original values
    result = arr.pc.interp_inverse(ones=[0, 7, 9], n=[27, 29])
    orig = arr.interp(ones=[0, 7, 9], tens=result)
    assert np.allclose(orig.isel(ones=0), [27, 29])
    assert np.allclose(orig.isel(ones=1), [27, 29])
    assert np.allclose(orig.isel(ones=2), [27, 29])
    assert np.allclose(orig, [27, 29])  # broadcasting is fine^^
    # [TODO] could probably do more checks,
    #   e.g. what happens if input array is not sorted,
    #   or what happens if it does not have only unique values.
    # [TODO] check coords & dims handled appropriately when inputs are DataArrays,
    #   especially DataArrays with different dimensions than the coord & array names.

def test_xarray_map():
    xx = pc.xrrange(4, 'x')
    yy = pc.xrrange(3, 'y')
    arr = -xx * yy + yy
    assert np.all(arr == [[0, 1, 2], [0, 0, 0], [0, -1, -2], [0, -2, -4]])
    sumx = arr.pc.map(np.sum, axis='x')
    assert np.all(sumx == [0, -2, -4])
    sumy = arr.pc.map(np.sum, axis='y')
    assert np.all(sumy == [3, 0, -3, -6])
    argsortx = arr.pc.map(np.argsort, axis='x')
    assert np.all(argsortx == [[0, 3, 3], [1, 2, 2], [2, 1, 1], [3, 0, 0]])
    argsorty = arr.pc.map(np.argsort, axis='y')
    assert np.all(argsorty == [[0, 1, 2], [0, 1, 2], [2, 1, 0], [2, 1, 0]])
