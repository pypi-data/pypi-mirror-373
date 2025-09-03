"""
File Purpose: Bifrost Stagger (align inputs to grid)

STAGGER ORDERS DEFINED HERE:
    1 - "simplest" method available.
            good enough, for most uses. ~20% faster than order=5
    5 - improved 5th order scheme.
            the improvement refers to improved precision for "shift" operations.

The implementations here use numpy.
Future implementations may use numba if numpy is too slow
    helita has numba implementation but numba can make installation more challenging;
    if adding numba here be sure to make it optional, not a requirement for PlasmaCalcs.

TESTED:
    seems to give same results as helita implementation, for 5th order numpy scheme.
    seems to take roughly the same amount of time as helita implementation
        (maybe 5 to 10% faster for shifts. Within 5% speed for derivatives.)


[TODO]
mod_J is not identical when comparing stagger_minimal_slicing=True & False modes,
    even though I would expect it to be identical in both cases.
    However, the result seems to be very close
        (e.g. J_z within 0.1% except for points with very small J)
    In the interest of time, I am saying "that's good enough" for now. (-SE, 2025/01/28)

Also, currently cannot slice using nontrivial step in multiple slices at once :(
"""

import collections
import re

import numpy as np
import xarray as xr

from ...defaults import DEFAULTS
from ...dimensions import YZ_FROM_X
from ...errors import (
    InputError, InputMissingError,
    DimensionalityError, DimensionSizeError,
    LoadingNotImplementedError,
)
from ...tools import (
    alias, alias_child, simple_property,
    xarray_isel, xarray_copy_kw,
    is_iterable,
)
from ...quantities import QuantityLoader


### --------------------- Stagger Constants --------------------- ###

XYZ_TO_INT = {'x': 0, 'y': 1, 'z': 2}
XYZ_TO_STR = {0: 'x', 1: 'y', 2: 'z', 'x': 'x', 'y': 'y', 'z': 'z'}
PAD_PERIODIC = 'wrap'     # how to pad periodic dimensions
PAD_NONPERIODIC = 'reflect'  # how to pad nonperiodic dimensions

StaggerConstants = collections.namedtuple('StaggerConstants', ('a', 'b', 'c'))

# # FIRST ORDER SCHEME # #
STAGGER_ABC_DERIV_o1 = StaggerConstants(1.0, 0, 0)
STAGGER_ABC_SHIFT_o1 = StaggerConstants(0.5, 0, 0)

# # FIFTH ORDER SCHEME # #
# derivatives
c = (-1 + (3**5 - 3) / (3**3 - 3)) / (5**5 - 5 - 5 * (3**5 - 3))
b = (-1 - 120*c) / 24
a = (1 - 3*b - 5*c)
STAGGER_ABC_DERIV_o5 = StaggerConstants(a, b, c)

# shifts (i.e. not a derivative)
c = 3.0 / 256.0
b = -25.0 / 256.0
a = 0.5 - b - c
STAGGER_ABC_SHIFT_o5 = StaggerConstants(a, b, c)

# remove temporary variables from the module namespace
del c, b, a


### --------------------- Stagger Tools --------------------- ###

def transpose_to_0(array, x):
    '''move x (int) axis to the front of array (numpy array), by swapping with 0th axis.
    
    Note this is its own inverse, i.e. transpose_to_0(transpose_to_0(array, x), x) == array.
    '''
    tup = transpose_to_0_tuple(array.ndim, x)
    return np.transpose(array, tup)

def transpose_to_0_tuple(ndim, x):
    '''return tuple to pass to np.transpose to swap axis 0 with axis x (int).

    T = np.transpose(array, result) gives array with x axis swapped with 0th axis.
    np.transpose(T, result) swaps them back.
    '''
    if x < 0:
        x = x + ndim  # e.g. (ndim=3, x=-1) --> x=2
    if x >= ndim:
        raise DimensionalityError(f'axis x={x} is out of bounds for ndim={ndim}')
    result = list(range(ndim))
    result[x] = 0
    result[0] = x
    return tuple(result)

def simple_slice(start_shift, end_shift):
    '''return slice(start_shift, end_shift), but if end_shift is 0 use None instead.'''
    return slice(start_shift, None if end_shift == 0 else end_shift)


