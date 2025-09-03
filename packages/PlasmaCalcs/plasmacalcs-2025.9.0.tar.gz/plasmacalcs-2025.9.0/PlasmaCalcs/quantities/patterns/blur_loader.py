"""
File purpose: blur calculations (e.g. convolution with a gaussian kernel)

Futurewarning: "blur" might eventually be more generic than gaussian_filter,
    e.g. might add a blur_mode with 'gaussian' as one option,
    if there are any other good blurring methods to consider.
"""

from ..quantity_loader import QuantityLoader
from ...tools import (
    alias, simple_property,
    format_docstring,
    UNSET,
    xarray_gaussian_filter, xarray_ensure_dims,
)
from ...defaults import DEFAULTS


class BlurLoader(QuantityLoader):
    '''blur calculations (e.g. convolution with a gaussian kernel)'''
    @format_docstring(xarray_gaussian_filter_docs=xarray_gaussian_filter.__doc__, sub_ntab=2)
    def gaussian_filter(self, array, dim=UNSET, sigma=UNSET, **kw_xarray_gaussian_filter):
        '''xarray_gaussian_filter with defaults from self.blur_dims, self.blur_sigma.
        kwargs are passed to xarray_gaussian_filter.

        For convenience, docs for xarray_gaussian_filter are copied below:
        xarray_gaussian_filter_docs
        ---------------------------
            {xarray_gaussian_filter_docs}
        '''
        if dim is UNSET:
            dim = self.blur_dims
            # sets dim = existing dims only, and promotes any coords to dims if needed:
            array, dim = xarray_ensure_dims(array, dim,
                            missing_dims='ignore', return_existing_dims=True)
        if sigma is UNSET:
            sigma = self.blur_sigma
        return xarray_gaussian_filter(array, dim=dim, sigma=sigma, **kw_xarray_gaussian_filter)

    blur = alias('gaussian_filter')

    cls_behavior_attrs.register('blur_dims', getdefault=lambda ql: getattr(ql, 'maindims', []))
    @property
    def blur_dims(self):
        '''the dims over which to possibly apply blur (BlurLoader methods).
        will only blur along these dims for an array if they actually appear in the array.
        None --> use self.maindims. (this is the default.)
        '''
        if getattr(self, '_blur_dims', None) is None:
            return getattr(self, 'maindims', [])
        else:
            return self._blur_dims
    @blur_dims.setter
    def blur_dims(self, value):
        self._blur_dims = value

    cls_behavior_attrs.register('blur_sigma', default=DEFAULTS.GAUSSIAN_FILTER_SIGMA)
    blur_sigma = simple_property('_blur_sigma', setdefault=lambda: DEFAULTS.GAUSSIAN_FILTER_SIGMA,
        doc=f'''the default sigma to use for blurring calculations.
        None --> use DEFAULTS.GAUSSIAN_FILTER_SIGMA (default: {DEFAULTS.GAUSSIAN_FILTER_SIGMA})''')

    # # # LOADABLE QUANTITIES # # #
    @known_pattern(r'(blur|gaussian_filter)_(.+)', deps=[1])  # 'blur_{var}' or 'gaussian_filter_{var}'
    def get_blur(self, var, *, _match=None):
        '''gaussian_filter(var). Applied along all self.blur_dims in array.
        'blur_var' or 'gaussian_filter_var'; both are equivalent.
        '''
        _blurstr, var = _match.groups()
        array = self(var)
        return self.blur(array)

    @known_pattern(r'(blurt|gaussian_filtert)_(.+)', deps=[1])  # 'blurt_{var}' or 'gaussian_filtert_{var}'
    def get_blurt(self, var, *, _match=None):
        '''gaussian_filter(var), temporarily using self.blur_dims = ['snap']
        'blurt_var' or 'gaussian_filtert_var'; both are equivalent.
        '''
        _blurstr, var = _match.groups()
        return self(f'blur_{var}', blur_dims=['snap'])

    @known_pattern(r'(blurk|gaussian_filterk)_(.+)', deps=[1])  # 'blurk_{var}' or 'gaussian_filterk_{var}'
    def get_blurk(self, var, *, _match=None):
        '''gaussian_filter(var), temporarily using self.blur_dims = ['k_x', 'k_y', 'k_z']
        'blurk_var' or 'gaussian_filterk_var'; both are equivalent.
        '''
        _blurstr, var = _match.groups()
        return self(f'blur_{var}', blur_dims=['k_x', 'k_y', 'k_z'])
