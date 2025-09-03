"""
File Purpose: tools related to xarray dimensions
"""
import numpy as np
import xarray as xr
try:
    from xarray.computation.rolling import DataArrayCoarsen
except ImportError:
    from xarray.core.rolling import DataArrayCoarsen
# note: can't use "xr.core.rolling.DataArrayCoarsen" directly in a new python kernel,
#    although it does work after creating an xr.DataArray.coarsen() object.
#    imported it here so that we can use xr.DataArray.coarsen docstring.

from .xarray_accessors import pcAccessor
from .xarray_misc import xarray_copy_kw
from ..docs_tools import format_docstring
from ..sentinels import UNSET
from ...errors import (
    DimensionalityError, DimensionValueError, DimensionKeyError,
    InputConflictError,
)


### --------------------- Docstrings --------------------- ###

_paramdocs_ensure_dims = {
    'promote_dims_if_needed': '''bool
        whether to promote non-dimension coords to dimensions.
        if False, raise DimensionKeyError if any relevant coord is not already a dimension.''',
    'missing_dims': '''str in ('ignore', 'warn', 'raise')
        what to do if any coord is not found:
            'ignore' --> do nothing.
            'warn' --> raise a warning.
            'raise' --> raise DimensionKeyError.''',
}


### --------------------- Dimensions --------------------- ###

def is_iterable_dim(value, *, min_length=None):
    '''returns whether value represents multiple values (of a dimension).

    if value.ndim exists,
        return False if ndim==0,
        else True if ndim > 0,
        else raise DimensionalityError.
    # else, return whether iter(value) succeeds.  # <-- no longer used; use is_scalar from xr.
    else, return (not xr.core.utils.is_scalar(value))

    min_length: None or int
        if provided, before returning True, require that len(value) >= min_length.
    '''
    if hasattr(value, 'ndim'):
        ndim = value.ndim
        if ndim == 0:
            result = False
        elif ndim > 0:
            result = True
        else:
            raise DimensionalityError(f"expected ndim >= 0, but got ndim={ndim}.")
    else:
        result = (not xr.core.utils.is_scalar(value))
    if result and (min_length is not None):
        try:
            L = len(value)
        except TypeError:
            result = False  # couldn't determine length, so assume it's not long enough.
        else:
            result = result and (L >= min_length)
    return result

def take_along_dimension(dimension, array, at=None, *, i=None, default=UNSET,
                         drop_labels=False, as_dict=False, item=False):
    '''returns something like: [array.sel({dimension: val}) for val in ``at``]
    i.e., list of taking these values along this dimension of array.

    at: None or list-like of values in this dimension
        take at these values. None --> use values from array.coords[dimension]
    i: None or indices.
        (if provided) take only at these indices; use isel.
    default: UNSET or any value
        if provided, use this value for any at[i] not in array.coords[dimension].
        if not already an xarray.DataArray, convert it, and set coords[dimension]=at[i].
            (e.g. take_along_dimension('component', arr, at=['x'], default=0),
            if arr doesn't have 'component'=='x', will give xarray.DataArray(0, coords={'component': 'x'}))
    drop_labels: bool, default False
        if True, drop the labels along the taken dimension.
        E.g., if dimension=='component' and labels=['x', 'y'],
            by default, result[0].component=='x' and result[1].component=='y'
            but if drop_labels then result[0] and result[1] will not have .component at all.
    as_dict: bool, default False
        if True, return dict of {dim value: array value at this dim}
            (instead of a list of array value at each dim value)
    item: bool
        if True, convert arrays to single values via array.item().

    if array is 0-d along dimension,
        returns [array] if labels corresponds to the one label in this dimension.
    '''
    if i is not None:
        if at is not None:
            raise InputConflictError('cannot provide both "at" and "i".')
        iseled = array.isel({dimension: i})
        return take_along_dimension(dimension, iseled, drop_labels=drop_labels, as_dict=as_dict)
    # else, i is None
    coords = array.coords[dimension]
    # 0d coords
    if coords.ndim == 0:
        coord = coords.item()
        if at is None:
            result = [array]
            used_at = [coord]
        else:
            if all(val == coord for val in at):
                result = [array] * len(at)  # list multiplication
                used_at = at
            else:
                errmsg = (f'provided value for "at" is incompatible with 0-d {dimension!r} values; '
                          f'\ncoords={coords};\nat={at}')
                raise DimensionalityError(errmsg)
    # 1d coords
    elif coords.ndim == 1:
        if at is None:
            # use all of them.
            result = [array.isel({dimension: i_}) for i_ in range(len(coords))]
            used_at = [val.item() for val in coords]
        else:
            # use only some of them.
            # [TODO] xarray.sel doesn't really like DimensionValue... why not?
            #   (using another way to do it, in the meantime.)
            result = []
            for val in at:
                i_ = np.nonzero((coords == val).values)[0]
                if len(i_) == 0:
                    if default is UNSET:
                        raise DimensionValueError(f'no match for val={val!r} in coords={coords}')
                    else:
                        if isinstance(default, xr.DataArray):
                            result.append(default)
                        else:
                            result.append(xr.DataArray(default, coords={dimension: val}))
                elif len(i_) == 1:
                    result.append(array.isel({dimension: i_[0]}))
                else:
                    raise DimensionValueError(f'expected 1 match, but got {len(i_)} matches for val={val!r}')
            used_at = at
    # 2d+ coords
    else:
        raise NotImplementedError(f'take_along_dimension {dimension!r} with ndim={coords.ndim}')
    # postprocessing / bookkeping
    if drop_labels:
        result = [array.drop_vars(dimension) for array in result]
    if item:
        result = [array.item() for array in result]
    if as_dict:
        result = {val: array for val, array in zip(used_at, result)}
    return result