class StaggerPrePadManager3D():
    '''manages pre-padding for stagger operations in 'x', 'y', 'z' dimensions.
    (3D stagger operations' inputs and outputs are always 3D arrays.)

    ops: str
        string of operations to do, separated by whitespace or '_'.
        each operation must be one of:
            'xup',   'xdn',   'yup',   'ydn',   'zup',   'zdn',
            'ddxup', 'ddxdn', 'ddyup', 'ddydn', 'ddzup', 'ddzdn'.
    slices: dict of indexers or None
        dict of 'x', 'y', 'z' to indexers (e.g. from a QuantityLoader).
        None --> empty dict.
    size: dict of int
        lengths of 'x', 'y', 'z' dimensions.

    calling self returns padded_slices:
        dict of 'x', 'y', 'z' slices to use to pad an array before doing this series of ops,
        such that the result will be properly aligned & shaped the same as non-staggered vars.
        Note: dims without slice will have result[dim] = None.
        dims with slice will have result[dim] =
            sum of self.PAD_AMOUNT['up' or 'dn'] for all ops with dim.
            E.g. 'xup ddxup xdn' --> result['x'] = (2,3) + (2,3) + (3,2) = (7,8).
    '''
    PAD_AMOUNT = {'up': (2,3), 'dn': (3,2)}

    def __init__(self, ops, slices=None, *, sizes):
        self.ops = ops.replace('_', ' ').split()
        self.slices = {} if slices is None else slices
        self.sizes = sizes
        self.pad_amounts = self.get_pad_amounts()
        self.modes = {}  # padding modes determined during self.get_prepad_slices(). Helps with debugging.
        self.to_squeeze_after = set()   # dims to squeeze after stagger operations are finished.

    def get_pad_amounts(self):
        '''return amounts of padding for each dim, based on ops (ignoring self.slices for now).'''
        padding = {x: (0,0) for x in ('x', 'y', 'z')}
        for op in self.ops:
            dd, x, up = re.fullmatch(r'(dd)?([xyz])(up|dn)', op).groups()
            pad_x = padding[x]
            if pad_x is not None:
                amount = self.PAD_AMOUNT[up]
                padding[x] = (pad_x[0] + amount[0],
                              pad_x[1] + amount[1])
        return padding

    def cumulative_pad_amounts(self):
        '''return amounts of padding for each dim, after each op.
        e.g. [{'x':(0,0),'y':(0,0),'z':(2,3)}, {'x':(2,3),'y':(0,0),'z':(2,3)}, ...]
        '''
        result = []
        padding = {x: (0,0) for x in ('x', 'y', 'z')}
        for op in self.ops:
            dd, x, up = re.fullmatch(r'(dd)?([xyz])(up|dn)', op).groups()
            pad_x = padding[x]
            if pad_x is not None:
                amount = self.PAD_AMOUNT[up]
                padding[x] = (pad_x[0] + amount[0],
                              pad_x[1] + amount[1])
            result.append(padding.copy())
        return result

    def get_prepad_slice(self, x):
        '''returns padded slice (or other indexer) for this dim ('x', 'y', or 'z')
        None if self.pad_amount[x] is None.
        None if self.slices[x] == slice(None).
        self.slices[x] if self.pad_amount[x] is (0,0).
        '''
        indexer = self.slices.get(x, None)
        if indexer is None:
            self.modes[x] = None
            return None
        if isinstance(indexer, slice) and indexer == slice(None):
            self.modes[x] = None
            return None
        pad_amount = self.pad_amounts[x]
        if pad_amount == (0,0):  # no ops occuring along this dim --> use original indexer.
            self.modes[x] = None
            if (not isinstance(indexer, slice)) and (not is_iterable(indexer)):  # i.e., indexer is int.
                # int indexers need to be converted to slice before stagger (can squeeze later),
                #  because stagger inputs and outputs are always 3D arrays.
                self.to_squeeze_after.add(x)  # need to squeeze this dim after stagger ops are completed.
                return slice(indexer, indexer+1)
            else:
                return indexer   # (still use original indexer though!)
        if is_iterable(indexer):
            errmsg = (f'{type(self).__name__}.get_prepad_slice(x={x!r}) with iterable indexer.\n'
                      f'Expected None, slice, or int; got {indexer}.\n'
                      '(This might be avoided if stagger_minimal_slicing=False)')
            raise NotImplementedError(errmsg)
        pad_start, pad_stop = pad_amount
        if isinstance(indexer, slice):
            start = indexer.start
            stop = indexer.stop
            step = indexer.step
            if step is None: step = 1
            if step == 1:
                self.modes[x] = 'simple_slice'
            else:
                self.modes[x] = 'step_slice'
        else:   # assume int.
            start = indexer
            stop = indexer + 1
            step = 1
            self.modes[x] = 'simple_int'
            self.to_squeeze_after.add(x)  # need to squeeze this dim after stagger ops are completed.
        # handle start & stop -- cleanup
        if x not in self.sizes:
            raise InputError(f'provided indexer for {x!r} but {x!r} not provided in self.sizes.')
        L = self.sizes[x]
        if start is None:
            start = 0
        if stop is None:
            stop = L
        if start < 0:
            start = L + start
            if start < 0:
                start = 0
        if stop < 0:
            stop = L + stop
            if stop < 0:
                stop = 0
        if start < pad_start:  # not enough room to pad easily on the left.
            errmsg = (f'{type(self).__name__}.get_prepad_slice(x={x!r}) '
                      f'when start (={start}) < pad_start (={pad_start}).\n'
                      '(This might be avoided if stagger_minimal_slicing=False)')
            raise NotImplementedError(errmsg)
        if stop > L - pad_stop:  # not enough room to pad easily on the right.
            errmsg = (f'{type(self).__name__}.get_prepad_slice(x={x!r}) '
                      f'when stop (={stop}) > len-pad_stop (={L-pad_stop}).\n'
                      '(This might be avoided if stagger_minimal_slicing=False)')
            raise NotImplementedError(errmsg)
        # handle step
        if step is None or step == 1:   # trivial step -- easy!
            start = start - pad_start
            stop = stop + pad_stop
            return slice(start, stop)
        elif step <= pad_start + pad_stop:
            errmsg = (f'{type(self).__name__}.get_prepad_slice(x={x!r}) '
                      f'when step ({step}) != 1 (or None), and step <= pad_start + pad_stop ({pad_start}+{pad_stop}).\n'
                      '(This might be avoided if stagger_minimal_slicing=False)')
            raise NotImplementedError(errmsg)
        else:   # create multiple independent regions.
            # E.g. slice(20, 41, 10), pad (2,3) --> [18,19,20,21,22,23, 28,29,30,31,32,33, 38,39,40,41,42,43]
            #  (note, slice(20, 40, 10) will exclude the 38-43 because unpadded would exclude the point at 40.)
            # for now, just use a python for loop for better readability. [TODO][EFF] if slow, improve efficiency.
            rr = range(L)
            result = []
            here = start
            while here < stop:
                region = list(rr[here - pad_start : here + pad_stop + 1])  # +1 so that here+pad_stop is included too.
                result = result + region
                here = here + step
            return result
            # note, using multiple independent regions is not particularly efficient;
            #   running it though the Staggerer will end up computing lots of meaningless values,
            #   e.g. in the example above, the result will have the values at:
            #       [20,21,22,23, 28,29,30,31,32,33, 38,39,40],
            #   and stagger_postprocess will return only the values at [20, 30, 40],
            #       since those are the values we care about.
            #   (also note, the value at 20 will be from [18,19,20,21,22,23] appropriately,
            #       however the value at 22, e.g., will be from [20,21,22,23,28,29],
            #       which isn't even the correct value at that point.)
            # however, it's definitely more efficient to do this, than to stagger the ENTIRE array,
            #   especially when step is large.
        assert False, 'coding error if reached this line.'

    __call__ = alias('get_prepad_slices')

    def get_prepad_slices(self):
        '''return padded_slices to use.
        like self.slices but with padding added to provided indexers.
        see help(type(self)) for more details.
        '''
        self.modes = {}  # <-- reset self.modes before getting all the prepad slices.
        self.to_squeeze_after = set()   # <-- reset self.to_squeeze_after, too.
        padded_slices = {}
        for x in ('x', 'y', 'z'):
            padded_x = self.get_prepad_slice(x)
            if padded_x is not None:
                padded_slices[x] = padded_x
        self._prepad_slices_result = padded_slices
        return padded_slices

    def get_prepad_dims(self):
        '''return dict of which dims are adjusted by prepadding.'''
        self.get_prepad_slices()
        modes = self.modes
        return list(x for x, mode in modes.items() if mode is not None)

    def _step_slice_unpadder_in_postprocess(self, x):
        '''unpadder for step_slice, in postprocessing.'''
        padx = self.pad_amounts[x]
        stepx = padx[0] + padx[1] + 1
        return slice(None, None, stepx)

    def stagger_postprocess(self, array):
        '''postprocessing of array after stagger ops, to deal with padding details.
        Here, does the following:
            (1) ensure that array is 3D. (probably a numpy array, but xarray is permitted too.)
            (2) if any modes are 'step_slice', slice to recover only the relevant values.
            (3) squeeze array after stagger ops, to respect any (unpadded) int indexers.
                Also asserts that dims to squeeze actually have size 1.
        '''
        # (1)
        if array.ndim != 3:
            raise DimensionalityError(f'expected 3D array; got {array.ndim}D.')
        # (2)
        if any(mode == 'step_slice' for mode in self.modes.values()):
            slices = [slice(None), slice(None), slice(None)]
            for i, x in enumerate(('x', 'y', 'z')):
                if self.modes.get(x, None) == 'step_slice':
                    slices[i] = self._step_slice_unpadder_in_postprocess(x)
            array = array[tuple(slices)]
        # (3)
        if 'z' in self.to_squeeze_after:
            if array.shape[2] != 1:
                raise DimensionSizeError(f'expected size 1 along z; got {array.shape[2]}.')
            array = array[:, :, 0]
        if 'y' in self.to_squeeze_after:
            if array.shape[1] != 1:
                raise DimensionSizeError(f'expected size 1 along y; got {array.shape[1]}.')
            array = array[:, 0]
        if 'x' in self.to_squeeze_after:
            if array.shape[0] != 1:
                raise DimensionSizeError(f'expected size 1 along x; got {array.shape[0]}.')
            array = array[0]
        return array

    def unpad1D(self, x, array):
        '''remove padding from 1D array corresponding to x dimension.
        assumes this is being called after self.get_prepad_slices()
            (i.e., expects self.modes and self.to_squeeze_after, to be set appropriately.)
        x: 'x', 'y', or 'z'.

        if self.to_squeeze_after[x], result will be a scalar instead of a 1D array.
        '''
        if array.ndim != 1:
            raise DimensionalityError(f'expected 1D array; got {array.ndim}D.')
        if x in self._prepad_slices_result:
            pad = self.pad_amounts[x]
            mode = self.modes[x]
            if mode is None:
                result = array
            elif mode == 'step_slice':
                result = array[pad[0] : -pad[1]]
                result = result[self._step_slice_unpadder_in_postprocess(x)]
            else:
                result = array if pad==(0,0) else array[pad[0] : -pad[1]]
        else:
            result = array
        if x in self.to_squeeze_after:
            if result.size != 1:
                raise DimensionSizeError(f'expected size 1; got {result.size}.')
            result = result[0]
        return result

    def xarray_copy_kw_from_unstaggered(self, unstaggered):
        '''return xarray_copy_kw(unstaggered), updated to remove padding.
        E.g.:
            staggered = stagger(unstaggered, op, pre_padded=self.get_prepad_slices())
            kw_data_array = self.xarray_copy_kw_from_unstaggered(unstaggered)
            as_data_array = xr.DataArray(staggered, **kw_data_array)
        '''
        result = xarray_copy_kw(unstaggered)
        coords = result['coords']
        dims = result['dims']
        for x in ('x', 'y', 'z'):
            if x in coords:
                coords[x] = self.unpad1D(x, coords[x])  # unpad1D also handles squeezing if needed.
        if any(x in dims for x in self.to_squeeze_after):
            result['dims'] = (x for x in dims if x not in self.to_squeeze_after)
        return result

    def op_prepad_kws(self):
        '''return list of dicts to use for stagger.do(array, op, **kw), for op in self.ops.
        [TODO] handle left_first=False.
        '''
        slices = self.get_prepad_slices()
        modes = self.modes
        padops = self.cumulative_pad_amounts()
        result = []
        for op, padop in zip(self.ops, padops):
            opresult = dict()
            dd, x, up = re.fullmatch(r'(dd)?([xyz])(up|dn)', op).groups()
            if modes.get(x, None) is not None:
                opresult['pre_padded'] = slices[x]
            if dd:
                opresult['depad_dx'] = padop[x]
            result.append(opresult)
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'ops={self.ops!r}',
                    f'slices={self.slices!r}',
                    f'sizes={self.sizes!r}',
                    f'pad_amounts={self.pad_amounts!r}',
                    f'modes={self.modes!r}'
                    ]
        return f'{type(self).__name__}({", ".join(contents)})'


