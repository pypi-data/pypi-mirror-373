"""
File Purpose: loading quantities with masks
"""
import xarray as xr

from .quantity_loader import QuantityLoader
from ..errors import InputError
from ..tools import (
    simple_property,
    UNSET,
    xarray_mask, xarray_unmask, xarray_has_mask, xarray_store_mask,
)

class MaskLoader(QuantityLoader):
    '''manage masks for quantities.'''

    # # # PROPERTIES # # #
    cls_behavior_attrs.register('mask', default=None)
    cls_behavior_attrs.register('masking', default='stacked')
    cls_behavior_attrs.register('output_mask', default=False)

    @property
    def _extra_kw_for_quantity_loader_call(self):
        '''extra kwargs which can be used to set attrs self during self.__call__.
        The implementation here returns ['assert_masking'] + any values from super().
        '''
        return ['assert_masking'] + super()._extra_kw_for_quantity_loader_call

    mask = simple_property('_mask', default=None,
        doc='''None or xarray.DataArray of bools,
        if self.masking, apply mask to results (with mask dims) at top-level (call_depth=1)
            (internal calls still do full calculations, so derivatives will still work.)
        applying mask means calling self.apply_mask(result);
            masking = True or 'stacked' --> xarray_mask(result, stack=True); i.e., drops all masked points.
                        (and, result will have '_mask_stack' dimension instead of mask.dims dimensions)
            masking = 'simple' --> xarray_mask(result, stack=False); i.e., masked points just replaced by nan.
        never applies mask if self.mask = None.
        setting self.mask = value is equivalent to calling self.set_mask(value).''')
    @mask.setter
    def mask(self, value):
        '''call self.set_mask(value). Probably just sets self._mask = value.'''
        self.set_mask(value)

    masking = simple_property('_masking', default='stacked',
        doc='''how to apply self.mask to results at top level, if mask exists.
        True --> alias for 'stacked'. This is the default.
        'stacked' --> apply stacked mask to self.stack(result), dropping masked points.
        'simple' --> apply mask to result, filling masked regions with np.nan.
        False --> do not apply mask, even if self.mask exists.''')
    @masking.setter
    def masking(self, value):
        '''set self._masking = value. If value is True, set to 'stacked'.'''
        if value == True:
            value = 'stacked'
        if value not in ('stacked', 'simple', False):
            raise InputError(f'self.masking must be True, False, "stacked", or "simple", not {value!r}')
        self._masking = value

    assert_masking = simple_property('_assert_masking', default=False,
        doc='''whether to assert self.masking != False and mask is not None, when getting values.''')

    output_mask = simple_property('_output_mask', default=False,
        doc='''whether to store_mask during xarray_mask calls if self.masking.
        False --> never store mask in results
        True --> always store mask in top-level results
                (all results will be xarray.Dataset objects with '_mask' data_var)
        None --> only store mask in results which would have been Datasets anyways.''')

    def set_mask(self, mask):
        '''sets self.mask = mask, and increments self._mask_cache_state (if checks succeed).
        Also does some checks:
            - mask is None or xarray.DataArray. If None, don't do any other checks.
        Also may alter mask slightly:
            - discard non-dimension coords
        '''
        if mask is None:
            self._mask = None
        else:
            if not isinstance(mask, xr.DataArray):
                raise InputError(f'mask must be None or xarray.DataArray, not {type(mask)}')
            nondim_coords = tuple(c for c in mask.coords if mask.coords[c].ndim == 0)
            if nondim_coords:
                mask = mask.drop_vars(nondim_coords)
            self._mask = mask
        self._mask_cache_state = 1 + getattr(self, '_mask_cache_state', -1)

    # # # STACKING AND MASKING -- HOOKUP TO __call__ # # #
    def _call_postprocess_toplevel(self, result, *, var, name=UNSET, item=UNSET):
        '''additional postprocessing for self.__call__ when call_depth=1.
        called from self._call_postprocess, after doing other postprocessing, when call_depth=1.

        result: any value, probably an xarray.DataArray
            result from self.__call__, after other postprocessing.
        var, name, item: UNSET or value
            passed directly from self.__call__.
            Don't need to handle these here because self._call_postprocess will handle it.

        The implementation here applies masking, if applicable.
            see help(type(self).mask) 
        '''
        if self.assert_masking:
            if self.masking == False:
                raise ValueError('assert_masking=True, but self.masking=False')
            if self.mask is None:
                raise ValueError('assert_masking=True, but self.mask=None')
        if self.mask is not None and self.masking != False:
            result_dims = getattr(result, 'dims', [])
            if all(d in result_dims for d in self.mask.dims):
                result = self.apply_mask(result)
        return super()._call_postprocess_toplevel(result, var=var, name=name, item=item)

    # # # STACKING AND MASKING -- METHODS # # #
    def apply_mask(self, arr, masking=UNSET):
        '''apply self.mask to arr, using self.masking to determine masking.
        arr must have dims from self.mask.dims.
        masking: UNSET, bool, 'stacked', or 'simple'
            UNSET --> use self.masking.
            True --> alias for 'stacked'
            'stacked' --> apply stacked mask to self.stack(arr), dropping masked points.
            'simple' --> apply mask to arr, filling masked regions with np.nan.
        will crash with ValueError if masking corresponds to False, or if self.mask is None.
        '''
        if masking is UNSET:
            masking = self.masking
        else:
            with self.using(masking=masking):
                masking = self.masking   # handles aliasing for True appropriately.
        if masking == False:
            raise ValueError('apply_mask when masking=False')
        if self.mask is None:
            raise ValueError('apply_mask when self.mask=None')
        output_mask = self.output_mask
        if masking == 'stacked':
            return xarray_mask(arr, self.mask, stack=True, store_mask=output_mask)
        elif masking == 'simple':
            return xarray_mask(arr, self.mask, stack=False, store_mask=output_mask)
        else:
            assert False, f'coding error... invalid masking should be caught by property setter.'

    def unmask(self, arr, **kw_xarray_unmask):
        '''restore arr to the same shape as unmasked unstacked arrays. masked vals will still be np.nan.
        Equivalent: xarray_unmask(arr) if arr has '_mask' data_var, else xarray_unmask(arr, mask=self.mask)
        '''
        if xarray_has_mask(arr):
            return xarray_unmask(arr, **kw_xarray_unmask)
        else:
            return xarray_unmask(arr, mask=self.mask, **kw_xarray_unmask)

    def store_mask(self, arr):
        '''equivalent: xarray_store_mask(arr, self.mask). Also equivalent: arr.pc.store_mask(self.mask)'''
        return xarray_store_mask(arr, self.mask)

    # # # KNOWN PATTERS # # #
    @known_pattern(r'(simple_|stacked_)?mask_(.+)', deps=[1])  # mask_{var} or simple_mask_{var} or stacked_mask_{var}
    def get_mask_var(self, var, *, _match=None):
        '''mask_var --> masked version of self(var).
        mask_var and stacked_mask_var = equivalent to self(var, masking='stacked').
        simple_mask_var = equivalent to self(var, masking='simple').
        '''
        mode, here = _match.groups()
        if mode is None:
            mode = 'stacked'
        return self(here, masking=mode)
