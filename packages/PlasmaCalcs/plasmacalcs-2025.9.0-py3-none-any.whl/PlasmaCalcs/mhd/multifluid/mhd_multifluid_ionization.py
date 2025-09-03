"""
File Purpose: ionization-related quantities (e.g. ionization fraction)
This includes an implementation of the saha ionization equation.
"""

import numpy as np
import xarray as xr

from .mhd_genrad_tables import GenradTableManager
from .mhd_fluids import Specie
from ..elements import Element
from ...defaults import DEFAULTS
from ...dimensions import SINGLE_FLUID
from ...errors import (
    FluidValueError, FluidKeyError,
    LoadingNotImplementedError,
)
from ...quantities import QuantityLoader
from ...tools import (
    simple_property,
    format_docstring,
    xarray_promote_dim,
)


### --------------------- Ionization Helper Methods --------------------- ###

_paramdocs_saha = {
    'ne': '''number or array
        number density of electrons.''',
    'T': '''number or array
        temperature.''',
    'xi': '''number
        first ionization potential.''',
    'g1g0': '''number
        ratio of element's g (degeneracy of states) for g1 (ions) to g0 (neutrals).''',
    'u': '''None or UnitsManager
        units to use; determines expected units system for input & output.
        Also will grab relevant physical constants (such as kB) directly from u.
        None --> make new UnitsManager with SI units.''',
    'saha_equation': ''''(n1/n0) = (1/ne) * (2.0 / lde^3) * (g1 / g0) * exp(-xi / (kB * T))
        where the terms are defined as follows:
            T : temperature
            ne: electron number density
            n1: number density of element's once-ionized ions.
            n0: number density of element's neutrals.
            g1: "degeneracy of states" for element's once-ionized ions.
            g0: "degeneracy of states" for element's neutrals.
            xi: element's first ionization energy.
            lde: electron thermal deBroglie wavelength:
                lde^2 = hplanck^2 / (2 pi me kB T)''',
}

# note: saha_n1n0 not used internally... provided for reference / possible convenience.
@format_docstring(**_paramdocs_saha)
def saha_n1n0(*, ne, T, xi, g1g0, u=None):
    '''return (n1/n0) for an element, via saha equation.

    ne: {ne}
    T: {T}
    xi: {xi}
    g1g0: {g1g0}
    u: {u}

    SAHA_EQUATION:
        {saha_equation}
    '''
    if u is None:
        u = UnitsManager()
    # [EFF] calculate (2.0 / lde^3) ignoring T, to avoid extra array multiplications.
    ldebroge_constant = 2.0 / (u('hplanck')**2 / (2 * np.pi * u('me') * u('kB')))**(3/2)
    ldebroge_factor = ldebroge_constant * T**(3/2)
    result = (ldebroge_factor / ne) * (g1g0 * np.exp(-xi / (u('kB') * T)))
    return result


### --------------------- MhdMultifluidIonizationLoader --------------------- ###

