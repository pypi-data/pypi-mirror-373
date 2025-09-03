"""
File Purpose: fft of numpy arrays.
"""

import numpy as np

from ..iterables import is_iterable
from ..math import float_rounding as math_float_rounding
from ...errors import InputConflictError, InputMissingError


### --------------------- fft --------------------- ###

def fftN(array, ds, axes=None, *, rad=False, **kw_np_fftn):
    '''calculates fft along N dimensions, as well as the corresponding frequencies.

    array: array-like
        take the fft of this array (along the indicated axes).
    ds: list-like with length == len(axes) (or array.ndim if axes is None)
        specifies the spacing between elements of array (in position-space), along each axis.
        This is necessary in order to provide the frequency coordinates for the result.
    axes: None, or iterable of ints
        axes to take fft over. (Negative values are supported & count from end.)
        None --> take fft over all axes.
    rad: bool
        if True, convert frequencies to "radians" by multiplying them by 2 * pi.
        E.g., for fft in space, rad=False gives 1/wavelength; rad=True gives wavenumber k.
    
    additional kwargs passed to np.fft.fftn.

    returns (shifted fftn(array, axes=axes, **kw_np_fftn), (freq0, freq1, ..., freqN)),
        where freq0, freq1, ..., freqN are the frequencies corresponding to the N axes,
        and all freqs & values are shifted with np.fft.fftshift to put the 0-frequency in the center.
    '''
    array = np.asanyarray(array)
    if axes is None:
        axes = list(range(array.ndim))
    if len(ds) != len(axes):
        raise InputConflictError(f"len(ds)={len(ds)} != len(axes)={len(axes)}")
    Ns = [array.shape[ax] for ax in axes]
    shifted_freqs = tuple(fftfreq_shifted(N, d, rad=rad) for N, d in zip(Ns, ds))
    # take fft & shift appropriately.
    vals = np.fft.fftn(array, axes=axes, **kw_np_fftn)
    vals = np.fft.fftshift(vals, axes=axes)
    return vals, shifted_freqs

def fft2(array, dx, dy, axes=(-2,-1), *, rad=False, **kw_np_fftn):
    '''calculates fft along 2 dimensions, as well as the corresponding frequencies.
    Equivalent to:
        fftN(array, (dx, dy), axes=axes, rad=rad, **kw_np_fftn).

    array: array-like
        take the fft of this array.
    dx, dy: numbers
        spacing between elements of array (in position-space), along each axis.
        This is necessary in order to provide the frequency coordinates for the result.
    axes: iterable of ints, default (-2,-1)
        axes to take fft over. (Negative values are supported & count from end.)
    rad: bool
        if True, convert frequencies to "radians" by multiplying them by 2 * pi.
        E.g., for fft in space, rad=False gives 1/wavelength; rad=True gives wavenumber k.
    
    additional kwargs passed to np.fft.fftn.

    returns (shifted fft2(array, axes=axes, **kw_np_fftn), (freqx, freqy)),
        where freqx, freqy are the frequencies corresponding to the x and y axes,
        and all freqs & values are shifted with np.fft.fftshift to put the 0-frequency in the center.
    '''
    return fftN(array, (dx, dy), axes=axes, rad=rad, **kw_np_fftn)

def fft1(array, dx, axis=-1, *, rad=False, **kw_np_fftn):
    '''calculates fft along 1 dimension, as well as the corresponding frequencies.
    Equivalent to:
        vals, freqs = fftN(array, (dx,), axes=(axis,), rad=rad, **kw_np_fftn);
        return vals, freqs[0]

    array: array-like
        take the fft of this array.
    dx: number
        spacing between elements of array (in position-space), along the axis.
        This is necessary in order to provide the frequency coordinates for the result.
    axis: int, default -1
        axis to take fft over. (Negative values are supported & count from end.)
    rad: bool
        if True, convert frequencies to "radians" by multiplying them by 2 * pi.
        E.g., for fft in space, rad=False gives 1/wavelength; rad=True gives wavenumber k.
    
    additional kwargs passed to np.fft.fftn.

    returns (shifted fft1(array, axis=axis, **kw_np_fftn), freqx),
        where freqx is the frequencies corresponding to the x axis,
        and all freqs & values are shifted with np.fft.fftshift to put the 0-frequency in the center.
    '''
    vals, freqs = fftN(array, (dx,), axes=(axis,), rad=rad, **kw_np_fftn)
    return vals, freqs[0]

def fftfreq_shifted(N, d, *, rad=False):
    '''returns the shifted frequencies corresponding to the fft of an array of length N,
    with spacing d between elements.
    if rad: convert frequencies to "radians" by multiplying them by 2 * pi.

    "shifted" means that the 0-frequency is in the center of the result.
    '''
    freq = np.fft.fftfreq(N, d)
    if rad:
        freq *= 2 * np.pi
    return np.fft.fftshift(freq)


