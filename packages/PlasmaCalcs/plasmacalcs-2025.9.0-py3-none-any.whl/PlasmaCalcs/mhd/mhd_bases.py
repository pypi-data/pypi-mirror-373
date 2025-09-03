"""
File Purpose: single-fluid mhd bases loader
"""
import numpy as np

from ..defaults import DEFAULTS
from ..dimensions import SINGLE_FLUID
from ..errors import (
    FluidValueError, LoadingNotImplementedError, SetvarNotImplementedError,
    InputError, InputMissingError,
)
from ..quantities import AllBasesLoader, SimpleDerivedLoader
from ..tools import simple_property


### --------------------- MhdBasesLoader --------------------- ###

class MhdBasesLoader(AllBasesLoader, SimpleDerivedLoader):
    '''base quantities based on single-fluid mhd variables: r, e, u, and B;
        r = mass density.
            Subclass might know n (number density) and m (mass) instead,
                in which case it should override get_r, get_n and get_m.
        e = internal energy density.
            Subclass might know P (pressure) or T (temperature) instead,
                in which case it should override get_e, get_P, and get_T.
        u = velocity (vector).
            Subclass might know p (momentum density) instead,
                in which case it should override get_u and get_p.
            (Subclasses knowing u already get SimpleDerivedLoader.get_p() == u * r.)
        B = magnetic field (vector).
    '''

    # # # SINGLE FLUID MODE CHECK # # #
    @property
    def in_single_fluid_mode(self):
        '''whether self is in "single fluid mode".
        MhdCalculator is always in single-fluid mode... but subclass might not be.
        Some vars (bases especially) assume single-fluid mode, so it is good to check.
            E.g. this ensures multifluid subclasses don't do weird things by accident.
        '''
        try:
            return self.fluid is SINGLE_FLUID
        except AttributeError:  # self doesn't have 'fluid' --> definitely single fluid mode.
            return True

    def assert_single_fluid_mode(self, varname='var', *, mode='getting'):
        '''asserts that self is in single fluid mode; else crash.
        varname: str
            name of var to include in error message if crashing.
        mode: str, 'getting' or 'setting'
            determines error type & error message if crashing.
            'getting' --> FluidValueError, with error message starting like:
                "{type(self)} getting {varname} requires self.in_single_fluid_mode..."
            'setting' --> SetvarNotImplementedError, with error message starting like:
                "var={varname}, when self not in_single_fluid_mode..."

        Use for operations which directly assume single fluid mode (e.g. get_r implementation here).
        Not necessary for operations which apply regardless of number of fluids,
            E.g. n = r / m for any number of fluids, and B is always independent of fluid.
        If unsure, err on the side of caution and use this function,
            to require multifluid subclass to explicitly handle the situation else crash.
        '''
        if not self.in_single_fluid_mode:
            if mode == 'getting':
                errmsg = (f'{type(self).__name__} getting {varname!r} requires self.in_single_fluid_mode,\n'
                          f'but got self.fluid={self.fluid!r} instead of SINGLE_FLUID.')
                raise FluidValueError(errmsg)
            elif mode == 'setting':
                errmsg = (f'var={varname!r}, when self not in_single_fluid_mode;\n'
                          f'got self.fluid={self.fluid!r} instead of SINGLE_FLUID.')
                raise SetvarNotImplementedError(errmsg)
            else:
                raise InputError(f"invalid mode={mode!r}; expected 'getting' or 'setting'.")

    @known_pattern(r'(SF|SINGLE_FLUID)_(.+)', deps=[1])  # SF_{var} or SINGLE_FLUID_{var}
    def get_single_fluid_var(self, var, *, _match=None):
        '''SF_{var} (or SINGLE_FLUID_{var}) --> {var}, definitely in single fluid mode.
        crashes with FluidValueError if not self.in_single_fluid_mode.

        The implementation here just does self.assert_single_fluid_mode(),
            then returns self(var) (var from SF_var or SINGLE_FLUID_var string).
        Subclass might override to also set self.fluid = SINGLE_FLUID.
        '''
        _sf, here, = _match.groups()
        self.assert_single_fluid_mode(here)
        return self(here)

    # # # BASES # # #
    @known_var
    def get_ne(self):
        '''electron number density
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('ne')

    # # # SIMPLE DERIVED # # #
    @known_var(deps=['e', 'r'])
    def get_eperm(self):
        '''internal energy (total, not density) per unit mass. eperm = e / r.'''
        return self('e') / self('r')

    @known_var(deps=['curl_B'])
    def get_J(self):
        '''current density (without displacement current). J = curl(B) / mu0.
        Per unit area, e.g. the SI units would be Amperes / meter^2.
        '''
        return self('curl_B') / self.u('mu0')

    # # # DERIVED FROM ASSUMED ABUNDANCES # # #
    cls_behavior_attrs.register('elements')
    elements = simple_property('_elements', setdefaultvia='_get_default_elements',
        doc='''ElementList of all elements in multifluid mixture assumed from single-fluid mhd.
        Used to infer SINGLE_FLUID m.''')

    def _get_default_elements(self):
        '''default value for elements. here, just returns self.tabin.elements,
        but raises a helpful error message if self.tabin not set.
        '''
        try:
            tabin = self.tabin
        except (AttributeError, InputMissingError):
            errmsg = (f"{type(self).__name__}.elements not set, and can't get default when self.tabin missing.\n"
                      "Either set self.elements or self.tabin, to proceed.")
            raise InputMissingError(errmsg)  # not from None; we want to keep tabin error info.
        return tabin.elements

    @known_var
    def get_m(self):
        '''abundance-weighted average fluid particle mass.
        m = self.elements.mtot() * (mass of 1 atomic mass unit).
        The "abundance-weighting" is as follows:
            m = sum_x(mx ax) / sum_x(ax), where ax = nx / nH, and x is any elem from self.elements.
            note: ax is related to abundance Ax via Ax = 12 + log10(ax).
        see help(self.elements.mtot) for more details, including a proof that mtot = rtot / ntot.

        (if self.elements does not exist, this method will crash with LoadingNotImplementedError)
        '''
        self.assert_single_fluid_mode('m')
        try:
            elements = self.elements
        except AttributeError:
            errmsg = f'{type(self).__name__}.get_m() when self.elements does not exist'
            raise LoadingNotImplementedError(errmsg) from None
        return elements.mtot() * self.u('amu')

    @known_var(deps=['r', 'm'])
    def get_n(self):
        '''number density. n = (r / m) = (mass density / mass)
        (Note: for single-fluid, this excludes electron number density.)
        '''
        r = self('r')
        m = self('m')
        r = self._upcast_if_max_n_requires_float64(r)
        return r / m

    def _max_n_requires_float64(self):
        '''returns whether max supported n, in self.units unit system, is too big for float32.
        max supported n, in SI units, is DEFAULTS.MHD_MAX_SAFE_N_SI
        crash with ValueError if max supported n is too big for float64 as well.
        without this check (and conversion to float64 if needed), some n values might become inf.
        '''
        max_n = DEFAULTS.MHD_MAX_SAFE_N_SI * self.u('n', convert_from='si')
        if max_n > np.finfo(np.float32).max:
            if max_n > np.finfo(np.float64).max:
                errmsg = (f'cannot guarantee support for DEFAULTS.MHD_MAX_SAFE_N_SI,'
                          f'{DEFAULTS.MHD_MAX_SAFE_N_SI}, even using float64.')
                raise ValueError(errmsg)
            return True
        return False

    def _upcast_if_max_n_requires_float64(self, array):
        '''if max n requires float64, upcast array to float64,
        unless array's dtype was already float64 or larger (in which case, just return array).
        see self._max_n_requires_float64 for details on when max n requires float64.
        '''
        if self._max_n_requires_float64():
            if np.finfo(array.dtype).max < np.finfo(np.float64).max:
                return array.astype(np.float64)
        else:
            return array

    # # # MISC # # #
    @known_var(deps=['ne', 'SF_n'])
    def get_ionfrac(self):
        '''ionization fraction. ionfrac = ne / n (from single fluid).
        Assumes quasineutrality, and that only once-ionized ions are relevant.
        '''
        self.assert_single_fluid_mode('ionfrac')
        return self('ne') / self('SF_n')

    # # # NEUTRALS # # #
    @known_var(deps=['SF_T'], aliases=['T_n'])
    def get_T_neutral(self):
        '''temperature of neutrals; T_n = T of SINGLE_FLUID.
        (subclass might implement better T, but here assumes T_n equivalent to SF_T.)
        '''
        return self('SF_T')


    # # # --- SETTING VALUES; KNOWN SETTERS --- # # #
    # used when using set_var.

    @known_setter
    def set_r(self, value, **kw):
        '''set r to this value. r = mass density.'''
        return self.set_var_internal('r', value, ['snap', 'fluid'], **kw, ukey='mass_density')

    @known_setter
    def set_n(self, value, **kw):
        '''set n to this value. n = number density == r / m.'''
        self.assert_single_fluid_mode('n', mode='setting')
        # ^^ implementation here doesn't work for mhd multifluid densities,
        #    because the multifluid densities usually infer r from n,
        #    instead of inferring n from r like single-fluid mode does.
        r = value * self('m')
        return self.set('r', r, **kw)

    @known_setter
    def set_e(self, value, **kw):
        '''set e to this value. e = energy density.'''
        self.assert_single_fluid_mode('e', mode='setting')
        return self.set_var_internal('e', value, ['snap', 'fluid'], **kw, ukey='energy_density')

    @known_setter
    def set_eperm(self, value, **kw):
        '''set eperm to this value. eperm = internal energy per unit mass == e / r.
        Depends on the current value of r; if also setting r be sure to set r first.
        '''
        self.assert_single_fluid_mode('eperm', mode='setting')
        e = value * self('r')
        return self.set('e', e, **kw)

    @known_setter
    def set_T_fromtable(self, value, **kw):
        '''set T_fromtable to this value. T_fromtable = single fluid temperature, from er table.
        Depends on the current value of r; if also setting r be sure to set r first.
        (internally, sets eperm such that T is the given value when doing lookups.)
        '''
        with self.using(coords_units=self.coords_units_explicit, units='raw'):
            r = self('SF_r')
        eperm = self.tabin['T'].interp_inverse(value, r=r)
        with self.using(units='raw'):
            return self.set('eperm', eperm, **kw)
