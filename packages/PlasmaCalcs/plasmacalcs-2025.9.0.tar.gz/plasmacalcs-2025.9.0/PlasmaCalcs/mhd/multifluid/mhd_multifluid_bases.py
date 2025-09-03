"""
File Purpose: base quantities for multifluid analysis of single-fluid mhd
"""

import xarray as xr

from ..mhd_bases import MhdBasesLoader
from ...dimensions import SINGLE_FLUID
from ...errors import (
    InputError, InputMissingError, FormulaMissingError,
)
from ...tools import (
    simple_property,
    UNSET,
)

class MhdMultifluidBasesLoader(MhdBasesLoader):
    '''base quantities for multifluid analysis of single-fluid mhd.
    if self.fluid is SINGLE_FLUID, results are equivalent to single-fluid mhd results.
    '''
    @known_var(load_across_dims=['fluid'])
    def get_q(self):
        '''charge of fluid particle. fluid.q [converted to self.units] if it exists.
        if fluid.q is None, give nan. If fluid.q does not exist, crash.
        '''
        f = self.fluid
        if hasattr(f, 'q'):
            q = f.q if f.q is None else (f.q * self.u('qe'))
            return xr.DataArray(q, attrs=self.units_meta())
        else:
            raise FormulaMissingError(f'charge q for fluid {f} without fluid.q attribute.')

    # # # BOOKKEEPING FOR VALUES WHICH ASSUME SINGLE FLUID # # #
    @known_pattern(r'(SF|SINGLE_FLUID)_(.+)',  deps=[(1, {'fluid': SINGLE_FLUID})], ignores_dims=['fluid'])
    def get_single_fluid_var(self, var, *, _match=None, **kw):
        '''SF_{var} (or SINGLE_FLUID_{var}) --> {var} using self.fluid=SINGLE_FLUID.
        (any kwargs get passed to self(var, **kw))
        '''
        _sf, here, = _match.groups()
        with self.using(fluid=SINGLE_FLUID):
            result = self(here, **kw)
        return result

    # # # NEUTRALS # # #
    @known_var(deps=['m'], ignores_dims=['fluid'], aliases=['m_n'])
    def get_m_neutral(self):
        '''mass, of a "single neutral particle". Equivalent to self('m') for neutral fluid.
        Only works if self.fluids (or self.jfluids) contains exactly 1 neutral Specie.
        '''
        return self.get_neutral('m')

    @known_var(deps=['n'], ignores_dims=['fluid'], aliases=['n_n'])
    def get_n_neutral(self):
        '''number density of neutral fluid. Equivalent to self('n') for neutral fluid.
        Only works if self.fluids (or self.jfluids) contains exactly 1 neutral Specie.
        '''
        return self.get_neutral('n')

    cls_behavior_attrs.register('assume_un', default=None)
    assume_un = simple_property('_assume_un', default=None,
        doc='''None, 'u', or xarray.DataArray to assume for u_neutral.
        value to assume for u_neutral (used when calculating u_neutral, and E_un0 if E_un0_mode=None).
        None --> cannot determine u_n (crash if trying to get it).
        'u' --> assume u_n = self('u'). Maybe reasonable for weakly-ionized plasma.
                in this case, E_un0 = E_u0, i.e. E(u=0 frame) == E(u_n=0 frame).
        xarray.DataArray --> assume these values for u_n.
                Should have 'x', 'y', 'z' components.''')

    @known_var(aliases=['u_n'])
    def get_u_neutral(self):
        '''velocity of neutral fluid. Depends on self.assume_un:
            None --> cannot get value; raise FormulaMissingError.
            'u' --> assume u_n == self('SINGLE_FLUID_u')
            else --> return self.assume_un
        '''
        assume_un = self.assume_un
        if assume_un is None:
            raise FormulaMissingError('u_neutral, when self.assume_un not provided (=None).')
        elif assume_un == 'u':
            return self('SINGLE_FLUID_u')
        else:
            return assume_un  # [TODO] handle assume_un components != self.component
