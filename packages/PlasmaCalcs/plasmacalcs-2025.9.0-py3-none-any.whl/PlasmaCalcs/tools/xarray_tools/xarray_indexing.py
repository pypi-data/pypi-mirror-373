"""
File Purpose: indexing xarrays
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor
from .xarray_coords import xarray_index_coords
from .xarray_dimensions import (
    is_iterable_dim,
    xarray_ensure_dims, _paramdocs_ensure_dims,
    xarray_squeeze,
)
from ..arrays import interprets_fractional_indexing
from ..docs_tools import format_docstring, docstring_but_strip_examples
from ..os_tools import next_unique_name
from ..sentinels import UNSET
from ...errors import DimensionValueError


### --------------------- Indexing --------------------- ###

@pcAccessor.register('isel')
@format_docstring(isel_doc=docstring_but_strip_examples(xr.DataArray.isel.__doc__),
                  fractional_indexing_doc=interprets_fractional_indexing.__doc__,
                  **_paramdocs_ensure_dims, sub_ntab=1)
def xarray_isel(array, indexers=None, *, promote_dims_if_needed=True,
                drop=False, missing_dims='raise', rounding='round', **indexers_as_kwargs):
    '''array.isel(...) which can also interpret fractional indexes between -1 and 1, and promotes non-dim coords.

    behaves just like xarray.DataArray.isel, but:
        - indexers also allow fractional indexes.
        - if any dim with index provided refers to a non-dimension coordinate, first promote it via swap_dims.
        - if any indexer has 'iseler' attr, use indexer.iseler(values) to determine indexes.
    In particular, for {{cname: index}}:
        - fractional indexes:
            if index is a slice, int, or iterable of ints, use it as is.
            if index contains any values between -1 and 1 (excluding -1, 0, and 1):
                treat that value as a fraction of L=len(array[cname]).
                E.g. 0.25 --> int(L * 0.25);
                    -0.1  --> -int(L * 0.1).
                This is equivalent to interprets_fractional_indexing(index, L)
        - non-dimension coordinates:
            if cname is a non-dimension coordinate, use xarray_promote_dim(array, cname).

    promote_dims_if_needed: {promote_dims_if_needed}
    drop, missing_dims: passed to array.isel; see below for details.
    rounding: passed to interprets_fractional_indexing; see below for details.

    xarray.DataArray.isel docs copied below:
    ----------------------------------------
        {isel_doc}

    interprets_fractional_indexing docs copied below:
    -------------------------------------------------
        {fractional_indexing_doc}
    '''
    if indexers is None:
        indexers = indexers_as_kwargs
    else:
        indexers = {**indexers, **indexers_as_kwargs}
    indexers_input = indexers
    array_input = array  # <-- helps with debugging in case of crash.
    # interpret fractional indexes, and promote coords to dims as necessary.
    indexers = dict()  # <-- not overwriting the originally-input value, this is a new dict.

    kw_ensure_dims = dict(promote_dims_if_needed=promote_dims_if_needed, missing_dims=missing_dims,
                          assert_1d=True,  # because here doesn't implement any way to index 2D+ dims.
                          return_existing_dims=True,  # so we can avoid indexing any missing dims!
                          )
    array, existing_dims = xarray_ensure_dims(array, list(indexers_input.keys()), **kw_ensure_dims)
    for cname in existing_dims:
        index = indexers_input[cname]
        coord = array.coords[cname]
        if hasattr(index, 'iseler'):
            ii = index.iseler(coord)
        else:
            ii = interprets_fractional_indexing(index, L=len(coord), rounding=rounding)
        indexers[cname] = ii
    # call isel
    return array.isel(indexers, drop=drop, missing_dims=missing_dims)

@pcAccessor.register('search')
def xarray_search(array, dim, value):
    '''return first index of value along dim
    (or coord. returns 0, not crash, if scalar coord which matches value.)
    Not efficient for large dims. For large sorted dims, see xarray.DataArray.searchsorted.

    crash with DimensionValueError if value not found in dim.
    '''
    for i, val in enumerate(np.atleast_1d(array.coords[dim].values)):
        if val == value:
            return i
    raise DimensionValueError(f'value={value!r} not found in array[{dim!r}]')

@pcAccessor.register('sel')
@format_docstring(sel_doc=docstring_but_strip_examples(xr.DataArray.sel.__doc__),
                  **_paramdocs_ensure_dims)
def xarray_sel(array, indexers=None, *, promote_dims_if_needed=True,
               method=None, tolerance=None, drop=False, **indexers_as_kwargs):
    '''array.sel(...) but prioritize general applicability over efficiency:
        - promote non-dimension coordinate dims first if applicable
        - (if coord.dtype is object) check coord equality,
            e.g. 0==Fluid('e', 0)=='e', so could use Fluid('e', 0), 'e', or 0 in sel.
            - can also use list, tuple, or 1D non-string iterable,
                e.g. ['e', 3, 'Fe+'] to get multiple fluids.
            - can also use slice,
                e.g. slice('e', 'Fe+', 2) to get every other fluid,
                starting from 'e', stopping before the first 'Fe+' match.
        - if indexer has 'iseler' attr, use indexer.iseler(values) to determine indexes.

    Assumes all indexing is for 1D dims. For indexing 2D+ dims, use xarray methods directly.

    promote_dims_if_needed: {promote_dims_if_needed}
    method: None or str
        method to use for inexact matches, for non-object dtype coords.

    xarray.DataArray.sel docs copied below:
    ----------------------------------------
        {sel_doc}
    '''
    if indexers is None:
        indexers = indexers_as_kwargs
    else:
        indexers = {**indexers, **indexers_as_kwargs}
    indexers_input = indexers
    sel_indexers = dict()  # indexing to delegate to xarray.sel
    obj_indexers = dict()  # indexing to handle here
    array_input = array  # <-- helps with debugging in case of crash.
    kw_ensure_dims = dict(promote_dims_if_needed=promote_dims_if_needed, missing_dims='raise',
                          assert_1d=True,  # because here doesn't implement any way to index 2D+ dims.
                          return_existing_dims=True,  # so we can avoid indexing any missing dims!
                          )
    array, existing_dims = xarray_ensure_dims(array, list(indexers_input.keys()), **kw_ensure_dims)
    for cname in existing_dims:
        if array[cname].dtype == object:
            obj_indexers[cname] = indexers_input[cname]
        else:
            sel_indexers[cname] = indexers_input[cname]
    # handle obj_indexers first.
    obj_isels = {}
    if len(obj_indexers) > 0:
        if method is not None:
            raise TypeError(f'cannot use method {method!r} with object dtype coords {list(obj_indexers)}.')
        for cname, index in obj_indexers.items():
            if hasattr(index, 'iseler'):
                obj_isels[cname] = index.iseler(array.coords[cname])
            elif is_iterable_dim(index):
                isel_here = []
                for ival in index:
                    isel_here.append(xarray_search(array, cname, ival))
                obj_isels[cname] = isel_here
            elif isinstance(index, slice):
                start, stop, step = index.start, index.stop, index.step
                istart, istop = None, None
                if start is not None:
                    istart = xarray_search(array, cname, start)
                if stop is not None:
                    istop = xarray_search(array, cname, stop)
                obj_isels[cname] = slice(istart, istop, step)
            else:  # index is a single value for a dim
                obj_isels[cname] = xarray_search(array, cname, index)
    array = array.isel(obj_isels, drop=drop)
    # handle sel_indexers
    return array.sel(sel_indexers, method=method, tolerance=tolerance, drop=drop)


### --------------------- Custom where --------------------- ###

@pcAccessor.register('where')
def xarray_where(array, cond, other=UNSET, *, drop=False, skip_if_no_matching_dims=True):
    '''like xarray's builtin where, but return array unchanged if it has no dims matching cond.

    array: xarray.DataArray or xarray.Dataset
        array to apply condition to.
    cond: xarray.DataArray, xarray.Dataset, or callable
        Locations at which to preserve array's values. Must have dtype=bool.
        callable --> replace with cond(array).
    other: UNSET, scalar, DataArray, Dataset, or callable, optional
        Value to use for locations in array where cond is False.
        By default, these locations are filled with NA.
        callable --> replace with other(array).
        UNSET --> do not pass this arg to xarray.where()
    drop: bool, default: False
        If True, coordinate labels that only correspond to False values of
        the condition are dropped from the result.
    skip_if_no_matching_dims: bool, default: True
        If True, return array unchanged if it has no dims matching cond.
                if Dataset, keep data_vars unchanged if they have no dims matching cond.
        If False, return array.where(cond, other=other, drop=drop) directly.
    '''
    kw_where = dict(drop=drop) if other is UNSET else dict(other=other, drop=drop)
    if skip_if_no_matching_dims:  # custom processing here
        if callable(cond):
            cond = cond(array)
        if not any(d in array.coords for d in cond.dims):
            return array
        if isinstance(array, xr.Dataset):
            ds = array
            ds0 = ds  # ds before changing ds var.
            # hit data_vars with any dims matching cond, then append remaining vars.
            to_where = []
            to_skip = []
            for var, val in ds.data_vars.items():
                if any(d in val.coords for d in cond.dims):
                    to_where.append(var)
                else:
                    to_skip.append(var)
            if len(to_where) == 0:
                assert False, 'coding error, should have been handled above.'
            ds = ds[to_where].where(cond, **kw_where)
            if len(to_skip) > 0:
                ds = ds.assign(ds0[to_skip])
            return ds
    # else:
    return array.where(cond, **kw_where)


### --------------------- Mapping --------------------- ###

@pcAccessor.register('map')
@format_docstring(**_paramdocs_ensure_dims)
def xarray_map(array, f, *args_f, axis=None, axes=None,
                     promote_dims_if_needed=True, missing_dims='raise', **kw_f):
    '''func(array, *args_f, **kw_f), but axis/axes can be provided as strings!

    Mainly useful if trying to apply f which expects unlabeled array & int axes inputs.
    E.g. numpy.mean can use axis kwarg as iterable of ints,
        but here can provide axis as a dim name str or list of dim names.
    Probably not super useful for mean, since xarray provides xr.mean,
        but may be useful for other functions e.g. scipy.ndimage.gaussian_filter,
        which might not have an existing equivalent in xarray.

    array: xarray.DataArray or Dataset
        apply f to this array, or each array in this Dataset
    f: callable
        will be called as f(array, *args_f, **kw_f),
        possibly will also be passed a value for axis or axes, if provided here
    axis, axes: None, str, or iterable of strs
        if provided, convert to axes positions in dataarray, and pass to f as int(s).
        Also promotes these coords to dims if necessary.
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}
    '''
    # if Dataset, just apply this to each array.
    if isinstance(array, xr.Dataset):
        ds = array
        result = ds.copy()
        for name, arr in ds.data_vars.items():
            result[name] = xarray_map(arr, f, *args_f, axis=axis, axes=axes,
                                      promote_dims_if_needed=promote_dims_if_needed,
                                      missing_dims=missing_dims, **kw_f)
        return result
    # bookkeeping on 'axis' & 'axes' inputs:
    if axis is None and axes is None:  # simplest case; will just apply f to entire array.
        coords = None
        kw_ax = dict()
    elif axis is not None:  # and axes is None
        coords = axis
        ax_key = 'axis'
    elif axes is not None:  # and axis is None
        coords = axes
        ax_key = 'axes'
    else:  # both axis and axes were provided
        raise InputConflictError('cannot provide both "axis" and "axes".')
    if coords is not None:
        _single_ax_mode = isinstance(coords, str)
        if isinstance(coords, str):
            coords = [coords]
        # ensure the coords exist:
        array, existing_dims = xarray_ensure_dims(array, coords,
                                                  promote_dims_if_needed=promote_dims_if_needed,
                                                  missing_dims=missing_dims, return_existing_dims=True)
        if _single_ax_mode and len(existing_dims) == 1:
            existing_dims = existing_dims.pop()  # e.g., np.argsort expects int ax, not tuple!
        # convert coords to ax nums:
        ax_nums = array.get_axis_num(existing_dims)
        kw_ax = {ax_key: ax_nums}
    # call f but use xarray.Dataset.map functionality to preserve coords/attrs/etc.
    array_name = array.name
    _data_var_name = next_unique_name('_internal_variable', [*array.coords, *array.dims])
    ds = array.to_dataset(name=_data_var_name)
    ds_result = ds.map(f, args=args_f, **kw_f, **kw_ax)
    result = ds_result[_data_var_name].rename(array_name)
    return result


### --------------------- Fancy sorting --------------------- ###

_paramdocs_sort = {
    # argsort & sort
    'newname': '''str
        result dim will be replaced by newname.format(dim=dim). Default: '{dim}_sort'.''',
    'ascending': '''bool
        result sorted in ascending order if True, descending if False.''',
    'nkeep': '''None or int
        number of sorted values to keep. E.g. nkeep=2 --> keep only the first 2 values.
        equivalent to using result.isel(newdim=(0, nkeep)), where newdim=newname.format(dim=dim).''',
    'promote_dims_if_needed': _paramdocs_ensure_dims['promote_dims_if_needed'],
    'squeeze': '''bool
        whether to drop redundant dims for argsort result.
        This means any dims with np.all(array==array.isel(dim=0)). (This includes dims with len=1.)''',
    'kind': '''None or str from {'quicksort', 'mergesort', 'heapsort', 'stable'}
        sorting algorithm. Passed directly to numpy.argsort; see help(numpy.argsort) for details.''',
    # sort, only
    'index': '''bool
        whether to use indexes for result's dim coord values, instead of original coord values.
        Either way, the relevant coord is multidimensional, varying across all array.dims except dim.
        True --> result['{dim}_index'] will be the indexes along original dim
        False --> result[dim] will be the original coord values.''',
    'newname_original': '''str
        name to use for original dim's coord values if store_original=True. Default: '{dim}_orig'.''',
}


@pcAccessor.register('argsort', totype='array')
@format_docstring(**_paramdocs_sort)
def xarray_argsort(array, dim, newname='{dim}_sort', *, ascending=True, nkeep=None,
                   promote_dims_if_needed=True, squeeze=True, kind=None):
    '''argsort for xarray.DataArray; returns indexes along dim which would sort array along dim.
    Drops original coords along dim, because the output along dim is now the indexes;
        result[i] corresponds to coord value array[dim][result[i]], not array[dim][i].

    Good examples to consider (where result=xarray_argsort(array, dim)):
        (1) sortarr = array.isel(dim=result) to get sorted array,
            which will have dim as a multidimensional coordinate with same dims as argsort result,
            and values telling original values of dim, sorted appropriately.
        (2) sortarr = array.isel(dim=result.isel(newdim=slice(0, N)) to get sorted array,
            similar to example (1), but only keeping first N lowest values
            (or N highest values if ascending=False when getting argsort result).

    array: xarray.DataArray
        array to argsort.
    dim: str
        dimension along which to sort.
    newname: {newname}
    ascending: {ascending}
    nkeep: {nkeep}
    promote_dims_if_needed: {promote_dims_if_needed}
    squeeze: {squeeze}
    kind: {kind}
    '''
    result = xarray_map(array, np.argsort, axis=dim,
                        promote_dims_if_needed=promote_dims_if_needed,
                        kind=kind)
    if not ascending:
        result = result.isel({dim: slice(None, None, -1)})
    newdim = newname.format(dim=dim)
    if newdim in array:
        raise NotImplementedError(f'xarray_argsort when newdim={newdim!r} already exists in array')
    result = result.drop_vars(dim).rename({dim: newdim})
    if nkeep is not None:
        result = result.isel({newdim: slice(0, nkeep)})
    if squeeze:
        result = xarray_squeeze(result)
    return result

@pcAccessor.register('sort_along', totype='array')
@format_docstring(**_paramdocs_sort)
def xarray_sort_array_along(array, dim, newname='{dim}_sort', *, ascending=True, nkeep=None,
                            index=False, store_original=False, newname_original='{dim}_orig',
                            promote_dims_if_needed=True, squeeze_argsort=True, kind=None):
    '''returns array, sorted along dim.
    
    array: xarray.DataArray
        array to sort.
    dim: str
        dimension along which to sort.
    newname: {newname}
    ascending: {ascending}
    nkeep: {nkeep}
    index: {index}
    store_original: bool
        whether to store original dim's coord values in result.
        True --> result will be a Dataset with data_vars array.name and '{{dim}}_orig';
            result[array.name] = sorted values (dims=array.dims but replace dim with newname.format(dim=dim))
            result['{{dim}}_orig'] = original values of dim (dims='{{dim}}_orig')
        False --> result will be a DataArray which does not track original dim's coord values separately.
    newname_original: {newname_original}
    promote_dims_if_needed: {promote_dims_if_needed}
    squeeze_argsort: {squeeze}
    kind: {kind}
    '''
    if store_original and array.name is None:
        raise InputConflictError('cannot use store_original=True, when array.name is None.')
    asort = xarray_argsort(array, dim, newname=newname, ascending=ascending, nkeep=nkeep,
                            promote_dims_if_needed=promote_dims_if_needed,
                            squeeze=squeeze_argsort, kind=kind)
    array_input = array
    if index:
        array = xarray_index_coords(array, dim, drop=True)
    result = array.isel({dim: asort})
    if store_original:
        origname = newname_original.format(dim=dim)
        if origname in array_input:
            raise NotImplementedError(f'xarray_sort_array_along when origname={origname!r} already exists')
        original = array_input[dim].rename({dim: origname})
        result = xr.Dataset({array.name: result, origname: original})
    return result

@pcAccessor.register('sort_along', totype='dataset')
@format_docstring(**_paramdocs_sort)
def xarray_sort_dataset_along(ds, var, dim, newname='{dim}_sort', *, ascending=True, nkeep=None,
                              index=False, store_original=True, newname_original='{dim}_orig',
                              promote_dims_if_needed=True, squeeze_argsort=True, kind=None):
    '''returns dataset, sorted along var's values for dim.

    dataset: xarray.Dataset
        dataset to sort.
    var: str
        data_var which determines sort order.
    dim: str
        dimension along which to sort.
    newname: {newname}
    ascending: {ascending}
    nkeep: {nkeep}
    index: {index}
    store_original: bool
        whether to store original dim's coord values in result.
        True --> result['{{dim}}_orig'] = original values of dim (dims='{{dim}}_orig')
        False --> do not add original values of dim as a data_var in result.
    newname_original: {newname_original}
    promote_dims_if_needed: {promote_dims_if_needed}
    squeeze_argsort: {squeeze}
    kind: {kind}
    '''
    ds_input = ds
    array = ds[var]
    asort = xarray_argsort(array, dim, newname=newname, ascending=ascending, nkeep=nkeep,
                            promote_dims_if_needed=promote_dims_if_needed,
                            squeeze=squeeze_argsort, kind=kind)
    if index:
        ds = xarray_index_coords(ds, dim, drop=True)
    result = ds.isel({dim: asort})
    if store_original:
        origname = newname_original.format(dim=dim)
        if origname in ds_input:
            raise NotImplementedError(f'xarray_sort_dataset_along when origname={origname!r} already exists')
        original = ds_input[dim].rename({dim: origname})
        result[origname] = original
    return result


### --------------------- Fancy argmin/max --------------------- ###
# [EFF] uses np.argmin/max instead of reusing algorithms above for a full sort.
# For argmin/max itself, use xarray builtin, e.g. array.argmin(dim=dim).

@pcAccessor.register('cmin', totype='array')
@format_docstring(**_paramdocs_sort)
def xarray_cmin(array, coord, where=UNSET, *, promote_dims_if_needed=True):
    '''return (array of) coord value(s) at array.argmin(dim=dim associated with coord).
    coord must be a dimension, or associated with a single 1D dimension.

    array: xarray.DataArray
        array to find minimum value in.
    coord: str
        coord along which to find min.
    promote_dims_if_needed: {promote_dims_if_needed}

    see also: xarray_min_coord_where
    '''
    array = xarray_ensure_dims(array, coord, promote_dims_if_needed=promote_dims_if_needed)
    argmin = array.argmin(coord)
    return array[coord].isel({coord: argmin})

@pcAccessor.register('cmax', totype='array')
@format_docstring(**_paramdocs_sort)
def xarray_cmax(array, coord, where=UNSET, *, promote_dims_if_needed=True):
    '''return (array of) coord value(s) at array.argmax(dim=dim associated with coord).
    coord must be a dimension, or associated with a single 1D dimension.

    array: xarray.DataArray
        array to find max value in.
    coord: str
        coord along which to find max.
    promote_dims_if_needed: {promote_dims_if_needed}

    see also: xarray_max_coord_where
    '''
    array = xarray_ensure_dims(array, coord, promote_dims_if_needed=promote_dims_if_needed)
    argmax = array.argmax(coord)
    return array[coord].isel({coord: argmax})

@pcAccessor.register('varmin', totype='dataset')
@format_docstring(**_paramdocs_sort)
def xarray_varmin(ds, *, promote_dims_if_needed=True):
    '''return (array of) var name(s) for var with minimum values in ds.
    equivalent: xarray_cmin(ds.to_dataarray(), 'variable')

    ds: xarray.Dataset
        dataset to find minimum value in.
    promote_dims_if_needed: {promote_dims_if_needed}
    '''
    return xarray_cmin(ds.to_array(), 'variable', promote_dims_if_needed=promote_dims_if_needed)

@pcAccessor.register('varmax', totype='dataset')
@format_docstring(**_paramdocs_sort)
def xarray_varmax(ds, *, promote_dims_if_needed=True):
    '''return (array of) var name(s) for var with maximum values in ds.
    equivalent: xarray_cmax(ds.to_dataarray(), 'variable')

    ds: xarray.Dataset
        dataset to find maximum value in.
    promote_dims_if_needed: {promote_dims_if_needed}
    '''
    return xarray_cmax(ds.to_array(), 'variable', promote_dims_if_needed=promote_dims_if_needed)

@pcAccessor.register('at_min_of')
@format_docstring(**_paramdocs_sort)
def xarray_at_min_of(array, of, dim=None, *, promote_dims_if_needed=True):
    '''return array values at locations of minimum `of`. Roughly: array.isel(of.argmin([dim])).
    But, here is nicer, in a few ways:
        (1) here doesn't require array to have all dims in dim.
            E.g., if array has dims 'x', 'kmod', and `of` has dims 'kmod', 'kang',
                and dim=['kmod', 'kang'], it will be handled in the intuitive way. Roughly:
                    amin = of.argmin(['kmod', 'kang'])
                    result = array.isel(kmod=amin['kmod'])
        (2) here allows All-NaN slice in `of`.
            all-nan slices in `of` will be filled with nan values in result.
            E.g., if dims=['d0', 'd1'], `of` has dims ['d0', 'd1', 'nmul', 'fluid'],
                and of.isnull().all(['d0', 'd1']) when nmul index == 4 or 5, and fluid index == 2,
                then result.isel(nmul=[4,5], fluid=2) will be filled with nan values.

    array: xarray.DataArray or xarray.Dataset
        array to get result values from.
    of: xarray.DataArray
        array to find minimum values in.
    dim: None, str, or list of str
        dim(s) along which to find the minimum values of `of`.
        Takes the "simultaneous" minimum along all these dims, as per argmin(dims)
        None --> use of.dims.
        (if dim is a list with len==0, return array, unchanged.)
    promote_dims_if_needed: {promote_dims_if_needed}
    '''
    if dim is None:
        dim = of.dims
    if isinstance(dim, str):
        dim = [dim]
    if len(dim) == 0:
        return array
    # compute indexing
    allnan = of.isnull().all(dim)
    any_allnan = allnan.any()
    if any_allnan:
        of = of.fillna(np.inf)  # np.inf never interferes with argmin results.
    idx = of.argmin(dim)
    # apply indexing to array
    array, existing = xarray_ensure_dims(array, dim, promote_dims_if_needed=promote_dims_if_needed,
                                         missing_dims='ignore', return_existing_dims=True)
    result = array.isel({d: idx[d] for d in existing})
    if any_allnan:
        result = result.where(~allnan)
    return result

@pcAccessor.register('at_max_of')
@format_docstring(**_paramdocs_sort)
def xarray_at_max_of(array, of, dim=None, *, promote_dims_if_needed=True):
    '''return array values at locations of maximum `of`. Roughly: array.isel(of.argmax([dim])).
    But, here is nicer, in a few ways:
        (1) here doesn't require array to have all dims in dim.
            E.g., if array has dims 'x', 'kmod', and `of` has dims 'kmod', 'kang',
                and dim=['kmod', 'kang'], it will be handled in the intuitive way. Roughly:
                    amax = of.argmax(['kmod', 'kang'])
                    result = array.isel(kmod=amax['kmod'])
        (2) here allows All-NaN slice in `of`.
            all-nan slices in `of` will be filled with nan values in result.
            E.g., if dims=['d0', 'd1'], `of` has dims ['d0', 'd1', 'nmul', 'fluid'],
                and of.isnull().all(['d0', 'd1']) when nmul index == 4 or 5, and fluid index == 2,
                then result.isel(nmul=[4,5], fluid=2) will be filled with nan values.

    array: xarray.DataArray or xarray.Dataset
        array to get result values from.
    of: xarray.DataArray
        array to find maximum values in.
    dim: None, str, or list of str
        dim(s) along which to find the maximum values of `of`.
        Takes the "simultaneous" maximum along all these dims, as per argmax(dims)
        None --> use of.dims.
        (if dim is a list with len==0, return array, unchanged.)
    promote_dims_if_needed: {promote_dims_if_needed}
    '''
    # [TODO] encapsulate repeated code from xarray_at_min_of.
    if dim is None:
        dim = of.dims
    if isinstance(dim, str):
        dim = [dim]
    if len(dim) == 0:  # edge case
        return array
    # compute indexing
    allnan = of.isnull().all(dim)  # check for allnan slices
    any_allnan = allnan.any()
    if any_allnan:
        of = of.fillna(-np.inf)  # -np.inf never interferes with argmax results.
    idx = of.argmax(dim)
    # apply indexing to array
    array, existing = xarray_ensure_dims(array, dim, promote_dims_if_needed=promote_dims_if_needed,
                                         missing_dims='ignore', return_existing_dims=True)
    result = array.isel({d: idx[d] for d in existing})
    if any_allnan:
        result = result.where(~allnan)
    return result

@pcAccessor.register('min_coord_where', totype='array')
@format_docstring(**_paramdocs_sort)
def xarray_min_coord_where(array, coord, where,  *, promote_dims_if_needed=True):
    '''return (array of) minimum value(s) of coord, where condition is True.

    array: xarray.DataArray
        array to find minimum value in.
    coord: str
        coord whose minimum value will appear in the result.
        Must correspond with a single dimension of array.
    where: xarray.DataArray or callable
        locations at which to consider values of coord.
        callable --> use where=where(array)
                    (will promote coord to dim first, if coord not dim yet.)
    promote_dims_if_needed: {promote_dims_if_needed}

    Example:
        xarray_min_coord_where(growth, 'E', lambda arr: arr>0)
        # returns the minimum value(s) of E across all regions where growth>0.
        # (result has no 'E' dim, but does retain any other dims from array.)

        Compare to xarray_cmin(growth.where(growth>0), 'E'),
        which tells the value of E at the location of minimum growth (where growth>0)
        (but not necessarily the minimum E across all regions with growth>0).
    '''
    array = xarray_ensure_dims(array, coord, promote_dims_if_needed=promote_dims_if_needed)
    if callable(where):
        where = where(array)
    tmp = array[coord].where(where)
    return tmp.min(dim=coord)

@pcAccessor.register('max_coord_where', totype='array')
@format_docstring(**_paramdocs_sort)
def xarray_max_coord_where(array, coord, where,  *, promote_dims_if_needed=True):
    '''return (array of) maximum value(s) of coord, where condition is True.

    array: xarray.DataArray
        array to find maximum value in.
    coord: str
        coord whose maximum value will appear in the result.
        Must correspond with a single dimension of array.
    where: xarray.DataArray or callable
        locations at which to consider values of coord.
        callable --> use where=where(array)
                    (will promote coord to dim first, if coord not dim yet.)
    promote_dims_if_needed: {promote_dims_if_needed}

    Example:
        xarray_max_coord_where(growth, 'kmod', lambda arr: arr>0)
        # returns the maximum value(s) of kmod across all regions where growth>0.
        # (result has no 'kmod' dim, but does retain any other dims from array.)

        Compare to xarray_cmax(growth.where(growth>0), 'kmod'),
        which tells the value of kmod at the location of max growth (where growth>0)
        (but not necessarily the maximum kmod across all regions with growth>0).
    '''
    array = xarray_ensure_dims(array, coord, promote_dims_if_needed=promote_dims_if_needed)
    if callable(where):
        where = where(array)
    tmp = array[coord].where(where)
    return tmp.max(dim=coord)