@pcAccessor.register
def take_along_dimensions(array, dimensions, *, atleast_1d=False, **kw_isel):
    '''returns result of taking array along each of these dimensions, in order.
    result will be a numpy array with dtype=object, shape=(d0, d1, ...),
        where di = len(array.coords[dimensions[i]]).
    each element of result will be an xarray.DataArray.

    any dimension can be None --> result shape will be 1 at that dimension, and nothing will be taken.
        E.g. take_along_dimensions(array, [None, 'fluid']) gives array of shape (1, len(fluids)).

    if dimensions is an empty list:
        result will be a scalar numpy array with result[()] = `array`,
        unless atleast_1d=True; then result has shape (1,) and result[0] = `array`.
    '''
    if isinstance(dimensions, str):
        dimensions = [dimensions]
    shape = tuple((1 if dim is None else len(array.coords[dim])) for dim in dimensions)
    result = np.empty(shape, dtype=object)
    if len(shape) == 0:
        if atleast_1d:
            result = np.empty((1,), dtype=object)
            result[0] = array
        else:
            result[()] = array
    else:
        for idx in np.ndindex(*shape):
            selecting = {dim: i for dim, i in zip(dimensions, idx) if dim is not None}
            result[idx] = array.isel(selecting, **kw_isel)
    return result

def join_along_dimension(dimension, arrays, labels=None, *, coords='minimal', **kw_xarray_concat):
    '''returns xr.concat(arrays, dimension). if len(arrays) == 1, instead return arrays[0], unchanged.
    if labels is provided, set result[dimension] = labels
    '''
    if len(arrays) == 1:
        return arrays[0]
    result = xr.concat(arrays, dimension, coords=coords, **kw_xarray_concat)
    if labels is not None:
        result[dimension] = labels
    return result

@pcAccessor.register('rename')
def xarray_rename(array, names=None, **more_names):
    '''return array.rename(names, **more_names), but skip any names not found in array.coords.
    names should be a dict, if provided.
    '''
    if names is not None:
        more_names.update(names)
    apply_names = {name: val for name, val in more_names.items() if name in array.coords}
    return array.rename(apply_names)