### --------------------- inverse fft --------------------- ###

def ifftN(array, df=None, axes=None, *, rad=False, x0=0, ds=None, **kw_np_ifftn):
    '''calculates inverse fft along N dimensions, as well as the corresponding positions.

    Caution: ifftN(fftN(arr)) == arr only approximately, due to floating point rounding errors.
        Can at least ensure coordinate alignment by providing ds during ifftN(fftN(arr), ds=...)

    array: array-like
        take the inverse fft of this array (along the indicated axes).
        the 0-frequency component should be centered in each axis,
            as per the output of np.fft.fftshift(np.fft.fft(position_space_array)).
    df: None, number, or list-like with length == len(axes)
        specifies the spacing between elements of array (in frequency-space), along each axis.
        None --> use ds instead. (Must provide ds or df.)
    axes: None, or iterable of ints
        axes to take inverse fft over. (Negative values are supported & count from end.)
        None --> take inverse fft over all axes.
    rad: bool
        if True, interpret frequency-spacing (df) like it is "in radians",
            dividing it by 2 * pi before converting to position-space.
    x0: None, number, or list-like with length == len(axes)
        if provided, alter position-space coordinates by adding a constant offset,
            such that the 0'th position for axes[i] equals x0[i].
    ds: None, number, or list-like with length == len(axes)
        specifies the spacing between elements of result (in position-space), along each axis.
        None --> use df instead. (Must provide ds or df.)
    
    additional kwargs passed to np.fft.ifftn.

    returns (shifted ifftn(array, axes=axes, **kw_np_ifftn), (pos0, pos1, ..., posN)),
        where pos0, pos1, ..., posN are the positions corresponding to the N axes,
        and all positions & values are shifted with np.fft.ifftshift to put the 0-position in the center.
    '''
    array = np.asanyarray(array)
    if axes is None:
        axes = list(range(array.ndim))
    Ns = [array.shape[ax] for ax in axes]
    df = [df] * len(axes) if not is_iterable(df) else df
    ds = [ds] * len(axes) if not is_iterable(ds) else ds
    x0 = [x0] * len(axes) if not is_iterable(x0) else x0
    if len(df) != len(axes):
        raise InputConflictError(f"len(df)={len(df)} != len(axes)={len(axes)}")
    if len(ds) != len(axes):
        raise InputConflictError(f"len(ds)={len(ds)} != len(axes)={len(axes)}")
    if len(x0) != len(axes):
        raise InputConflictError(f"len(x0)={len(x0)} != len(axes)={len(axes)}")
    shifted_pos = tuple(ifftfreq_shifted(N, df_, rad=rad, x0=x0_, ds=ds_) for N, df_, ds_, x0_ in zip(Ns, df, ds, x0))
    # take inverse fft & shift appropriately.  # [TODO] get the shift / inverse shift correct.
    array_unshifted = np.fft.ifftshift(array, axes=axes)
    vals = np.fft.ifftn(array_unshifted, axes=axes, **kw_np_ifftn)
    return vals, shifted_pos

# [TODO] ifft2, ifft1

def ifftfreq_shifted(N, df=None, *, rad=False, x0=0, ds=None, float_rounding=True):
    '''returns the shifted positions corresponding to the inverse fft of an array of length N.

    df: None or number
        spacing between elements of array (in frequency-space).
        None --> use ds to determine position coordinates instead.
    rad: bool
        whether to interpret frequency-spacing (df) like it is "in radians",
        dividing it by 2 * pi before converting to position-space.
    x0: None or number
        if provided, add value to result such that result[0] == x0.
        (This corresponds to altering position-space coordinates by a constant offset.)
    ds: None or number
        if provided, actually use this as position diff, instead of determining it from d & rad.
    float_rounding: bool
        if True, round ds to a more-likely-to-be-input float.
        e.g. 0.20000000001 --> float(0.2); 0.399999999 --> float(0.4); 0.123456781234 --> unchanged.
    '''
    if df is None and ds is None:
        raise InputMissingError("either df or ds must be provided")
    if df is not None:
        if rad:
            df = df / (2 * np.pi)   # avoid "/=" because it could directly alter the input d.
        ds = 1 / (N * df)
        # could do np.fft.fftfreq, but instead just use known ds & np.arange.
        #pos = np.fft.fftfreq(N, df)   # note, fftfreq is its own inverse.
        #result = np.fft.fftshift(pos)
    if float_rounding:
        ds = math_float_rounding(ds, prec=8)
    result = np.arange(N)
    if x0 is None:  # behave like fftfreq result
        result -= N//2
    result = result * ds
    if x0 is not None:  # choose value for result[0]
        result += x0
    return result
