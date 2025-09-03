"""
File Purpose: units in mhd
"""
import numpy as np

from ..defaults import DEFAULTS
from ..units import UnitsManager, _units_manager_helpstr
from ..tools import format_docstring, UNSET


### --------------------- MhdUnitsManager --------------------- ###

@format_docstring(helpstr=_units_manager_helpstr, sub_ntab=1)
class MhdUnitsManager(UnitsManager):
    '''units manager with the from_mhd method,
    which determines all units based on u_l, u_t, u_r, and mu0_raw.

    Note: cgs units for electromagnetic quantities are not supported here,
        because cgs electromagnetic equations differ from SI equations,
        e.g. cgs includes extra factors of 4*pi or c in various places.

    How to infer electromagnetic units from t, l, r, and mu0?
        Internally, this method determines:
            u_M = u_r * u_l**3   # mass
            u_N = u_M * u_l * u_t**-2   # energy (Newtons in SI)
        Amperes units:
            (mu0 [si]) = u_N * u_A**-2 * (mu0 [raw])
            --> u_A = sqrt(u_N * (mu0 [raw]) / (mu0 [si]))
            where mu0 [si] == DEFAULTS.PHYSICAL.CONSTANTS_SI['mu0'], approx. 4 * pi * 1e-7.
        Which yields, for charge units:
            u_q = u_A * u_t
        At which point, we have u_l, u_t, u_M, and u_q,
            which is sufficient to infer all other units (aside from K for temperature)

    --- MhdUnitsManager.help() will print a helpful message: ---
        {helpstr}
    '''
    @classmethod
    def from_mhd(cls, units='si', *, u_l, u_t, u_r, mu0_raw=1, K=1):
        '''create a MhdUnitsManager from u_l, u_t and u_r, the SI conversion factors.
        CAUTION: these are the SI conversion factors. NOT cgs.
        (some MHD simulations, like Bifrost, use similar names for the CGS factors.)
        
        units: 'si' or 'raw'
            by default, outputs of the resulting UnitsManager convert to this unit system.
            Can easily change later by setting result.units to a different value.
        u_l: number
            length [si] = u_l * length [raw]
        u_t: number
            time [si] = u_l * time [raw]
        u_r: number
            mass density [si] = u_r * mass density [raw]
        mu0_raw: number, default 1
            value of mu0 in 'raw' units system. Used to infer Amperes units via:
                u_M = u_r * u_l**3          # mass
                u_N = u_M * u_l * u_t**-2   # energy (Newtons in SI)
                mu0_si = u_N * u_A**-2 * mu0_raw
                u_A = sqrt(u_N * mu0_raw / mu0_si)
            where mu0_si == DEFAULTS.PHYSICAL.CONSTANTS_SI['mu0'], approx. 4 * pi * 1e-7.
        K: number, default 1
            temperature [si] = K * temperature [raw]
        '''
        u_M = u_r * u_l**3
        u_N = u_M * u_l * u_t**-2
        u_A = np.sqrt(u_N * mu0_raw / DEFAULTS.PHYSICAL.CONSTANTS_SI['mu0'])
        u_q = u_A * u_t
        return cls(units=units, q=u_q, M=u_M, l=u_l, t=u_t, K=K)

    @classmethod
    def from_mhd_cgs(cls, units='si', *, ucgs_l, ucgs_t, ucgs_r, mu0_raw=1, K=1):
        '''create a BifrostUnitsManager from ucgs_l, ucgs_t and ucgs_r, the CGS conversion factors.

        units: 'si' or 'raw'
            by default, outputs of the resulting UnitsManager convert to this unit system.
            Can easily change later by setting result.units to a different value.
        ucgs_l: number
            length [cgs] = ucgs_l * length [raw]
        ucgs_t: number
            time [cgs] = ucgs_t * time [raw]
        ucgs_r: number
            mass density [cgs] = ucgs_r * mass density [raw]
        mu0_raw: number, default 1
            value of mu0 in 'raw' units system. Used to infer Amperes units via:
                u_M = u_r * u_l**3          # mass
                u_N = u_M * u_l * u_t**-2   # energy (Newtons in SI)
                mu0_si = u_N * u_A**-2 * mu0_raw
                u_A = sqrt(u_N * mu0_raw / mu0_si)
            where mu0_si == DEFAULTS.PHYSICAL.CONSTANTS_SI['mu0'], approx. 4 * pi * 1e-7.
        K: number, default 1
            temperature [cgs] = K * temperature [raw]
        '''
        # length [si]  = u_l    * length [raw]
        # length [cgs] = ucgs_l * length [raw]
        # --> u_l / ucgs_l = length [si] / length [cgs]
        # e.g. length [si] = 1, length [cgs] = 100 --> u_l = ucgs_l * 1e-2
        u_l = ucgs_l * 1e-2
        # s to s... cgs and si use same time units
        u_t = ucgs_t
        # similar logic as for length... but now we have g/cm^3 to kg/m^3,
        # so g to kg gives 10^-3, and cm^-3 to m^-3 gives 10^6
        u_r = ucgs_r * 1e3
        return cls.from_mhd(units=units, u_l=u_l, u_t=u_t, u_r=u_r, mu0_raw=mu0_raw, K=K)

    # # # DISPLAY # # #
    def _repr_show_factors(self):
        '''returns dict of name and conversion factor to si, to include in repr(self).
        Here, include l, t, and r. Also include K if it is not 1.
        Also include mu0_raw if it is not 1.
        '''
        factors = {key: self(key, 'si', 'raw') for key in ('l', 't', 'r', 'K')}
        if factors['K'] == 1:
            del factors['K']
        if not np.isclose(self('mu0', 'raw'), 1):
            factors['mu0_raw'] = self('mu0', 'raw')
        return factors
