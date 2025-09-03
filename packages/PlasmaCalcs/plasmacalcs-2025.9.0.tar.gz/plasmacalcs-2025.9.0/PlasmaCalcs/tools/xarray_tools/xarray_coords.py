"""
File Purpose: tools related to xarray coords
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor
from .xarray_dimensions import xarray_promote_dim, xarray_ensure_dims
from .xarray_misc import xarray_dtype_object_to_str
from ..arrays import ndindex_array
from ..math import float_rounding as math_float_rounding
from ...errors import (
    DimensionalityError, DimensionValueError, DimensionKeyError,
    InputError, InputConflictError, InputMissingError,
)


# note: see xarray_indexing.py for xarray_cmin, xarray_cmax,
#   xarray_min_coord_where, and xarray_max_coord_where.

### --------------------- Coords --------------------- ###

@pcAccessor.register('nondim_coords')
def xarray_nondim_coords(array, *, scalars_only=False, item=False, _sort=True):
    '''returns dict of {coord name: coord.values} for all non-dimension coords (not in array.dims).
    scalars_only: bool
        whether to only include coords with ndim==0.
    item: bool
        whether to use coord.item() for scalars.

    _sort: bool
        whether to sort, if any '{coord}_index' coords appear consecutively,
        (when doing the default array.coords.items() order), sort those alphabetically.
        If their non-index counterparts also appear consecutively, sort those too.
        E.g. order: 'C', 'A', 'B', 'other_index', 'D', 'C_index', 'A_index', 'D_index', 'B_index', 'E',
           becomes: 'A', 'B', 'C', 'other_index', 'D', 'A_index', 'B_index', 'C_index', 'D_index', 'E'.
    '''
    result = {cname: coord.values for cname, coord in array.coords.items() if cname not in array.dims}
    if scalars_only:
        result = {cname: val for cname, val in result.items() if np.ndim(val) == 0}
    if item:
        result = {cname: val.item() if val.ndim==0 else val for cname, val in result.items()}
    if not _sort:
        return result
    else:  # _sort=True
        # sorting (stylistic choice only. Might affect plot title order.)
        # [TODO] make an xarray_sort_coords function to produce a standard order, instead of writing it here.
        order = list(result.keys())
        new_order = []
        grouped_indexes = []
        iter_order = iter(order)
        for cname in iter_order:
            group = []
            cname2 = None
            if cname.endswith('_index'):
                group.append(cname)
                for cname2 in iter_order:
                    if cname2.endswith('_index'):
                        group.append(cname2)
                    else:
                        break
            if len(group) > 1:
                group = sorted(group)
                grouped_indexes.append(group)
                new_order.extend(group)
                new_order.append(cname2)
            elif cname2 is not None:  # found an index coord, but only 1 consecutively.
                new_order.append(cname)
                new_order.append(cname2)
            else:  # not an index coord.
                new_order.append(cname)
            order = new_order
        # (look for non-index counterparts to sort)
        if len(grouped_indexes) > 0:
            nonindex_groups = [[cname[:-len('_index')] for cname in group] for group in grouped_indexes]
            new_order = []
            iter_order = iter(order)
            for cname in iter_order:
                group = []
                for ng in nonindex_groups:
                    if cname in ng:
                        group.append(cname)
                        break
                else:  # this cname doesn't have an index group.
                    new_order.append(cname)
                    continue
                for cname2 in iter_order:
                    if cname2 in ng:
                        group.append(cname2)
                    else:
                        new_order.extend(sorted(group))
                        new_order.append(cname2)
                        break
            order = new_order
        return {cname: result[cname] for cname in order}

@pcAccessor.register('dims_coords')
def xarray_dims_coords(array, *, include_dims_as_coords=True):
    '''returns dict of {dim name: [coord name for all coords with this dim]}.
    result[()] will be list of all scalar coords (ndim=0 so no associated dims).
    coords associated with multiple dims will appear in multiple places in the result.

    include_dims_as_coords: bool
        whether to include dims as coord names in the result.
        Dims with no same-named coord will appear in appropriate place in result.
    '''
    result = dict()
    unused_dims = set(array.dims)
    for cname, coord in array.coords.items():
        unused_dims -= set([cname])
        if len(coord.dims) == 0:
            result.setdefault((), []).append(cname)
        for dim in coord.dims:
            result.setdefault(dim, []).append(cname)
    if include_dims_as_coords and unused_dims:
        for dim in unused_dims:
            result.setdefault(dim, []).append(dim)
    return result

@pcAccessor.register('assign_self_as_coord', totype='array')
def xarray_assign_self_as_coord(array):
    '''return copy of array with coord named array.name, equal to array values.
    Equivalent: array.assign_coords({array.name: array})
    '''
    if array.name is None:
        raise InputError('assign_self_coord expects non-None array.name')
    return array.assign_coords({array.name: array})

@pcAccessor.register('fill_coords')
def xarray_fill_coords(array, dim=None, *, need=None):
    '''return copy of array with coords filled for indicated dims.
    (if all indicated dims have coords already, return original array, not a copy.)
    E.g. array with dim_1 length 50 but no coords
        --> result is just like array but has dim_1 coords = np.arange(50)

    dim: None, str, or iterable of strs
        dims for which to consider filling coords. None --> array.dims.
    need: None, str, or iterable of str or None
        coords which the result must contain.
        if any of these look like '{coord}_index', 'log_{coord}', or 'str_{coord}',
            create them via xarray_index_coords, xarray_log_coords, or xarray_str_coords.
    '''
    if dim is None: dim = array.dims
    elif isinstance(dim, str): dim = [dim]
    to_assign = {}
    for d in dim:
        if d not in array.coords:
            to_assign[d] = array[d]  # array[d] == np.arange(len(array[d]))
    if to_assign:
        array = array.assign_coords(to_assign)
    if need is not None:
        if isinstance(need, str): need = [need]
        for cname in need:
            if cname is None or cname in array.coords:
                continue
            elif cname.endswith('_index'):
                array = xarray_index_coords(array, coords=cname[:-len('_index')], drop=False)
            elif cname.startswith('log_'):
                array = xarray_log_coords(array, coords=cname[len('log_'):], drop=False)
            elif cname.startswith('str_'):
                array = xarray_str_coords(array, coords=cname[len('str_'):], drop=False)
            else:
                errmsg = (f'cname={cname!r} in need={need} but not in '
                          f'array.dims ({list(array.dims)}) nor array.coords ({list(array.coords)}).\n'
                          '(Also no implied coord to create; cname not like "{coord}_index" or "log_{coord}".')
                raise InputConflictError(errmsg)
    return array

@pcAccessor.register('index_coords')
def xarray_index_coords(array, coords=None, newname='{coord}_index', *,
                        drop=False, promote=False, exist_ok=False, max_ndim=None):
    '''return copy of array with coord_index coords telling np.arange() for each coord.
    0D coords' index will be 0 if provided explicitly in coords input, else ignored.
    1D coords' index will be np.arange, e.g. coord_index[i] == i.
    2D+ coords' index will be reshaped np.ndindex, such that coord_index[i,j] == (i,j).

    coords: None or iterable of strs
        if None, use all coords and dims which don't already have coord_index.
        (e.g. 'fluid' --> make 'fluid_index', unless 'fluid_index' already exists.)
    newname: str
        string for new (index) coord names: newname.format(coord=coord).
        Default: '{coord}_index'. To keep original names, use '{coord}'
    drop: bool
        whether to drop original coords after creating coord_index coords.
        (e.g. 'fluid' --> drop 'fluid' after making 'fluid_index')
    promote: bool
        whether to promote all non-dim new index coords to dimensions.
        if True, xarray_promote_dim for all new index coords.
    exist_ok: bool
        whether it is okay if newname for coord (e.g. 'fluid_index') already exists.
        True --> replace existing coord with new coord_index.
    max_ndim: None or int
        if not None, skip any coords with ndim > max_ndim.
        E.g. max_ndim=1 prevents making indexes for coords with ndim>=2.
    '''
    if coords is None:
        nonscalar_coords = [cname for cname, cval in array.coords.items() if cval.ndim >= 1]
        coords = list(set(nonscalar_coords).union(array.dims))
    elif isinstance(coords, str):
        coords = [coords]
    newnames = {cname: newname.format(coord=cname) for cname in coords}
    if len(set(newnames.values())) != len(newnames):  # crash if any newname apears multiple times:
        raise InputConflictError(f'old to new name map must have unique values but got: {newnames!r}')
    if not exist_ok:
        existing = set(array.coords).intersection(newnames.values())
        if existing:
            raise InputConflictError(f'some new coord names already exist in array.coords: {existing!r}')
    # computing new coords
    to_assign = {}
    for cname in coords:
        cc = array.coords[cname]
        if (max_ndim is not None) and cc.ndim > max_ndim:
            continue
        if cc.ndim == 0:
            index = np.array(0, dtype=np.min_scalar_type(0))
        else:
            index = ndindex_array(cc.shape)
        newval = cc.copy(data=index)
        if drop:
            newval = newval.drop_vars(coords, errors='ignore')  # 'ignore' if newval missing any coords
        to_assign[newnames[cname]] = newval
    # creating result
    if drop:
        array = array.drop_vars(coords, errors='ignore')
    result = array.assign_coords(to_assign)
    if promote:
        result = xarray_ensure_dims(result, list(newnames.values()))
    return result

@pcAccessor.register('promote_index_coords')
def xarray_promote_index_coords(array, coords=None):
    '''promote to dims all '{cname}_index' coords for which '{cname}' is associated with a 1D dim.
    
    coords: None, str, or list of str
        coords (with or without '_index' suffix) to consider promoting to dims.
        None --> all index coords.
        str --> treat as list of 1 element.
    '''
    if coords is None:
        coords = [c for c in array.coords if c.endswith('_index')]
    elif isinstance(coords, str):
        coords = [coords]
    index_names = [c if c.endswith('_index') else f'{c}_index' for c in coords]
    orig_names = [c[:-len('_index')] for c in index_names]
    for oo, ii in zip(orig_names, index_names):
        if ii in array.coords:
            cval = array.coords[ii]
            if cval.ndim == 1:
                array = xarray_promote_dim(array, ii)
    return array

@pcAccessor.register('demote_index_coords')
def xarray_demote_index_coords(array, coords=None):
    '''demote '{cname}_index' dims to coords by promoting '{cname}' coords to dim instead.
    Skips index dims for which associated '{cname}' coord does not exist.

    coords: None, str, or list of str
        coords (with or without '_index' suffix) to consider demoting to dims.
        None --> all index coords.
        str --> treat as list of 1 element.
    '''
    if coords is None:
        coords = [c for c in array.coords if c.endswith('_index')]
    elif isinstance(coords, str):
        coords = [coords]
    index_names = [c if c.endswith('_index') else f'{c}_index' for c in coords]
    orig_names = [c[:-len('_index')] for c in index_names]
    for oo, ii in zip(orig_names, index_names):
        if oo in array.coords:
            cval = array.coords[oo]
            if cval.ndim == 1:
                array = xarray_promote_dim(array, oo)
    return array

@pcAccessor.register('scale_coords')
def xarray_scale_coords(array, scale=None, *, missing_ok=True, **scale_as_kw):
    '''return copy of array with coords multiplied by scale.
    scale: None or dict of {coord: scale}
        dict --> multiply each coord by the corresponding number.
        None --> provide as kwargs (scale_as_kw) instead.
    scale_as_kw: if scale is None, can provide scale dict as kwargs instead.
    missing_ok: bool
        whether it is okay if some coords are missing (if yes, skip missing coords).
    '''
    if scale is None and len(scale_as_kw) == 0:
        raise InputMissingError('must provide either "scale" or "scale_as_kw".')
    if scale is not None and len(scale_as_kw) > 0:
        raise InputConflictError('cannot provide both "scale" and "scale_as_kw".')
    if scale is None:
        scale = scale_as_kw
    assign_coords = {}
    for cname, cscale in scale.items():
        try:
            cvals = array.coords[cname]
        except KeyError:
            if not missing_ok:
                raise DimensionKeyError(f'coord={cname!r} not found in array.coords.') from None
            continue
        assign_coords[cname] = cvals * cscale
    return array.assign_coords(assign_coords)

@pcAccessor.register('shift_coords')
def xarray_shift_coords(array, shift=None, *, missing_ok=True, **shift_as_kw):
    '''return copy of array with coords shifted by shift.
    shift: None or dict of {coord: shift}
        dict --> shift each coord by the corresponding number.
        None --> provide as kwargs (shift_as_kw) instead.
    shift_as_kw: if shift is None, can provide shift dict as kwargs instead.
    missing_ok: bool
        whether it is okay if some coords are missing (if yes, skip missing coords).
    '''
    if shift is None and len(shift_as_kw) == 0:
        raise InputMissingError('must provide either "shift" or "shift_as_kw".')
    if shift is not None and len(shift_as_kw) > 0:
        raise InputConflictError('cannot provide both "shift" and "shift_as_kw".')
    if shift is None:
        shift = shift_as_kw
    assign_coords = {}
    for cname, cshift in shift.items():
        try:
            cvals = array.coords[cname]
        except KeyError:
            if not missing_ok:
                raise DimensionKeyError(f'coord={cname!r} not found in array.coords.') from None
            continue
        assign_coords[cname] = cvals + cshift
    return array.assign_coords(assign_coords)

@pcAccessor.register('mod_coords')
def xarray_mod_coords(array, mod=None, *, missing_ok=True, modshift=0, **mod_as_kw):
    '''return copy of array with coords modded (via np.mod) by `mod`.
    mod: None or dict of {coord: mod}
        dict --> mod each coord by the corresponding number.
        None --> provide as kwargs (mod_as_kw) instead.
    mod_as_kw: if mod is None, can provide mod dict as kwargs instead.
    modshift: value
        shift each coord by modshift before modding, then -modshift after modding.
        E.g. if modshift=90, mod=180, then modded coord = np.mod(coord+90, 180)-90.
    missing_ok: bool
        whether it is okay if some coords are missing (if yes, skip missing coords).
    '''
    if mod is None and len(mod_as_kw) == 0:
        raise InputMissingError('must provide either "mod" or "mod_as_kw".')
    if mod is not None and len(mod_as_kw) > 0:
        raise InputConflictError('cannot provide both "mod" and "mod_as_kw".')
    if mod is None:
        mod = mod_as_kw
    assign_coords = {}
    for cname, cmod in mod.items():
        try:
            cvals = array.coords[cname]
        except KeyError:
            if not missing_ok:
                raise DimensionKeyError(f'coord={cname!r} not found in array.coords.') from None
            continue
        assign_coords[cname] = np.mod(cvals + modshift, cmod) - modshift
    return array.assign_coords(assign_coords)

@pcAccessor.register('log_coords')
def xarray_log_coords(array, coords=None, newname='log_{coord}', *,
                      base=10, drop=True, promote=False):
    '''return copy of array with coords replaced by log coords (& renamed to log_coord)

    coords: None, str, or iterable of strs
        coords to replace with log. None --> all coords.
    newcoord: str
        string for new (logged) coord names: newcoord.format(coord=coord).
        Default: 'log_{coord}'. To keep original names, use '{coord}'
    base: number or 'e'
        log in this base. default 10.
        if not 10, result.assign_attrs({'log_base': base}).
    drop: bool
        whether to drop original coords' values.
        True --> drop original coords.
        False --> add new coords but do not adjust original coords.
    promote: bool
        whether to promote all non-dim new log coords to dimensions.
        if True, xarray_promote_dim for all new log coords.
    '''
    # bookkeeping
    if coords is None:
        coords = array.coords
    elif isinstance(coords, str):
        coords = [coords]
    newnames = {cname: newname.format(coord=cname) for cname in coords}
    if len(set(newnames.values())) != len(newnames):  # crash if any newname apears multiple times:
        raise InputConflictError(f'old to new name map must have unique values but got: {newnames!r}')
    if base == 10:
        f_log = np.log10
    else:
        array = array.assign_attrs({'log_base': base})
        if base == 'e':
            f_log = np.log
        elif base == 2:
            f_log = np.log2
        else:
            f_log = lambda x: np.log(x) / np.log(base)
    # computing new coords
    newcoords = {}
    for cname in coords:
        cvals = array.coords[cname]
        if drop:
            cvals = cvals.drop_vars(coords, errors='ignore')
        newvals = f_log(cvals)
        newcoords[newnames[cname]] = newvals
    # creating result appropriately
    if drop:
        array = array.drop_vars(coords, errors='ignore')
    result = array.assign_coords(newcoords)
    if promote:
        result = xarray_ensure_dims(result, list(newnames.values()))
    return result

@pcAccessor.register('str_coords')
def xarray_str_coords(array, coords=None, newname='str_{coord}', *, drop=True, promote=False,
                      missing_ok=False):
    '''return copy of array with coords replaced by str coords (& renamed to str_coord)
    E.g. array.pc.str_coords('fluid') --> result['str_fluid'] == str(f) for f in array['fluid']

    coords: None, str, or iterable of strs
        coords to replace with str. None --> all coords.
    newcoord: str
        string for new (converted-to-str) coord names: newcoord.format(coord=coord).
        Default: 'str_{coord}'. To keep original names, use '{coord}'
    drop: bool
        whether to drop original coords' values.
        True --> drop original coords.
        False --> add new coords but do not adjust original coords.
    promote: bool
        whether to promote all non-dim new str coords to dimensions.
        if True, xarray_promote_dim for all new str coords.
    missing_ok: bool
        whether it is okay for some provided `coords` to be missing from array.coords.
    '''
    # bookkeeping
    if coords is None:
        coords = array.coords
    elif isinstance(coords, str):
        coords = [coords]
    if missing_ok:
        coords = [c for c in coords if c in array.coords]  # skips missing coords.
    newnames = {cname: newname.format(coord=cname) for cname in coords}
    if len(set(newnames.values())) != len(newnames):
        raise InputConflictError(f'old to new name map must have unique values but got: {newnames!r}')
    # computing
    newcoords = {}
    for cname in coords:
        cvals = array.coords[cname]
        if drop:
            cvals = cvals.drop_vars(coords, errors='ignore')
        if cvals.dtype == object:
            newvals = xarray_dtype_object_to_str(cvals)
        else:
            newvals = cvals.astype(str)
        newcoords[newnames[cname]] = newvals
    # creating result
    if drop:
        array = array.drop_vars(coords, errors='ignore')
    result = array.assign_coords(newcoords)
    if promote:
        result = xarray_ensure_dims(result, list(newnames.values()))
    return result

@pcAccessor.register('is_sorted', totype='array')
def xarray_is_sorted(array, *, increasing=True):
    '''returns whether array is sorted; array must be 1D.

    increasing: bool
        True --> check for increasing order. vals[i] <= vals[i+1]
        False --> check for decreasing order. vals[i] >= vals [i+1]
    '''
    if array.ndim != 1:
        raise DimensionalityError('is_sorted expects 1D array.')
    vals = array.data
    if increasing:
        return np.all(vals[:-1] <= vals[1:])
    else:
        return np.all(vals[:-1] >= vals[1:])


### --------------------- Coord Math --------------------- ###

@pcAccessor.register('get_dx_along')
def xarray_get_dx_along(array, coord, *, atol=0, rtol=1e-5, float_rounding=False):
    '''returns number equal to the diff along array.coords[coord], after checking that it is constant.
    result will be a single number, equal to array.coords[coord].diff(coord)[0].item().

    (Technically, also promotes coord to dim during calculations if coord was a non-dimension coordinate.)
    
    before returning result, ensure that np.allclose(array.diff(dim), atol=atol, rtol=rtol);
        if that fails, raise DimensionValueError.

    float_rounding: bool
        if True, re-create floating point result if it seems to be wrong by only a small amount,
        e.g. 0.20000000001 --> float(0.2); 0.39999999999 --> float(0.4); 0.123456781234 --> unchanged
        This sometimes improves "exact" float comparisons, if float was input from a string.
        See tools.float_rounding for more details.
    '''
    carr = array.coords[coord]
    carr = xarray_promote_dim(carr, coord)
    diff = carr.diff(coord)
    if len(diff) == 0:
        raise DimensionValueError(f'expected non-empty diff({coord!r})')
    result = diff[0].item()
    if not np.allclose(diff, result, atol=atol, rtol=rtol):
        errmsg = f'expected evenly-spaced coordinates along coord {coord!r}, but got diff={diff}'
        raise DimensionValueError(errmsg)
    if float_rounding:
        result = math_float_rounding(result)
    return result

@pcAccessor.register('differentiate')
def xarray_differentiate(array, coord, *, keep_attrs=True, **kw__differentiate):
    '''differentiate array along coord, treating array like it is an xarray.DataArray.
    more lenient than xarray.DataArray.differentiate;
        returns 0 if can't differentiate along coord (due to coord having size 1 or not existing.)

    keep_attrs: bool
        whether to copy attrs from array into the result. Default True.

    requires that array.coords and array.differentiate exist, otherwise raises AttributeError.
    '''
    coords = array.coords
    try:
        coords_x = coords[coord]
    except KeyError:
        return xr.zeros_like(array)
    size_x = np.size(coords_x)
    if size_x <= 1:
        return xr.zeros_like(array)
    else:
        result = array.differentiate(coord, **kw__differentiate)
        if keep_attrs:
            result = result.assign_attrs(array.attrs.copy())
        return result