### --------------------- Staggerer --------------------- ###

class Staggerer():
    '''class to do staggering along an axis.
    internally, staggering will transpose, stagger along 0th axis, then transpose back.
    
    x: int or str
        the axis to take the derivative along.
        str --> 'x', 'y', or 'z', corresponding to 0, 1, 2.
        internally stored as int.
    periodic: bool
        whether to treat the array as periodic along x.
        True --> use pad='wrap' to fill values for stagger at edges of array.
        False --> use pad='reflect' to fill values for stagger at edges of array.
    dx: None, number, or 1D array
        spacing along this axis. relevant for deriv but not shift.
        None --> deriv methods will crash.
    order: 1 or 5.
        order of the scheme to use, by default.
    mode: str
        method for stagger calculations. Right now, only supports 'numpy_improved'.
        Eventually might support 'numpy', 'numba', and 'numba_improved'.
    short_ok: bool
        whether it is okay for arrays to be too short along x axis.
        True --> if too short: for shift, return as-is; for derivative, return zeros.
        False --> if too short: raise DimensionSizeError
    assert_ndim: None or int
        if provided, assert ndim(array) equals this value, before staggering.
        e.g. if expecting all arrays to be 3D, use assert_ndim=3.
    '''
    PAD_AMOUNT = {'up': (2,3), 'dn': (3,2)}

    def __init__(self, x, *, periodic, dx=None, order=5, mode='numpy_improved',
                 short_ok=True, assert_ndim=None):
        self.x = XYZ_TO_INT.get(x, x)   # self.x is an int.
        self.xstr = XYZ_TO_STR[self.x]
        self.periodic = periodic
        self.order = order
        self.dx = dx
        self.mode = mode
        if mode != 'numpy_improved':
            raise NotImplementedError(f'mode={mode!r}. Only implemented mode="numpy_improved" so far.')
        self.short_ok = short_ok
        self.assert_ndim = assert_ndim

    # # # PROPERTIES # # #
    dx = simple_property('_dx',
            doc='''spacing along this axis. relevant for deriv but not shift.
            if None, getting self.dx will raise InputMissingError.''')
    @dx.getter
    def dx(self):
        result = getattr(self, '_dx', None)
        if result is None:
            raise InputMissingError('dx is None, but dx required for derivatives.')
        return result

    # # # SIZE CHECK # # #
    def size_x(self, array):
        '''returns size of array along x axis.'''
        return array.shape[self.x]

    def at_least_size_x(self, array, size, *, short_ok=None):
        '''returns whether array has at least this size along x axis.
        short_ok: None or bool
            whether it is okay for arrays to be too short along x axis.
            None --> use self.short_ok.
            False --> raise DimensionSizeError if too short.
        '''
        if short_ok is None:
            short_ok = self.short_ok
        size_x = self.size_x(array)
        if size_x < size:
            if short_ok:
                return False
            else:
                errmsg = f'array too short in axis {self.x}: got {size_x}; expected >= {size}.'
                raise DimensionSizeError(errmsg)
        else:
            return True

    # # # STAGGER PREP & POST # # #
    def pad(self, transposed_array, *, up):
        '''pad array along 0th axis as appropriate, to prepare it for staggering computations.
        up=True (up) or False (down)
        '''
        pad_mode = PAD_PERIODIC if self.periodic else PAD_NONPERIODIC
        pad_amount = self.PAD_AMOUNT['up' if up else 'dn']
        np_padding = [pad_amount] + [(0, 0)] * (transposed_array.ndim - 1)
        return np.pad(transposed_array, np_padding, mode=pad_mode)

    def transpose(self, array):
        '''swap axis self.x with axis 0.
        Note, this is its own inverse, i.e. transpose(transpose(array)) == array.
        '''
        return transpose_to_0(array, self.x)

    def _pre_stagger_prep(self, array, *, up, pre_padded=False):
        '''return array prepped for staggering.
        i.e., transpose to put x axis at front, then pad appropriately.
        Also ensure array ndim == self.assert_ndim if provided.

        pre_padded: None, bool, iterable, or slice
            bool(pre_padded) tells whether array has already been padded in the relevant dim.
        '''
        if self.assert_ndim is not None:
            if array.ndim != self.assert_ndim:
                errmsg = f'array ndim ({array.ndim}) != assert_ndim ({self.assert_ndim})'
                raise DimensionalityError(errmsg)
        array_transpose = self.transpose(array)
        if is_iterable(pre_padded) or bool(pre_padded):   # is_iterable checked to avoid bool(numpy array)
            return array_transpose
        else:
            return self.pad(array_transpose, up=up)

    def _post_stagger(self, array, **kw_None):
        '''return array converted back to original format, post-staggering.
        i.e., transpose to put x axis from front back to original position.
        '''
        return self.transpose(array)

    def _stagger_dx_padding(self, dx, *, up, pre_padded=False, depad_dx=None):
        '''returns dx, or dx[pre_padded][unpad] if pre_padded provided.
        unpad = depad_dx if provided, else slice to remove padding implied by self & up.
        '''
        if is_iterable(dx) and (is_iterable(pre_padded) or bool(pre_padded)):
            result = dx[pre_padded]
            if depad_dx is None:
                up = 'up' if up else 'dn'
                result = result[self.PAD_AMOUNT[up][0] : -self.PAD_AMOUNT[up][1]]
            else:
                result = result[depad_dx[0] : -depad_dx[1]]
            return result
        else:
            return dx

    # # # SHIFTS # # #
    def shift(self, array, *, up, **kw):
        '''shift array along x axis, staggering as appropriate.
        up=True (up) or False (down)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        order = self.order
        if order == 1:
            return self.shift_o1(array, up=up, **kw)
        elif order == 5:
            return self.shift_o5(array, up=up, **kw)
        else:
            raise InputError(f'order={order} not supported; must be 1 or 5')

    def shift_o1(self, array, *, up, pre_padded=False, **kw_None):
        '''first order shift, staggering up.'''
        raise NotImplementedError('[TODO]')  # could use 

    def shift_o5(self, array, *, up, pre_padded=False, **kw_None):
        '''fifth order shift, staggering as appropriate.'''
        if not self.at_least_size_x(array, 5):
            return array
        f = self._pre_stagger_prep(array, up=up, pre_padded=pre_padded)
        A, B, C = STAGGER_ABC_SHIFT_o5
        upshift = 1 if up else 0
        Pstart, Pend = self.PAD_AMOUNT['up' if up else 'dn']
        start = Pstart + upshift
        end = -Pend + upshift
        i00 = simple_slice(start + 0, end + 0)
        i1p = simple_slice(start + 1, end + 1)
        i2p = simple_slice(start + 2, end + 2)
        i1m = simple_slice(start - 1, end - 1)
        i2m = simple_slice(start - 2, end - 2)
        i3m = simple_slice(start - 3, end - 3)
        f0 = f[i00]
        out = f0 + (A * (            f[i1m]-f0) +
                    B * (f[i1p]-f0 + f[i2m]-f0) +
                    C * (f[i2p]-f0 + f[i3m]-f0))
        result = self._post_stagger(out)
        return result

    # # # DERIVATIVES # # #
    def deriv(self, array, *, up, **kw):
        '''take derivative of array along x axis, staggering as appropriate.
        up=True (up) or False (down)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        order = self.order
        if order == 1:
            return self.deriv_o1(array, up=up, **kw)
        elif order == 5:
            return self.deriv_o5(array, up=up, **kw)
        else:
            raise InputError(f'order={order} not supported; must be 1 or 5')

    def deriv_o1(self, array, *, up, pre_padded=False, depad_dx=None):
        '''first order derivative, staggering up.'''
        raise NotImplementedError('[TODO]')

    def deriv_o5(self, array, *, up, pre_padded=False, depad_dx=None):
        '''fifth order derivative, staggering as appropriate.'''
        if not self.at_least_size_x(array, 5):
            return np.zeros_like(array)
        dx = self.dx
        if 0 < np.ndim(dx) < np.ndim(array):  # add enough np.newaxis for dx dims if needed.
            dx = np.expand_dims(dx, tuple(range(np.ndim(dx), np.ndim(array))))
        dx = self._stagger_dx_padding(dx, up=up, pre_padded=pre_padded, depad_dx=depad_dx)
        f = self._pre_stagger_prep(array, up=up, pre_padded=pre_padded)
        A, B, C = STAGGER_ABC_DERIV_o5
        upshift = 1 if up else 0
        Pstart, Pend = self.PAD_AMOUNT['up' if up else 'dn']
        start = Pstart + upshift
        end = -Pend + upshift
        i00 = simple_slice(start + 0, end + 0)
        i1p = simple_slice(start + 1, end + 1)
        i2p = simple_slice(start + 2, end + 2)
        i1m = simple_slice(start - 1, end - 1)
        i2m = simple_slice(start - 2, end - 2)
        i3m = simple_slice(start - 3, end - 3)
        out = dx * (A * (f[i00] - f[i1m]) + 
                    B * (f[i1p] - f[i2m]) +
                    C * (f[i2p] - f[i3m]))
        result = self._post_stagger(out)
        return result

    # # # SHORTHANDS # # #
    def shift_up(self, array, **kw):
        '''shift array up. Equivalent: shift(array, up=True)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.shift(array, up=True, **kw)

    def shift_dn(self, array, **kw):
        '''shift array down. Equivalent: shift(array, up=False)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.shift(array, up=False, **kw)

    def deriv_up(self, array, **kw):
        '''take derivative of array up. Equivalent: deriv(array, up=True)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.deriv(array, up=True, **kw)

    def deriv_dn(self, array, **kw):
        '''take derivative of array down. Equivalent: deriv(array, up=False)'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.deriv(array, up=False, **kw)

    up = alias('shift_up')
    dn = alias('shift_dn')
    ddup = alias('deriv_up')
    dddn = alias('deriv_dn')

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'x={self.x!r}',
                    f'periodic={self.periodic}',
                    f'order={self.order}'
                    ]
        if self._dx is None:
            contents.append('dx=None')
        if self.mode != 'numpy_improved':
            contents.append(f'mode={self.mode!r}')
        return f'{type(self).__name__}({", ".join(contents)})'


