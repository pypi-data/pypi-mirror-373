"""
File Purpose: base & simple derived quantities.

The way to load BASE_QUANTS should be defined in hookups,
    as they will depend on the kind of input data being loaded.

The way to load SIMPLE_DERIVED_QUANTS is defined in this file,
    as they depend only on BASE_QUANTS.
    However, they are decently likely to be overwritten, depending on kind of input.
        E.g. Ebysus saves 'r' and 'm', not 'n'.
            Since 'n' is a base quant, EbysusCalculator needs to overwrite it anyways,
                however it will use something like n = r / m, rather than n = number density from file.
            Meanwhile, EbysusCalculator reads 'r' from file, rather than r = n * m.

Other parts of PlasmaCalcs may assume it is possible to load BASE_QUANTS and SIMPLE_DERIVED_QUANTS.
    PlasmaCalcs will fail with LoadingNotImplementedError when the way to load the quant
    hasn't been defined yet, for the kind of input data being loaded.
"""
import numpy as np

from .quantity_loader import QuantityLoader
from ..errors import LoadingNotImplementedError

# -- this dict is purely for documentation purposes, and not used by the code --
BASE_QUANTS = {
    # -- non-plasma quantities --
    'ds': 'vector(spatial scale), e.g. [dx, dy, dz]',
    # -- fluid constant quantities --
    'm': 'mass',    # of a "single particle". for protons, ~= +1 atomic mass unit
    'q': 'charge',  # of a "single particle". for protons, == +1 elementary charge
    'gamma': 'adiabatic index',
    # -- fluid quantities --
    'n': 'number density',
    'u': 'velocity',    # vector quantity (depends on self.component)
    'T': 'temperature', # "maxwellian" temperature (classical T in thermodynamics)
    'nusj': 'collision frequency',  # for a single particle of s to collide with any of j
    # -- global electromagnetic quantities --
    'E': 'electric field',
    'B': 'magnetic field',
    # -- neutral quantities --
    'm_neutral': 'mass of neutral(s)',    # of a "single particle". for Hydrogen, ~= +1 atomic mass unit
    'n_neutral': 'number density of neutral(s)',
    'u_neutral': 'velocity of neutral(s)',   # vector quantity.
    'T_neutral': 'temperature of neutral(s)',  # "maxwellian" temperature (classical T in thermodynamics)
}

# -- this dict is purely for documentation purposes, and not used by the code --
SIMPLE_DERIVED_QUANTS = {
    # -- non-E&M quantities --
    'r': 'mass density', 
    'p': 'momentum density',  # note - lowercase
    'P': 'pressure ("isotropic/maxwellian")',      # note - uppercase
    'Tjoule': 'temperature ("isotropic/maxwellian"), in energy units (multipled by kB). Joules if SI units',
    'e': 'energy density',
    'nusn': 'collision frequency with neutrals',  # for a single particle of s to collide with any neutral
    'nuns': 'collision frequency of neutrals with s',  # for a single neutral to collide with any s
    # -- E&M quantities --
    'nq': 'charge density',
    'Jf': 'current density (associated with fluid)',  # per area, e.g. A/m^2
    'J': 'total current density',  # per area, e.g. A/m^2
    'E_un0': 'electric field in the u_neutral=0 frame',
}

