"""
File Purpose: collision frequency calculations
"""
import numpy as np
import xarray as xr

from .collisions_cross_sections_loader import CollisionsCrossSectionsLoader
from ...errors import (
    QuantInfoMissingError, CollisionsModeError,
    FluidValueError,
)
from ...tools import simple_property, UNSET
from ...defaults import DEFAULTS


class CollisionsLoader(CollisionsCrossSectionsLoader):
    '''collision frequency calculations, for collisions related to momentum / energy transfer.
    (Collisions between the same species, e.g. electron-electron or proton-proton, are assumed to be 0)'''
    cls_behavior_attrs.register('collisions_mode', default='best')

    COLLISIONS_MODE_OPTIONS = {
        'best':
            '''Use coulomb for charge-charge, fromtable if table exists, maxwell otherwise.
            For charge-neutral, if table doesn't exist, self('collisions_cross_section') will give 0.''',
        'table':
            '''Use coulomb for charge-charge, else fromtable.
            For charge-neutral, if table doesn't exist, raise QuantInfoMissingError.''',
        'maxwell':
            '''Use coulomb for charge-charge, maxwell otherwise.
            Does not affect collisions_cross_section.''',
        'neutral_only':
            '''Use 0 for charge-charge, fromtable if table exists, maxwell otherwise.
            For charge-neutral, if table doesn't exist, self('collisions_cross_section') will give 0.''',
        'table_only':
            '''Use 0 for charge-charge, else fromtable.
            For charge-neutral, if table doesn't exist, raise QuantInfoMissingError.''',
    }

    collisions_mode = simple_property('_collisions_mode', default='best', validate_from='COLLISIONS_MODE_OPTIONS',
        doc='''str, the collisions mode to use when getting nusj. See COLLISIONS_MODE_OPTIONS for details.
        Note that you can always calculate collisions using a specific formula with the appropriate var,
            regardless of collisions_mode; e.g., nusj_maxwell will always use maxwell formula.''')

    # # # ALL COLLISIONS (DISPATCHER) # # #
    @known_var(load_across_dims=['fluid', 'jfluid'])
    def get_collision_type(self):
        '''collision type between self.fluid and self.jfluid.
        result depends on fluids and on self.collisions_mode.
            '0' <--> fluid and jfluid are the same fluid.
            'coulomb' <--> do coulomb collisions
            'maxwell' <--> do maxwell collisions
            'fromtable' <--> get collision cross section from a table
        '''
        fs = self.fluid
        fj = self.jfluid
        mode = self.collisions_mode
        if fs == fj:  # same-same collisions
            result = '0'
        # hard-code the options list here in case subclass provides more keys in COLLISIONS_MODE_OPTIONS;
        # the implementation below assumes collisions_mode is one of these 5 options.
        elif mode not in ('best', 'table', 'maxwell', 'neutral_only', 'table_only'):
            errmsg = f'{type(self).__name__}.get_collision_type not implemented when collisions_mode = {mode!r}'
            raise CollisionsModeError(errmsg)
        elif fs.q != 0 and fj.q != 0:  # coulomb collisions
            if mode in ('neutral_only', 'table_only'):
                result = '0'
            else:
                result = 'coulomb'
        else:  # charge-neutral or neutral-neutral collisions.
            if mode in ('table', 'table_only'):
                result = 'fromtable'
            elif mode == 'maxwell':
                result = 'maxwell'
            else:
                assert mode in ('best', 'neutral_only')
                table_exists = ((fs, fj) in self.collisions_cross_mapping)
                if table_exists:
                    result = 'fromtable'
                else:
                    result = 'maxwell'
        return xr.DataArray(result)

    COLLISION_TYPE_TO_VAR = {  # used in self.get_nusj.
        # Subclasses might copy this dict and update it with more types.
        '0': '0',
        'coulomb': 'nusj_coulomb',
        'maxwell': 'nusj_maxwell',
        'fromtable': 'nusj_fromtable'
    }

    @known_var(partition_across_dim=('fluid', 'collision_type'), partition_deps='COLLISION_TYPE_TO_VAR')
    def get__nusj_singlej(self, *, collision_type):
        '''_nusj_singlej = collision frequency between self.fluid and a single jfluid.
        Implementation detail... may be removed later. Use self('nusj') instead.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.jfluid_is_iterable():
            raise FluidValueError('get__nusj_singlej should only be used for a single jfluid.')
        try:
            var = self.COLLISION_TYPE_TO_VAR[collision_type]
        except KeyError:
            raise ValueError(f'unknown collision_type: {collision_type!r}')
        else:
            return self(var)

    @known_var(load_across_dims=['jfluid'], deps=['_nusj_singlej'])
    def get_nusj(self):
        '''collision frequency.
        "frequency for one particle of s (self.fluid) to collide with any of j (self.jfluid)."
        Uses the appropriate formula based on self.collisions_mode, and self.fluid & self.jfluid.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self('_nusj_singlej')

    @known_var(load_across_dims=['jfluid'], deps=['_nusj_singlej'])
    def get_nusj_best(self):
        '''collision frequency, using self.collisions_mode='best'.
        "frequency for one particle of s (self.fluid) to collide with any of j (self.jfluid)."
        Uses the appropriate formula based on self.fluid & self.jfluid.
        Use coulomb for charge-charge, fromtable if table exists, maxwell otherwise.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self('_nusj_singlej', collisions_mode='best')

    # # # COULOMB COLLISIONS # # #
    @known_var(deps=['T', 'n'])
    def get_coulomb_logarithm(self):
        '''Coulomb logarithm, ln(Lambda). Used in coulomb collisions.
        result = ln(Lambda) = 23.0 + 1.5 ln(Te [K] / 10^6) - 0.5 ln(ne [m^-3] / 10^12)
        '''
        electron = self.fluids.get_electron()  # get the one and only electron fluid.
        with self.using(fluid=electron, units='si'):
            T = self('T')
            ne = self('n')
        return 23.0 + 1.5 * np.log(T / 1e6) - 0.5 * np.log(ne / 1e12)

    @known_var(aliases=['nusj_cl'], deps=['coulomb_logarithm', 'T', 'm', 'q', 'n', 'm_sj', 'T_sj', 'delta_sj'])
    def get_nusj_coulomb(self):
        '''coulomb collision frequency.
        "frequency for one particle of s (self.fluid) to collide with any of j (self.jfluid)."
        This is a good model for nusj when:
            - s & j are both charged species.

        nusj_coulomb = (1 Hz) * (1.7/20) * (ln(Lambda))
                        * (m_p/m_s) * (m_sj/m_p)^(1/2)
                        * (T_sj / Kelvin)^(-3/2)
                        * (q_s/q_e)^2 * (q_j/q_e)^2
                        * (n_j / (10^6 meters^-3)), where:
            ln(Lambda) = Coulomb logarithm (see self.help('coulomb_logarithm') for details)
            n_j = number density of j (self.jfluid).
            m_sj = weighted mass = m_s * m_j / (m_s + m_j)
            T_sj = mass-weighted temperature = (m_s * T_j + m_j * T_s) / (m_s + m_j)
            m_p = mass of proton
            q_e = charge of electron
            m_s, m_j = mass of s, j
            T_s, T_j = temperature of s, j.
            q_s, q_j = charge of s, j
        '''
        logcoul = self('coulomb_logarithm')  # [dimensionless]
        m_p = self.u('m_p', 'si')
        q_e = self.u('q_e', 'si')
        with self.using(units='si'):
            m_s = self('m')
            q_s = self('q')
            T_s = self('T')
            m_j = self.getj('m')
            q_j = self.getj('q')
            T_j = self.getj('T')
            n_j = self.getj('n')
        m_sj = self('m_sj', _m_s=m_s, _m_j=m_j)
        T_sj = self('T_sj', _m_s=m_s, _T_s=T_s, _m_j=m_j, _T_j=T_j)
        Z_s = q_s / q_e
        Z_j = q_j / q_e
        result_si = (1.7 / 20) * logcoul * \
                    (m_p / m_s) * np.sqrt(m_sj / m_p) * \
                    T_sj**(-3/2) * \
                    Z_s**2 * Z_j**2 * \
                    (n_j / 1e6)
        result = result_si * self.u('Hz', self.units, convert_from='si')
        result = result * (1 - self('delta_sj'))   # exclude same-same collisions
        return result

    # # # MAXWELL COLLISIONS # # #
    @known_var(aliases=['nusj_mx'], deps=['m', 'n', 'delta_sj'])
    def get_nusj_maxwell(self):
        '''maxwell collision frequency.
        "frequency for one particle of s (self.fluid) to collide with any of j (self.jfluid)."
        This is a good model for nusj when:
            - s or j is neutral hydrogen.
                (assumed by the implementation here; could be improved in the future)
            - the charged species is a heavy ion.
                (collisions between [e-,H] and [H+,H] behave differently.)

        nusj_maxwell = (1 Hz) * (1.95856) * n_j * sqrt(
                        (alpha_n * q_e^2 / eps0) * (m_j / (m_s * (m_s + m_j)))
                        ), where:
            n_j = number density of j [si units, i.e. meters^-3]
            alpha_n = polarizability of neutral hydrogen. [si units, i.e. meters^3]
            q_e = charge of electron. [si units, i.e. C]
            eps0 = permittivity of free space; standard definition for eps0. [si units]
            m_s, m_j = mass of s, j. [si units, i.e. kg]

        (formula from Oppenheim+2020, Appendix A.)
        '''
        ## constants. 
        CONST_MULT = 1.95856  # factor in front.
        CONST_ALPHA_N = 6.67e-31  # [m^3]    #polarizability for Hydrogen   #(should be different for different species)
        qe = self.u('qe', 'si')    # [C]
        eps0 = self.u('eps0', 'si')  # [kg^-1 m^-3 s^4 (C^2 s^-2)] #epsilon0, standard definition
        amu = self.u('amu', 'si')   # [kg]   one atomic mass unit, in kg
        CONST_RATIO = (qe / amu) * (qe / eps0) * CONST_ALPHA_N   # [s^-2]   # parenthesis to avoid floating point errors
        # -- units of CONST_RATIO: [C^2 kg^-1 [eps0]^-1 m^3] == [C^2 kg^-1 (kg^1 m^3 s^-2 C^-2) m^-3] == [s^-2]
        ## values of other variables in formula
        with self.using(units='si'):
            m_s = self('m') / amu    # [amu]; mass of species s in amu
            m_j = self.getj('m') / amu   # [amu]; mass of species j in amu
            n_j = self.getj('n')
        ## the actual calculation
        result_si = CONST_MULT * n_j * np.sqrt(CONST_RATIO * m_j / (m_s * (m_s + m_j)))
        result = result_si * self.u('Hz', self.units, convert_from='si')
        result = result * (1 - self('delta_sj'))   # exclude same-same collisions
        return result

    # # # FROMTABLE COLLISIONS (i.e., cross section from a table) # # #
    @known_var(deps=['collisions_cross_section', 'T', 'm', 'n', 'm_sj', 'T_sj', 'delta_sj'])
    def get_nusj_fromtable(self):
        '''collision frequency from a table.
        "frequency for one particle of s (self.fluid) to collide with any of j (self.jfluid)."
        Requires that the relevant CrossTable(s) are provided, in self.collisions_cross_mapping.
        
        nusj_fromtable = n_j * (m_j / (m_s + m_j)) * C(T_sj) * sqrt(8 * kB * T_sj / (pi * m_sj)), where:
            n_j = number density of j (self.jfluid)
            m_sj = weighted mass = m_s * m_j / (m_s + m_j)
            T_sj = mass-weighted temperature = (m_s * T_j + m_j * T_s) / (m_s + m_j)
            m_s, m_j = mass of s, j
            T_s, T_j = temperature of s, j
            C(T_sj) = collisions_cross_section between s & j at temperature T_sj
            kB = Boltzmann constant
        '''
        cross = self('collisions_cross_section')
        m_s = self('m')
        T_s = self('T')
        m_j = self.getj('m')
        T_j = self.getj('T')
        n_j = self.getj('n')
        m_sj = self('m_sj', _m_s=m_s, _m_j=m_j)
        T_sj = self('T_sj', _m_s=m_s, _T_s=T_s, _m_j=m_j, _T_j=T_j)
        Tsj_speed = np.sqrt((8 * self.u('kB')/(np.pi * m_sj)) * T_sj)
        result = n_j * (m_j / (m_s + m_j)) * cross * Tsj_speed
        return result

    def _handle_missing_collisions_crosstab(self):
        '''handles the case of a missing collisions cross table between self.fluid & self.jfluid.
        depending on self.collisions_mode, this either returns 0, or raises a QuantInfoMissingError
        see self.COLLISIONS_MODE_OPTIONS for details.
        '''
        mode = self.collisions_mode
        RETURN_0_OPTIONS = ('best', 'neutral_only')
        RAISE_ERROR_OPTIONS = ('table', 'table_only', 'maxwell')
        if mode in RETURN_0_OPTIONS:
            return self('0')   # 0, as an xarray
        elif mode in RAISE_ERROR_OPTIONS:
            errmsg = ('missing a required cross table. This error can be fixed via set_collisions_crosstab,\n'
                     f'or ignored by switching collisions_mode from {mode!r} to one of {RETURN_0_OPTIONS}.')
            raise QuantInfoMissingError(errmsg)
        else:
            raise CollisionsModeError(f'unknown collisions_mode: {mode!r}')

    # # # COLLISIONS HELPER VARS # # #
    @known_var(deps=['m'])
    def get_m_sj(self, *, _m_s=UNSET, _m_j=UNSET):
        '''weighted mass. m_sj = m_s * m_j / (m_s + m_j).
        s = self.fluid; j = self.jfluid.
        [EFF] for efficiency, can provide m_s and/or m_j, if already known.
        '''
        m_s = self('m') if _m_s is UNSET else _m_s
        m_j = self.getj('m') if _m_j is UNSET else _m_j
        # parenthesis to avoid floating point errors:
        m_sum = m_s + m_j
        m_sj = m_s * (m_j / m_sum)
        return m_sj

    @known_var(deps=['m', 'T'])
    def get_T_sj(self, *, _m_s=UNSET, _T_s=UNSET, _m_j=UNSET, _T_j=UNSET):
        '''mass-weighted temperature. T_sj = (m_s * T_j + m_j * T_s) / (m_s + m_j).
        s = self.fluid; j = self.jfluid.
        [EFF] for efficiency, can provide any of m_s, T_s, m_j, T_j, if already known.
        '''
        m_s = self('m') if _m_s is UNSET else _m_s
        T_s = self('T') if _T_s is UNSET else _T_s
        m_j = self.getj('m') if _m_j is UNSET else _m_j
        T_j = self.getj('T') if _T_j is UNSET else _T_j
        # parenthesis to avoid floating point errors:
        m_sum = m_s + m_j
        T_sj = (m_s / m_sum) * T_j + (m_j / m_sum) * T_s
        return T_sj

    @known_var(load_across_dims=['fluid', 'jfluid'])
    def get_delta_sj(self):
        '''kronecker delta function between self.fluid and self.jfluid.
        1 where self.fluid == self.jfluid; 0 otherwise.
        Useful e.g. to avoid counting collisions between the same species.
        '''
        # [TODO][EFF] faster to avoid calculating same-species collisions in the first place,
        #     instead of calculating them and then multiplying by (1 - delta_sj)?
        if self.fluid == self.jfluid:
            return self('1')  # 1, as an xarray
        else:
            return self('0')  # 0, as an xarray
