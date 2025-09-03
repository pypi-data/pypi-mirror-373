"""
File Purpose: units in Bifrost
"""
from .bifrost_io_tools import read_bifrost_snap_idl
from ...mhd import MhdUnitsManager
from ...tools import format_docstring
from ...units import _units_manager_helpstr


### --------------------- BifrostUnitsManager --------------------- ###

@format_docstring(helpstr=_units_manager_helpstr, sub_ntab=1)
class BifrostUnitsManager(MhdUnitsManager):
    '''units manager with the from_bifrost method,
    which determines all units based on only u_l, u_t, and u_r.

    Note: cgs units for electromagnetic quantities are not supported here,
        because cgs electromagnetic equations differ from SI equations,
        e.g. cgs includes extra factors of 4*pi or c in various places.

    How to infer electromagnetic units from t, l, and r alone?
        It is possible because 'raw' Bifrost units guarantee mu0 = 1,
            while in 'si', mu0 = 4 * pi * 10^-7 Newtons Ampere^-2
        Internally, this method determines:
            u_M = u_r * u_l**3   # mass
            u_N = u_M * u_l * u_t**-2   # energy (Newtons in SI)
        Amperes units:
            (mu0 [si]) = u_N * u_A**-2 * (mu0 [raw])
            --> u_A = sqrt(u_N * (mu0 [raw]) / (mu0 [si]))
            --> u_A = sqrt(u_N * (1) / (4 * pi * 10^-7))
        Which yields, for charge units:
            u_q = u_A * u_t
        At which point, we have u_l, u_t, u_M, and u_q,
            which is sufficient to infer all other units (aside from K for temperature)

    --- BifrostUnitsManager.help() will print a helpful message: ---
        {helpstr}
    '''
    @classmethod
    def from_bifrost_calculator(cls, bifrost_calculator, units='si', *, K=1):
        '''create a BifrostUnitsManager from a BifrostCalculator instance.

        bifrost_calculator: BifrostCalculator
            determine units based on this calculator's params: u_l, u_t, and u_r.
            (Assumes all snaps have the same u_l, u_t, and u_r.)
            CAUTION: the names u_l, u_t, u_r refer to cgs in Bifrost, but SI in PlasmaCalcs.
        units: 'si' or 'raw'
            by default, outputs of the resulting UnitsManager convert to this unit system.
            Can easily change later by setting result.units to a different value.
        K: number, default 1
            temperature [si] = K * temperature [raw]

        see help(cls) for more details on how the units are inferred.
        '''
        params = bifrost_calculator.params
        ucgs = dict(ucgs_l=params['u_l'],
                    ucgs_t=params['u_t'],
                    ucgs_r=params['u_r'])
        return cls.from_mhd_cgs(units=units, **ucgs, mu0_raw=1, K=K)

    @classmethod
    def from_snap_idl(cls, filename, units='si', *, K=1):
        '''create a BifrostUnitsManager from a Bifrost snap's snapname_NNN.idl file.

        filename: str
            path to the snap's IDL file.
        units: 'si' or 'raw'
            by default, outputs of the resulting UnitsManager convert to this unit system.
            Can easily change later by setting result.units to a different value.
        K: number, default 1
            temperature [si] = K * temperature [raw]

        see help(cls) for more details on how the units are inferred.
        '''
        params = read_bifrost_snap_idl(filename, eval=True)
        ucgs = dict(ucgs_l=params['u_l'],
                    ucgs_t=params['u_t'],
                    ucgs_r=params['u_r'])
        return cls.from_mhd_cgs(units=units, **ucgs, mu0_raw=1, K=K)
