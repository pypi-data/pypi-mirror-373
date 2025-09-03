"""
File Purpose: fft of xarrays.
"""

import numpy as np
import xarray as xr

from .array_fft import fftN, ifftN
from .fft_dimnames import FFTDimname
from .fft_slices import FFTSlices, _paramdocs_fft_slices
from ..docs_tools import format_docstring
from ..iterables import is_iterable
from ..sentinels import UNSET
from ..xarray_tools import (
    pcAccessor, xarray_promote_dim, xarray_get_dx_along,
)
from ...defaults import DEFAULTS
from ...errors import InputConflictError, InputMissingError


### --------------------- fft --------------------- ###

@pcAccessor.register('fftN', aliases=['fft'], totype='array')
@format_docstring(**_paramdocs_fft_slices)
def xarray_fftN(array, dim=None, ds=None, *, rad=None, abs=False,
                slices=dict(), keep=UNSET, half=UNSET, step=UNSET, missing_slices=UNSET, **kw_np_fftn):
    '''calculates fft(array) along N dimensions.
    shifts frequencies such that the 0-frequency is in the center.
    replaces result dimensions & coordinates appropriately, to indicate which dims were fft'd.

    dim: None, str, or iterable of strs
        coordinates(s) to take fft over.
        Can be pre-fft or post-fft names. (e.g. 'x', 'freq_x', 'freqrad_x', 'k_x')
        promote_dim(array, coord) for any non-dimension coordinates, as needed.
        None --> equivalent to array.dims
        str --> just this coordinate.
        iterable of strs --> just these coordinates.
    ds: None, number, or dict of {{dim: d}}
        spacing between elements of array (pre-transform), along each dim.
        if number, use the same value for all dims.
        if None, infer via array.coords[dim].diff(dim) for each dim
            (requires evenly-spaced coordinates in dim; spacing checked with np.allclose)
    rad: None or bool
        whether to convert frequencies to "radians" by multiplying them by 2 * pi.
        E.g., for fft in space, rad=False gives 1/wavelength; rad=True gives wavenumber k.
        if None, infer from dim if any post-fft names provided, else default to False.
    abs: bool
        if True, return np.abs(result), instead.
    slices: dict or FFTSlices
        instructions for slicing the final result.
        Can provide {{cname: indexer}} instructing to slice post-fft dimension
            associated with cname, via indexer. (cname can be pre-fft or post-fft name.)
            These understand fractional indexing: can provide a fractional value
            between -1 and 1, to use that fraction of the length along the relevant dimension.
        Can also provide `keep`, `half`, `step`, and/or `missing_slices`, here (Or, as kwargs).
            (raise InputConflictError if any provided in both places and have conflicting values.)
        See those kwargs for more details.
    keep: {keep}
        UNSET --> use None.
    half: {half}
        UNSET --> use None.
    step: {step}
        UNSET --> use None.
    missing_slices: {missing_slices}
        UNSET --> use 'ignore'

    additional kwargs passed to np.fft.fftn.

    returns result of fftn(...), shifted such that the 0-frequency is in the center,
        and with the relevant dimensions renamed as specified.
    '''
    # # parse input # #
    _input_dim = dim  # store input values --> helpful for debugging
    _input_rad = rad
    _input_slices = slices
    # dim
    dims = array.dims if (dim is None) else ([dim] if isinstance(dim, str) else list(dim))
    # freq_dims
    fnames = []
    for dim in dims:
        fname = FFTDimname.implied_from(dim, array.coords, rad=rad)  # (will crash if bad dim or rad)
        fnames.append(fname)
        rad = fname.rad  # <-- all fnames must have compatible rad!
    freq_dims = {fd.pre: fd.post for fd in fnames}   # {pre-fft: post-fft}
    dims = list(freq_dims)  # dims is now the pre-fft names.
    # promote non-dimension coordinates to dimensions, if necessary
    for dim in dims:
        array = xarray_promote_dim(array, dim)
    # ds
    if ds is None:
        ds = {dim: xarray_get_dx_along(array, dim, float_rounding=True) for dim in dims}
    elif isinstance(ds, str):  # raise helpful error message. Maybe caused by typo when inputting args.
        raise TypeError(f'expected None or dict-like ds; got ds={ds!r}')
    elif not is_iterable(ds):
        ds = {dim: ds for dim in dims}
    # slices
    if isinstance(slices, FFTSlices):
        slices = slices.as_kw()
    else:
        slices = slices.copy()  # make a copy, so we can update it without modifying the input.
    kw_slices = dict(keep=keep, half=half, step=step, missing_slices=missing_slices)
    for k, v in kw_slices.items():
        if v is not UNSET:
            if k not in slices:
                slices[k] = v
            elif slices[k] != v:
                raise InputConflictError(f'provided {k!r} both in slices and as kwargs, with conflicting values!')
    slices = FFTSlices(**slices)
    # # convert input to numpy-acceptable format # #
    np_array = array.values
    axes = tuple(array.dims.index(dim) for dim in dims)
    np_ds = tuple(ds[dim] for dim in dims)
    # # take the fft (and handle the fftshift, too) # #
    vals, freqs = fftN(np_array, ds=np_ds, axes=axes, rad=rad, **kw_np_fftn)
    # # converting to xarray # #
    # dims (order matters, must match dims order in vals)
    result_dims = list(array.dims)
    for i, dim in enumerate(result_dims):
        if dim in freq_dims:
            result_dims[i] = freq_dims[dim]
    # coords (update any coordinate info relevant to fft)
    freq_coords = {d: f for d, f in zip(dims, freqs)}    # dict of {original dim name: associated freq values}
    result_coords = array.coords.copy(deep=False)
    for cname, cval in tuple(result_coords.items()):
        if cname in freq_dims:  # a dimension where we applied fft.
            del result_coords[cname]
            fd = freq_dims[cname]
            result_coords[fd] = freq_coords[cname]
        elif any(cd in dims for cd in cval.dims):  # otherwise associated with a dimension where we applied fft.
            del result_coords[cname]  # discard info -- fft'd dims coords don't really map 1-to-1 to input coords.
        else:  # not associated with a dimension where we applied fft.
            pass  # keep the coordinate information.
    # if DEFAULTS.DEBUG:   # if debugging, these lines might help.
    #     return vals, result_dims, result_coords
    attrs = array.attrs.copy() if xr.get_options()['keep_attrs'] else None
    result = xr.DataArray(vals, dims=result_dims, coords=result_coords, attrs=attrs)
    # # slice the result if slices provided # #
    result = slices.applied_to(result, dims=dims)
    # # abs if requested # #
    if abs:
        result = np.abs(result)
    return result


