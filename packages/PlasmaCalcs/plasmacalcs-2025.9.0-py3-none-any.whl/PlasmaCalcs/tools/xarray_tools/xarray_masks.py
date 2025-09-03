"""
File Purpose: tools related to masking xarray objects

for simply filling masked regions with nan, can use xarray_obj.where(...).
But, that can cause a lot of memory full of nan which is not desireable.
Methods in here help with stacking/unstacking mask dimensions,
    so it can be possible to keep only the non-nan points.

Datasets are able to store the full mask info as a data_var,
    so it is possible to ds.pc.mask() or ds.pc.unmask() if '_mask' already in ds.
DataArrays can't store extra dimensions,
    so mask needs to be passed, e.g. arr.pc.mask(mask), arr.pc.unmask(mask)
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor
from .xarray_coords import xarray_dims_coords
from .xarray_dimensions import (
    xarray_ensure_dims, _paramdocs_ensure_dims,
    xarray_drop_vars,
)
from .xarray_misc import xarray_as_array, xarray_convert_types
from .xarray_indexing import xarray_where
from ..docs_tools import format_docstring
from ...errors import (
    InputError, InputConflictError, InputMissingError,
    DimensionKeyError,
)


### --------------------- Masking --------------------- ###

@pcAccessor.register('mask')
@format_docstring(**_paramdocs_ensure_dims)
def xarray_mask(array, mask=None, stackdim='_mask_stack', *, stack=True, create_index=True,
                skip_arrays_without_mask_dims=True, store_mask=None, promote_dims_if_needed=True):
    '''mask an xarray object; result has non-nan values only where mask=False.
    By default, also stack along mask dimensions, and drop points where mask=True.

    array: xarray.DataArray or xarray.Dataset
        object to be masked.
    mask: None or xarray.DataArray
        mask to apply to array.
        None --> use array['_mask'] (and array must be a Dataset)
    stackdim: str, default '_mask_stack'
        result.dims[stackdim] has the mask dimensions stacked.
    stack: bool
        whether to stack result.
        if False, don't stack, just use array.where(~mask). (~ means negation)
    create_index: bool
        whether to create a MultiIndex for stackdim in the result, if stack.
    skip_arrays_without_mask_dims: bool
        whether to apply mask to arrays without mask dims.
        if True, only arrays originally containing at least one mask dim will be masked.
        if False, all results will have mask dims (or stackdim) via array.where(~mask).
    store_mask: None or bool
        whether to store full mask as a data_var in result.
        None --> True if array is a Dataset, else False
        True --> result Dataset will have full mask in data_var '_mask'.
                If stack, mask dims replaced by '_mask_{{d}}' for d in mask.dims,
                    to avoid conflict with original mask dims' coords in result.
                If input DataArray, first convert to Dataset with data_var array.name.
        False --> do not store mask in result.
    promote_dims_if_needed: {promote_dims_if_needed}

    crash with DimensionKeyError if any relevant dim (stackdim, '_mask', '_mask_{{d}}') already exists.
    '''
    if mask is None:
        if xarray_has_mask(array):
            mask, array = xarray_popped_mask(array)
        else:
            raise InputMissingError('mask() requires mask input, or array=<Dataset with "_mask" data_var>.')
    if store_mask is None:
        store_mask = isinstance(array, xr.Dataset)
    if store_mask and isinstance(array, xr.DataArray) and array.name is None:
        raise InputConflictError('store_mask=True when array is a DataArray with name=None.')
    kw_where = dict(skip_if_no_matching_dims=skip_arrays_without_mask_dims)
    if stack:
        array = xarray_ensure_dims(array, mask.dims, promote_dims_if_needed=promote_dims_if_needed)
        stacked = array.stack({stackdim: mask.dims}, create_index=create_index)
        keeping = ~mask.stack({stackdim: mask.dims}, create_index=create_index)  # ~ means negation
        result = xarray_where(stacked, keeping, drop=True, **kw_where)
    else:
        result = xarray_where(array, ~mask, **kw_where)
    if store_mask:
        result = xarray_store_mask(result, mask)
    return result


### --------------------- Helper methods --------------------- ###

@pcAccessor.register('has_mask')
def xarray_has_mask(array):
    '''returns whether an xarray object has a mask. I.e., has '_mask' data_var.
    (Always False for DataArrays).
    '''
    return isinstance(array, xr.Dataset) and '_mask' in array

@pcAccessor.register('store_mask')
def xarray_store_mask(array, mask):
    '''return Dataset like input but containing data_var '_mask'.
    crash with DimensionKeyError if '_mask' already exists in input.

    if mask.dims not already in array.dims, rename mask dims d to '_mask_{d}'.
        (this will occur when storing mask in a stacked result,
        because the stacked result will have stackdim instead of mask dims.)

    array: xarray.DataArray or xarray.Dataset
        if DataArray, will be converted to Dataset with data_var array.name.
    '''
    if isinstance(array, xr.DataArray):
        if array.name is None:
            raise InputError('cannot store mask in DataArray with name=None.')
        ds = array.to_dataset()
    else:
        ds = array  # input was a Dataset already
    if '_mask' in ds:
        raise DimensionKeyError('dataset already has "_mask"; cannot store mask.')
    if any(d not in array.dims for d in mask.dims):
        mask = mask.rename({d: f'_mask_{d}' for d in mask.dims})
    return ds.assign(_mask=mask)

@pcAccessor.register('stored_mask', totype='dataset')
def xarray_stored_mask(ds):
    '''returns original mask, based on info stored in ds.
    original mask must be stored in data_var '_mask'.
    if ds['_mask'] dims look like '_mask_{d}', rename them to {d}.
    '''
    if '_mask' not in ds:
        if isinstance(ds, xr.DataArray):
            raise InputError("cannot retrieve stored_mask; ds doesn't have '_mask' data_var.")
        else:
            raise InputError(f'cannot retrieve stored_mask from non-Dataset object of type {type(ds)}')
    mask = ds['_mask']
    to_rename = {d: d[len('_mask_'):] for d in mask.dims if d.startswith('_mask_')}
    if to_rename:
        mask = mask.rename(to_rename)
    return mask

@pcAccessor.register('popped_mask', totype='dataset')
def xarray_popped_mask(ds):
    '''returns (stored mask, copy of ds without '_mask')
    See also: xarray_stored_mask, xarray_popped.
    '''
    mask = xarray_stored_mask(ds)
    return mask, xarray_drop_vars(ds, '_mask')


### --------------------- Unmasking --------------------- ###

_paramdocs_unmask = {
    'stackdim': '''str, default '_mask_stack'
        dimension along which the mask stacking occurred.''',
    'store_mask': '''None or bool
        whether to store full mask as a data_var in result.
        None --> True if result would otherwise be a Dataset, else False
        True --> result will be a Dataset with full mask in data_var '_mask'.
        False --> do not store mask in result.''',
    'as_array': '''None or bool
        whether to ensure result is a DataArray.
        None --> True if result would be a Dataset with a single data_var, else False.
        True --> result will be a DataArray; crash if not possible
                    (e.g. crash if output would have multiple vars, or if store_mask=True).
        False --> result will be a Dataset, unless input was a DataArray and store_mask=False.''',
    'reindex': '''bool
        whether to result.reindex_like(mask). Highly recommended, but not required...''',
    '_upcast_bool': '''bool
        whether to upcast dtype=bool array or data_vars to int8 before unstacking.
        when False, unstacking produces a dtype=object array due to the nans for missing values.
        (when True, unstacking makes dtype=float32, using 0 for False, 1 for True, nan for nan.)''',
}


@pcAccessor.register('unmask')
@format_docstring(**_paramdocs_unmask)
def xarray_unmask(array, mask=None, stackdim='_mask_stack', *, store_mask=False,
                  as_array=None, reindex=True, _upcast_bool=True):
    '''unmask (i.e., unstack) a masked (and stacked) xarray object.
    array.pc.unmask(mask) is equivalent to mask.pc.demask(array).
    See also: xarray_unmask_var, to get a single unmasked var from a Dataset.

    array: xarray.DataArray or xarray.Dataset
        object to unmask.
    mask: None or xarray.DataArray
        the (unstacked) mask. If None, use mask stored in array['_mask'] (and array must be a Dataset).
    stackdim: {stackdim}
    store_mask: {store_mask}
    as_array: {as_array}
    reindex: {reindex}
    _upcast_bool: {_upcast_bool}

    In the simplest case (mask not None; array=non-boolean DataArray with MultiIndex in stackdim),
        this method behaves just like array.unstack(stackdim).reindex_like(mask).
    All the other stuff here helps to handle more complicated cases,
        e.g. Dataset containing mask, possibly without MultiIndex along stackdim.
    '''
    if isinstance(mask, str):
        raise InputError('did not expect mask to be str... maybe you input args in the wrong order?')
    if not isinstance(stackdim, str):
        raise InputError(f'expected str stackdim; got object of type {type(stackdim)}.')
    if stackdim not in array.dims:
        errmsg = f'stackdim={stackdim!r} not found in array.dims={array.dims}.'
        if stackdim in mask.dims:
            errmsg = errmsg + ('\nIf you wanted syntax like mask.pc.unmask(masked_array), '
                               'consider mask.pc.demask(masked_array) instead.')
        raise DimensionKeyError(errmsg)
    # bookkeeping for mask input
    array_has_mask = xarray_has_mask(array)
    if (not array_has_mask) and (mask is None):
        raise InputMissingError("unmask() expects mask kwarg or input array=<Dataset with '_mask' data_var>.")
    if array_has_mask:
        arrmask, array = xarray_popped_mask(array)
        if mask is None:
            mask = arrmask
        elif not np.array_equal(arrmask, mask):
            raise InputConflictError("unmask(array, mask); array['_mask'] conflicts with input mask.")
    # infer stackdim coords from mask if necessary (i.e. if stackdim doesn't have coord already)
    if stackdim not in array.coords:  # need to define MultiIndex coord for stackdim before we can unstack.
        stackdim_coords = xarray_dims_coords(array, include_dims_as_coords=True)[stackdim]
        for mask_d in mask.dims:
            if mask_d not in stackdim_coords:
                errmsg = (f'masked array has no {mask_d!r} coord along stackdim(={stackdim!r})).\n'
                          f'The {mask_d!r} coord is required because it appears in mask.dims={mask.dims}.')
                if array_has_mask: raise DimensionKeyError(errmsg)
                else: raise InputConflictError(errmsg)
        array = array.set_xindex(mask.dims)  # sets stackdim coord
        # (knows about stackdim because mask.dims coords in array are coords along stackdim.)
    if _upcast_bool:
        array = xarray_convert_types(array, {bool: np.int8})
    # >> actually unstack & reindex <<
    result = array.unstack(stackdim)
    if reindex:
        result = result.reindex_like(mask)
    # postprocessing
    if as_array is None and store_mask is None:
        as_array = isinstance(result, xr.DataArray) or len(result.data_vars)==1
        store_mask = (not as_array) and isinstance(result, xr.Dataset)
    if store_mask is None:
        store_mask = isinstance(array, xr.Dataset)
    if store_mask:
        result = xarray_store_mask(result, mask)
    # convert to DataArray if desired & possible
    if as_array is None:
        as_array = isinstance(result, xr.DataArray) or len(result.data_vars)==1
    if as_array:
        result = xarray_as_array(result)
    return result

@pcAccessor.register('demask', totype='array')
@format_docstring(**_paramdocs_unmask)
def xarray_demask_from_mask(mask, array, stackdim='_mask_stack', *, store_mask=False,
                            as_array=None, reindex=True, _upcast_bool=True):
    '''unmask (i.e., unstack) a masked (and stacked) xarray object, using this mask.
    Equivalent to xarray_unmask(array, mask=mask, ...)

    mask: xarray.DataArray
        the (unstacked) mask.
    array: xarray.DataArray or xarray.Dataset
        object to unmask.
    stackdim: {stackdim}
    store_mask: {store_mask}
    as_array: {as_array}
    reindex: {reindex}
    _upcast_bool: {_upcast_bool}
    '''
    return xarray_unmask(array, mask=mask, stackdim=stackdim, store_mask=store_mask,
                         as_array=as_array, reindex=reindex, _upcast_bool=_upcast_bool)

@pcAccessor.register('demask', totype='dataset')
@format_docstring(**_paramdocs_unmask)
def xarray_demask_from_ds(ds, array, stackdim='_mask_stack', *, store_mask=False,
                          as_array=None, reindex=True, _upcast_bool=True):
    '''unmask (i.e., unstack) a masked (and stacked) xarray object, using mask=xarray_stored_mask(ds).
    Equivalent to xarray_unmask(array, mask=xarray_stored_mask(ds), ...)
    Also equivalent to xarray_demask_from_mask(xarray_stored_mask(ds), array, ...)
    
    ds: xarray.Dataset
        will use xarray_stored_mask(ds) as the mask.
    array: xarray.DataArray or xarray.Dataset
        object to unmask.
    stackdim: {stackdim}
    store_mask: {store_mask}
    as_array: {as_array}
    reindex: {reindex}
    _upcast_bool: {_upcast_bool}
    '''
    return xarray_demask_from_mask(xarray_stored_mask(ds), array, stackdim=stackdim, store_mask=store_mask,
                                    as_array=as_array, reindex=reindex, _upcast_bool=_upcast_bool)

@pcAccessor.register('unmask_var', totype='dataset')
@format_docstring(**_paramdocs_unmask)
def xarray_unmask_var(ds, var, mask=None, stackdim='_mask_stack', *, reindex=True, _upcast_bool=True):
    '''unmask a single variable from a Dataset. returns a DataArray of the unmasked var.
    Equivalent: xarray_unmask(ds[['_mask', var]], ...) if '_mask' in ds.data_vars
        else xarray_unmask(ds[[var]], mask=mask, ...)

    ds: xarray.Dataset
        will unmask ds[var].
    var: str
        variable whose unmasked value should be returned
    mask: None or xarray.DataArray
        mask to use. If None, use mask stored in ds['_mask'].
    stackdim: {stackdim}
    reindex: {reindex}
    _upcast_bool: {_upcast_bool}
    '''
    if var not in ds:
        raise InputConflictError(f'input dataset ds does not have variable var={var!r}.')
    to_unmask = ds[[var, '_mask']] if '_mask' in ds.data_vars else ds[[var]]
    kw_pass = dict(mask=mask, stackdim=stackdim, reindex=reindex, _upcast_bool=_upcast_bool)
    return xarray_unmask(to_unmask, **kw_pass, store_mask=False, as_array=True)

@pcAccessor.register('unmask_vars', totype='dataset')
@format_docstring(**_paramdocs_unmask)
def xarray_unmask_vars(ds, vars, mask=None, stackdim='_mask_stack', *, store_mask=False,
                       reindex=True, _upcast_bool=True):
    '''unmask multiple variables from a Dataset. returns a Dataset with unmasked vars.

    ds: xarray.Dataset
        will unmask ds[vars].
    vars: str or list of str
        variables whose unmasked values should be returned.
        if single str, treated as [vars].
    mask: None or xarray.DataArray
        mask to use. If None, use mask stored in ds['_mask'].
    store_mask: {store_mask}
    stackdim: {stackdim}
    reindex: {reindex}
    _upcast_bool: {_upcast_bool}
    '''
    if isinstance(vars, str):
        vars = [vars]
    if not all(v in ds for v in vars):
        raise InputConflictError(f'input dataset ds does not have all variables in vars={vars}.')
    to_unmask = ds[vars + (['_mask'] if '_mask' in ds.data_vars else [])]
    kw_pass = dict(mask=mask, stackdim=stackdim, reindex=reindex, _upcast_bool=_upcast_bool)
    return xarray_unmask(to_unmask, **kw_pass, store_mask=store_mask, as_array=False)
