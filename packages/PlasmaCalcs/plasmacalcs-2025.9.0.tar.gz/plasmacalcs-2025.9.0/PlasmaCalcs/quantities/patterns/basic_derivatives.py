"""
File Purpose: derivatives (in one dimension at a time).
"""
import numpy as np
import xarray as xr

from ..quantity_loader import QuantityLoader
from ...errors import QuantCalcError, InputError
from ...tools import (
    simple_property,
    xarray_differentiate, xarray_isel, interprets_fractional_indexing,
)

DVARS = 'xyzt'  # one-letter string coordinate name options for differentiation.

class BasicDerivativeLoader(QuantityLoader):
    '''derivatives (in one dimension at a time).
    E.g. 'ddx_n' --> derivative of n with respect to x
    '''
    cls_behavior_attrs.register('deriv_before_slice', default='step')
    _VALID_DERIV_BEFORE_SLICE_MODES = (True, False, 'step')
    deriv_before_slice = simple_property('_deriv_before_slice', default='step',
        validate_from='_VALID_DERIV_BEFORE_SLICE_MODES',
        doc='''bool or 'step'. Whether to apply derivatives before any maindims slicing.
        see help(type(self).slices) for slicing details.

        True --> get derivatives before applying slices.
                E.g. if slices=dict(x=slice(10, 30, 4)), getting ddx_var,
                    would compute var across the entire domain, then ddx, then slice by x[10:30:4].
                This mode is most computationally expensive, but derivatives are trustworthy everywhere.
        'step' --> get derivatives before slicing step, but after slicing start & stop.
                E.g. if slices=dict(x=slice(10, 30, 4)), getting ddx_var,
                    would compute var from x[10] to x[30], then ddx, then slice by x[::4].
                Note: if slicing by non-slice (e.g. x=5, or y=[0, 7, 10]), apply slicing afterwards.
                This mode balances computational cost and trustworthiness;
                    derivatives are trustworthy everywhere except near slices' start & stop.
        False --> get derivatives after applying slices.
                E.g. if slices=dict(x=slice(10, 30, 4)), getting ddx_var,
                    would compute var from x[10:30:4], then ddx.
                This mode is computationally cheapest, but derivatives are least trustworthy.''')

    def _pre_and_post_deriv_slices(self, x):
        '''return slices to apply before & after differentiation. (result is a 2-tuple of dicts.)

        x: str, or list of str.
            only slices relevant to these dimensions will be adjusted.
            (e.g. there's no need to touch 'y' slices during ddx.)

        Result depends primarily on self.deriv_before_slice.
        Note if self.deriv_before_slice=False, this method just returns (self.slices, {}).
        '''
        if isinstance(x, str):
            x = [x]
        mode = self.deriv_before_slice
        if mode == 'step':  # slice steps afterwards, slice other things beforehand.
            pre = self.slices.copy()
            post = {}
            maindims_sizes = None
            for dim in x:
                if dim in pre:
                    ss = pre[dim]
                    if isinstance(ss, slice):
                        if ss.step is not None and ss.step != 1:
                            if (-1 < ss.step < 1) and ss.step != 0:  # i.e., step is fractional
                                # must interpret fractional indexing before splitting into pre & post.
                                # otherwise, e.g., if didn't do it, (0, 200, 0.1), with len=500, implies 0.1 <--> step=50;
                                # but splitting to (0, 200, None), then (None, None, 0.1), implies 0.1 <--> step=20,
                                # causing result shape to depend on deriv_before_slice mode, which is not desireable...
                                if maindims_sizes is None:
                                    maindims_sizes = self.maindims_full_sizes  # sizes without slices
                                ss = interprets_fractional_indexing(ss, maindims_sizes[dim])
                        if ss.step is not None and ss.step != 1:
                            pre[dim] = type(ss)(ss.start, ss.stop, None)
                            post[dim] = type(ss)(None, None, ss.step)
                    else:  # non-slice ss: apply it afterwards.
                        del pre[dim]
                        post[dim] = ss
        elif mode == True:  # slice everything (relevant to x) afterwards.
            pre = self.slices.copy()
            post = {}
            for dim in x:
                if dim in pre:
                    post[dim] = pre.pop(dim)
        elif mode == False:  # slice everything beforehand.
            pre = self.slices
            post = {}
        else:
            assert False, f'coding error; invalid mode ({mode!r}) should be prevented by deriv_before_slice setter.'
        return (pre, post)

    @known_pattern(fr'dd([{DVARS}])_(.+)', deps=[1])  # 'dd{x}_{var}'
    def get_derivative(self, var, *, _match=None):
        '''derivative. dd{x}_{var} --> d{var}/d{x}.
        self(var) must return an object with {x} in its coordinates.
            E.g. for x='y', self(var).coords['y'] are required.
        '''
        x, var = _match.groups()
        pre_slices, post_slices = self._pre_and_post_deriv_slices(x)
        with self.using(slices=pre_slices):
            val0 = self(var)
        result = xarray_differentiate(val0, x)
        if post_slices:
            result = xarray_isel(result, **post_slices)
        return result