@pcAccessor.register('assign')
def xarray_assign(array, coords=None, attrs=None, *, name=UNSET, overwrite=None, expand_if_iterable=False):
    '''array.assign_coords(coords).assign_attrs(attrs).rename(name)
    
    coords: None or dict of {dim: coord}
        each coord must be "non-iterable", as per is_iterable_dim(),
        unless expand_if_iterable=True.
    attrs: None or dict
        assign these attrs. dict of arbitrary values.
    name: UNSET, None, or str
        assign this name to the result, if provided.
    overwrite: None or bool
        whether to overwrite an existing value for coord in array.
        (note - array will never be altered here; only the result might be altered.)
        If any coord already in array.coords, behavior depends on overwrite:
            None --> crash with DimensionKeyError.
            True --> overwrite the coord using the new value.
            False --> return array, unchanged.
    expand_if_iterable: bool
        whether to expand_dims for any iterable coords,
        e.g. array.expand_dims(coords) for the relevant coords.
    '''
    array0 = array  # helps with debugging
    if coords is not None:
        iterable_coords = {dim: val for dim, val in coords.items() if is_iterable_dim(val)}
        if iterable_coords:
            if expand_if_iterable:
                array = array.expand_dims(iterable_coords)
                coords = {dim: val for dim, val in coords.items() if dim not in iterable_coords}
            else:
                errmsg = (f'cannot assign iterable coord(s) when expand_if_iterable=False;'
                          f'got these iterable coords: {iterable_coords}')
                raise DimensionalityError(errmsg)
        if not overwrite:
            coords_already_assigned = set(array.coords).intersection(coords)
            if coords_already_assigned:
                if overwrite is None:
                    errmsg = (f'cannot assign already-assigned coords: {coords_already_assigned}, '
                              f'when overwrite=None.\nTo disable this error, use '
                              f'overwrite=True to update existing coords, or False to skip existing coords.')
                    raise DimensionKeyError(errmsg)
                else:
                    coords = {dim: val for dim, val in coords.items() if dim not in coords_already_assigned}
        if len(coords) > 0:
            array = array.assign_coords(coords)
    if attrs is not None:
        array = array.assign_attrs(attrs)
    if name is not UNSET:
        array = array.rename(name)
    return array

@pcAccessor.register('promote_dim')
def xarray_promote_dim(array, coord, *coords_as_args):
    '''Promote this coord (or these coords) to be a dimension, if it isn't already.
    
    coord: str or iterable of strs
        name of coord(s) to promote.
        if already in array.dims, do nothing.
        if 0D, array.expand_dims(coord).
                (This occurs when coord has no associated dimension, in array.)
        if 1D, array.swap_dims(dict(dim=coord)),
                where dim is the dimension associated with coord.
        if 2D+, crash with DimensionalityError.

    returns array, or a copy of array where coord is one of the dimensions.
    '''
    coords = [coord] if isinstance(coord, str) else coord
    coords = list(coords) + list(coords_as_args)
    to_expand = []
    to_swap = {}
    for coord in coords:
        if coord in array.dims:
            continue  # no need to promote this dim.
        c = array.coords[coord]
        cdims = c.dims
        if len(cdims) == 0:
            to_expand.append(coord)
        elif len(cdims) == 1:
            d = cdims[0]
            if d in to_swap:
                errmsg = (f'multiple coords ({to_swap[d]!r}, {coord!r}) with same dimension ({d!r}), '
                            'cannot promote both of them at the same time.')
                raise DimensionKeyError(errmsg)
            to_swap[d] = coord
        else:
            errmsg = f'cannot promote_dim(coord={coord!r}) for coord with >1 dims: {cdims}'
            raise DimensionalityError(errmsg)
    if 0 == len(to_expand) == len(to_swap):
        return array  # nothing to change.
    if to_expand:
        array = array.expand_dims(tuple(to_expand))
    if to_swap:
        array = array.swap_dims(to_swap)
        # NOTE: swapping when to_swap is empty SHOULD probably just make a copy of array,
        #    however it fails (in xarray version 2024.7.0, at least) to maintain MultiIndex properly,
        #    leading to 'ValueError: cannot re-index or align objects with conflicting indexes...'
        #    with MultiIndex conflicting indexes all completely unrelated to the to_expand and to_swap here,
        #    when doing array math with some promote_dim'd arrays and some non-promote_dim'd arrays.
        # (Workaround: use an 'if' block, so we only swap dims if there are dims to swap.
        #    This workaround might not work always, but it at least prevents the issue when to_swap is empty.)
    return array