### --------------------- ifft --------------------- ###

@pcAccessor.register('ifftN', aliases=['ifft'], totype='array')
def xarray_ifftN(array, dim=None, df=None, *, rad=None, pos_dims=None, ds=None, x0=0, **kw_np_ifftn):
    '''calculates ifft(array) along N dimensions.
    shifts positions such that the 0-position is in the center.
    replaces result dimensions & coordinates appropriately, to indicate which dims were ifft'd.

    For convenience, all coordinate names can be pre-fft OR post-fft names,
        e.g. 'x', 'freq_x', 'freqrad_x', or 'k_x'.
        "post-fft" names look like 'freq_dim', 'freqrad_dim',
            or any value in DEFAULTS.FFT_FREQ_RAD_DIMNAMES.values(), e.g. 'k_x'.

    Caution: ifft(fft(arr)) == arr only approximately, due to floating point rounding errors.
        Can at least ensure coordinate alignment by providing ds during ifft(fft(arr), ds=...)

    dim: None, str, or iterable of strs
        coordinates(s) of array to take ifft over.
        promote_dim(array, coord) for any non-dimension coordinates, as needed.
        None --> equivalent to array.dims
    df: None, number, or dict of {dim: d}
        spacing between elements of array (in frequency-space).
        None --> infer from ds if provided, else infer from array.
        number --> use this as df for all dims.
    rad: None or bool
        if True, interpret frequency-spacing (df) like it is "in radians",
            dividing it by 2 * pi before converting to position-space.
        None --> infer rad from names of the dims being ifft'd.
    ds: None, number, or dict of {dim: d}
        spacing between elements of result (in position-space), along dims from result.
        number --> use this as ds for all dims.
        None --> infer from df if provided, else infer from array.
        Note: provide ds to guarantee ifft(fft(arr)) == arr, exactly;
            otherwise position coords might include small rounding errors.
    x0: None, number, or dict of {dim: value}
        if provided, alter position-space coordinates by adding a constant offset,
            such that the 0'th position for each dim equals x0[dim].
        number --> apply the same number to all dims.
        iterable --> use these numbers; kwarg `dim` must also be provided as an iterable of strs.
        dict --> dict of {dim: x0} specifying the value associated with each dim
    '''
    # # parse input # #
    _dim_input = dim  # helpful for debugging; dim may be altered below.
    _rad_input = rad  # helpful for debugging. rad may be altered below.
    _df_input = df  # helpful for debugging. df may be altered below.
    _ds_input = ds  # helpful for debugging. ds may be altered below.
    # dim
    dims = array.dims if (dim is None) else ([dim] if isinstance(dim, str) else list(dim))
    # pos_dims
    fnames = []
    for dim in dims:
        fname = FFTDimname.implied_from(dim, array.coords, rad=rad, post_fft=True)  # (will crash if bad dim or rad)
        fnames.append(fname)
        rad = fname.rad  # <-- all fnames must have compatible rad!
    pos_dims = {fd.post: fd.pre for fd in fnames}  # {post-fft: pre-fft}. i.e., {pre-ifft: post-ifft}
    dims = list(pos_dims)  # dims is now the post-fft names. i.e., pre-ifft names.
    # promote non-dimension coordinates to dimensions, if necessary
    for dim in dims:
        array = xarray_promote_dim(array, dim)
    # df & ds
    if (df is not None) and (ds is not None):
        raise InputConflictError('provided df and ds. Expect ds, df, or neither, but not both!')
    if (df is None) and (ds is None):  # infer df from array coords
            df = {dim: xarray_get_dx_along(array, dim, float_rounding=True) for dim in dims}
    elif isinstance(df, str):  # raise helpful error message. Maybe caused by typo when inputting args.
        raise TypeError(f'expected None or dict-like df; got df={df!r}')
    if (df is not None) and (not is_iterable(df)):
        df = {dim: df for dim in dims}
    elif isinstance(df, dict):  # df is a dict, but user chose keys so they might not correspond to dims yet.
        df = {FFTDimname.implied_from(k, array.coords, rad=rad, post_fft=True).post: v for k, v in df.items()}
    if (ds is not None) and (not is_iterable(ds)):  # ds is a number
        ds = {dim: ds for dim in dims}
    elif isinstance(ds, dict):  # ds is a dict, but user chose keys so they might not correspond to dims yet.
        ds = {FFTDimname.implied_from(k, array.coords, rad=rad, post_fft=True).post: v for k, v in ds.items()}
    # x0
    if (x0 is not None) and (not is_iterable(x0)):  # x0 is a number
        x0 = {dim: x0 for dim in dims}
    elif isinstance(x0, dict):  # x0 is a dict, but user chose keys so they might not correspond to dims yet.
        x0 = {FFTDimname.implied_from(k, array.coords, rad=rad, post_fft=True).post: v for k, v in x0.items()}
    # # convert input to numpy-acceptable format # #
    np_array = array.values
    axes = tuple(array.dims.index(dim) for dim in dims)
    if df is not None: df = tuple(df.get(dim, None) for dim in dims)
    if ds is not None: ds = tuple(ds.get(dim, None) for dim in dims)
    if x0 is not None: x0 = tuple(x0.get(dim, None) for dim in dims)
    # # take the ifft (and handle the ifftshift, too) # #
    vals, pos = ifftN(np_array, df=df, axes=axes, rad=rad, x0=x0, ds=ds, **kw_np_ifftn)
    # # converting to xarray # #
    # dims (order matters, must match dims order in vals)
    result_dims = list(array.dims)
    for i, dim in enumerate(result_dims):
        if dim in pos_dims:
            result_dims[i] = pos_dims[dim]
    # coords (update any coordinate info relevant to ifft)
    pos_coords = {d: p for d, p in zip(dims, pos)}    # dict of {original freq dim name: associated pos values}
    result_coords = array.coords.copy(deep=False)
    for cname, cval in tuple(result_coords.items()):
        if cname in pos_dims:  # a dimension where we applied ifft.
            del result_coords[cname]
            pd = pos_dims[cname]
            result_coords[pd] = pos_coords[cname]
        elif any(cd in dims for cd in cval.dims):  # otherwise associated with a dimension where we applied ifft.
            del result_coords[cname]  # discard info -- ifft'd dims coords don't really map 1-to-1 to input coords.
        else:  # not associated with a dimension where we applied ifft.
            pass  # keep the coordinate information.
    attrs = array.attrs.copy() if xr.get_options()['keep_attrs'] else None
    result = xr.DataArray(vals, dims=result_dims, coords=result_coords, attrs=attrs)
    return result