class AllBasesLoader(QuantityLoader):
    '''all base quantities.
    The implementation here just raises LoadingNotImplementedError, for all the BASE_QUANTS.

    Subclasses should override these methods to load the quantities as appropriate,
        probably either from a file or from calculations involving other quantities loaded from files.

    See also: BASE_QUANTS
    '''
    # # # NON-PLASMA QUANTITIES # # #
    @known_var
    def get_ds(self):
        '''vector(spatial scale), e.g. [dx, dy, dz]
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('ds')

    # # # FLUID CONSTANT QUANTITIES # # #
    @known_var
    def get_m(self):
        '''mass, of a "single particle". For protons, ~= +1 atomic mass unit.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('m')

    @known_var
    def get_q(self):
        '''charge, of a "single particle". for protons, == +1 elementary charge.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('q')

    @known_var
    def get_gamma(self):
        '''adiabatic index.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('gamma')

    # # # FLUID QUANTITIES # # #
    @known_var
    def get_n(self):
        '''number density.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('n')

    @known_var(dims=['component'])
    def get_u(self):
        '''velocity. vector quantity (result depends on self.component)
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('u')

    @known_var
    def get_T(self):
        '''temperature. "maxwellian" temperature (classical T in thermodynamics).
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('T')

    @known_var
    def get_nusj(self):
        '''collision frequency. for a single particle of s to collide with any of j.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('nusj')

    # # # GLOBAL ELECTROMAGNETIC QUANTITIES # # #
    @known_var
    def get_E(self):
        '''electric field.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('E')

    @known_var
    def get_B(self):
        '''magnetic field.
        [Not implemented for this class]
        '''
        raise LoadingNotImplementedError('B')

    # # # NEUTRAL QUANTITIES # # #
    # (since it's common for plasma codes to treat neutrals in some special way.)
    @known_var(aliases=['m_n'], ignores_dims=['fluid'])
    def get_m_neutral(self):
        '''mass, of a "single neutral particle". For Hydrogen, ~= +1 atomic mass unit.
        [Uses self.get_neutral('m') if possible, else crash. Subclass may override.]
        '''
        if hasattr(self, 'get_neutral'):  # (works if self is a FluidHaver with neutral fluids.)
            return self.get_neutral('m')
        # else, crash. provided 'm_neutral' var separately because sometimes non-FluidHavers
        #   (e.g. single-fluid mhd) might still have ideas about "what is the neutral fluid doing?".
        raise LoadingNotImplementedError('m_neutral')

    @known_var(aliases=['n_n'], ignores_dims=['fluid'])
    def get_n_neutral(self):
        '''number density of neutrals.
        [Uses self.get_neutral('n') if possible, else crash. Subclass may override.]
        '''
        if hasattr(self, 'get_neutral'):
            return self.get_neutral('n')
        raise LoadingNotImplementedError('n_neutral')

    @known_var(aliases=['u_n'], dims=['component'], ignores_dims=['fluid'])
    def get_u_neutral(self):
        '''velocity of neutrals. vector quantity (result depends on self.component)
        [Uses self.get_neutral('u') if possible, else crash. Subclass may override.]
        '''
        if hasattr(self, 'get_neutral'):
            return self.get_neutral('u')
        raise LoadingNotImplementedError('u_neutral')

    @known_var(aliases=['T_n'], ignores_dims=['fluid'])
    def get_T_neutral(self):
        '''temperature of neutrals. "maxwellian" temperature (classical T in thermodynamics).
        [Uses self.get_neutral('T') if possible, else crash. Subclass may override.]
        '''
        if hasattr(self, 'get_neutral'):
            return self.get_neutral('T')
        raise LoadingNotImplementedError('T_neutral')


class SimpleDerivedLoader(QuantityLoader):
    '''simple quantities derived from the base quantities.
    Subclasses are decently-likely to override these methods, depending on the kind of input,
        because these provide similar information to the base quantities so different kinds of input
        might save these instead of saving base quantities.
        (E.g. Ebysus saves 'r' instead of 'n', so EbysusCalculator
            will override get_r to read from file, and get_n to n = r / m.)

    See also: SIMPLE_DERIVED_QUANTS
    '''
    # # # NON-E&M QUANTITIES # # #
    @known_var(deps=['n', 'm'])
    def get_r(self):
        '''mass density. r = (n * m) = (number density * mass)'''
        return self('n') * self('m')

    @known_var(deps=['u', 'r'])
    def get_p(self):
        '''momentum density. p = (u * r) = (velocity * mass density).'''
        return self('u') * self('r')

    @known_var(deps=['n', 'Tjoule'])
    def get_P(self):
        '''pressure ("isotropic/maxwellian"). P = (n * Tjoule) = (number density * T [energy units])'''
        return self('n') * self('Tjoule')

    @known_var(deps=['T'])
    def get_Tjoule(self):
        '''temperature ("isotropic/maxwellian"), in energy units. Tjoule = kB * T.
        If using SI units, result will be in Joules.
        '''
        return self.u('kB') * self('T')

    @known_var(deps=['gamma', 'P'])
    def get_e(self):
        '''energy density. e = P / (gamma - 1) = pressure / (adiabatic index - 1)'''
        return self('P') / (self('gamma') - 1)

    @known_var(deps=['nusj'], ignores_dims=['jfluid'])
    def get_nusn(self):
        '''collision frequency. for a single particle of s to collide with any neutral.
        Computed as self('nusj', jfluid=self.jfluids.get_neutral()).
        '''
        neutral = self.jfluids.get_neutral()  # if crash, subclass should implement nusn separately.
        with self.using(jfluid=neutral):
            return self('nusj')

    @known_var(deps=['nusn', 'm/m_n', 'n/n_n'])
    def get_nuns(self):
        '''collision frequency. for a single neutral particle to collide with any s.
        nuns = nusn * (m / m_neutral) * (n / n_neutral).
        (from conservation of momentum, and summing collisional momentum transfer between species)
        '''
        return self('nusn') * self('m/m_n') * self('n/n_n')

    # # # E&M QUANTITIES # # #
    @known_var(deps=['n', 'q'])
    def get_nq(self):
        '''charge density. nq = (n * q) = (number density * charge)'''
        return self('n') * self('q')

    @known_var(deps=['nq', 'u'])
    def get_Jf(self):
        '''current density (associated with fluid). Jf = (nq * u) = (charge density * velocity)
        This is per unit area, e.g. the SI units would be Amperes / meter^2.

        (If self is not a FluidHaver, this will equal the total current density.)
        '''
        return self('nq') * self('u')

    @known_var(deps=['Jf'], ignores_dims=['fluid'])
    def get_J(self):
        '''total current density. J = sum_across_fluids(n*q*u)
        This is per unit area, e.g. the SI units would be Amperes / meter^2.
        '''
        try:
            fluids = self.fluids
        except AttributeError:
            errmsg = f'J, for object of type {type(self)} which has no .fluids attribute'
            raise LoadingNotImplementedError(errmsg) from None
        charged = fluids.charged()  # [EFF] exclude uncharged fluids, for efficiency.
        Jfs = self('Jf', fluid=charged)
        return Jfs.sum('fluid')  # [TODO] handle "only 1 fluid" case?

    @known_var(deps=['E', 'u_n'])
    def get_E_un0(self):
        '''electric field in the u_neutral=0 frame.
        Here, asserts all of self('u_n')==0, then returns self('E').
        if the assertion fails, raise NotImplementedError (expect subclass to handle it).
        '''
        if not np.all(self('u_n', component=None)==0):
            raise NotImplementedError('E_un0 implementation here assumes u_n=0')
        return self('E')


class DirectBasesLoader(AllBasesLoader, SimpleDerivedLoader):
    '''AllBasesLoader & SimpleDerivedLoader, but load_direct when available.'''
    # # # BASES # # #
    @known_var
    def get_ds(self):
        '''vector(spatial scale), e.g. [dx, dy, dz].
        The implementation here just does self.load_direct('ds').
        '''
        return self.load_direct('ds')

    @known_var
    def get_m(self):
        '''mass, of a "single particle". For protons, ~= +1 atomic mass unit.
        The implementation here just does self.load_direct('m').
        '''
        return self.load_direct('m')

    @known_var
    def get_q(self):
        '''charge, of a "single particle". for protons, == +1 elementary charge.
        The implementation here just does self.load_direct('q').
        '''
        return self.load_direct('q')

    @known_var
    def get_gamma(self):
        '''adiabatic index.
        The implementation here just does self.load_direct('gamma').
        '''
        return self.load_direct('gamma')

    @known_var
    def get_n(self):
        '''number density.
        The implementation here just does self.load_direct('n').
        '''
        return self.load_direct('n')

    @known_var
    def get_u(self):
        '''velocity (or speed, if self doesn't have vector component dimension)
        The implementation here just does self.load_direct('u').
        '''
        return self.load_direct('u')

    @known_var
    def get_T(self):
        '''temperature. "maxwellian" temperature (classical T in thermodynamics).
        The implementation here just does self.load_direct('T').
        '''
        return self.load_direct('T')

    @known_var
    def get_nusj(self):
        '''collision frequency. for a single particle of s to collide with any of j.
        The implementation here just does self.load_direct('nusj').
        '''
        return self.load_direct('nusj')

    @known_var
    def get_E(self):
        '''electric field.
        The implementation here just does self.load_direct('E').
        '''
        return self.load_direct('E')

    @known_var
    def get_B(self):
        '''magnetic field.
        The implementation here just does self.load_direct('B').
        '''
        return self.load_direct('B')

    @known_var(aliases=['m_n'])
    def get_m_neutral(self):
        '''mass, of a "single neutral particle". For Hydrogen, ~= +1 atomic mass unit.
        self.load_direct('m_neutral') if possible, else self.load_direct('m_n')
        '''
        if 'm_neutral' in self.directly_loadable_vars():
            return self.load_direct('m_neutral')
        else:
            return self.load_direct('m_n')

    @known_var(aliases=['n_n'])
    def get_n_neutral(self):
        '''number density of neutrals.
        self.load_direct('n_neutral') if possible, else self.load_direct('n_n')
        '''
        if 'n_neutral' in self.directly_loadable_vars():
            return self.load_direct('n_neutral')
        else:
            return self.load_direct('n_n')

    @known_var(aliases=['u_n'])
    def get_u_neutral(self):
        '''velocity (or speed) of neutrals.
        self.load_direct('u_neutral') if possible, else self.load_direct('u_n')
        '''
        if 'u_neutral' in self.directly_loadable_vars():
            return self.load_direct('u_neutral')
        else:
            return self.load_direct('u_n')

    @known_var(aliases=['T_n'])
    def get_T_neutral(self):
        '''temperature of neutrals. "maxwellian" temperature (classical T in thermodynamics).
        self.load_direct('T_neutral') if possible, else self.load_direct('T_n')
        '''
        if 'T_neutral' in self.directly_loadable_vars():
            return self.load_direct('T_neutral')
        else:
            return self.load_direct('T_n')

    # # # SIMPLE DERIVED # # #
    can_load_direct_r = property(lambda self: 'r' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_r', {True: [], False: ['n', 'm']})])
    def get_r(self):
        '''mass density. self.load_direct('r') if possible, else r = (n * m)'''
        if self.can_load_direct_r:
            return self.load_direct('r')
        return super().get_r()

    can_load_direct_p = property(lambda self: 'p' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_p', {True: [], False: ['u', 'r']})])
    def get_p(self):
        '''momentum density. self.load_direct('p') if possible, else p = (u * r)'''
        if self.can_load_direct_p:
            return self.load_direct('p')
        return super().get_p()

    can_load_direct_P = property(lambda self: 'P' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_P', {True: [], False: ['n', 'Tjoule']})])
    def get_P(self):
        '''pressure ("isotropic/maxwellian"). self.load_direct('P') if possible, else P = (n * Tjoule)'''
        if self.can_load_direct_P:
            return self.load_direct('P')
        return super().get_P()

    can_load_direct_Tjoule = property(lambda self: 'Tjoule' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_Tjoule', {True: [], False: ['T']})])
    def get_Tjoule(self):
        '''temperature ("isotropic/maxwellian"), in energy units.
        self.load_direct('Tjoule') if possible, else Tjoule = kB * T
        '''
        if self.can_load_direct_Tjoule:
            return self.load_direct('Tjoule')
        return super().get_Tjoule()

    can_load_direct_e = property(lambda self: 'e' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_e', {True: [], False: ['P', 'gamma']})])
    def get_e(self):
        '''energy density. self.load_direct('e') if possible, else e = P / (gamma - 1)'''
        if self.can_load_direct_e:
            return self.load_direct('e')
        return super().get_e()

    can_load_direct_nusn = property(lambda self: 'nusn' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_nusn', {True: [], False: ['nusj']})])
    def get_nusn(self):
        '''collision frequency. for a single particle of s to collide with any neutral.
        self.load_direct('nusn') if possible, else nusn = nusj(neutral)
        '''
        if self.can_load_direct_nusn:
            return self.load_direct('nusn')
        return super().get_nusn()

    can_load_direct_nq = property(lambda self: 'nq' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_nq', {True: [], False: ['n', 'q']})])
    def get_nq(self):
        '''charge density. self.load_direct('nq') if possible, else nq = (n * q)'''
        if self.can_load_direct_nq:
            return self.load_direct('nq')
        return super().get_nq()

    can_load_direct_Jf = property(lambda self: 'Jf' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_Jf', {True: [], False: ['nq', 'u']})])
    def get_Jf(self):
        '''current density (associated with fluid). self.load_direct('Jf') if possible, else Jf = (nq * u)'''
        if self.can_load_direct_Jf:
            return self.load_direct('Jf')
        return super().get_Jf()

    can_load_direct_J = property(lambda self: 'J' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_J', {True: [], False: ['Jf']})])
    def get_J(self):
        '''total current density. self.load_direct('J') if possible, else J = sum_across_fluids(n*q*u)'''
        if self.can_load_direct_J:
            return self.load_direct('J')
        return super().get_J()

    can_load_direct_E_un0 = property(lambda self: 'E_un0' in self.directly_loadable_vars())
    @known_var(attr_deps=[('can_load_direct_E_un0', {True: [], False: ['E', 'u_n']})])
    def get_E_un0(self):
        '''electric field in the u_neutral=0 frame.
        self.load_direct('E_un0') if possible, else E_un0 = E
        '''
        if self.can_load_direct_E_un0:
            return self.load_direct('E_un0')
        return super().get_E_un0()
