"""
File Purpose: xarray math with error propagation.
"""

import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor
from .xarray_agg_stats import (
    _paramdocs_aggregator, _xarray_aggregator_setup,
    xarray_stats,
)
from ..docs_tools import format_docstring
from ...errors import InputError, InputConflictError


### --------------------- mean with error --------------------- ###

@pcAccessor.register('werrmean', totype='array')
@format_docstring(**_paramdocs_aggregator)
def xarray_werrmean(array, dim=None, *, keep=None,
                    promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''returns Dataset of 'mean' and 'std' for array.
    Equivalent: xarray_stats(array, stats=['mean', 'std'], ...)

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.mean and std.
    Can provide skipna=True/False to skip NaNs or not; default True for float dtypes.

    see also: xarray_werradd, xarray_werrsub, xarray_werrmul, xarray_werrdiv.
    Example:
        ds = arr.pc.werrmean().pc.werradd(arr2.pc.werrmean())
        ds['mean'] == arr.mean() + arr2.mean(),
        ds['std'] == sqrt(arr.std()**2 + arr2.std()**2)
    '''
    kw.update(stats=['mean', 'std'],
              dim=dim, keep=keep,
              promote_dims_if_needed=promote_dims_if_needed,
              missing_dims=missing_dims)
    return xarray_stats(array, **kw)

@pcAccessor.register('werr2pmstd', totype='dataset')
def xarray_werr2pmstd(ds, *, keep_mean=False):
    '''return ds but replacing 'std' data_var with 'mean+std' and 'mean-std'.
    ds: xarray.Dataset
        must have 'mean' and 'std' data vars.
    keep_mean: bool
        whether to keep 'mean' data_var in the result.

    see also: xarray_pmstd2werr
    '''
    mean = ds['mean']
    std = ds['std']
    ds = ds.drop_vars('std')
    to_assign = {}
    to_assign['mean+std'] = mean + std
    if keep_mean: to_assign['mean'] = mean
    to_assign['mean-std'] = mean - std
    ds = ds.assign(to_assign)
    return ds

@pcAccessor.register('pmstd2werr', totype='dataset')
def xarray_pmstd2werr(ds):
    '''return ds but replacing 'mean+std' and 'mean-std' data_vars with 'std'.
    ds: xarray.Dataset
        must have 'mean+std', and 'mean-std' data vars.
        if also has 'mean' data var, assert mean = ('mean+std' + 'mean-std') / 2,
            crashing with InputConflictError if not.

    see also: xarray_werr2pmstd
    '''
    mean = (ds['mean+std'] + ds['mean-std']) / 2
    std = ds['mean+std'] - mean
    if 'mean' in ds.data_vars and (not np.allclose(ds['mean'], mean)):
        raise InputConflictError('datavar mean != (mean+std + mean-std) / 2')
    ds = ds.drop_vars(['mean+std', 'mean-std'])
    ds = ds.assign({'std': std})
    return ds

@pcAccessor.register('mean_pm_std', totype='array')
@format_docstring(**_paramdocs_aggregator)
def xarray_mean_pm_std(array, dim=None, *, keep=None,
                       promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''returns Dataset of 'mean+std', 'mean', 'mean-std' for array.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.mean and std.
    Can provide skipna=True/False to skip NaNs or not; default True for float dtypes.
    '''
    array, dim, keep = _xarray_aggregator_setup(array, dim, keep, promote_dims_if_needed, missing_dims)
    mean = array.mean(dim, **kw)
    std = array.std(dim, **kw)
    attrs = array.attrs.copy() if xr.get_options()['keep_attrs'] else None
    results = {'mean+std': mean + std, 'mean': mean, 'mean-std': mean - std}
    return xr.Dataset(results, attrs=attrs)


### --------------------- math with error propagation --------------------- ###

_paramdocs_werrmath = {
    'A_B': '''xarray.Dataset or DataArray; B can also be any other value.
        Dataset --> mean = ds['mean']; std = ds.get('std', default=0).
        else --> assume it represents 'mean', with std=0.''',
    'require_std': '''bool
        whether to require at least one of A or B to have 'std'.
        if True and std missing from both, crash with InputError.''',
}

def _xarray_werrmath_inputs(A, B, *, require_std=True):
    '''return meanA, stdA, meanB, stdB.
    if 'std' missing from one, assume std=0 for that one.
    if require_std and std missing from both, crash with InputError.
    '''
    found_std = []
    if isinstance(A, xr.Dataset):
        Amean = A['mean']
        Astd = A.get('std', 0)
        found_std.append('A')
    else:
        Amean = A
        Astd = 0
    if isinstance(B, xr.Dataset):
        Bmean = B['mean']
        Bstd = B.get('std', 0)
        found_std.append('B')
    else:
        Bmean = B
        Bstd = 0
    if require_std and not found_std:
        raise InputError('to use werrmath, A and/or B must be a Dataset with "std" data_var.')
    return Amean, Astd, Bmean, Bstd

def _xarray_werrmath_postprocess(A, B, mean, std):
    '''return Dataset of mean and std, copying all other details from A (if Dataset) else B.
    (other details include coords, attrs, and any data_vars unrelated to werrmath.)
    '''
    if isinstance(A, xr.Dataset):
        result = A
    elif isinstance(B, xr.Dataset):
        result = B
    else:
        raise InputError(f'expected A or B to be a Dataset, got {type(A)} and {type(B)}')
    result = result.assign({'mean': mean, 'std': std})
    return result

@pcAccessor.register('werradd')
@format_docstring(**_paramdocs_werrmath)
def xarray_werradd(A, B, *, require_std=True):
    '''returns dataset of 'mean' and 'std' for A + B, including error propagation.
    Assumes independent errors and applies the "standard" formula:
        mean(A + B) = mean(A) + mean(B)
        std(A + B) = sqrt(std(A)**2 + std(B)**2)

    A, B: {A_B}
    require_std: {require_std}
    '''
    Amean, Astd, Bmean, Bstd = _xarray_werrmath_inputs(A, B, require_std=require_std)
    mean = Amean + Bmean
    std = np.sqrt(Astd**2 + Bstd**2)
    return _xarray_werrmath_postprocess(A, B, mean, std)

@pcAccessor.register('werrsub')
@format_docstring(**_paramdocs_werrmath)
def xarray_werrsub(A, B, *, require_std=True):
    '''returns dataset of 'mean' and 'std' for A - B, including error propagation.
    Assumes independent errors and applies the "standard" formula:
        mean(A - B) = mean(A) - mean(B)
        std(A - B) = sqrt(std(A)**2 + std(B)**2)

    A, B: {A_B}
    require_std: {require_std}
    '''
    Amean, Astd, Bmean, Bstd = _xarray_werrmath_inputs(A, B, require_std=require_std)
    mean = Amean - Bmean
    std = np.sqrt(Astd**2 + Bstd**2)
    return _xarray_werrmath_postprocess(A, B, mean, std)

@pcAccessor.register('werrmul')
@format_docstring(**_paramdocs_werrmath)
def xarray_werrmul(A, B, *, require_std=True):
    '''returns dataset of 'mean' and 'std' for A * B, including error propagation.
    Assumes independent errors and applies the "standard" formula:
        z = A * B
        mean(z) = mean(A) * mean(B)
        std(z) = abs(mean(z)) * sqrt((std(A)/mean(A))**2 + (std(B)/mean(B))**2)

    A, B: {A_B}
    require_std: {require_std}
    '''
    Amean, Astd, Bmean, Bstd = _xarray_werrmath_inputs(A, B, require_std=require_std)
    mean = Amean * Bmean
    std = np.abs(mean) * np.sqrt((Astd/Amean)**2 + (Bstd/Bmean)**2)
    return _xarray_werrmath_postprocess(A, B, mean, std)

@pcAccessor.register('werrdiv')
@format_docstring(**_paramdocs_werrmath)
def xarray_werrdiv(A, B, *, require_std=True):
    '''returns dataset of 'mean' and 'std' for A / B, including error propagation.
    Assumes independent errors and applies the "standard" formula:
        z = A / B
        mean(z) = mean(A) / mean(B)
        std(z) = abs(mean(z)) * sqrt((std(A)/mean(A))**2 + (std(B)/mean(B))**2)

    A, B: {A_B}
    require_std: {require_std}
    '''
    Amean, Astd, Bmean, Bstd = _xarray_werrmath_inputs(A, B, require_std=require_std)
    mean = Amean / Bmean
    std = np.abs(mean) * np.sqrt((Astd/Amean)**2 + (Bstd/Bmean)**2)
    return _xarray_werrmath_postprocess(A, B, mean, std)