class MhdMultifluidIonizationLoader(QuantityLoader):
    '''ionization-related quantities (e.g. ionization fraction)
    Includes an implementation of the saha ionization equation.
    [TODO] include more ionization-related quantities, such as rates?
    '''
    # # # IONFRAC GENERIC / DISPATCH # # #
    cls_behavior_attrs.register('ionfrac_mode', default='best_no_radtab')
    ionfrac_mode = simple_property('_ionfrac_mode',
        default='best_no_radtab',  # because I'm not convinced radtab is any better than saha (-SE, 2025/01/31)
        validate_from='IONFRAC_MODE_OPTIONS',
        doc='''mode for calculating self('ionfrac').
        ignored when self.fluid is SINGLE_FLUID. See self.IONFRAC_MODE_OPTIONS for options.''')
    IONFRAC_MODE_OPTIONS = {
        'best': '''use 'n' if self.fluid is an ion Specie, else 'best_no_n'.''',
        'best_no_radtab': '''use 'n' if self.fluid is an ion Specie, else 'saha'.''',
        'n': '''ionfrac = n / n_elem, and fluid must be an ion Specie ([TODO] or IonMixture?).
            [EFF] use 'saha' if self.fluid ntype is 'elem' or 'saha'
                (computes saha_n1n0, and ionfrac_saha from that).
                Otherwise, directly compute nII and n_elem, and take their ratio
                (ensures consistency e.g. if nII is coming from aux not saha).''',
        'best_no_n': '''best mode without getting n directly. 'radtab' if available else 'saha'.''',
        'saha': '''use saha ionization equation to calculate ionfrac.''',
        'radtab': '''lookup from self.radtab.''',
    }

    @known_var(load_across_dims=['fluid'])
    def get_ionfrac_type(self):
        '''ionfrac_type for self.fluid; affects 'ionfrac' result.
        The output array values will each be one of:
            'SINGLE_FLUID' <--> ionfrac = ne / n.
            'n' <--> ionfrac from n / n_elem, and fluid must be an ion Specie.
            'saha' <--> ionfrac from saha equation
            'radtab' <--> ionfrac based on self.radtab table lookup
            'nan' <--> ionfrac not defined for this fluid
        '''
        f = self.fluid
        if f is SINGLE_FLUID:
            result = 'SINGLE_FLUID'
        elif f.is_electron():
            result = 'nan'
            self._handle_typevar_nan(errmsg=f"ionfrac_type, when fluid={self.fluid!r}")
        else:
            result = self.ionfrac_mode
            if result == 'best':
                if isinstance(f, Specie) and f.is_ion():
                    result = 'n'
                else:
                    result = 'best_no_n'
            if result == 'best_no_radtab':
                if isinstance(f, Specie) and f.is_ion():
                    result = 'n'
                else:
                    result = 'saha'
            if result == 'best_no_n':
                if self.radtab.neufrac_available(f):
                    result = 'radtab'
                else:
                    result = 'saha'
            if result == 'n':
                # use saha if appropriate.
                ntype = self('ntype').item()
                if ntype == 'saha':
                    result = 'saha'
        return xr.DataArray(result)

    _IONFRAC_TYPE_TO_IONFRAC_DEPS = {
        'SINGLE_FLUID': ['ne', 'SF_n'],
        'n': ['n', 'n_elem'],
        'saha': ['ionfrac_saha'],
        'radtab': ['ionfrac_radtab'],
    }
    @known_var(partition_across_dim=('fluid', 'ionfrac_type'), partition_deps='_IONFRAC_TYPE_TO_IONFRAC_DEPS')
    def get_ionfrac(self, *, ionfrac_type):
        '''ionization fraction(s) of element(s) of self.fluid
        if SINGLE_FLUID, return ne / n.
            where ne = electron number density, n = total number density for all elements, excluding electrons.
            assumes quasineutrality, and that only once-ionized ions are relevant --> sum_ions(nion) = ne.
        else if self.ionfrac_mode implies 'n', return n / n_elem.
        else if self.ionfrac_mode implies 'saha', return 1 / (1 + 1/saha_n1n0).
        else if self.ionfrac_mode implies 'radtab', return ionfrac based on self.radtab table lookup from self('T')
        '''
        if ionfrac_type == 'SINGLE_FLUID':
            if self.current_n_fluid() > 1:
                raise LoadingNotImplementedError('[TODO] get_ionfrac with multiple SINGLE_FLUID...')
            with self.using(fluid=SINGLE_FLUID):
                result = self.assign_fluid_coord(self('ne/n'), overwrite=True)
        elif ionfrac_type == 'n':
            result = self('n') / self('n_elem')
        elif ionfrac_type == 'saha':
            result = self('ionfrac_saha')
        elif ionfrac_type == 'radtab':
            result = self('ionfrac_radtab')
        elif ionfrac_type == 'nan':
            result = self('nan')
        else:
            raise LoadingNotImplementedError(f'ionfrac_type={ionfrac_type!r} not yet supported.')
        return result

    @known_var(deps=['ionfrac'])
    def get_neufrac(self):
        '''neutral fraction(s) of element(s) of self.fluid. neufrac = 1 - ionfrac.'''
        return 1 - self('ionfrac')

    @known_var(deps=['ionfrac', 'n_elem'])
    def get_nII(self):
        '''number density of once-ionized species of element(s) of self.fluid. nII = n * ionfrac
        see help(self.get_ionfrac) for more details.
        '''
        return self('n_elem') * self('ionfrac')

    @known_var(deps=['neufrac', 'n_elem'])
    def get_nI(self):
        '''number density of neutral species of element(s) of self.fluid. nI = n * neufrac == n * (1 - ionfrac)
        see help(self.get_saha_n1n0) and help(self.get_ionfrac) for more details.
        assumes only once-ionized ions are relevant (ignore twice+ ionized ions).
        '''
        return self('n_elem') * self('neufrac')

    @known_var(load_across_dims=['fluid'])
    def get_n_from_ionfrac_charge__type(self):
        '''n_from_ionfrac_charge__type for self.fluid, for inferring densities from ionization fraction.
            'I' <--> neutrals
            'II' <--> once-ionized ions
            'III+' <--> twice+ ionized ions
            'nan' <--> unknown charge, or electrons (getting ne from ionfrac not possible here).
        '''
        q = getattr(self.fluid, 'q', None)
        if (q is None) or q < 0:
            result = 'nan'
        elif q == 0:
            result = 'I'
        elif q == 1:
            result = 'II'
        else:
            assert q > 1
            result = 'III+'
        if result == 'nan':
            self._handle_typevar_nan(errmsg=f"n_from_ionfrac_charge__type, when fluid={self.fluid!r}")
        return xr.DataArray(result)

    # # # SAHA IONIZATION EQUATION # # #
    @known_var(deps=['T'])
    def get_ldebroge(self):
        '''electron thermal deBroglie wavelength.
        lde^2 = hplanck^2 / (2 pi me kB T)
        '''
        T = self('T')
        const = np.sqrt(self.u('hplanck')**2 / (2 * np.pi * self.u('me') * self.u('kB')))
        return const / np.sqrt(T)

    @known_var(deps=['SF_T'], ignores_dims=['fluid'])
    def get_saha_factor_ldebroge(self, *, _T=None):
        '''(2.0 / lde^3) for saha equation. (See help(self.get_saha_n1n0) for full saha equation.)
        [EFF] computed "efficiently", i.e. combine all constants before including T contribution.
        [EFF] for efficiency, can provide (single fluid) T if already known.
        '''
        ldebroge_constant = 2.0 / (self.u('hplanck')**2 / (2 * np.pi * self.u('me') * self.u('kB')))**(3/2)
        T = self('SF_T') if _T is None else _T
        return ldebroge_constant * T**(3/2)

    @known_var(deps=['ne', 'saha_factor_ldebroge'])
    def get_saha_factor_ldebroge_ne(self, *, _T=None):
        '''(ldebroge_factor / ne) for saha equation. (See help(self.get_saha_n1n0) for full saha equation.)
        [EFF] for efficiency, can provide (single fluid) T if already known.
        '''
        return self('saha_factor_ldebroge', _T=_T) / self('ne')

    @known_var(load_across_dims=['fluid'])
    def get_saha_g1g0(self):
        '''ratio of self.fluid element's g (degeneracy of states) for g1 (ions) to g0 (neutrals).'''
        f = self.fluid
        if f is SINGLE_FLUID:
            raise FluidValueError('get_saha_g1g0 requires self.fluid correspond to element(s), not SINGLE_FLUID.')
        elif isinstance(f, (Element, Specie)):
            return xr.DataArray(f.get_element().saha_g1g0)
        else:
            raise NotImplementedError(f'fluid of type {type(f)} not yet supported for get_saha_g1g0.')

    @known_var(load_across_dims=['fluid'], aliases=['first_ionization_energy'])
    def get_ionize_energy(self):
        '''self.fluid element's first ionization energy.'''
        f = self.fluid
        if f is SINGLE_FLUID:
            raise FluidValueError('get_ionize_energy requires self.fluid correspond to element(s), not SINGLE_FLUID.')
        elif isinstance(f, (Element, Specie)):
            return xr.DataArray(f.get_element().ionize_ev * self.u('eV'))
        else:
            raise NotImplementedError(f'fluid of type {type(f)} not yet supported for get_ionize_energy.')

    @known_var(deps=['ionize_energy', 'SF_T'])
    def get_saha_factor_exp(self, *, _T=None):
        '''exp(-xi / (kB * T)) for saha equation. (See help(self.get_saha_n1n0) for full saha equation.)
        xi = first ionization energy.
        [EFF] for efficiency, can provide (single fluid) T if already known.
        '''
        T = self('SF_T') if _T is None else _T
        return np.exp(-self('ionize_energy') / (self.u('kB') * T))

    @known_var(deps=['saha_factor_ldebroge_ne', 'saha_g1g0', 'saha_factor_exp'])
    @format_docstring(**_paramdocs_saha, sub_ntab=1)
    def get_saha_n1n0(self):
        '''(n1/n0) for an element, via saha equation:
            {saha_equation}
        '''
        T = self('T', fluid=SINGLE_FLUID)
        f_ldebroge_ne = self('saha_factor_ldebroge_ne', _T=T)
        f_g1g0 = self('saha_g1g0')
        f_exp = self('saha_factor_exp', _T=T)
        return f_ldebroge_ne * f_g1g0 * f_exp

    @known_var(deps=['saha_n1n0'])
    def get_ionfrac_saha(self):
        '''ionization fraction based on saha equation: ionfrac_saha = 1 / (1 + 1 / saha_n1n0)

        Equivalent: n1 / (n1 + n0), where n1 & n0 = number density for element's ions (n1) & neutrals (n0).
            assumes only once-ionized ions are relevant (i.e., n0 + n1 = element's total number density).
        '''
        return 1 / (1 + 1 / self('saha_n1n0'))

    @known_var(deps=['ionfrac_saha'])
    def get_neufrac_saha(self):
        '''neutral fraction based on saha ionization. neufrac_saha = 1 - ionfrac_saha.'''
        return 1 - self('ionfrac_saha')

    @known_var(deps=['ionfrac_saha', 'n_elem'], aliases=['saha_n1'])
    def get_nII_saha(self):
        '''number density of once-ionized species of element(s) of self.fluid. nII = n * ionfrac_saha
        assumes only once-ionized ions are relevant (ignore twice+ ionized ions).
        '''
        with self.using(ionfrac_mode='saha'):
            return self('nII')

    @known_var(deps=['ionfrac_saha', 'n_elem'], aliases=['saha_n0'])
    def get_nI_saha(self):
        '''number density of neutral species of element(s) of self.fluid. nI = n * (1 - ionfrac_saha)
        assumes only once-ionized ions are relevant (ignore twice+ ionized ions).
        '''
        with self.using(ionfrac_mode='saha'):
            return self('nI')

    @known_var(partition_across_dim=('fluid', 'n_from_ionfrac_charge__type'),
               partition_deps={'I': 'nI_saha', 'II': 'nII_saha', 'III+': '0', 'nan': 'nan'})
    def get_n_saha(self, *, n_from_ionfrac_charge__type):
        '''number density self.fluid, based on saha ionization.
        result depends on n_from_ionfrac_charge__type, which is based on fluid.q.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        type_to_var = {'I': 'nI_saha', 'II': 'nII_saha', 'III+': '0', 'nan': 'nan'}
        qtype = n_from_ionfrac_charge__type
        if qtype in type_to_var:
            var = type_to_var[qtype]
            return self(var)
        else:
            raise LoadingNotImplementedError(f'n_from_ionfrac_charge__type={qtype!r} not yet supported.')

    # # # GENRAD # # #
    radtab_cls = GenradTableManager  # class for making radtab during self._default_radtab()

    radtab = simple_property('_radtab', setdefaultvia='_default_radtab',
        doc='''dict-like manager for Genrad tables.
        Each table=radtab[var] should have a table.interp(values) method,
            which returns value of var given appropriate values.
            See table.invar for name of expected inputs.''')

    def _default_radtab(self):
        '''return default value of self.radtab: GenradTableManager.from_defaults().'''
        return self.radtab_cls.from_defaults()

    @known_var(deps=['SF_T'])
    def get_neufrac_radtab(self):
        '''neutral fraction based on self.radtab and self('SF_T').
        crash if radtab not applicable to all fluids in self.fluid.
        '''
        T = self('SF_T')
        elems = [f.get_element() for f in self.fluid_list()]
        for f in self.fluid_list():
            if not self.radtab.neufrac_available(f):
                available = list(self.radtab.neufrac_available().keys())
                errmsg = (f'neufrac_radtab not available for all elements in self.fluid. '
                          f'Available: {available!r}; requested: {[str(e) for e in elems]}')
                if self.call_depth > 1 and self.ionfrac_mode == 'radtab':
                    errmsg += "\nConsider using a different ionfrac_mode, e.g. 'best' or 'saha'."
                raise FluidKeyError(errmsg)
        squeeze_later = (not self.fluid_is_iterable())
        result = []
        for f in self.iter_fluid():
            neufrac = self.radtab.neufrac_table(f).interp(T)
            neufrac = self.assign_fluid_coord(neufrac, overwrite=True)
            result.append(neufrac)
        result = self.join_fluids(result)
        if squeeze_later:
            result = xarray_promote_dim(result, 'fluid').squeeze('fluid')
        return result

    @known_var(deps=['neufrac_radtab'])
    def get_ionfrac_radtab(self):
        '''ionization fraction based on self.radtab. ionfrac_radtab = 1 - neufrac_radtab.
        crash if radtab not applicable to all fluids in self.fluid.
        '''
        return 1 - self('neufrac_radtab')

    @known_var(deps=['ionfrac_radtab', 'n_elem'])
    def get_nII_radtab(self):
        '''number density of once-ionized species of element(s) of self.fluid. nII = n * ionfrac_radtab'''
        with self.using(ionfrac_mode='radtab'):
            return self('nII')

    @known_var(deps=['ionfrac_radtab', 'n_elem'])
    def get_nI_radtab(self):
        '''number density of neutral species of element(s) of self.fluid. nI = n * neufrac_radtab'''
        with self.using(ionfrac_mode='radtab'):
            return self('nI')

    @known_var(partition_across_dim=('fluid', 'n_from_ionfrac_charge__type'),
               partition_deps={'I': 'nI_radtab', 'II': 'nII_radtab', 'III+': '0', 'nan': 'nan'})
    def get_n_radtab(self, *, n_from_ionfrac_charge__type):
        '''number density self.fluid, based on self.radtab lookups of self('SF_T')
        result depends on n_from_ionfrac_charge__type, which is based on fluid.q.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        type_to_var = {'I': 'nI_radtab', 'II': 'nII_radtab', 'III+': '0', 'nan': 'nan'}
        qtype = n_from_ionfrac_charge__type
        if qtype in type_to_var:
            var = type_to_var[qtype]
            return self(var)
        else:
            raise LoadingNotImplementedError(f'n_from_ionfrac_charge__type={qtype!r} not yet supported.')