### --------------------- lowpass filtering --------------------- ###

@pcAccessor.register('lowpass', totype='array')
@format_docstring(default_lowpass=DEFAULTS.LOWPASS_KEEP)
def xarray_lowpass(array, dim=None, keep=UNSET, *, keep_r=UNSET, ds=None, real=None, return_fft=False):
    '''return array after putting it through a lowpass filter using fft & ifft.
    This is equivalent to ifft(fft(array) * filter), where filter is 0 at all "large" frequency values.
    "large" is determined by keep & r; see below.

    dim: None or iterable or strs
        coordinates to apply lowpass filter over. If None, use all array.dims.
        promote_dim(array, coord) for any non-dimension coordinates, as needed.
    keep: UNSET, True, dict, or number between 0 < keep <= 1
        fraction of frequencies to keep, along each dim.
        (Must provide this or keep_r but not both.)
        True --> use DEFAULTS.FFT_LOWPASS_KEEP.
        number --> use this value for all dims.
    keep_r: UNSET, True, or number between 0 < keep <= 1
        radius of N-sphere to keep in normalized frequency-space,
            normalized such that max(frequencies)==1 along each dim.
        All values outside of this N-sphere will be set to 0.
        Similar to `keep`, but here use an N-sphere instead of an N-cube.
        (Must provide this or keep but not both.)
        True --> use DEFAULTS.FFT_LOWPASS_KEEP.
        [TODO] more options than just spherical? (e.g. ellipsoid)
    ds: None, number, or dict of {{dim: d}}
        spacing between elements of array along each dim.
        number --> use the same value for all dims.
        None --> infer via array.coords[dim].diff(dim) for each dim
            (requires evenly-spaced coordinates in dim; spacing checked with np.allclose)
    real: None or bool
        whether to return np.real(ifft) instead of just ifft (which might have imaginary part)
        None --> infer from array. Use True if np.all(np.isreal(array)), else False.
    return_fft: bool
        whether to return (result, masked fft) instead of just result.
        mainly intended for debugging purposes.
    '''
    # # parse input # #
    _input_dim = dim   # remembering original inputs helps with debugging.
    _input_keep = keep
    _input_ds = ds
    # dim
    dims = array.dims if dim is None else dim
    for dim in dims:
        array = xarray_promote_dim(array, dim)
    # real
    if real is None:
        real = np.all(np.isreal(array))
    # ds
    if ds is None:
        ds = {dim: xarray_get_dx_along(array, dim, float_rounding=True) for dim in dims}
    # keep
    if keep is UNSET and keep_r is UNSET:
        raise InputMissingError('must provide keep or keep_r.')
    if keep is not UNSET and keep_r is not UNSET:
        raise InputConflictError('Expect keep or keep_r, but not both.')
    if keep is not UNSET:
        if keep is True:
            keep = DEFAULTS.LOWPASS_KEEP
        if not isinstance(keep, dict):
            keep = {dim: keep for dim in dims}
        post_keep = {FFTDimname(k).post: v for k, v in keep.items()}  # {post-fft dimname: keep}
    if keep_r is not UNSET:
        if keep_r is True:
            keep_r = DEFAULTS.LOWPASS_KEEP
    # # fft # #
    fft = xarray_fftN(array, dim=dims, ds=ds)
    fft_dims = [FFTDimname(d).post for d in dims]  # post-fft name for each dim in dims.
    # # lowpass filter # #
    # assumes that coords from xarray_fftN are centered around 0, and evenly spaced.
    if keep is not UNSET:  # set values outside of N-cube to 0.
        for dim, k in post_keep.items():
            # fft = 0 wherever |coords| > keep * max(|coords|)
            abs_coords = np.abs(fft.coords[dim])
            max_coord = np.max(abs_coords)
            fft = fft.where(abs_coords <= k * max_coord, other=0)  # values outside cube become 0.
    else:  # keep_r is not UNSET
        # fft = 0 wherever (distance from origin in normalized frequency space) >= keep_r
        dists = np.sqrt(sum((fft.coords[dim] / np.max(fft.coords[dim]))**2 for dim in fft_dims))
        fft = fft.where(dists <= keep_r, other=0)  # values outside sphere become 0.
    # # ifft # #
    result = xarray_ifftN(fft, dim=fft_dims, ds=ds)
    # # postprocessing # #
    if real:
        result = np.real(result)
    if return_fft:
        return result, fft
    return result