@pcAccessor.register('ensure_dims')
@format_docstring(**_paramdocs_ensure_dims)
def xarray_ensure_dims(array, coords, *,
                       promote_dims_if_needed=True, missing_dims='raise',
                       assert_1d=False, return_existing_dims=False):
    '''return array but ensure these coords are dimensions.

    coords: str or iterable of strings
        coords to ensure are dimensions.
    promote_dims_if_needed: {promote_dims_if_needed}
            0D coord --> array.expand_dims(coord)
            1D coord --> array.swap_dims(dict(dim=coord)) for associated dim
            2D+ coord --> crash with DimensionalityError.
    missing_dims: {missing_dims}
    assert_1d: bool, default False
        whether to assert that each of these coords is 1D (after promoting if needed).
    return_existing_dims: bool, default False
        True --> returns [array, set of dims (from input coords) which actually exist]
        probably only useful if missing_dims != 'raise'.
    '''
    if isinstance(coords, str):
        coords = [coords]
    found_missing_dims = set()
    # promote coords
    for cname in coords:
        if promote_dims_if_needed and cname in array.coords:
            array = xarray_promote_dim(array, cname)
        if cname not in array.dims:
            found_missing_dims.add(cname)
            continue
        if assert_1d:
            c = array.coords[cname]
            if c.ndim != 1:
                errmsg = f'ensure_dims expected 1D coord={cname!r}, but got ndim={c.ndim}.'
                raise AssertionError(errmsg)
    # handle missing dims
    if len(found_missing_dims) > 0:
        if missing_dims not in ('ignore', 'warn', 'raise'):
            errmsg = f'invalid missing_dims={missing_dims!r}. Expected "ignore", "warn" or "raise".'
            raise InputError(errmsg)
        if missing_dims =='raise' or missing_dims == 'warn':  # define the error message
            c_or_d = 'coords' if promote_dims_if_needed else 'dims'
            errmsg = (f'Dimensions {found_missing_dims} not found in '
                      f'array.{c_or_d}={set(getattr(array, c_or_d))},\n'
                      f'and missing_dims={missing_dims!r} (using "ignore" would ignore this instead).')
            if missing_dims == 'raise':
                raise DimensionKeyError(errmsg)
            elif missing_dims == 'warn':
                warnings.warn(errmsg)
    # return result
    if return_existing_dims:
        existing_dims = set(coords) - found_missing_dims
        return array, existing_dims
    else:
        return array

@pcAccessor.register('squeeze', totype='array')
def xarray_squeeze(array, dim=None, *, keep=None, drop=True):
    '''return array but drop redundant dims.
    dims are redundant if np.all(array==array.isel(dim=0)).
    This is a more aggressive version of array.squeeze():
        all dims with size 1 are trivially redundant and will be dropped;
        but here, additionally, all dims which are redundant in any way will be dropped.

    dim: None, str, or list of strs
        if provided, only consider dropping these dims.
    keep: None, str, or list of strs
        if provided, do not consider dropping these dims.
        (can provide dim or keep, but not both.)
    drop: bool
        whether to drop coord for size-1 redundant dims.
        if False, will keep scalar coord for size-1 redundant dims.

    E.g. [[0,1,2],[0,1,2]] --> [0,1,2]. (But, as xarray, so result remains well-labeled.)
    '''
    if keep is not None and dim is not None:
        raise InputConflictError(f'cannot provide both dim & keep. Got dim={dim!r}, keep={keep!r}')
    if keep is None:
        dims = array.dims if dim is None else ([dim] if isinstance(dim, str) else dim)
        if any(d not in array.dims for d in dims):
            raise DimensionKeyError(f'all dims must exist, but got dims={dims!r}, array.dims={array.dims}')
    else:
        if isinstance(keep, str): keep = [keep]
        dims = set(array.dims) - set(keep)
    for d in dims:
        dropped = array.isel({d: 0}, drop=drop)
        # could just check np.all(dropped == array), but let's do a few smaller checks first,
        #    to save some computation time in case of large arrays.
        if array.sizes[d] == 1:  # trivially redundant
            array = dropped
        elif np.any(dropped != array.isel({d: 1})):  # clearly not redundant
            continue
        elif np.all(dropped == array):
            array = dropped
    return array

