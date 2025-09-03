"""
File Purpose: xarray stats, math, and any other aggregation functions.
(aggregation: reducing array along one or more dims)
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor
from .xarray_dimensions import (
    xarray_ensure_dims, _paramdocs_ensure_dims,
)
from ..docs_tools import format_docstring
from ...errors import InputConflictError
from ...defaults import DEFAULTS


### --------------------- Docstrings --------------------- ###

_paramdocs_aggregator = {
    'dim': '''None, str, or iterable of strs
        apply operation along these dimensions''',
    'keep': '''None, str, or iterable of strs
        apply operation along all except for these dimensions.
        (can provide keep or dim, but not both.)''',
    'promote_dims_if_needed': _paramdocs_ensure_dims['promote_dims_if_needed'],
    'missing_dims': f'''{_paramdocs_ensure_dims['missing_dims']}
        if not 'raise', any missing dims will be skipped.''',
}


### --------------------- Aggregators setup --------------------- ###

@format_docstring(**_paramdocs_aggregator)
def _xarray_aggregator_setup(array, dim=None, keep=None, promote_dims_if_needed=True, missing_dims='raise'):
    '''returns (array, dim, keep), adjusted appropriately.
    adjustments include:
        - result dim & keep will be None or list of str. (replace str input s with [s])
        - if keep provided, infer dim from array.
        - can provide dim or keep but not both.
        - (if dim or keep provided) ensure all dim in array.dims.
            promote relevant scalar coords if promote_dims_if_needed.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    if dim is not None and keep is not None:
        raise InputConflictError('cannot provide both "dim" and "keep".')
    if keep is not None:
        keep = [keep] if isinstance(keep, str) else list(keep)
        dim = set(array.dims) - set(keep)
    if dim is not None:
        dim = [dim] if isinstance(dim, str) else list(dim)
        array, dim = xarray_ensure_dims(array, dim, promote_dims_if_needed=promote_dims_if_needed,
                                        missing_dims=missing_dims, return_existing_dims=True)
    return array, dim, keep

@pcAccessor.register('aggregate', aliases=['agg'])
@format_docstring(**_paramdocs_aggregator)
def xarray_aggregate(array, f, dim=None, *, keep=None,
                     promote_dims_if_needed=True, missing_dims='raise', **kw_agg_f):
    '''returns array aggregated along dim using f.

    f: callable or str
        function to aggregate along dim. E.g. xarray.DataArray.sum, or 'mean'.
        Call signature should be like: f(array, dim, **kw).
        str --> will call getattr(array, f)(dim, **kw).
    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to f.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    array, dim, keep = _xarray_aggregator_setup(array, dim, keep, promote_dims_if_needed, missing_dims)
    if isinstance(f, str):
        g = getattr(array, f)
        return g(dim, **kw_agg_f)
    else:
        return f(array, dim, **kw_agg_f)


### --------------------- Math (except stats) --------------------- ###

@pcAccessor.register('sum')
@format_docstring(**_paramdocs_aggregator)
def xarray_sum(array, dim=None, *, keep=None,
               promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray sum but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.sum.
    '''
    return xarray_aggregate(array, 'sum', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)

@pcAccessor.register('prod')
@format_docstring(**_paramdocs_aggregator)
def xarray_prod(array, dim=None, *, keep=None,
               promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray prod but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.prod.
    '''
    return xarray_aggregate(array, 'prod', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)


### --------------------- Stats --------------------- ###

@pcAccessor.register('stats')
@format_docstring(**_paramdocs_aggregator)
def xarray_stats(array, dim=None, stats=None, *, keep=None,
                 promote_dims_if_needed=True, missing_dims='raise',
                 to_da=None, **kw):
    '''returns Dataset of stats for array: min, mean, median, max, std, rms.

    array: xarray.DataArray or xarray.Dataset
        the array (or dataset) from which to compute stats.
        if dataset, compute separate stats for each data var,
            and result will be a dataset with 'stat' dim;
            equivalent to doing xarray_stats for each data_var, with `to_da`='stat'.
    dim: {dim}
    stats: None or iterable of str from ('min', 'mean', 'median', 'max', 'std', 'rms')
        which stats to compute & include in the result.
        None --> equivalent to stats=['min', 'mean', 'median', 'max', 'std', 'rms'].
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}
    to_da: None, bool, or str
        whether to return DataArray instead of Dataset.
        None --> True if `array` is a Dataset, else False.
        False --> result is a Dataset with stats as data vars.
                  (incompatible with input `array` being a Dataset)
        True --> equivalent to to_da='stat'.
        str --> stats reported along this dimension (must not already exist in `array`).
                result type is the same type as input (DataArray or Dataset).

    additional kwargs are passed to array.min, mean, median, max, and std.
    Can provide skipna=True/False to skip NaNs or not; default True for float dtypes.
    '''
    array, dim, keep = _xarray_aggregator_setup(array, dim, keep, promote_dims_if_needed, missing_dims)
    stats = ['min', 'mean', 'median', 'max', 'std', 'rms'] if stats is None else list(stats)
    results = dict()
    if 'min' in stats: results['min'] = array.min(dim, **kw)
    if 'mean' in stats: results['mean'] = array.mean(dim, **kw)
    if 'median' in stats: results['median'] = array.median(dim, **kw)
    if 'max' in stats: results['max'] = array.max(dim, **kw)
    if 'std' in stats: results['std'] = array.std(dim, **kw)
    if 'rms' in stats: results['rms'] = (array**2).mean(dim, **kw)**0.5
    results = {k: results[k] for k in stats}  # <-- style: put in same order as stats.
    # convert to appropriate format for output
    if to_da is None:
        to_da = isinstance(array, xr.Dataset)
    if to_da == False:
        if isinstance(array, xr.Dataset):
            raise InputConflictError('cannot use to_da=False when input is a Dataset.')
        attrs = array.attrs.copy() if xr.get_options()['keep_attrs'] else None
        return xr.Dataset(results, attrs=attrs)
    # <-- if we reached this point, it means we will concatenate. to_da is True (or str).
    if not isinstance(to_da, str):
        to_da = 'stat'
    if to_da in array.coords:
        raise InputConflictError(f'to_da={to_da!r} already in array.coords={set(array.coords)}')
    results = {k: results[k].assign_coords({to_da: k}) for k in results}
    return xr.concat(list(results.values()), dim=to_da)

@pcAccessor.register('min')
@format_docstring(**_paramdocs_aggregator)
def xarray_min(array, dim=None, *, keep=None,
               promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray min but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.min.
    '''
    return xarray_aggregate(array, 'min', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)

@pcAccessor.register('mean')
@format_docstring(**_paramdocs_aggregator)
def xarray_mean(array, dim=None, *, keep=None,
                promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray mean but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.mean.
    '''
    return xarray_aggregate(array, 'mean', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)

@pcAccessor.register('median')
@format_docstring(**_paramdocs_aggregator)
def xarray_median(array, dim=None, *, keep=None,
                  promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray median but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.median.
    '''
    return xarray_aggregate(array, 'median', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)

@pcAccessor.register('max')
@format_docstring(**_paramdocs_aggregator)
def xarray_max(array, dim=None, *, keep=None,
               promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray max but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.max.
    '''
    return xarray_aggregate(array, 'max', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)

@pcAccessor.register('std')
@format_docstring(**_paramdocs_aggregator)
def xarray_std(array, dim=None, *, keep=None,
               promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''Like xarray std but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs are passed to array.std.
    '''
    return xarray_aggregate(array, 'std', dim=dim, keep=keep,
                            promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)

@pcAccessor.register('rms')
@format_docstring(**_paramdocs_aggregator)
def xarray_rms(array, dim=None, *, keep=None,
               promote_dims_if_needed=True, missing_dims='raise', **kw):
    '''(array**2).mean(dim, **kw)**0.5

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}
    '''
    mean2 = xarray_mean(array**2, dim=dim, keep=keep,
                        promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims, **kw)
    return mean2**0.5


### --------------------- Non-aggregators --------------------- ###

def xarray_minimum(array0, *arrays):
    '''minimum across these arrays. Repeatedly apply np.minimum.
    if only input one array, return it, unchanged.
    '''
    if len(arrays) == 0:
        return array0
    result = array0
    for array in arrays:
        result = np.minimum(result, array)
    return result

@pcAccessor.register('minimum', totype='dataset')
def xarray_minimum_of_datavars(ds, *varnames):
    '''minimum across these datavars from ds. Repeatedly apply np.minimum.
    0 varnames --> minimum across all datavars.
    1 varname --> return ds[varname]
    2+ varnames --> minimum across these varnames.
                    equivalent: ds.to_dataarray()[varnames].min(dim='variable')
    '''
    if len(varnames) == 0:
        varnames = list(ds.data_vars)
    vals = [ds[varname] for varname in varnames]
    return xarray_minimum(*vals)

def xarray_maximum(array0, *arrays):
    '''maximum across these arrays. Repeatedly apply np.maximum.
    if only input one array, return it, unchanged.
    '''
    if len(arrays) == 0:
        return array0
    result = array0
    for array in arrays:
        result = np.maximum(result, array)
    return result

@pcAccessor.register('maximum', totype='dataset')
def xarray_maximum_of_datavars(ds, *varnames):
    '''maximum across these datavars from ds. Repeatedly apply np.maximum.
    0 varnames --> maximum across all datavars.
    1 varname --> return ds[varname]
    2+ varnames --> maximum across these varnames.
                    equivalent: ds.to_dataarray()[varnames].max(dim='variable')
    '''
    if len(varnames) == 0:
        varnames = list(ds.data_vars)
    vals = [ds[varname] for varname in varnames]
    return xarray_maximum(*vals)