### --------------------- Stagger Interface 3D --------------------- ###

class StaggerInterface3D():
    '''class to do staggering along 'x', 'y', or 'z', axes.
    Call self(array, opstr) to do the operation(s) implied by opstr (from left to right)
        E.g. self(array, 'xup ddzdn') --> shift array up x, then take z derivative down.

    periodic_x, periodix_y, periodic_z: bool
        whether to treat (unsliced) arrays as periodic along x, y, z axes.
        True --> use pad='wrap' to fill values for stagger at edges of array.
        False --> use pad='reflect' to fill values for stagger at edges of array.
    dx, dy, dz: None, number, or 1D array
        spacing along each axis. relevant for deriv but not shift.
        None --> deriv methods will crash.
    order: 1 or 5.
        order of the scheme to use, by default.
    mode: str
        method for stagger calculations. Right now, only supports 'numpy_improved'.
        Eventually might support 'numpy', 'numba', and 'numba_improved'.

    self.x, self.y, self.z store Staggerer objects for each axis.
    '''
    staggerer_cls = Staggerer
    PAD_AMOUNT = {'up': (2,3), 'dn': (3,2)}

    def __init__(self, *,
                 periodic_x, periodic_y, periodic_z,
                 dx=None, dy=None, dz=None,
                 order=5, mode='numpy_improved'):
        kw_shared = dict(order=order, mode=mode, assert_ndim=3)
        self.x = self.staggerer_cls('x', periodic=periodic_x, dx=dx, **kw_shared)
        self.y = self.staggerer_cls('y', periodic=periodic_y, dx=dy, **kw_shared)
        self.z = self.staggerer_cls('z', periodic=periodic_z, dx=dz, **kw_shared)

    # # # ALIASES - ORDER AND MODE # # #
    order = alias_child('x', 'order')
    @order.setter
    def order(self, value):
        self.x.order = value
        self.y.order = value
        self.z.order = value

    mode = alias_child('x', 'mode')
    @mode.setter
    def mode(self, value):
        self.x.mode = value
        self.y.mode = value
        self.z.mode = value

    # # # ALIASES - OPERATIONS # # #
    xup = alias_child('x', 'shift_up')
    xdn = alias_child('x', 'shift_dn')
    yup = alias_child('y', 'shift_up')
    ydn = alias_child('y', 'shift_dn')
    zup = alias_child('z', 'shift_up')
    zdn = alias_child('z', 'shift_dn')

    ddxup = alias_child('x', 'deriv_up')
    ddxdn = alias_child('x', 'deriv_dn')
    ddyup = alias_child('y', 'deriv_up')
    ddydn = alias_child('y', 'deriv_dn')
    ddzup = alias_child('z', 'deriv_up')
    ddzdn = alias_child('z', 'deriv_dn')

    # # # DO / CALL # # #
    def do(self, array, opstr, *, prepadder=None, left_first=True):
        '''do the operation(s) implied by opstr.

        opstr: str
            string of operations to do, separated by whitespace or '_'.
            each operation must be one of:
                'xup',   'xdn',   'yup',   'ydn',   'zup',   'zdn',
                'ddxup', 'ddxdn', 'ddyup', 'ddydn', 'ddzup', 'ddzdn'.
        prepadder: None or StaggerPrePadManager3D
            manages prepadding info for array.
            None --> array has not been prepadded; need to pad internally.
            else --> array has already been prepadded.
        left_first: bool
            when multiple operations, tells order in which to apply them.
            True --> apply operations from left to right.
                    E.g. 'xup ddzdn' --> first shift x up, then take z derivative down.
            False --> apply operations from right to left.
                    E.g. 'xup ddzdn' --> first take z derivative down, then shift x up.
        '''
        ops = opstr.replace('_', ' ').split()
        if not left_first:
            ops = ops[::-1]
        if prepadder is None:
            op_prepad_kws = [{} for op in ops]
        else:
            op_prepad_kws = prepadder.op_prepad_kws()
        for op, kw in zip(ops, op_prepad_kws):
            x = op.lstrip('dd')[0]  # 'x', 'y', or 'z'
            xup = getattr(self, op)  # one of the ops, e.g. self.xup or self.ddzdn
            array = xup(array, **kw)
        return array

    __call__ = alias('do')

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'periodic_x={self.x.periodic}',
                    f'periodic_y={self.y.periodic}',
                    f'periodic_z={self.z.periodic}',
                    f'order={self.order}'
                    ]
        if self.x.dx is None:
            contents.append('dx=None')
        if self.y.dx is None:
            contents.append('dy=None')
        if self.z.dx is None:
            contents.append('dz=None')
        if self.mode != 'numpy_improved':
            contents.append(f'mode={self.x.mode!r}')
        return f'{type(self).__name__}({", ".join(contents)})'