@pcAccessor.register('squeeze_close', totype='array')
def xarray_squeeze_close(array, dim=None, tol=1e-3, *, closeness_name='closeness_{dim}', keep=None, drop=True):
    '''return array but drop redundant dims, with an tolerance when checking equality.
    dims are redundant if all values are close along that dim.
        Closeness check here is: (array.isel(dim=0)/array).std() < tol.
    For each removed dim:
        result will just use array.isel(dim=0).
        result will add coord 'closeness_{dim}' == std(array.isel(dim=0)/array).
    This is a much more aggressive version of array.squeeze():
        all dims with size 1 are trivially redundant and will be dropped;
        but here, additionally, all dims which are redundant in any way will be dropped.
        NOTE: performs all closeness checks before dropping any dims.

    dim: None, str, or list of strs
        if provided, only consider dropping these dims.
    tol: number
        drops dim with tol > (array.isel(dim=0)/array).std().
    closeness_name: None or str, default 'closeness_{dim}'
        add new coord with this name, with value == (array.isel(dim=0)/array).std(),
        for each dim dropped. (smaller is closer.) (always 0 for dims of size 1.)
        (closeness_{dim} value tells the pre-squeeze variation along that dim.)
        None --> do not add this coord.
    keep: None, str, or list of strs
        if provided, do not consider dropping these dims.
        (can provide dim or keep, but not both.)
    drop: bool
        whether to drop coord for size-1 redundant dims.
        if False, will keep scalar coord for size-1 redundant dims.

    See also: xarray_closeness
    '''
    # [TODO] encapsulate code from xarray_squeeze instead of copy-pasting
    if keep is not None and dim is not None:
        raise InputConflictError(f'cannot provide both dim & keep. Got dim={dim!r}, keep={keep!r}')
    if keep is None:
        dims = array.dims if dim is None else ([dim] if isinstance(dim, str) else dim)
        if any(d not in array.dims for d in dims):
            raise DimensionKeyError(f'all dims must exist, but got dims={dims!r}, array.dims={array.dims}')
    else:
        if isinstance(keep, str): keep = [keep]
        dims = set(array.dims) - set(keep)
    to_drop = []  # (handle all dropping at the end)
    for d in dims:
        dropped = array.isel({d: 0})
        if array.sizes[d] == 1:  # trivially redundant
            closeness = 0
            to_drop.append(d)
        else:
            closeness = (dropped / array).std()
            if closeness < tol:
                to_drop.append(d)
            else:
                continue
        if closeness_name is not None:
            closeness_coord = closeness_name.format(dim=d)
            array = array.assign_coords({closeness_coord: closeness})
    if len(to_drop) > 0:
        array = array.isel({d: 0 for d in to_drop}, drop=drop)
    return array

@pcAccessor.register('closeness', totype='array')
def xarray_closeness(array, dim=None):
    '''computes "closeness" along each dim: (array.isel(dim=0)/array).std()
    Result is a dataset with one scalar data_var telling closeness of each dim.
    Note: the std() is always taken across ALL dims of the array.
        [TODO] allow to keep some dims?

    dim: None, str, or list of strs
        if provided, only consider these dims.

    See also: xarray_squeeze_close
    '''
    if dim is None:
        dims = array.dims
    elif isinstance(dim, str):
        dims = [dim]
    else:
        dims = dim
    result = {}
    for d in dims:
        dropped = array.isel({d: 0})
        closeness = (dropped / array).std()
        result[d] = closeness
    copy_kw = xarray_copy_kw(array, array_to_dataset=True)
    return xr.Dataset(result, **copy_kw)

@pcAccessor.register('drop_unused_dims', totype='dataset')
def xarray_drop_unused_dims(dataset, only=None):
    '''dataset.drop_dims(dims which do not appear in any of the data_vars).
    only: None, str, or list of str
        if provided, only consider dropping dims in this list.
    '''
    used_dims = set()
    for v in dataset.data_vars:
        used_dims.update(dataset[v].dims)
    unused_dims = set(dataset.dims) - used_dims
    if only is not None:
        if isinstance(only, str): only = [only]
        unused_dims &= set(only)
    return dataset.drop_dims(unused_dims)

