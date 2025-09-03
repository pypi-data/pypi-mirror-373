"""
File Purpose: UnitsManagerPIC class
"""

from .units_manager import UnitsManager, _units_manager_helpstr
from ..errors import InputMissingError, InputConflictError
from ..tools import format_docstring
from ..defaults import DEFAULTS


### --------------------- UnitsManagerPIC --------------------- ###

@format_docstring(helpstr=_units_manager_helpstr, sub_ntab=1)
class UnitsManagerPIC(UnitsManager):
    '''units manager with the from_pic method, and some other helpful PIC things.

    Manages units, including conversion factors and physical constants in different unit systems.

    --- UnitsManagerPIC.help() will print a helpful message: ---
        {helpstr}
    '''
    SIC_QUANTITIES = ("time", "length", "mass", "current", "temperature", "charge", "frequency", "speed", "wave_number",
                "mass_density", "charge_density", "number_density", "current_density", "permittivity", "permeability",
                "pressure", "energy", "power", "potential", "b_field", "h_field", "e_field")
    # ^ SIC stands for self.sic here, which stores "si conversions". It's not a typo from 'PIC'.
    _PIC_DEFAULTS = {key: UnitsManager.PHYSICAL_CONSTANTS_SI[key][0] for key in ('qe', 'me', 'eps0')}

    @classmethod
    def from_pic(cls, units='si', *,
                 u_l=None, u_t=None, u_n=None, ne=None, ne_si=None,
                 qe=None, me=None, eps0=None,
                 qe_si=None, me_si=None, eps0_si=None,
                 M=None, q=None, u_eps=None,
                 **kw_init):
        """create a UnitsManagerPIC from pic parameters.
        'raw' units refers to the units from the PIC code.

        REQUIRED PARAMETERS
            There is an ambiguity in the units from a PIC code (e.g. from eppic).
            Indicate length or time units in one of the following ways:
                u_l: length [si] = u_l * length [raw]
                u_t: time [si] = u_t * time [raw]
                u_n: number density [si] = u_n * number density [raw]
                ne and ne_si: number density n for electrons; ne = n [raw]; ne_si = n [si]

        OPTIONAL PARAMETERS
            :param qe: None or value
                absolute value of electron charge [raw units].
                if None, use cls._PIC_DEFAULTS['qe']. Default: SI value of qe.
            :param me: None or value
                electron mass [raw units].
                if None, use cls._PIC_DEFAULTS['me']. Default: SI value of me.
            :param eps0: None or value
                permittivity of free space [raw units].
                if None, use cls._PIC_DEFAULTS['eps0']. Default: SI value of epsilon0
            :param qe_si, me_si, eps0_si: None or value
                optionally, specify a non-traditional SI value
                for electron charge, electron mass, and/or epsilon0.
            :param M, q, u_eps: None or value
                if provided, set u_M = M, u_q = q, or u_eps=u_eps,
                and ignore info about me, qe, or eps0.
        """
        # get required value
        u_l_and_t = cls.pic_ambiguous_unit(u_l=u_l, u_t=u_t, u_n=u_n, ne=ne, ne_si=ne_si)
        u_l = u_l_and_t['u_l']
        u_t = u_l_and_t['u_t']

        # get defaults / optional kwargs values
        if qe is None: qe = cls._PIC_DEFAULTS['qe']
        if me is None: me = cls._PIC_DEFAULTS['me']
        if eps0 is None: eps0 = cls._PIC_DEFAULTS['eps0']

        if qe_si is None: qe_si = cls.PHYSICAL_CONSTANTS_SI['qe'][0]
        if me_si is None: me_si = cls.PHYSICAL_CONSTANTS_SI['me'][0]
        if eps0_si is None: eps0_si = cls.PHYSICAL_CONSTANTS_SI['eps0'][0]

        # GET BASE RAW UNITS (CHARGE, MASS, TEMPERATURE, LENGTH, TIME)
        u_q = qe_si / qe if q is None else q  # qe [raw] * u_q == qe [si]
        u_M = me_si / me if M is None else M  # me [raw] * u_M == me [si]
        u_eps0 = eps0_si / eps0 if u_eps is None else u_eps  # eps0 [raw] * u_eps0 == eps0 [si]
        # eps0 as units constraint:
        #   F = (1 / (4 pi eps0)) * (q1 q2 / r^2)
        #   --> u_M * u_l * u_t^-2 = u_eps0^-1 * u_q^2 * u_l^-2
        #   --> u_l^3 * u_t^-2 = u_M^-1 * u_eps0^-1 * u_q^2
        #   --> u_l = (u_M^-1 * u_eps0^-1 * u_q^2 * u_t^2)**(1/3)
        #       u_t = (u_M * u_eps0 * u_q^-2 * u_l^3)**(1/2)
        if u_l is None:  # u_t is known
            u_l = (u_M**-1 * u_eps0**-1 * u_q**2 * u_t**2)**(1/3)
        else:   # u_l is known
            u_t = (u_M * u_eps0 * u_q**-2 * u_l**3)**(1/2)

        # return
        return cls(units=units, q=u_q, M=u_M, l=u_l, t=u_t, **kw_init)

    @staticmethod
    def pic_ambiguous_unit(u_l=None, u_t=None, u_n=None, ne=None, ne_si=None):
        '''Returns dict of u_l and u_t.
        Requires that u_l or u_t can be determined, but not both.
        raise InputConflictError if too many inputs; InputMissingError if not enough inputs.

        Indicate length or time units in one of the following ways:
            u_l: length [si] = u_l * length [raw]
            u_t: time [si] = u_t * time [raw]
            u_n: number density [si] = u_n * number density [raw]
            ne and ne_si: number density n for electrons; ne = n [raw]; ne_si = n [si]

        DEFAULTS.pic_ambiguous_unit can be set to a dict of default values instead;
            if DEFAULTS.pic_ambiguous_unit exists, use it when all inputs to this function are None.
            E.g. DEFAULTS.pic_ambiguous_unit = dict(u_t=1) --> pic seconds are SI seconds, by default.
            Ignored when any input is not None (or when providing ne or ne_si but not both).
        '''
        n_provided = sum((val is not None) for val in (u_l, u_t, u_n, ne and ne_si))
        if n_provided < 1:
            default = getattr(DEFAULTS, 'pic_ambiguous_unit', dict())
            if len(default) == 0:
                errmsg = "UnitsManagerPIC requires one of u_l, u_t, u_n, or (ne and ne_si)"
                raise InputMissingError(errmsg)
            else:
                n_provided = len(default)
                u_l = default.get('u_l', None)
                u_t = default.get('u_t', None)
                u_n = default.get('u_n', None)
                ne = default.get('ne', None)
                ne_si = default.get('ne_si', None)
        if n_provided > 1:
            errmsg = "UnitsManagerPIC requires only one of u_l, u_t, u_n, or (ne and ne_si)"
            raise InputConflictError(errmsg)
        if (ne is not None) and (ne_si is not None):
            u_n = ne / ne_si
        if u_n is not None:
            u_l = u_n ** (-1/3)
        return dict(u_l=u_l, u_t=u_t)