### --------------------- Stagger Interface 3D Haver --------------------- ###

class BifrostStaggerable(QuantityLoader):
    '''manages stagger stuff for BifrostCalculator'''
    stagger_interface_cls = StaggerInterface3D
    stagger_prepad_cls = StaggerPrePadManager3D

    stagger = simple_property('_stagger', setdefaultvia='_create_stagger_interface',
            doc='''stagger interface object, for doing staggering operations.
            BifrostCalculator staggers values to grid cell centers upon loading, by default.
            When all values are at cell centers, can proceed without any more staggering.
            Note: this object assumes lengths are in 'raw' units when doing derivatives.''')

    def _create_stagger_interface(self):
        '''create stagger interface based on self.params'''
        params = self.params
        kw = {}
        kw['periodic_x'] = params['periodic_x']
        kw['periodic_y'] = params['periodic_y']
        kw['periodic_z'] = params['periodic_z']
        if self.has_meshfile():
            mesh_coords = self.load_mesh_coords()
            kw['dx'] = mesh_coords['dx']
            kw['dy'] = mesh_coords['dy']
            kw['dz'] = mesh_coords['dz']
        else:
            if 'meshfile' in self.params:  # but not self.has_meshfile()
                print('warning: meshfile file does not exist',
                      f'(but meshfile param is defined in .idl file): {self.meshfile!r}.',
                      'Defaulting to dx, dy, dz from .idl file, during stagger operations.')
            kw['dx'] = params['dx']
            kw['dy'] = params['dy']
            kw['dz'] = params['dz']  # might crash... but that's ok;
            # PlasmaCalcs doesn't yet know how to handle different dz for each snapshot.
        return self.stagger_interface_cls(**kw)

    # # # BEHAVIOR ATTRS # # #
    cls_behavior_attrs.register('stagger_order', default=5)
    stagger_order = alias_child('stagger', 'order')
    cls_behavior_attrs.register('stagger_mode', default='numpy_improved')
    stagger_mode = alias_child('stagger', 'mode')

    # # # PADDING / MINIMAL SLICES # # #
    cls_behavior_attrs.register('stagger_minimal_slicing', default=False)
    stagger_minimal_slicing = simple_property('_stagger_minimal_slicing',
        setdefaultvia='_default_stagger_minimal_slicing',
        doc='''whether to use "smart" minimal slicing when getting stagger vars.
        default depends on self.maindims_full_size and DEFAULTS.ARRAY_MBYTES_MAX
            (default = True if maindims arrays smaller than 1/3rd max size, else False.)
            (eventually, might always use default=True, but currently lacking some essential features,
                like slice with step!=1. The default here disables those crashes for small enough snaps,
                but enables the far-superior efficiency of minimal slicing, for very large snaps.)

        When True, e.g. self('xup_var', slices=dict(x=slice(10, 20))
            would get prepadder for  array = self('var', slices=dict(x=slice(8, 23)),
            then self.stagger(array, 'xup', prepadder=dict(x=slice(8, 23)).
        CAUTION: calling self.stagger.do directly will not incorporate minimal slicing.
        Note: the result should be equivalent to when not using minimal slicing,
            [EFF] but using minimal slicing is much more efficient for large arrays.''')

    def _default_stagger_minimal_slicing(self):
        '''returns default value to use for stagger_minimal_slicing.
        The default is True if maindims_full_size implies arrays bigger than ARRAY_MBYTES_MAX/3.
        See help(type(self).stagger_minimal_slicing) for more details.
        '''
        size = self.maindims_full_size
        check_dtype = DEFAULTS.ARRAY_MEMORY_CHECK_DTYPE_MIN
        maindims_mbytes = size * np.dtype(check_dtype).itemsize / 1024**2
        return (maindims_mbytes > DEFAULTS.ARRAY_MBYTES_MAX / 3)

    def stagger_prepad_manager(self, ops):
        '''get stagger prepad manager to use for padding an array before doing this series of ops,
        such that the result will be properly aligned & shaped the same as non-staggered vars.
        '''
        slices = self.standardized_slices()
        sizes = self.maindims_full_sizes
        return self.stagger_prepad_cls(ops, slices=slices, sizes=sizes)

    def stagger_prepad_slices(self, ops):
        '''get self.slices to use for padding an array before doing this series of ops,
        such that the result will be properly aligned & shaped the same as non-staggered vars.
        '''
        return self.stagger_prepad_manager(ops).get_prepad_slices()

    def _stagger_direct_and_slice(self, array, ops):
        '''return result of applying these stagger ops to array, and slicing by self.slices.
        
        array: numpy array with same shape as self.maindims_full_shape
            e.g. result of np.memmap, inside the self.load_fromfile method.
        ops: str
            ops to do, separated by whitespace or '_'. Passed to stagger methods.
        '''
        if self.stagger_minimal_slicing:
            if (not self._slice_maindims_in_load_direct):
                errmsg = 'stagger_minimal_slicing=True but _slice_maindims_in_load_direct=False'
                raise LoadingNotImplementedError(errmsg)
            prepadder = self.stagger_prepad_manager(ops)
            prepad_slices = prepadder.get_prepad_slices()
            with self.using(slices=prepad_slices):
                array = self._slice_direct_numpy(array)
            result = self.stagger(array, ops, prepadder=prepadder)
            result = prepadder.stagger_postprocess(result)
        else:
            result = self.stagger(array, ops)
            result = self._slice_direct_numpy(result)
        return result

    def _staggering_minimal_slicing_with_nontrivial_step(self, ops_or_axes):
        '''returns whether self.stagger_minimal_slicing and self.slices have nontrivial step relevant to ops.
        ops_or_axes: str
            ops, separated by '_' or whitespace.
            or, string containing all relevant axes, e.g. 'xyz'.
        '''
        if not self.stagger_minimal_slicing:
            return False
        if not self.slices:
            return False
        for x in ('x', 'y', 'z'):
            if x in ops_or_axes:
                slicex = self.slices.get(x, None)
                if isinstance(slicex, slice):
                    if (slicex.step is not None) and slice.step != 1:
                        return True
                elif is_iterable(slicex):
                    return True
        return False

    # # # VARS # # #
    @known_pattern(r'((?:(?:dd)?[xyz](?:up|dn)_)+)(.+)', deps=[1])  # e.g. xup_r, ddzdn_r, yup_ddydn_n
    def get_stagger_var(self, var, *, _match=None):
        '''stagger var, shifting and/or taking derivatives, up or down, by half grid cell.
        E.g. xup_r --> shift r up along x axis.
        E.g. ddxup_r --> take x derivative of r up along x axis.

        Multiple ops can be combined, e.g. xup_ddxdn_r
            --> first shift r up along x, then take x derivative down.
        '''
        # implementation notes:
        # (?:) is syntax for a "non-capturing group" in a regular expression;
        #    the match.groups()[0] will contain a string like op1_op2_op3_...opN_.
        # grouped these together into one pattern instead of letting QuantityLoader split it up,
        #    so that chained stagger ops only require padding once, if using stagger_minimal_slicing.
        #    this is usually just for efficiency, but essential if slices have non-trivial step (!=1);
        #    because the first op would pad with iterable of indices in that case,
        #       (e.g. [18,19,20,21,22,23, 28,29,30,31,32,33, ...]),
        #    and currently there's no implementation for further padding a list like that.
        #    But, grouping into one pattern means the padding will just be larger, but only done once.

        # preprocessing bookkeeping
        ops, var = _match.groups()
        ops.rstrip('_')  # remove trailing '_'. Now ops is like, e.g., 'xup' or 'xup_ddxdn_zup_ydn' ...
        if self.stagger_minimal_slicing:
            prepadder = self.stagger_prepad_manager(ops)
            slices = prepadder.get_prepad_slices()
        else:
            prepadder = None
            slices = None
        # >> actual computations <<
        unstaggered = self(var, slices=slices, squeeze_direct=False)
        result = self.stagger(unstaggered.values, ops, prepadder=prepadder)
        # postprocessing bookkeeping
        if 'dd' in ops:  # stagger assumes raw length for dx; need to convert units.
            # divides by u('l') for each derivative op (contains 'dd') in ops.
            result = result / self.u('length', convert_from='raw')**(ops.count('dd'))
        if prepadder is None:
            copy_kw = xarray_copy_kw(unstaggered)
        else:
            copy_kw = prepadder.xarray_copy_kw_from_unstaggered(unstaggered)
            result = prepadder.stagger_postprocess(result)
        result = xr.DataArray(result, **copy_kw)
        if self.slices and not self.stagger_minimal_slicing:
            result = xarray_isel(result, self.slices)
        if self.squeeze_direct:
            result = self._squeeze_direct_result__post_slicing(result)
        return result

    @known_pattern(r'facecurl_(.+)', deps=[0])
    def get_facecurl(self, var, *, _match=None):
        '''return curl of face-centered var, staggered from cell faces to cell edges
        E.g. facecurl_B --> curl of B, staggered to cell edges:
            (ddydn_B_z - ddzdn_B_y, ddzdn_B_x - ddxdn_B_z, ddxdn_B_y - ddydn_B_x).

        Assumes, but does not check, that var is face-centered, e.g. B, u, xup_r.

        [EFF] can make more efficient, if slow; current implementation gets component twice.
        '''
        here, = _match.groups()
        curls = []
        for x in self.iter_component():
            y, z = YZ_FROM_X[x]
            ddy_vz = self(f'dd{y}dn_{here}_{z}')
            ddz_vy = self(f'dd{z}dn_{here}_{y}')
            curl_x = self.assign_component_coord(ddy_vz - ddz_vy, x)
            curls.append(curl_x)
        result = self.join_components(curls)
        return result

    @known_pattern(r'centered_facecurl_(.+)', deps=[0])
    def get_centered_facecurl(self, var, *, _match=None):
        '''return curl of face-centered var, staggered from cell faces to cell centers
        E.g. centered_facecurl_B --> curl of B, staggered to cell centers:
            at_edges = (ddydn_B_z - ddzdn_B_y, ddzdn_B_x - ddxdn_B_z, ddxdn_B_y - ddydn_B_x).
            result = (yup_zup(at_edges_x), zup_xup(at_edges_y), xup_yup(at_edges_z)).

        Assumes, but does not check, that var is face-centered, e.g. B, u, xup_r.

        [EFF] can make more efficient, if slow; current implementation gets component twice.
        '''
        here, = _match.groups()
        curls = []
        simple_mode = True
        if self.stagger_minimal_slicing:
            if self.current_n_component() == 1:
                y, z = YZ_FROM_X[self.component_list()[0]]
                relevant_axes = f'{y}{z}'
            else:
                relevant_axes = 'xyz'
            if self._staggering_minimal_slicing_with_nontrivial_step(relevant_axes):
                # need to be careful to group stagger ops.
                simple_mode = False
        if simple_mode:
            # this is what happens "usually". Easier to read. Re-uses get_facecurl logic.
            for x in self.iter_component():
                y, z = YZ_FROM_X[x]
                centered_curl_x = self(f'{y}up_{z}up_facecurl_{here}', component=x)
                curls.append(centered_curl_x)
        else:
            # explicitly group stagger ops (including from facecurl), so padding occurs only once.
            for x in self.iter_component():
                y, z = YZ_FROM_X[x]
                ddy_vz = self(f'{y}up_{z}up_dd{y}dn_{here}_{z}')
                ddz_vy = self(f'{y}up_{z}up_dd{z}dn_{here}_{y}')
                curl_x = self.assign_component_coord(ddy_vz - ddz_vy, x)
                curls.append(curl_x)
        result = self.join_components(curls)
        return result
