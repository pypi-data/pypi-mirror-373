"""
File Purpose: tools for arrays (more generic than xarrays)
"""

import numpy as np

from .docs_tools import format_docstring
from .iterables import is_iterable
from .math import round_to_int
from .sentinels import UNSET
from ..errors import (
    InputError, InputConflictError, InputMissingError, 
    MemorySizeError,
    DimensionalityError,
)
from ..defaults import DEFAULTS


### --------------------- Size in Memory --------------------- ###

def memory_size_check(array, *, MBmax=UNSET, dtype_min=UNSET, safety=1, errmsg=None):
    '''raise MemorySizeError if array is too large.
    Too large if safety * array.nbytes/1024**2 > MBmax.

    array: array, e.g. numpy array
        must have .size and .dtype attributes which tell number of elements and numpy dtype.
        Or, can be an xarray.Dataset, in which case will add up the size of all DataArrays.
    MBmax: UNSET, None, or int
        maximum size allowed, in Megabytes.
        UNSET --> use DEFAULTS.ARRAY_MBYTES_MAX
        None --> no limit.
    dtype_min: UNSET or numpy dtype
        calculate memory as if array elements will have at least as many bytes as dtype_min.itemsize.
        (if array elements already have more bytes than this, use array.dtype instead.)
        UNSET --> use DEFAULTS.ARRAY_MEMORY_CHECK_DTYPE_MIN
        None --> don't impose any minimum, just use array.dtype.
    safety: number
        safety factor; safety * array.nbytes/1024**2 is the actual limit.
    errmsg: None or str
        if provided, if raising MemorySizeError, use this for the error message,
        after formatting with .format(nMB=nMB, MBmax=MBmax, safety=safety, nMB_total=nMB * safety,
                                    dtype=dtype used, shape=array.shape, size=array.size).
        if None, use:
            "array too large: {nMB:.1e} MB > MBmax / safety. (MBmax={MBmax} MB, safety={safety})".
    '''
    if MBmax is UNSET: MBmax = DEFAULTS.ARRAY_MBYTES_MAX
    if dtype_min is UNSET: dtype_min = DEFAULTS.ARRAY_MEMORY_CHECK_DTYPE_MIN
    if MBmax is not None:
        arrays = [array] if not hasattr(array, 'data_vars') else list(array.data_vars.values())
        # ^ handles xarray.Dataset, which has data_vars which lists arrays.
        nMB = 0
        for array in arrays:
            size = array.size
            dtype = array.dtype
            itemsize = array.dtype.itemsize
            if dtype_min is not None:
                min_itemsize = np.dtype(dtype_min).itemsize
                if min_itemsize > array.dtype.itemsize:
                    dtype = dtype_min
                    itemsize = min_itemsize
            nbytes = size * itemsize
            nMB = nMB + nbytes / 1024**2
        if safety * nMB > MBmax:
            if errmsg is None:
                errmsg = ('array too large: {nMB:.1e} MB > MBmax / safety; '
                          '(MBmax={MBmax} MB, safety={safety})')
            errmsg = errmsg.format(nMB=nMB, MBmax=MBmax, safety=safety, nMB_total=nMB * safety,
                                   dtype=dtype, shape=array.shape, size=array.size)
            raise MemorySizeError(errmsg)

