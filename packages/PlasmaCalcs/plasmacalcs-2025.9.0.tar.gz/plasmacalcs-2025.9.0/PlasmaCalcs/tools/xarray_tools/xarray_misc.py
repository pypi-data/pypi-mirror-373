"""
File Purpose: misc. tools related to xarray
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor
from ..arrays import np_dtype_object_to_str
from ...errors import InputError, InputConflictError, DimensionKeyError


### --------------------- Copying --------------------- ###

@pcAccessor.register('copy_kw')
def xarray_copy_kw(array, dims=None, *, name=None, array_to_dataset=False):
    '''return dict of info suitable for creating a similar array or dataset.
    result includes dims, coords, and attrs (unchanged, copied).

    dims: None, str, or iterable of str
        if provided, only include these dims (and related coords) in the result.
        Useful if only interested in some of the dims,
            e.g. if array has x,y,z,t dims but only want to mimic dims and coords from x,t.
    name: None, bool, or str
        whether to also include name in result
        None --> True if array has name, else False
        True --> name = array.name.
        str --> name = name.
    array_to_dataset: bool
        if True, result will be suitable for creating a Dataset based on the input DataArray.
        (Equivalent to using dims=[], name=False, and deleting 'dims' key from result.)
    '''
    # handle array_to_dataset mode:
    if array_to_dataset:
        result = xarray_copy_kw(array, dims=[], name=False, array_to_dataset=False)
        del result['dims']
        return result
    # 'usual' usage
    result = dict()
    if isinstance(dims, str): dims = [dims]
    if dims is None: dims = array.dims
    elif any(d not in array.dims for d in dims):
        errmsg = (f'cannot copy_kw for dims={dims!r} because some dims not in array.dims={array.dims}.')
        raise DimensionKeyError(errmsg)
    result['dims'] = dims
    coords = dict()
    for cname, cval in array.coords.items():
        if len(cval.dims) == 0:  # scalar coord; always keep!
            coords[cname] = cval
        elif len(cval.dims) == 1 and cval.dims[0] in dims:  # 1D coord, and relevant
            coords[cname] = cval
        elif all(d in dims for d in cval.dims):  # 2D+ coord, and all relevant dims exist
            coords[cname] = (tuple(cval.dims), cval.data)
    result['coords'] = coords
    attrs = array.attrs.copy()
    result['attrs'] = attrs
    if name is None:
        name = hasattr(array, 'name')
    if name == True:
        name = array.name
    if name != False:
        result['name'] = name
    return result

@pcAccessor.register('with_data', totype='array')
def xarray_with_data(xarray, data, dims=None, *, name=None):
    '''return data as an xr.DataArray with dims, coords, name, and attrs copied from xarray.
    Similar to DataArray.copy(data=data), but here allows a bit more control.

    dims: None, str, or iterable of str
        if provided, only include these dims (and related coords) in the result.
        Useful if only interested in some of the dims,
            e.g. if array has x,y,z,t dims but only want to mimic dims and coords from x,t.
    name: None, bool, or str
        whether to also include name in result
        None --> True if array has name, else False
        True --> name = array.name.
        str --> name = name.
    '''
    if not isinstance(xarray, xr.DataArray):
        raise InputError(f'xarray_with_data expects args[0] to be a DataArray, not {type(xarray)}.')
    kw = xarray_copy_kw(xarray, dims=dims, name=name)
    return xr.DataArray(data, **kw)


### --------------------- Converting Dataset to Array --------------------- ###

@pcAccessor.register('as_array')
def xarray_as_array(array):
    '''return array if DataArray, else array[var] if array is Dataset with one var.
    if array is Dataset with multiple vars, crash with InputError.
    '''
    if isinstance(array, xr.DataArray):
        return array
    elif isinstance(array, xr.Dataset):
        if len(array) == 1:
            return array[list(array)[0]]
        else:
            errmsg = ('as_array(Dataset) only possible if Dataset has exactly 1 data_var, '
                     f'but got Dataset with {len(array)} vars: {list(array.data_vars)}.')
            raise InputError(errmsg)
    else:
        raise InputError(f'cannot convert object of type {type(array)} to DataArray.')


### --------------------- Vars from dataset --------------------- ###

@pcAccessor.register('vars_lookup', totype='dataset')
def xarray_vars_lookup(ds, lookup={}, **lookup_as_kw):
    '''return dict of {key from lookup: ds[lookup[key]]}
    result vals will be None for keys not found in ds.

    lookup: dict of {key: None, varname, or list of varnames}
        look for these varnames in ds. if list, use first varname found.
        if None, use key as varname.
    '''
    if lookup and lookup_as_kw:
        raise InputConflictError('provide lookup or lookup_as_kw, not both!')
    if lookup_as_kw:
        lookup = lookup_as_kw
    result = {}
    for key, find in lookup.items():
        result[key] = None
        if find is None:
            find = key
        if isinstance(find, str):
            find = [find]
        for varname in find:
            if varname in ds:
                result[key] = ds[varname]
                break
    return result

@pcAccessor.register('vars_lookup_with_defaults', totype='dataset')
def xarray_vars_lookup_with_defaults(ds, provided, lookup={}, defaults={}):
    '''return dict of {key from lookup: value for that key}.
    
    provided: dict of {key: None, str, or other value}
        provided values or lookup instructions for each key.
        None --> use instructions from lookup if key in lookup,
                 else value from defaults if key in defaults.
        str --> varname; result uses ds[varname]. (crash if not possible.)
        callable --> f of one arg; result uses f(ds).
        other value --> result uses this value directly.
    lookup: dict of {key: None, str, or list of str}
        'default' lookup instructions. Used when provided[key] is None.
    defaults: dict of {key: value or callable}
        default values for each key.
        Used when provided[key] is None and ds[lookup[key]] not found.
        callable --> called with ds as arg to get value.

    Examples:
        xarray_vars_lookup_with_defaults(ds, {}, {'n': None}, {'n': 100})
        # {'n': ds['n']} if ds['n'] exists, else {'n': 100}
        
        xarray_vars_lookup_with_defaults(ds, {}, {'n': 'var1'}, {'n': lambda ds: ds.size})
        # {'n': ds['var1']} if ds['var1'] exists, else {'n': ds.size}

        xarray_vars_lookup_with_defaults(ds, {'n': 'var1'}, {'n': 'var2'}, {'n': 7})
        # {'n': ds['var1']} if ds['var1'] exists, else crash.
        # (lookup & defaults are fully ignored, if non-None value in provided.)
    '''
    result = {}
    all_keys = set(provided) | set(lookup) | set(defaults)
    for key in all_keys:
        prov = provided.get(key, None)
        if prov is None:
            find = lookup.get(key, None)
            if find is None:
                find = key
            if isinstance(find, str):
                find = [find]
            for varname in find:
                if varname in ds:
                    result[key] = ds[varname]
                    break
            else:
                if key in defaults:
                    val = defaults[key]
                    if callable(val):
                        val = val(ds)
                    result[key] = val
                else:
                    errmsg = (f'no value for key={key!r}; not provided directly, '
                              f'varnames {find} not in ds, and no default provided.')
                    raise InputError(errmsg)
        elif isinstance(prov, str):
            if prov in ds:
                result[key] = ds[prov]
            else:
                errmsg = f'provided varname={prov!r} (for key={key!r}) not found in ds.'
                raise InputError(errmsg)
        elif callable(prov):
            result[key] = prov(ds)
        else:
            result[key] = prov
    return result


### --------------------- Math Checks --------------------- ###

@pcAccessor.register('where_finite')
def xarray_where_finite(array):
    '''returns array, masked with NaNs anywhere that the values are not finite.'''
    return array.where(np.isfinite)


### --------------------- Type Casting --------------------- ###

@pcAccessor.register('astypes', totype='dataset')
def xarray_astypes(ds, var_to_dtype):
    '''return copy of ds with var.astype(dtype) for each var, dtype in var_to_dtype.items()'''
    to_assign = {dvar: ds[dvar].astype(dtype) for dvar, dtype in var_to_dtype.items()}
    return ds.assign(**to_assign)

@pcAccessor.register('convert_types')
def xarray_convert_types(array, oldtype_to_newtype):
    '''return copy of array or dataset, using var.astype(newtype) for any var with oldtype,
    for oldtype, newtype in oldtype_to_newtype.items().
    '''
    if isinstance(array, xr.Dataset):
        ds = array
        to_convert = dict()
        for var, val in ds.items():
            for oldtype, newtype in oldtype_to_newtype.items():
                if val.dtype == oldtype:
                    to_convert[var] = newtype
                    break
        return xarray_astypes(ds, to_convert)
    else:
        for oldtype, newtype in oldtype_to_newtype.items():
            if array.dtype == oldtype:
                return array.astype(newtype)
        else:  # no match found during loop
            return array

@pcAccessor.register('dtype_object_to_str', totype='array')
def xarray_dtype_object_to_str(array):
    '''convert array with dtype=object to dtype=str, by doing str(x) for every x in array.'''
    return array.copy(data=np_dtype_object_to_str(array.values))


### --------------------- Converting coords to strings --------------------- ###

@pcAccessor.register('object_coords_to_str')
def xarray_object_coords_to_str(array, *, maxlen=None, ndim_min=1):
    '''return copy of array with coords (of dtype=object) converted to string.
    maxlen: None or int>=5
        if int, truncate longer strings to this length-3, and add '...' to end.
    ndim_min: int
        minimum number of dimensions for a coord to be converted.
        e.g. ndim_min=1 --> coords with ndim=0 will not be altered
    '''
    to_assign = {}
    for cname, cc in array.coords.items():
        if cc.dtype == object and cc.ndim >= ndim_min:
            if cc.ndim >= 2:
                raise NotImplementedError('object_coords_to_str does not yet support ndim>=2.')
            cvals = [str(v) for v in cc.values]
            if maxlen is not None:
                cvals = [v[:maxlen-3] + '...' if len(v) > maxlen else v for v in cvals]
            to_assign[cname] = cc.copy(data=cvals)
    return array.assign_coords(to_assign)
