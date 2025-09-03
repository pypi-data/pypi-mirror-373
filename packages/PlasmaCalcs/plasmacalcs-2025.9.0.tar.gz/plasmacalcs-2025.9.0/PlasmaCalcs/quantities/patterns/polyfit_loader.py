"""
File Purpose: fitting polynomials to values along a dimension.

# [TODO] write a test which compares linregt_var to ddt_var for a few vars.
#   they should be similar when data changes smoothly.
"""

from ..quantity_loader import QuantityLoader
from ...tools import (
    alias, alias_key_of,
    UNSET,
    xarray_coarsened_polyfit,
)

class PolyfitLoader(QuantityLoader):
    '''polyfit calculations. E.g. linear regression.
    For generic polyfitting see arr.polyfit or arr.pc.polyfit, where arr is an xarray.DataArray.
    '''
    # # # HELPER METHODS # # #
    def polyfit(self, array_or_var, coord, degree, window=UNSET, **kw):
        '''polyfit along coord. Might coarsen array, polyfit in each window, and concat results.

        array_or_var: xarray.DataArray, or str
            array to polyfit.
            str --> use array=self(array_or_var). (Note; **kw will NOT go to self.get(array_or_var))
        coord: str
            coordinate to polyfit along.
            If coord is not already a dimension, use array=promote_dim(array, coord).
        degree: int
            degree of polynomial to fit.
        window: UNSET, None, or int.
            UNSET --> use self.polyfit_window
            None --> don't use windowing; polyfit to the entire array along coord.
            int --> coarsen array along dim, using windows of this length,
                    then polyfit in each window, then concat results along coord.

        Pass additional kwargs to xarray_coarsened_polyfit;
            also use self.polyfit_kw as defaults (for any kwargs not provided here).

        returns an xarray.DataSet which is the result of polyfit.
        '''
        kw_use = {**self.polyfit_kw, **kw}
        window_self = kw_use.pop('window', None)
        if window is UNSET:
            window = window_self
        if isinstance(array_or_var, str):
            var = array_or_var
            array = self(var)
        else:
            array = array_or_var
        return xarray_coarsened_polyfit(array, coord, degree, window, **kw_use)

    # # # BEHAVIOR ATTRS # # #
    cls_behavior_attrs.register('polyfit_kw', default={'window': None, 'boundary': 'trim'})
    @property
    def polyfit_kw(self):
        '''kwargs to pass to self.polyfit(), other than array, coord, degree, and window.
        See polyfit_kw_key_aliases for a list of aliases to some of these kwargs, as attributes of self.

        getting self.polyfit_kw will also set keys to default values from aliases,
            e.g. polyfit_boundary has default of 'trim' --> if polyfit_kw['boundary'] not set, set it to 'trim'.
        '''
        try:
            result = self._polyfit_kw
        except AttributeError:
            result = dict()
            self._polyfit_kw = result
        if not getattr(self, '_inside_polyfit_kw_logic', False):
            with self.using(_inside_polyfit_kw_logic=True):
                for attr, key in self.polyfit_kw_key_aliases.items():
                    if key not in result:
                        val = getattr(self, attr)
                        if val is not UNSET:
                            result[key] = val
        return result
    @polyfit_kw.setter
    def polyfit_kw(self, v):
        '''set self.polyfit_kw.'''
        self._polyfit_kw = v   # defaults handled by getter.
    @polyfit_kw.deleter
    def polyfit_kw(self):
        '''delete self.polyfit_kw; restore defaults.'''
        del self._polyfit_kw   # defaults handled by getter.

    polyfit_kw_key_aliases = {  # attribute of self: key in self.polyfit_kw
            'polyfit_window': 'window',
            'polyfit_boundary': 'boundary',
            'polyfit_full': 'full',
            'polyfit_cov': 'cov',
            'polyfit_stddev': 'stddev',
            'polyfit_keep_coord': 'keep_coord',
    }

    @property
    def _extra_kw_for_quantity_loader_call(self):
        '''extra kwargs which can be used to set attrs self during self.__call__.
        The implementation here returns ['window'] + self.polyfit_kw_key_aliases.keys() + any values from super().
        '''
        # [TODO] it's a little ambiguous what will happen if user enters polyfit_kw AND a polyfit_kw_key_alias.
        return ['window'] + list(self.polyfit_kw_key_aliases.keys()) + super()._extra_kw_for_quantity_loader_call

    polyfit_window = alias_key_of('polyfit_kw', 'window', default=None,
            doc='''When polyfitting, tells window size to use for coarsening arrays before fitting.
            E.g., polyfit_window=10 --> windows of length 10, polyfit in each window, concat results.''')

    window = alias('polyfit_window')  # deprecation warning: might become more generic than polyfit_window.

    polyfit_boundary = alias_key_of('polyfit_kw', 'boundary', default='trim',
            doc='''alias to self.polyfit_kw['boundary'].
            When polyfitting, tells how to handle boundaries when coarsening array.
            probably 'exact', 'trim', or 'pad'.''')

    polyfit_full = alias_key_of('polyfit_kw', 'full', default=UNSET,
            doc='''alias to self.polyfit_kw['full'].
            When polyfitting, tells whether to also return residuals, matrix rank and singular values.''')

    polyfit_cov = alias_key_of('polyfit_kw', 'cov', default=UNSET,
            doc='''alias to self.polyfit_kw['cov'].
            When polyfitting, tells whether to also return the covariance matrix.
            only used if self.polyfit_full=False.''')

    polyfit_stddev = alias_key_of('polyfit_kw', 'stddev', default=UNSET,
            doc='''alias to self.polyfit_kw['stddev'].
            When polyfitting, tells whether to also return the standard deviations of the coefficients.
            incompatible with self.polyfit_full=True.''')

    polyfit_keep_coord = alias_key_of('polyfit_kw', 'keep_coord', default=UNSET,
            doc='''alias to self.polyfit_kw['keep_coord'].
            When polyfitting, tells whether to keep some of the original coord values in result.
            probably 'left', 'middle', 'right', or False.''')

    # # # LOADABLE QUANTITIES # # #
    @known_pattern(r'linregt_(.+)', deps=[0], reduces_dims=['snap'])
    def get_linregt(self, var, *, _match=None):
        '''linear regression along 't' coord. result is an xarray.DataSet including 'polyfit_coefficients'.
        Equivalent to self.polyfit(var, 't', degree=1).

        behavior affected by self.polyfit_kw; see help(type(self).polyfit_kw) for details.
        '''
        here, = _match.groups()
        array = self(here)
        return self.polyfit(array, 't', degree=1)

    @known_pattern(r'slopet_(.+)', deps=[{0: 'linregt_{group0}'}])
    def get_slopet(self, var, *, _match=None):
        '''slope calculated from linear regression along 't' coord.
        self('slopet_var') == self('linregt_var)['polyfit_coefficients'].sel(degree=1).drop_vars('degree')

        behavior affected by self.polyfit_kw; see help(type(self).polyfit_kw) for details.
        '''
        here, = _match.groups()
        linregt = self(f'linregt_{here}')
        return linregt['polyfit_coefficients'].sel(degree=1).drop_vars('degree')  # don't keep the 'degree' coordinate.

    @known_pattern(r'growthrate_(.+)', deps=[{0: 'slopet_ln_abs_{group0}'}])
    def get_growthrate(self, var, *, _match=None):
        '''self('growthrate_var') --> exponential growth rate of var. i.e., slope of ln|var| vs 't'.
        self('growthrate_var') == self('slopet_ln_abs_var').

        behavior affected by self.polyfit_kw; see help(type(self).polyfit_kw) for details.
        '''
        here, = _match.groups()
        return self(f'slopet_ln_abs_{here}')

    @known_pattern(r'growth(_vs_)?k_(.+)', deps=[{1: 'growthrate_radfft_{group1}'}])
    def get_growthk(self, var, *, _match=None):
        '''self('growthk_var') --> exponential growth rate of radfft_var.
        i.e. for each k, gives slope of ln|radfft_var| vs 't'.
        self('growthk_var') == self('growthrate_radfft_var').
        
        Accepts strings starting with 'growth_vs_k_' or 'growthk_'.
        behavior affected by self.polyfit_kw; see help(type(self).polyfit_kw) for details.

        Assumes, but does not check, that fft_dims are spatial, only.
        '''
        _vs_str, here, = _match.groups()
        return self(f'growthrate_radfft_{here}')

    @known_pattern(r'growthfit_(.+)', deps=[{0: 'linregt_ln_abs_{group0}'}])
    def get_growthfit(self, var, *, _match=None):
        '''self('growthfit_var') --> linear regression along 't' coord, of ln|var|.

        result['polyfit_coefficients'].sel(degree=1).drop_vars('degree') gives the growth rate,
            because growth rate = slope of natural log of |var| vs 't'.

        result might also contain other variables, depending on self.polyfit_kw;
            might want to use polyfit_stddev=True, polyfit_cov=True or polyfit_full=True to get more info.
            see help(type(self).polyfit_kw) for more options.
        '''
        here, = _match.groups()
        return self(f'linregt_ln_abs_{here}')

    @known_pattern(r'growthfit(_vs_)?k_(.+)', deps=[{1: 'growthfit_radfft_{group1}'}])
    def get_growthfitk(self, var, *, _match=None):
        '''self('growthfitk_var') --> linear regression along 't' coord, of ln|radfft_var|.
        
        result['polyfit_coefficients'].sel(degree=1).drop_vars('degree') gives the growth rate,
            because growth rate = slope of natural log of |var| vs 't'.

        result might also contain other variables, depending on self.polyfit_kw;
            might want to use polyfit_stddev=True, polyfit_cov=True or polyfit_full=True to get more info.
            see help(type(self).polyfit_kw) for more options.

        Assumes, but does not check, that fft_dims are spatial, only.
        '''
        _vs_str, here, = _match.groups()
        return self(f'growthfit_radfft_{here}')
