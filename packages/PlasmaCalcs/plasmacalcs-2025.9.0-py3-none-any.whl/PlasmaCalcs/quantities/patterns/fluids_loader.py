"""
File Purpose: FluidsLoader
"""

from ..quantity_loader import QuantityLoader

from ...dimensions import ELECTRON, IONS
from ...tools import simple_property, xarray_sum, xarray_prod

class FluidsLoader(QuantityLoader):
    '''load fluid-related quantities, e.g. fluids_sum_{var}'''

    @known_pattern(r'sum_(s|fluid)_(.+)', deps=[1], reduces_dims=['fluid'])  # e.g. sum_s_n, sum_fluid_T
    def get_sum_fluid_var(self, var, *, _match=None):
        '''var summed across self.fluid. Equivalent: self(var).pc.sum('fluid').
        (if not self.fluid_is_iterable(), result numerically equivalent to self(var).)
        aliases: sum_fluid_var or sum_s_var.
        '''
        _s_or_fluid, var, = _match.groups()
        return xarray_sum(self(var), dim='fluid')
    
    @known_pattern(r'sum_fluids_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. sum_fluids_n
    def get_sum_fluids_var(self, var, *, _match=None):
        '''var summed across self.fluids. Equivalent: self(var, fluid=None).pc.sum('fluid').'''
        var, = _match.groups()
        return xarray_sum(self(var), dim='fluid')

    @known_pattern(r'sum_(j|jfluid)_(.+)', deps=[1], reduces_dims=['jfluid'])  # e.g. sum_j_n, sum_jfluid_T
    def get_sum_jfluid_var(self, var, *, _match=None):
        '''var summed across self.jfluid. Equivalent: self(var).pc.sum('jfluid').
        (if not self.jfluid_is_iterable(), result numerically equivalent to self(var).)
        aliases: sum_jfluid_var or sum_j_var.
        '''
        _j_or_jfluid, var, = _match.groups()
        return xarray_sum(self(var), dim='jfluid')

    @known_pattern(r'sum_jfluids_(.+)', deps=[0], ignores_dims=['jfluid'])  # e.g. sum_jfluids_n
    def get_sum_jfluids_var(self, var, *, _match=None):
        '''var summed across self.jfluids. Equivalent: self(var, jfluid=None).pc.sum('jfluid').'''
        var, = _match.groups()
        return xarray_sum(self(var), dim='jfluid')

    @known_pattern(r'sum_ions_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. sum_ions_n
    def get_sum_ions_var(self, var, *, _match=None):
        '''var summed across all ions in self.fluids.
        Equivalent: self(var, fluid=self.fluids.ions()).pc.sum('fluid').
        '''
        var, = _match.groups()
        return xarray_sum(self(var, fluid=self.fluids.ions()), dim='fluid')

    @known_pattern(r'sum_neutrals_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. sum_neutrals_n
    def get_sum_neutrals_var(self, var, *, _match=None):
        '''var summed across all neutrals in self.fluids.
        Equivalent: self(var, fluid=self.fluids.neutrals()).pc.sum('fluid').
        '''
        var, = _match.groups()
        return xarray_sum(self(var, fluid=self.fluids.neutrals()), dim='fluid')

    @known_pattern(r'prod_(s|fluid)_(.+)', deps=[1], reduces_dims=['fluid'])  # e.g. prod_s_n, prod_fluid_T
    def get_prod_fluid_var(self, var, *, _match=None):
        '''var prodmed across self.fluid. Equivalent: self(var).pc.prod('fluid').
        (if not self.fluid_is_iterable(), result numerically equivalent to self(var).)
        aliases: prod_fluid_var or prod_s_var.
        '''
        _s_or_fluid, var, = _match.groups()
        return xarray_prod(self(var), dim='fluid')

    @known_pattern(r'prod_fluids_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. prod_fluids_n
    def get_prod_fluids_var(self, var, *, _match=None):
        '''var prodmed across self.fluids. Equivalent: self(var, fluid=None).pc.prod('fluid').'''
        var, = _match.groups()
        return xarray_prod(self(var), dim='fluid')

    @known_pattern(r'prod_(j|jfluid)_(.+)', deps=[1], reduces_dims=['jfluid'])  # e.g. prod_j_n, prod_jfluid_T
    def get_prod_jfluid_var(self, var, *, _match=None):
        '''var prodmed across self.jfluid. Equivalent: self(var).pc.prod('jfluid').
        (if not self.jfluid_is_iterable(), result numerically equivalent to self(var).)
        aliases: prod_jfluid_var or prod_j_var.
        '''
        _j_or_jfluid, var, = _match.groups()
        return xarray_prod(self(var), dim='jfluid')

    @known_pattern(r'prod_jfluids_(.+)', deps=[0], ignores_dims=['jfluid'])  # e.g. prod_jfluids_n
    def get_prod_jfluids_var(self, var, *, _match=None):
        '''var prodmed across self.jfluids. Equivalent: self(var, jfluid=None).pc.prod('jfluid').'''
        var, = _match.groups()
        return xarray_prod(self(var), dim='jfluid')

    @known_pattern(r'prod_ions_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. prod_ions_n
    def get_prod_ions_var(self, var, *, _match=None):
        '''var prodmed across all ions in self.fluids.
        Equivalent: self(var, fluid=self.fluids.ions()).pc.prod('fluid').
        '''
        var, = _match.groups()
        return xarray_prod(self(var, fluid=self.fluids.ions()), dim='fluid')

    @known_pattern(r'prod_neutrals_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. prod_neutrals_n
    def get_prod_neutrals_var(self, var, *, _match=None):
        '''var prodmed across all neutrals in self.fluids.
        Equivalent: self(var, fluid=self.fluids.neutrals()).pc.prod('fluid').
        '''
        var, = _match.groups()
        return xarray_prod(self(var, fluid=self.fluids.neutrals()), dim='fluid')

    # # # nnefrac # # #
    @known_var(deps=['n', ('n', {'fluid': ELECTRON})])
    def get_nnefrac(self):
        '''ratio of number density to electron number density: n / ne.'''
        return self('n') / self('n', fluid=ELECTRON)

    @known_var(deps=[('nnefrac', {'fluid': IONS})], ignores_dims=['fluid'])
    def get_ionnefrac(self):
        '''ratio of n_ions / ne. Equivalent: self('nnefrac', fluid=self.fluids.ions()).'''
        return self('nnefrac', fluid=IONS)

    cls_behavior_attrs.register('nnefrac_tiny_thresh', default=0.01)
    nnefrac_tiny_thresh = simple_property('_nnefrac_tiny_thresh', default=0.01,
        doc='''threshhold for where_nnefrac_tiny and where_nnefrac_significant.
        tiny if n/ne < nnefrac_tiny_thresh, significant if n/ne >= nnefrac_tiny_thresh.''')

    @known_var(deps=['nnefrac'])
    def get_nnefrac_tiny(self):
        '''boolean array telling whether n/ne < self.nnefrac_tiny_thresh'''
        return self('nnefrac') < self.nnefrac_tiny_thresh

    @known_var(deps=['ionnefrac'])
    def get_ionnefrac_tiny(self):
        '''boolean array telling whether n_ions/ne < self.nnefrac_tiny_thresh'''
        return self('ionnefrac') < self.nnefrac_tiny_thresh

    @known_var(deps=['nnefrac_tiny'], aliases=['nnefrac_not_tiny'])
    def get_nnefrac_significant(self):
        '''boolean array telling whether n/ne >= self.nnefrac_tiny_thresh.
        Equivalent: self('not_nnefrac_tiny')
        '''
        return self('not_nnefrac_tiny')

    @known_var(deps=['ionnefrac_tiny'], aliases=['ionnefrac_not_tiny'])
    def get_ionnefrac_significant(self):
        '''boolean array telling whether n_ions/ne >= self.nnefrac_tiny_thresh.
        Equivalent: self('not_ionnefrac_tiny')
        '''
        return self('not_ionnefrac_tiny')