def memory_size_check_loading_arrays_like(array1, nload=1, *, MBmax=UNSET, dtype_min=UNSET):
    '''raise MemorySizeError if loading nload arrays like array1 will be too large.
    Too large if total size in MB would be more than MBmax.

    array1: array, e.g. numpy array
        must have .nbytes attribute, which tells size in bytes.
    n: int
        number of arrays like array1 which will be loaded.
    MBmax: UNSET, None, or int
        maximum size allowed, in Megabytes.
        UNSET --> use DEFAULTS.ARRAY_MBYTES_MAX
        None --> no limit.
    dtype_min: UNSET or numpy dtype
        calculate memory as if array elements will have at least as many bytes as dtype_min.itemsize.
        (if array elements already have more bytes than this, use array.dtype instead.)
        UNSET --> use DEFAULTS.ARRAY_MEMORY_CHECK_DTYPE_MIN
        None --> don't impose any minimum, just use array.dtype.

    return size of array1, in MB.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    # this function just calls memory_size_check, with a more helpful error message if it fails.
    errmsg = ("array too large to load n = {safety} simultaneously, with array memory size = {nMB:.4g} MB.\n"
              "Calculated memory with dtype = {dtype}, array.size = {size:.2e} elements, array.shape = {shape}.\n"
              "Consider loading fewer arrays simultaneously. "
              "Alternatively, adjust the limit by setting DEFAULTS.ARRAY_MBYTES_MAX.\n"
              "Current limit = {MBmax:.4g} MB. Here, would need at least {nMB_total:.4g} MB.")
    return memory_size_check(array1, MBmax=MBmax, dtype_min=dtype_min, safety=nload, errmsg=errmsg)


### --------------------- Finite operations --------------------- ###

def finite_op(arr, op, *, if_empty=UNSET):
    '''returns op(arr), hitting only the finite values of arr.

    arr: array-like or list of differently-sized array-like objects.
        will do op(array, or list of arrays to flatten & concatenate).
        if arr is a single array-like has only finite values,
            finite_op(arr, op) == op(arr).
        if arr is a single array-like and has some nonfinite values (infs or nans),
            finite_op(arr, op) == op(arr[np.isfinite(arr)])
        if np.asanyarray(arr) fails with ValueError,
            attempt to interpret arr as a list of differently-sized array-like objects;
            convert each to array via np.asanyarray, reshape(-1), then concatenate.

    if_empty: UNSET or any value
        value to return if arr is an empty array (or there are no finite values in it).
        UNSET --> use numpy default behavior (e.g. np.mean([]) --> nan; np.min([]) --> crash)
        any value --> return this value.
    '''
    try:
        arr = np.asanyarray(arr)
    except ValueError:  # might be a list of differently-sized arrays-like objects.
        arrs = [np.asanyarray(a).reshape(-1) for a in arr]
        arr = np.concatenate(arrs)
    finite = np.isfinite(arr)
    if np.count_nonzero(finite) < finite.size:
        arr_use = arr[finite]   # [EFF] index by finite only if there's any non-finite values.
    else:
        arr_use = arr
    if (if_empty is not UNSET) and (arr_use.size == 0):
        return if_empty
    return op(arr_use)

def finite_min(arr, *, if_empty=np.nan):
    '''returns min of all the finite values of arr. (return if_empty if arr has no finite values.)'''
    return finite_op(arr, np.min, if_empty=if_empty)

def finite_mean(arr, *, if_empty=np.nan):
    '''returns mean of all the finite values of arr.  (return if_empty if arr has no finite values.)'''
    return finite_op(arr, np.mean, if_empty=if_empty)

def finite_max(arr, *, if_empty=np.nan):
    '''returns max of all the finite values of arr. (return if_empty if arr has no finite values.)'''
    return finite_op(arr, np.max, if_empty=if_empty)

def finite_std(arr, *, if_empty=np.nan):
    '''returns std of all the finite values of arr. (return if_empty if arr has no finite values.)'''
    return finite_op(arr, np.std, if_empty=if_empty)

def finite_median(arr, *, if_empty=np.nan):
    '''returns median of all the finite values of arr. (return if_empty if arr has no finite values.)'''
    return finite_op(arr, np.median, if_empty=if_empty)

def finite_percentile(arr, percentile, *, if_empty=np.nan):
    '''returns percentile of all the finite values of arr.  (return if_empty if arr has no finite values.)'''
    if getattr(arr, 'dtype', None) == bool:
        raise TypeError("finite_percentile does not support boolean arrays.")
    return finite_op(arr, lambda arr: np.percentile(arr, percentile), if_empty=if_empty)


### --------------------- unique close --------------------- ###

def unique_close(arr, *, rtol=1e-5, atol=1e-8):
    '''returns unique values of arr, within relative tolerance rtol and absolute tolerance atol.
    Like np.unique(arr), but it uses np.isclose to compare values, instead of exact equality.
    '''
    result = []
    arr = np.asanyarray(arr)
    for elem in arr.flat:
        close = np.isclose(result, elem, atol=atol, rtol=rtol)
        if not np.any(close):
            result.append(elem)
    return np.array(result)


### --------------------- indexing --------------------- ###

@format_docstring(default_rounding=DEFAULTS.FRACTIONAL_INDEX_ROUNDING)
def interprets_fractional_indexing(indexer, L=None, *, rounding=UNSET):
    '''interprets any fractional values, i.e. non-integers between -1 and 1.
    returns indexer in "canonical" form, no longer containing any fractional values.
    If indexer contains no fractional values, return indexer unchanged.

    indexer: None, int, slice, iterable, or non-integer between -1 and 1.
        indexer to interpret; might contain fractional value(s), i.e. non-integers between -1 and 1.
        any fractional values will be converted to value*(L+1), then rounded to an integer.
            rounding method is determined by `rounding`, unless indexer is a slice,
            in which case rounding for start & stop is handled differently.
        fractional values might appear in any of the following ways:
            - as an individual float, e.g. 0.3
            - as a float inside an iterable, e.g. [0, 0.25, 0.5, 0.75, 1]
            - as a float inside a slice, e.g. slice(0, -0.1, 0.02)
        "fractional" is tested via (-1 < value < 1) and (value != 0).
    L: None or int
        length of the object being indexed. Required if any fractional values provided.
        None --> if any fractional values provided, raise InputMissingError.
        L must be >= 2. [TODO] handle L=1 case (have all fractional values imply 0).
    rounding: UNSET, 'round', 'floor', 'ceil' or 'int'
        method to use for rounding fractional values to integers, except for slice.start or slice.stop.
        UNSET --> use DEFAULTS.FRACTIONAL_INDEX_ROUNDING (default: {default_rounding})
        'round' --> as per builtins.round(). round to nearest integer, ties toward even integers.
        'int' --> as per builtins.int(). round towards 0.
        'floor' --> as per math.floor(). round towards negative infinity.
        'ceil' --> as per math.ceil(). round towards positive infinity.
    
    Rounding for slice.start and start.stop will ALWAYS include all indices between start*(L-1) and stop*(L-1)
        For positive (or None) step, this means: round all numbers toward +infinity.
            Examples (floats here are after multiplying input by L-1, e.g. 0.1 * 153 --> 15.3):
                slice(15.3, 29.2, 1)    --> slice(16, 30, 1)     # 15.3, [16, 17, ..., 29], 29.2
                slice(-29.2, -15.3, 1)  --> slice(-29, -15, 1)   # -29.2, [-29, -28, ..., -16], -15.3
                slice(15.3, -15.3, 1)   --> slice(16, -15, 1)    # 15.3, [16, 18, ..., -17, -16], -15.3
                slice(-29.2, 100.1, 1)  --> slice(-29, 101, 1)   # -29.2, [-29, -28, ..., 99, 100], 100.1
        For negative step, this means: round all numbers toward -infinity.
            Examples (floats here are after multiplying input by L-1, e.g. 0.1 * 153 --> 15.3):
                slice(29.2, 15.3, -1)   --> slice(29, 15, -1)    # 29.2, [29, 28, ..., 17, 16], 15.3
                slice(-15.3, -29.2, -1) --> slice(-16, -30, -1)  # -15.3, [-16, -17, ..., -28, -29], -29.2
                slice(-15.3, 15.3, -1)  --> slice(-16, 15, -1)   # -15.3, [-16, -17, ..., 16, 15], 15.3
                slice(100.1, -29.2, -1) --> slice(100, -30, -1)  # 100.1, [100, 99, ..., -28, -29], -29.2
    Rounding mode for slice.step is determined by `rounding`, applying to step*L (not L-1).
        however if this causes step=0, instead use step=1 or step=-1, based on sign of original step.

    --- Examples ---
        # [TODO] update these when considering N = L-1 is what is actually being multiplied.
        interprets_fractional_indexing(0.5, L=10)  --> 5
        interprets_fractional_indexing(slice(0.2, 0.9, 0.1), L=10)  --> slice(2, 9, 1)
        interprets_fractional_indexing([0.2, 0.5, -3, 8, 7, 0.9], L=10)  --> [2, 5, -3, 8, 7, 9]
        interprets_fractional_indexing(0.23, L=10, rounding='int')  --> 2
        interprets_fractional_indexing(0.23, L=10, rounding='ceil')  --> 3
    '''
    if indexer is None:
        return indexer
    if np.ndim(indexer) > 1:
        raise NotImplementedError("interprets_fractional_indexing does not yet support multi-dimensional indexers.")
    def is_fractional(value):
        return (-1 < value < 1) and (value != 0)
    def check_L_because_it_is_required():
        if L is None:
            raise InputMissingError('L is required if any fractional values are provided.')
        if L <= 1:
            raise ValueError(f"fractional indexing not supported when L <= 1; got L={L}")
    if rounding is UNSET:
        rounding = DEFAULTS.FRACTIONAL_INDEX_ROUNDING
    if L is not None:
        N = L - 1
    if isinstance(indexer, slice):
        start, stop, step = indexer.start, indexer.stop, indexer.step
        step_is_frac = ((step is not None) and is_fractional(step))
        start_is_frac = ((start is not None) and is_fractional(start))
        stop_is_frac = ((stop is not None) and is_fractional(stop))
        if not start_is_frac and not stop_is_frac and not step_is_frac:
            return indexer  # no fractional values; return indexer unchanged.
        #else:
        check_L_because_it_is_required()
        if start_is_frac or stop_is_frac:
            if (step is None) or (step > 0):
                if start_is_frac: start = round_to_int(start * N, mode='ceil')
                if stop_is_frac: stop = round_to_int(stop * N, mode='ceil')
            else:
                if start_is_frac: start = round_to_int(start * N, mode='floor')
                if stop_is_frac: stop = round_to_int(stop * N, mode='floor')
        if step_is_frac:
            orig_step = step
            step = round_to_int(step * L, mode=rounding)
            if step == 0:
                step = 1 if (orig_step > 0) else -1
        return type(indexer)(start, stop, step)
    # else
    try:
        iter(indexer)
    except TypeError:
        is_iterable = False
    else:
        is_iterable = True
    if is_iterable:
        indexer_type = type(indexer)
        result = [val for val in indexer]
        fractional = [is_fractional(val) for val in result]
        if any(fractional):
            check_L_because_it_is_required()
            result = [(round_to_int(val * N, mode=rounding) if f else val) for val, f in zip(result, fractional)]
            return indexer_type(result)
        else:
            return indexer  # no fractional values; return indexer unchanged.
    else:  # not iterable
        if is_fractional(indexer):
            check_L_because_it_is_required()
            return round_to_int(indexer * N, mode=rounding)
        else:
            return indexer
    assert False, "unreachable code"

def ndindex_array(shape):
    '''returns an array of indexes, where each element is its own np.ndindex.
    For 0D, crash with DimensionalityError.
    For 1D, result[i] == i
        (Do not use tuple results for 1D. Also, optimize dtype to np.min_scalar_type.)
        E.g. ndindex_array((3,)) --> np.array([0,1,2], dtype=uint8).
    For 2D+, result[index] == index, where index is a tuple.
        E.g. in 2D, result[i,j] == (i,j). And, ndindex_array((2,3)) -->
            np.array([[(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)]], dtype=object)
    '''
    if not is_iterable(shape):
        shape = [shape]
    if len(shape) == 0:
        raise DimensionalityError('ndindex_array does not support 0D arrays.')
    elif len(shape) == 1:
        result = np.arange(shape[0], dtype=np.min_scalar_type(shape[0]))
    else:  # 2D+
        result = np.empty(shape, dtype=object)
        for index in np.ndindex(shape):
            result[index] = index
    return result


### --------------------- array from nested list --------------------- ###

def looks_flat(x):
    '''returns whether x looks flat, i.e. looks like an iterable with no internal layers.
    Only checks x[0]. (If x is not iterable, raise TypeError. If len(x)==0, return True).
    Note: might behave unexpectedly for strings.
    '''
    if not is_iterable(x):
        raise TypeError(f'looks_flat(x) expected iterable x but got x={x}')
    if len(x)==0:
        return True
    return not is_iterable(x[0])

def nest_shape(nested_list, is_element=looks_flat):
    '''returns the implied shape for a numpy object array constructed from nested_list.
    Only considers 0th element of list(s) (recursively, as needed). Stops when reaching an is_element(obj).
    To avoid infinite recursion, raise ValueError if current[0] is current (e.g. with strings).
    (To properly handle strings, provide a more sophisticated is_element than the default value.)
    
    is_element: callable of one input
        if is_element(obj), stop going deeper into lists.
        otherwise, append len(obj) to result, then inspect obj[0].
        (to start, use obj = nested_list.)
        default (looks_flat) stops when obj is iterable but obj[0] is not.
    '''
    shape = []
    current = nested_list
    while not is_element(current):
        if current[0] is current:
            raise DimensionalityError('nest_shape failed: obj[0] is obj. Crash to avoid infinite loop.')
        l = len(current)
        shape.append(l)
        current = current[0]
    return shape


### --------------------- wrap 1D list --------------------- ###

def wraplist(x, wraprow=None, wrapcol=None, *, fill=None, dtype=object):
    '''wrap 1D list into a 2D array. Fill missing elements with fill.

    Must provide wraprow or wrapcol, but not both:
    wraprow: None or int
        result rows will have this length. result goes left to right then top to bottom.
        E.g. [1,2,3,4,5,6,7,8,9], wraprow=4 --> [[1,2,3,4], [5,6,7,8], [9,fill,fill,fill]]
    wrapcol: None or int
        result cols will have this length. result goes top to bottom then left to right.
        E.g. [1,2,3,4,5,6,7,8,9], wrapcol=4 --> [[1,5,9], [2,6,fill], [3,7,fill], [4,8,fill]]
    fill: None or any value
        fill missing elements with this value.
    dtype: any valid specifier for a numpy dtype
        dtype for resulting numpy array.
    '''
    if wraprow is None and wrapcol is None:
        raise InputMissingError('wraplist requires either wraprow or wrapcol to be provided.')
    if wraprow is not None and wrapcol is not None:
        raise InputConflictError('wraplist requires either wraprow or wrapcol, not both.')
    Lx = len(x)
    # var names below as if we are using wraprow. Code works for wrapcol too though.
    Lrow = wraprow if (wraprow is not None) else wrapcol
    Lcol = Lx // Lrow + (0 if (Lx % Lrow)==0 else 1)
    # shape=(Lcol, Lrow) because Lrow = number of cols. E.g. Lrow=7 means there are 7 cols.
    result = np.full((Lcol, Lrow), fill, dtype=dtype)
    result.flat[:Lx] = x   # without [:Lx], this wraps around unexpectedly...
    if wrapcol is not None:
        result = result.T
    return result

def ndenumerate_nonNone(arr, none=None):
    '''np.ndenumerate(arr) but skip wherever value is none (compared via 'is', not '==').'''
    for index, value in np.ndenumerate(arr):
        if value is not none:
            yield index, value




### --------------------- types --------------------- ###

def np_dtype_object_to_str(array):
    '''convert a numpy array of dtype==object into array of str(x) for all x in array.'''
    try:
        return array.astype(str)
    except ValueError:  # e.g. ValueError: setting an array element with a sequence
        pass  # handled below -- call str() on each element individually
    result = np.empty(array.shape, dtype=object)  # can't dtype=str here because it would do '<U1'.
    for index, value in np.ndenumerate(array):
        result[index] = str(value)
    return result.astype(str)