@pcAccessor.register('drop_vars', totype='dataset')
def xarray_drop_vars(dataset, names, *, errors='ignore', drop_unused_dims=True):
    '''dataset.drop_vars(names, errors=errors), then drop any unused dims.
    errors: 'ignore' or 'raise'
        what to do if any name not found in dataset.
        (passed directly to dataset.drop_vars)
    drop_unused_dims: bool
        whether to also xarray_drop_unused_dims for dims from dropped vars.
    '''
    if isinstance(names, str): names = [names]
    result = dataset.drop_vars(names, errors=errors)
    if drop_unused_dims:
        dropped_var_dims = set()
        for name in names:
            dropped_var_dims.update(dataset[name].dims)
        result = xarray_drop_unused_dims(result, only=dropped_var_dims)
    return result

@pcAccessor.register('popped', totype='dataset')
def xarray_popped(ds, var):
    '''returns (ds[var], copy of ds without var)
    the copy of ds without var also drops any now-unused dims.
    '''
    return (ds[var], xarray_drop_vars(ds, var, drop_unused_dims=True))


### --------------------- Broadcasting --------------------- ###

@pcAccessor.register('broadcastable', totype='array')
def xarray_broadcastable_array(array, dims):
    '''return broadcastable version of array, standardizing dims to the list provided.
    missing dims will be expanded to size 1. result dims will be put in this order.

    dims: list of str
        result will have all these dims, in this order, with size 1 if not present in array.
        if any array.dims not present in dims, raise DimensionKeyError.
    '''
    extra_dims = set(array.dims) - set(dims)  # dims in array
    if extra_dims:
        errmsg = (f'array not broadcastable to input dims={dims}, '
                  f'due to {extra_dims} in array.dims but not input dims.')
        raise DimensionKeyError(errmsg)
    missing_dims = tuple(set(dims) - set(array.dims))
    if missing_dims:
        array = array.expand_dims(missing_dims)
    return array.transpose(*dims)

@pcAccessor.register('broadcastable', totype='dataset')
def xarray_broadcastable_from_dataset(dataset, var=None, *, dims=None):
    '''return dict of broadcastable versions of data_var(s) from dataset, standardizing data vars' dims.
    missing dims will be expanded to size 1. result's dims will be put in order.

    var: None, str, or list of str.
        str --> return a broadcastable version of this data_var. Result is an xarray.DataArray.
        list of str --> return dict of {v: broadcastable version of v} across v in var.
        None --> use var = list(dataset.keys())
    dims: None or list of str
        result will have all these dims, in this order, with size 1 if not present in array.
        if any array.dims not present in dims, raise DimensionKeyError.
        None --> use dataset.dims.
    '''
    if dims is None:
        dims = dataset.dims
    if isinstance(var, str):
        return xarray_broadcastable_array(dataset[var], dims)
    # else, return dict of {v: broadcastable version of v} across v in var.
    result = {}
    if var is None:
        var = list(dataset.keys())
    for v in var:
        result[v] = xarray_broadcastable_array(dataset[v], dims)
    return result

@pcAccessor.register('from_broadcastable')
def xarray_from_broadcastable(array, broadcastable, *, dims=None, squeeze=True):
    '''return xarray from broadcastable values, using dims/coords/attrs from input.

    array: xarray.DataArray or xarray.Dataset
        read relevant dims, coords, and attrs from this array; copy to result.
    broadcastable: array (possibly numpy array) or dict of arrays
        result's data comes from this array(s).
        single array --> result.data = array.
        dict of arrays --> result.data = array[v] for v in array.  # [TODO] not yet implemented.
    dims: None or list of str
        list of dim names for broadcastable's dims. len(dims) == broadcastable.ndim.
        None --> use array.dims.
    squeeze: bool
        whether to squeeze away dims with size 1 in broadcastable.
        True --> result.dims will only include dims with size > 1 in broadcastable.
    '''
    if dims is None:
        dims = array.dims
    if isinstance(broadcastable, dict):
        raise NotImplementedError('xarray_from_broadcastable not yet implemented for dict inputs.')
    # else, broadcastable is a single array.
    shape = broadcastable.shape
    if len(dims) != len(shape):
        errmsg = f'length of broadcastable shape ({shape}) != length of input dims ({dims}).'
        raise DimensionalityError(errmsg)
    relevant_dims = [d for d, s in zip(dims, shape) if s > 1]
    kw = xarray_copy_kw(array, dims=relevant_dims, name=False)
    if squeeze:
        broadcastable = np.squeeze(broadcastable)
    else:
        kw['dims'] = dims  # using all dims not just relevant dims.
    return xr.DataArray(broadcastable, **kw)



