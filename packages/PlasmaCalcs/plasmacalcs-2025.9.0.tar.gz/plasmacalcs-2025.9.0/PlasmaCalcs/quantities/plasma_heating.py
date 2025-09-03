"""
File Purpose: calculating plasma heating, e.g. equilibrium T from E & collisions
"""

import numpy as np
import xarray as xr

from .plasma_parameters import PlasmaParametersLoader
from ..dimensions import CHARGED
from ..errors import QuantCalcError
from ..tools import xarray_sum


class PlasmaHeatingLoader(PlasmaParametersLoader):
    '''plasma heating. See help(self.get_Eheat) for more details.'''
    
    # # # HEATING OF CHARGED SPECIES # # #

    @known_var(deps=['m_n', 'skappa', 'mod_B', 'u_n'])
    def get_Eheat_perp_coeff(self, *, _Eheat_par_coeff=None):
        '''Eheat_perp = Eheat_perp_coeff * |E_perp|^2. for E heating perp to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.

        [EFF] for efficiency, can provide _Eheat_par_coeff if known.
        '''
        Eheat_par_coeff = self('Eheat_par_coeff') if _Eheat_par_coeff is None else _Eheat_par_coeff
        return Eheat_par_coeff / (1 + self('skappa')**2)

    @known_var(deps=['m_n', 'skappa', 'mod_B', 'u_n'])
    def get_Eheat_par_coeff(self):
        '''Eheat_par = Eheat_par_coeff * |E_par|^2. for E heating parallel to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.
        '''
        return (self('m_n') / (3 * self.u('kB'))) * (self('skappa')**2 / self('mod2_B'))

    @known_var(deps=['Eheat_perp_coeff', 'E_perpmag_B'])
    def get_Eheat_perp(self, *, _E_un0=None, _B=None, _Eheat_par_coeff=None):
        '''Eheat_perp = Eheat_perp_coeff * |E_perp|^2. heating perp to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.

        [EFF] for efficiency, can provide _E_un0, _B and/or _Eheat_par_coeff if known.
            caution: if providing _E_un0 or _B, will assume any missing components are 0.
        '''
        perp_coeff = self('Eheat_perp_coeff', _Eheat_par_coeff=_Eheat_par_coeff)
        return perp_coeff * self('E_un0_perpmag_B', _E_un0=_E_un0, _B=_B)**2

    @known_var(deps=['Eheat_par_coeff', 'E_parmag_B'])
    def get_Eheat_par(self, *, _E_un0=None, _B=None, _Eheat_par_coeff=None):
        '''Eheat_par = Eheat_par_coeff * |E_par|^2. heating parallel to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.

        [EFF] for efficiency, can provide _E_un0, _B and/or _Eheat_par_coeff if known.
            caution: if providing _E_un0 or _B, will assume any missing components are 0.
        '''
        par_coeff = self('Eheat_par_coeff') if _Eheat_par_coeff is None else _Eheat_par_coeff
        return par_coeff * self('E_un0_parmag_B', _E_un0=_E_un0, _B=_B)**2

    @known_var(deps=['Eheat_perp', 'Eheat_par'])
    def get_Eheat(self):
        '''Eheat = Eheat_perp + Eheat_par. total heating from electric field. Units of Kelvin.
        
        From assuming u_n=0 and derivatives=0 in heating & momentum equations, which yields:
            T_s = T_n + Eheat_perp + Eheat_par, where
                Eheat_perp = Eheat_perp_coeff * |E_perp|^2,
                Eheat_par  = Eheat_par_coeff * |E_par|^2,
                E_perp = E(in u_n=0 frame) perp to B,
                E_par  = E(in u_n=0 frame) parallel to B,
                Eheat_perp_coeff = (m_n / (3 kB)) (kappa_s^2 / B^2) * (1 / (1 + kappa_s^2)),
                Eheat_par_coeff  = (m_n / (3 kB)) (kappa_s^2 / B^2).
        '''
        with self.using(component=None):  # all 3 vector components
            E_un0 = self('E_un0')
            B = self('B')
            Eheat_par_coeff = self('Eheat_par_coeff')
        Eheat_perp = self('Eheat_perp', _E_un0=E_un0, _B=B, _Eheat_par_coeff=Eheat_par_coeff)
        Eheat_par = self('Eheat_par', _E_un0=E_un0, _B=B, _Eheat_par_coeff=Eheat_par_coeff)
        return Eheat_perp + Eheat_par


    # # # HEATING OF NEUTRALS # # #

    @known_var(deps=['Eheat_perp', 'nuns'])
    def get_Eheat_perp_rate_n_s(self):
        '''zeroth order rate of heating of neutrals due to collisions with s (self.fluid).
        Eheat_perp_rate_n_s = 2 * nuns * Eheat_perp
        == 2 * (m_s / m_n) * (n_s / n_n) * nusn * Eheat_perp
        == (2 m_s / (3 kB)) * (n_s / n_n) * nusn * (kappa_s^2 / (1 + kappa_s^2)) * (|E_perp|^2 / |B|^2)

        Derived from plugging T_from_Eheat_perp and |u_drift| formulae into the neutral heating equation:
            dTn/dt + (2/3) T_n div(u_n) =
                sum_s (2 m_n / (m_n + m_s)) nu_{n,s} [(m_s / (3 kB)) |u_s - u_n|^2 + (T_s - T_n)]
            in the neutral reference frame (u_n=0),
            and using m_n n_n nu_{n,s} = m_s n_s nu_{s,n} which comes from conservation of momentum.

        See also: Eheat_perp_rate_n
        '''
        Eheat_perp = self('Eheat_perp')  # on its own line for easy debugging in case of crash
        return 2 * self('nuns') * Eheat_perp

    @known_var(deps=['Eheat_perp_rate_n'], reduces_dims=['fluid'])
    def get_Eheat_perp_rate_n(self):
        '''zeroth order rate of heating of neutrals due to collisions with all charged species.
        Eheat_perp_rate_n = sum_s Eheat_perp_rate_n_s
        == sum_s 2 * nuns * Eheat_perp
        == sum_s 2 * (m_s / m_n) * (n_s / n_n) * nusn * Eheat_perp
        == sum_s (2 m_s / (3 kB)) * (n_s / n_n) * nusn * (kappa_s^2 / (1 + kappa_s^2)) * (|E_perp|^2 / |B|^2)
    
        Derived from plugging T_from_Eheat_perp and |u_drift| formulae into the neutral heating equation:
            dTn/dt + (2/3) T_n div(u_n) =
                sum_s (2 m_n / (m_n + m_s)) nu_{n,s} [(m_s / (3 kB)) |u_s - u_n|^2 + (T_s - T_n)]
            in the neutral reference frame (u_n=0),
            and using m_n n_n nu_{n,s} = m_s n_s nu_{s,n} which comes from conservation of momentum.
        '''
        return xarray_sum(self('Eheat_perp_rate_n_s', fluid=CHARGED), dim='fluid')

    @known_var(deps=['m', 'm_n', 'nuns', 'mod2_u', 'T', 'T_n'])
    def get_dTndt_s_ds(self):
        '''dataset of contributions to rate of heating of neutrals due to collisions with s.
        dTndt_s = 2 m_n / (m_n + m_s) * nuns * [(m_s / (3 kB)) |u_s|^2 + (T_s - T_n)]
        Assumes u_n==0; else crash with QuantCalcError.

        result has keys:
            'dTndt_u2': 2 m_n / (m_n + m_s) * nuns * [(m_s / (3 kB)) |u_s|^2]
            'dTndt_T': 2 m_n / (m_n + m_s) * nuns * [(T_s - T_n)]
        '''
        if not np.all(self('u_n')==0):
            raise QuantCalcError('dTndt implementation assumes u_n==0, but it is not.')
        outer = 2 * self('m_n/(m+m_n)') * self('nuns')
        inner_u = self('m/(3*kB)') * self('mod2_u')
        inner_T = self('T-T_n')
        result = xr.Dataset({
            'dTndt_u2': outer * inner_u,
            'dTndt_T': outer * inner_T,
        })
        return result

    @known_var(deps=['dTndt_s_ds'])
    def get_dTndt_s_u2(self):
        '''velocity contribution to rate of heating of neutrals due to collisions with s.
        dTndt_s_u2 = 2 m_n / (m_n + m_s) * nuns * [(m_s / (3 kB)) |u_s|^2]
        '''
        return self('dTndt_s_ds')['dTndt_u2']

    @known_var(deps=['dTndt_s_ds'])
    def get_dTndt_s_T(self):
        '''temperature contribution to rate of heating of neutrals due to collisions with s.
        dTndt_s_T = 2 m_n / (m_n + m_s) * nuns * [(T_s - T_n)]
        '''
        return self('dTndt_s_ds')['dTndt_T']

    @known_var(deps=['m', 'm_n', 'nuns', 'mod2_u', 'T', 'T_n'])
    def get_dTndt_s(self):
        '''rate of heating of neutrals due to collisions with s (self.fluid).
        dTndt_s = 2 m_n / (m_n + m_s) * nuns * [(m_s / (3 kB)) |u_s|^2 + (T_s - T_n)]
        '''
        ds = self('dTndt_s_ds')
        return ds['dTndt_u2'] + ds['dTndt_T']

    @known_var(deps=['dTndt_s'], ignores_dims=['fluid'])
    def get_dTndt(self):
        '''rate of heating of neutrals due to collisions with all charged species.
        dTndt = sum_s dTndt_s
        == sum_s 2 m_n / (m_n + m_s) * nuns * [(m_s / (3 kB)) |u_s|^2 + (T_s - T_n)]
        '''
        return xarray_sum(self('dTndt_s', fluid=CHARGED), dim='fluid')


    # # # PLASMA PARAMETERS AFFECTED BY HEATING # # #

    @known_var(deps=['Eheat', 'T_n'])
    def get_T_from_Eheat(self):
        '''T_from_Eheat = T_n + Eheat. Units of Kelvin.
        see help(self.get_Eheat) for more details.
        '''
        return self('T_n') + self('Eheat')

    @known_var(deps=['Eheat_perp', 'T_n'])
    def get_T_from_Eheat_perp(self):
        '''T_from_Eheat_perp = T_n + Eheat_perp. Units of Kelvin.
        see help(self.get_Eheat) for more details.
        '''
        return self('T_n') + self('Eheat_perp')

    @known_var(deps=['eqperp_ldebye2'])
    def get_eqperp_ldebye(self):
        '''Debye length (of self.fluid), using T_from_Eheat_perp instead of T.
        eqperp_ldebye = sqrt(epsilon0 kB T_from_Eheat_perp / (n q^2))
        '''
        return self('eqperp_ldebye2')**0.5

    @known_var(deps=['T_from_Eheat_perp', 'n', 'abs_q'])
    def get_eqperp_ldebye2(self):
        '''squared Debye length (of self.fluid), using Eheat_perp instead of T.
        eqperp_ldebye2 = epsilon0 kB T_from_Eheat_perp / (n q^2)
        '''
        T = self('T_from_Eheat_perp')
        return self.u('eps0') * self.u('kB') * T / (self('n') * self('abs_q')**2)

    @known_var(deps=['eqperp_ldebye2'], ignores_dims=['fluid'])
    def get_eqperp_ldebye_total(self):
        '''total Debye length for all fluids: sqrt(epsilon0 kB / sum_fluids(n q^2 / T)),
        using T = T_from_Eheat_perp.
        Equivalent: sqrt( 1 / sum_fluids(1/eqperp_ldebye^2) )
        '''
        return xarray_sum(1 / self('eqperp_ldebye2'), dim='fluid')**-0.5

    @known_var(deps=['T_from_Eheat_perp', 'm'])
    def get_eqperp_vtherm(self):
        '''thermal velocity, using T_from_Eheat_perp instead of T.
        eqperp_vtherm = sqrt(kB T_from_Eheat_perp / m)
        '''
        T = self('T_from_Eheat_perp')
        return (T * (self.u('kB') / self('m')))**0.5

    @known_var(deps=['dsmin_for_timescales', 'eqperp_vtherm'])
    def get_timescale_eqperp_vtherm(self):
        '''timescale from thermal velocity, using T_from_Eheat_perp instead of T.
        dsmin / eqperp_vtherm.
        '''
        return self('dsmin_for_timescales') / self('eqperp_vtherm')

    @known_var(deps=['eqperp_vtherm', 'nusn'], aliases=['eqperp_lmfp'])
    def get_eqperp_mean_free_path(self):
        '''collisional mean free path, using eqperp_vtherm instead of vtherm.
        eqperp_lmfp = eqperp_vtherm / nusn
        '''
        return self('eqperp_vtherm') / self('nusn')