### --------------------- Coarsen / windowing --------------------- ###

_coarsen_doc = xr.DataArray.coarsen.__doc__
_construct_doc = DataArrayCoarsen.construct.__doc__
if 'Examples\n' in _coarsen_doc:  # gives docstring with Examples removed
    _coarsen_doc = _coarsen_doc[:_coarsen_doc.index('Examples\n')].rstrip()
if 'Examples\n' in _construct_doc:  # gives docstring with Examples removed
    _construct_doc = _construct_doc[:_construct_doc.index('Examples\n')].rstrip()

@pcAccessor.register('coarsened')
@format_docstring(coarsen_doc=_coarsen_doc, construct_doc=_construct_doc)
def xarray_coarsened(array, dim, window_len, dim_coarse='window', dim_fine=None, *,
                     assign_coarse_coords=False,
                     # kw for coarsen:
                     boundary=UNSET, side=UNSET,
                     # kw for construct:
                     stride=UNSET, fill_value=UNSET, keep_attrs=UNSET,
                     ):
    '''construct a coarsened version of array, where dim is coarsened by window_len,
    and becomes two dims: dim_coarse and dim_fine.
    Original dim coords will be associated with dim_coarse and dim_fine in the new array.

    dim: str
        dimension to coarsen.
        if a non-dimension coordinate, will attempt to promote it to a dimension (e.g. via swap_dims).
    window_len: int
        length of the window to coarsen over.
    dim_coarse: str, default 'window'
        name of coarse dimension; the i'th value here corresponds to the i'th window.
    dim_fine: None or str
        name of fine dimension; the j'th value here corresponds to the j'th element within a window.
        if None, use '_'+dim, e.g. dim='t' --> dim_fine='_t'.
    assign_coarse_coords: bool or coords
        coords to assign along the dim_coarse dimension.
        True --> use np.arange.
        False --> don't assign coords.
    boundary, side: UNSET or value
        if provided (not UNSET), pass this value to coarsen().
        boundary should be 'exact', 'trim', or 'pad'.
        side should be 'left' or 'right'.
    stride, fill_value, keep_attrs: UNSET or value
        if provided (not UNSET), pass this value to construct().
    
    docs for coarsen and construct are copied below, for convenience:

    xarray.DataArray.coarsen
    ------------------------
    {coarsen_doc}


    xr.core.rolling.DataArrayRolling.construct
    ------------------------------------------
    {construct_doc}
    '''
    # bookkeeping
    kw_coarsen = dict(boundary=boundary, side=side)
    kw_construct = dict(stride=stride, fill_value=fill_value, keep_attrs=keep_attrs)
    for kw in kw_coarsen, kw_construct:
        for key, val in tuple(kw.items()):
            if val is UNSET:
                del kw[key]
    if dim_fine is None:
        dim_fine = f'_{dim}'
    # promote non-coordinate dim if necessary, else returns array unchanged.
    arr = xarray_promote_dim(array, dim)
    # coarsen & reconstruct
    coarse = arr.coarsen({dim: window_len}, **kw_coarsen)
    result = coarse.construct({dim: (dim_coarse, dim_fine)}, **kw_construct)
    # bookkeeping
    if assign_coarse_coords is not False:
        if assign_coarse_coords is True:
            assign_coarse_coords = np.arange(len(result[dim_coarse]))
        result = result.assign_coords({dim_coarse: assign_coarse_coords})
    return result

