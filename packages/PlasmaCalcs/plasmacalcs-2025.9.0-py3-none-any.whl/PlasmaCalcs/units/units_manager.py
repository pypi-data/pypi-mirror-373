"""
File Purpose: handle unit conversions
"""

from ..errors import (
    UnitsError, UnitsUnknownError,
    InputConflictError,
)
from ..tools import (
    alias, simple_property,
    format_docstring, UNSET,
)
from ..defaults import DEFAULTS


### --------------------- CONSTANTS & KNOWN SYMBOLS --------------------- ###

# DIMENSIONLESS
DIMENSIONLESS = '1'  # used to indicate dimensionless quantity.

# SI BASE UNIT SYMBOLS
SI_BASE_UNIT_SYMBOLS = (
    "kg",   # M; mass; kilograms
    "m",    # l; length; meters
    "s",    # t; time; seconds
    "A",    # A; current; amperes
    "K",    # K; temperature; kelvin
    )

# OTHER SI UNITS
#    [TODO] use intuitive definitions instead of SI base units? e.g. J = N m
#    The intuitive definitions might help to ensure there are no typos;
#    e.g. it's easier to check {'S': 'Ohm-1'} than {'S': 'kg-1 m-2 s3 A2'}
SI_OTHER_UNIT_SYMBOLS = {
    'Hz'     : 's-1',               # hertz
    'N'      : 'kg m s-2',          # newton
    'Pa'     : 'kg m-1 s-2',        # pascal
    'J'      : 'kg m2 s-2',         # joule
    'W'      : 'kg m2 s-3',         # watts
    'C'      : 's A',               # coulomb
    'V'      : 'kg m2 s-3 A-1',     # volt
    'F'      : 'kg-1 m-2 s4 A2',    # farad
    'Ohm'    : 'kg m2 s-3 A-2',     # ohm
    'S'      : 'kg-1 m-2 s3 A2',    # siemens   # inverse ohm
    'Wb'     : 'kg m2 s-2 A-1',     # weber   # magnetic flux
    'T'      : 'kg s-2 A-1',        # tesla
    'H'      : 'kg m2 s-2 A-2',     # ???   # permeability = H / m
}

# KNOWN CONVERSION SYMBOLS
KNOWN_CONVERSION_SYMBOLS = {
    'dimensionless'   : '1',        #'1': 'dimensionless',
    'time'            : 's',       't': 'time',
    'length'          : 'm',       'l': 'length',
    'mass'            : 'kg',      'M': 'mass',
    'current'         : 'A',
    'temperature'     : 'K',       'Th': 'temperature', 'tg': 'temperature',
    'charge'          : 'C',       'q': 'charge',
    'frequency'       : 'Hz',
    'speed'           : 'm s-1',   'u': 'speed',
    'acceleration'    : 'm s-2',   'a': 'acceleration',
    'area'            : 'm2',
    'volume'          : 'm3',
    'wave_number'     : 'm-1',     'lambda': 'wave_number',
    'momentum'        : 'M u',     'p': 'momentum',
    'force'           : 'N',       'f': 'force',
    'pressure'        : 'Pa',      'P': 'pressure', 'energy_density': 'pressure',
    'energy'          : 'J',       'E': 'energy',  'kT': 'energy',
    'power'           : 'W',
    'number_density'  : 'm-3',     'n': 'number_density', 'nr': 'number_density',
    'mass_density'    : 'n M',     'r': 'mass_density', 'rho': 'mass_density',
    'charge_density'  : 'n C',     'nq': 'charge_density', 'rhoc': 'charge_density',
    'current_density' : 'A m-2',   'j': 'current_density',
    'energy_density'  : 'J m-3',
    'flux'            : 'n u',
    'momentum_density': 'n M u',  'pr': 'momentum_density',
    'permittivity'    : 'F m-1',
    'permeability'    : 'H m-1',
    'potential'       : 'V',       'phi': 'potential',
    'capacitance'     : 'F',
    'resistance'      : 'Ohm',
    'conductance'     : 'S',
    'b_flux'          : 'Wb',
    'b_field'         : 'T',       'b': 'b_field',
    'h_field'         : 'A m-1',
    'inductance'      : 'H',
    'e_field'         : 'V m-1',   'ef': 'e_field',
    'opacity'         : 'l2 m-2',
}

# dict of all symbols which we can convert into SI base units
KNOWN_CONVERSIONS = {DIMENSIONLESS: DIMENSIONLESS,
                    **{key: key for key in SI_BASE_UNIT_SYMBOLS},
                    **SI_OTHER_UNIT_SYMBOLS,
                    **KNOWN_CONVERSION_SYMBOLS}

# PHYSICAL_CONSTANTS_SI = dict of {constant: (value, units string)}
PHYSICAL_CONSTANTS_USTRS = {
    'amu'     : 'M',            # atomic mass unit
    'c'       : 'u',            # speed of light
    'kB'      : 'J K-1',        # boltzmann constant
    'eps0'    : 'permittivity', # permittivity of free space
    'mu0'     : 'permeability', # permeability of free space
    'qe'      : 'q',            # elementary charge
    'me'      : 'M',            # electron mass
    'qme'     : 'q M-1',        # q / m_e
    'hplanck' : 'J s',          # planck constant (not hbar)
    'm_proton': 'M',            # proton mass
    'eV'      : 'J',            # electron volt
    'eV kB-1' : 'K',            # eV / kB
    'me amu-1': '1',            # m_e / amu
}
for _key, _alias in (('qe', 'q_e'), ('me', 'm_e'), ('m_proton', 'm_p'), ('hplanck', 'h')):
    PHYSICAL_CONSTANTS_USTRS[_alias] = PHYSICAL_CONSTANTS_USTRS[_key]
del _key, _alias

PHYSICAL_CONSTANTS_SI = {cname: (DEFAULTS.PHYSICAL.CONSTANTS_SI[cname], ustr) \
    for cname, ustr in PHYSICAL_CONSTANTS_USTRS.items()}
# [TODO] allow physical constants to be involved in the conversion factor notation, in general.


### --------------------- helper functions --------------------- ###

# FUNCTIONS WHICH READ AND MODIFY THE INPUT STRINGS
def _get_symbol_and_exponent(unit_string):
    '''
    Extract the unit symbol and the exponent from the unit string
    :param unit_string: string of units (e.g. "m-1")
    :return: unit symbol, exponent (e.g. "m", -1)
    '''
    symbol = unit_string
    exponent = 1
    for position in range(len(unit_string)):
        letter = unit_string[position]
        if letter == "-":
            symbol = unit_string[:position]
            number = unit_string[position + 1:]
            if "." not in number:
                exponent = -int(number)
            else:
                exponent = -float(number)
            break
        elif letter.isnumeric():
            if position == 0:
                if unit_string != '1':
                    raise UnitsError(f"Invalid unit string: {unit_string!r}")
                else:
                    return unit_string, 1
            symbol = unit_string[:position]
            number = unit_string[position:]
            if "." not in number:
                exponent = int(number)
            else:
                exponent = float(number)
            break
    return symbol, exponent


### --------------------- UnitsStringManager --------------------- ###

class UnitsStringManager(dict):
    '''manages string of units; keys are unit symbol bases, values are exponents.'''
    bases = SI_BASE_UNIT_SYMBOLS
    known = KNOWN_CONVERSIONS

    def _get_bases_and_known(self, bases=None, known=None):
        '''return bases & known, using value from self if None is entered'''
        if bases is None: bases = self.bases
        if known is None: known = self.known
        return bases, known

    @classmethod
    def from_string(cls, string_of_units, *, bases=None, known=None):
        '''new UnitsStringManager from a string of units; just gets the symbols & exponents.'''
        units = string_of_units.split()
        symbols_and_exponents = [_get_symbol_and_exponent(unit) for unit in units]
        totals = dict()
        for s, exp in symbols_and_exponents:
            totals[s] = totals.get(s, 0) + exp
        result = cls(totals)
        if bases is not None: result.bases = bases
        if known is not None: result.known = known
        return result

    def _new(self, dict_):
        '''create new instance of self given this dict.'''
        return type(self)(dict_)

    def __pow__(self, exp):
        '''raise self to exponent; multiplies each value in self by exp.'''
        return self._new({key: value * exp for key, value in self.items()})

    def __mul__(self, other):
        '''multiply self by other UnitsStringManager; adds values where keys match.'''
        result = self.copy()
        for key, value in other.items():
            if key in result:
                result[key] = result[key] + value
            else:
                result[key] = value
        return result

    def __eq__(self, other):
        '''tells whether self equals another UnitsStringManager.'''

    def clean(self):
        '''return result of deleting all keys with value == 0.'''
        return self._new({key: value for key, value in self.items() if value != 0})

    def copy(self):
        '''return copy of self.'''
        return self._new(super().copy())

    def expand_once(self, *, bases=None, known=None):
        '''returns result of replacing all keys other than bases with their known conversions.'''
        bases, known = self._get_bases_and_known(bases, known)
        result = self._new({})  # empty dict.
        if len(self.items()) == 1 and DIMENSIONLESS in self:
            return result  # return empty dict; self only has DIMENSIONLESS in it.
        for key, value in self.items():
            if key in bases:
                result = result * self._new({key: value})
            elif key in known:
                result = result * (self.from_string(known[key]) ** value)
            else:
                raise UnitsError(f"Unknown unit: {key!r}")
        return result

    def expand(self, *, bases=None, known=None):
        '''returns result of expanding repeatedly until all keys are si base units.'''
        bases, known = self._get_bases_and_known(bases, known)
        result = self
        safety = tuple(self.items())
        while not all(key in bases for key in result.keys()):
            result = result.expand_once(bases=bases, known=known)
            if safety == tuple(result.items()):
                raise NotImplementedError('expand_once made no changes... raising error to stop endless loop.')
        return result

    def __str__(self):
        '''convert self into units string.'''
        self = self.clean()
        result = ' '.join([f'{key}{value}' for key, value in self.items()])
        return result

    def evaluate_partial(self, values_dict):
        '''evaluates all the parts of self which can be evaluated based on values_dict.
        returns (numerical value, UnitsStringManager with still-unevaluated units)

        if no keys in self are also in values_dict, result[0] will be 1.
        if all keys in self are also in values_dict, len(result[1]) will be 0.

        if values_dict provides any relevant key with value None, returns (None, {})
        '''
        value = 1
        unevaluated = self.copy()
        for key, exponent in self.items():
            if key in values_dict:
                vdval = values_dict[key]
                if vdval is None:
                    return None, type(self)()
                value = value * values_dict[key] ** exponent
                del unevaluated[key]
        return value, unevaluated

    def evaluate_iteratively(self, values_dict):
        '''evaluates all the parts of self which can be evaluated based on values_dict,
        and also calling result[1].expand_once() after each incomplete evaluation attempt.
        returns numerical value.

        raises UnitsError if any units are not in values_dict after expanding as many times as possible.
        '''
        result, units = self.evaluate_partial(values_dict)
        while len(units) > 0:
            u_expanded = units.expand_once()
            if u_expanded == units:
                raise UnitsError(f'Could not fully evaluate {self!r}; missing values for {list(units.keys())}.')
            next_number, units = u_expanded.evaluate_partial(values_dict)
            if next_number is None:
                return None
            result = result * next_number
        return result

    def evaluate(self, values_dict):
        '''evaluates self based on values_dict, returning a numerical value.
        if any units are not in values_dict, raises UnitsError.

        Equivalent to self.evaluate_partial(values_dict)[0], when all units are in values_dict.
        '''
        result = self.evaluate_partial(values_dict)
        if len(result[1]) > 0:
            raise UnitsError(f'Could not fully evaluate {self!r}; missing values for {list(result[1].keys())}.')
        return result[0]


def units_string_to_si_bases(string_of_units, *, bases=SI_BASE_UNIT_SYMBOLS, known=KNOWN_CONVERSIONS):
    '''convert string of any units to string of SI base units.'''
    return str(UnitsStringManager.from_string(string_of_units, bases=bases, known=known).expand())


### --------------------- UnitsManager --------------------- ###

_units_manager_helpstr = \
    '''BASES tells all the SI base unit symbols.
    KNOWN tells all the known conversions between symbols (just strings, not numerical values).
    PHYSICAL_CONSTANTS_SI tells all the known physical constants, as tuples of (SI value, units string)).
    physical_constants_raw (or pcr) tells all the known physical constants, in 'raw' units;
        first do self.populate_pcr() to calculate them all.

    self.sic tells all the known values for unit conversions, from raw to SI.
        e.g., Mass [raw] * self.sic['M'] == Mass [si].
        new conversion factors are cached here the first time they are calculated,
            to avoid recalculating the values multiple times.
        to remove all cached values, self.clear_sic().

    call the object to get conversion factor. E.g.:
        density_si = density_raw * self('r', 'si', 'raw')
        density_raw = density_si * self('r', 'raw', 'si')
    or call the object to get physical constant. E.g.:
        c_si = self('c', 'si')   # speed of light in 'si' units
        c_raw = self('c', 'raw') # speed of light in 'raw' units.

    Conversion factors can be combined and raised to powers, e.g.:
        self('u0.5 m-1') == self('u')**0.5 * self('m')**-1
    '''

@format_docstring(helpstr=_units_manager_helpstr, sub_indent=DEFAULTS.TAB)
class UnitsManager():
    '''Manages units, including conversion factors and physical constants in different unit systems.

    :param units: str
        the default unit system to convert to ("si", "raw", or "cgs")
    :param M: value, default 1.        Mass_si = M * Mass_raw
    :param l: value, default 1.      Length_si = l * Length_raw
    :param t: value, default 1.        Time_si = t * Time_raw
    :param q: value, default 1.      Charge_si = q * Charge_raw
    :param K: value, default 1. Temperature_si = K * Temperature_raw
    :param sic_quantities: iterable
        calculate all these conversion factors & shorthands once, ahead of time.
        if None, use cls.SIC_QUANTITIES (default empty list)

    To alter cgs unit conversions (e.g. to specify q units), make a new self.CGS_UNITS.
        The default is CGS_UNITS = UnitsManager(M=1e-3, l=1e2, t=1, q=None, K=1).
        (don't alter the default one directly; make a new one with the desired values.)
        q=None is the default because electromagnetic cgs units are ambiguous,
            there are multiple options for how to convert to si and the equations differ.

    --- UnitsManager.help() will print a helpful message: ---
        {helpstr}
    '''
    BASES = SI_BASE_UNIT_SYMBOLS
    KNOWN = KNOWN_CONVERSIONS
    PHYSICAL_CONSTANTS_SI = PHYSICAL_CONSTANTS_SI
    pcr = alias('physical_constants_raw')
    SIC_QUANTITIES = []

    _helpstr = _units_manager_helpstr

    @classmethod
    def help(cls):
        '''prints a helpful message about using cls.'''
        print(f'Help for {cls.__name__}:\n{cls._helpstr}')

    # # # INITIALIZATION # # #
    def __init__(self, units="si", *, M=1, l=1, t=1, q=1, K=1, sic_quantities=None):
        self.units = units
        self.bases = dict(M=M, l=l, t=t, q=q, K=K)
        self._init_sic_quantities = sic_quantities
        self._init_from_bases()

    def _init_from_bases(self):
        '''initialize all other parts of self, using self.bases (and self._init_sic_quantities).'''
        self.init_sic()
        self.populate_sic(self._init_sic_quantities)
        self.populate_physical_constants_raw([])

    def init_sic(self):
        '''initialize self.sic from self.bases.'''
        b = self.bases
        A = None if ((b['q'] is None) or (b['t'] is None)) else b['q'] / b['t']
        self.sic = dict(kg=b['M'], m=b['l'], s=b['t'], A=A, K=b['K'])

    def clear_sic(self):
        '''clear self.sic. delete self.sic, then do self.init_sic()'''
        del self.sic
        self.init_sic()

    alts = simple_property('_alts', setdefault=dict,
        doc='''dict of {key: units} for alternative objects' unit systems.
        e.g. CoordsUnitsHaver might set alts['coords'] = 'si' to indicate coords always in si.''')

    # # # BASES # # #
    def _base_unit_property(ustr, longname):
        '''create property for base unit -- link to self.bases[ustr]. re-initialize self if changed.'''
        def getter(self):
            return self.bases[ustr]
        def setter(self, value):
            self.bases[ustr] = value
            self._init_from_bases()
        return property(getter, setter, doc=f'''{longname}_si = {ustr} * {longname}_raw''')

    M = _base_unit_property('M', 'Mass')
    l = _base_unit_property('l', 'Length')
    t = _base_unit_property('t', 'Time')
    q = _base_unit_property('q', 'Charge')
    K = _base_unit_property('K', 'Temperature')

    def is_trivial(self):
        '''returns whether self has only trivial conversion factors in it (all factors 1 or not provided).'''
        return all(val is None or val==1 for val in self.bases.values())

    # # # CGS UNITS # # #
    CGS_UNITS = simple_property('_CGS_UNITS', setdefaultvia='CGS_UNITS_DEFAULT',
            doc='''UnitsManager for cgs units. Default is UnitsManager(M=1e-3, l=1e2, t=1, q=None, K=1).
            q=None is the default because electromagnetic cgs units are ambiguous,
                there are multiple options for how to convert to si and the equations differ.
            Note that for CGS_UNITS, 'raw' means 'cgs'.
            Feel free to set self.CGS_UNITS = a new UnitsManager with a known q,
                if you have decided on a specific cgs system to remove relevant ambiguities.''')

    @classmethod
    def CGS_UNITS_DEFAULT(cls):
        '''UnitsManager for cgs units. Default is UnitsManager(M=1e-3, l=1e2, t=1, q=None, K=1).
        q=None is the default because electromagnetic cgs units are ambiguous,
            there are multiple options for how to convert to si and the equations differ.
        Note that for the CGS_UNITS result,'raw' means 'cgs'.
        '''
        # M=1e-3 because 1 g == 1e-3 kg. --> Mass [si] = 1e-3 * Mass [raw]
        # l=1e-2 because 1 cm == 1e-2 m. --> Length [si] = 1e-2 * Length [raw]
        return cls(M=1e-3, l=1e-2, t=1, q=None, K=1)

    # # # CONVERTING UNITS # # #
    def __call__(self, ustr, units=UNSET, convert_from='raw', *, alt=None):
        ''' return quantity or conversion factor in the specified unit system.
        ustr: str
            physical constant or quantity (e.g. "c" for speed of light or "M" for mass units)
        units: UNSET, None, 'si', 'raw', or 'cgs'
            unit system to convert to.
            UNSET --> units = self.alts.get(alt, self.units). (Equivalent to None if alt is None)
            None --> use self.units.
        convert_from: 'si', 'raw', or 'cgs'
            unit system to convert from.
            Ignored if ustr is a quantity (e.g. "c") instead of conversion factor (e.g. "mass")
        alt: object (probably None or str)
            if units is UNSET, use units = self.alts.get(alt, self.units)
            otherwise, alt must be None.
        :return: a converted physical constant or a conversion factor
        '''
        if units is UNSET:
            units = self.alts.get(alt, self.units)
        elif alt is not None:
            raise InputConflictError(f'cannot provide both units & alt! got alt={alt!r}, units={units!r}')
        if units is None:
            units = self.units

        # IF PHYSICAL CONSTANT, GET VALUE & UNIT STR.
        if ustr in self.PHYSICAL_CONSTANTS_SI:
            if units=='si':
                return self.PHYSICAL_CONSTANTS_SI[ustr][0]
            elif units=='raw':
                pcr = self.physical_constants_raw
                try:
                    return pcr[ustr]
                except KeyError:
                    pass  # handled below to avoid layered error messages if crash
                value, new_ustr = self.PHYSICAL_CONSTANTS_SI[ustr]
                result = value * self(new_ustr, 'raw', convert_from='si')
                pcr[ustr] = result
                return result
            elif units=='cgs':
                cgsunits = self.CGS_UNITS
                return cgsunits(ustr, 'raw')  # for CGS_UNITS, 'raw' means 'cgs'.
            else:
                raise NotImplementedError(f'unit system {units!r}, for physical constant {ustr!r}')
        
        # ELSE, NOT A PHYSICAL CONSTANT. RETURN CONVERSION FACTOR
        unit_systems = set((units, convert_from))
        if convert_from == units:
            return 1
        if "raw" in unit_systems:
            raw_to_si = self.get_sic_factor(ustr)
            if "si" in unit_systems:  # raw & si
                if (units == "si") and (convert_from == "raw"):
                    return raw_to_si
                elif (units == "raw") and (convert_from == "si"):
                    return 1 / raw_to_si
                assert False, 'coding error if reached this line'
            elif "cgs" in unit_systems:  # raw & cgs
                cgsunits = self.CGS_UNITS
                si_to_cgs = cgsunits(ustr, 'raw', 'si')  # for CGS_UNITS, 'raw' means 'cgs'.
                raw_to_cgs = raw_to_si * si_to_cgs
                if (units == "cgs") and (convert_from == "raw"):
                    return raw_to_cgs
                elif (units == "raw") and (convert_from == "cgs"):
                    return 1 / raw_to_cgs
                assert False, 'coding error if reached this line'
        elif unit_systems == set(("si", "cgs")):
            cgsunits = self.CGS_UNITS
            if units == "si":   # and convert_from == "cgs"
                return cgsunits(ustr, 'si', 'raw')  # for CGS_UNITS, 'raw' means 'cgs'.
            else: # units == "cgs" and convert_from == "si"
                return cgsunits(ustr, 'raw', 'si')  # for CGS_UNITS 'raw' means 'cgs'.
        raise NotImplementedError(f'units conversion from {convert_from!r} to {units!r}')

    def calc_sic_factor(self, ustr):
        '''Calculate conversion factor from raw units to SI units.
        Also save result in self.sic for future use.
        :param ustr: string of units (e.g. "m-3")
        :return: conversion factor from raw units to SI units
        '''
        uobj = UnitsStringManager.from_string(ustr)
        result = uobj.evaluate_iteratively(self.sic)
        self.sic[ustr] = result
        return result

    def get_sic_factor(self, ustr):
        '''Get conversion factor from raw units to SI units.
        If not already calculated, calculate it first.
        :param ustr: string of units (e.g. "m-3")
        :return: conversion factor from raw units to SI units

        if None, raise UnitsUnknownError instead.
        '''
        sic = self.sic
        if ustr in sic:
            result = sic[ustr]
        else:
            result = self.calc_sic_factor(ustr)
        if result is None:
            errmsg = (f'Cannot determine units for {ustr!r}. This most likely means '
                      f'it depends on one or more base units which are unknown (i.e. None). '
                      f'Bases defined here are: {self.bases!r}.')
            raise UnitsUnknownError(errmsg)
        return result

    def string_to_si_bases(self, string_of_units):
        '''convert string of any units to string of SI base units.'''
        return units_string_to_si_bases(string_of_units, bases=self.BASES, known=self.KNOWN)

    # # # CALCULATING LOTS OF QUANTITIES # # #
    def populate_sic(self, quantities=None, *, reset=False):
        '''Calculate lots of conversion factors.
        :param quantities: None or iterable of strings
            calculate these conversion factors and put them in self.sic.
            e.g. "p", "momentum", "M u", "kg m s-1".
            if None, use self.SIC_QUANTITIES.
        :reset: bool, default False.
            if True, clear self.sic before calculating.
        :return: self.sic, after adding all the requested conversion factors.
        '''
        if quantities is None: quantities = self.SIC_QUANTITIES
        if reset: self.clear_sic()
        for quantity in quantities:
            self.get_sic_factor(quantity)
        return self.sic

    def populate_physical_constants_raw(self, quantities=None):
        '''Calculate all the physical constants in raw units.
        :param quantities: None or iterable of strings
            calculate only these physical constants.
            if None, use self.PHYSICAL_CONSTANTS_SI.keys()
        :return: self.physical_constants_raw, after creating and filling it.
        '''
        if quantities is None: quantities = self.PHYSICAL_CONSTANTS_SI.keys()
        pcr = {key: self(key, 'raw') for key in quantities}
        self._physical_constants_raw = pcr
        return self._physical_constants_raw

    @property
    def physical_constants_raw(self):
        '''dict of all the physical constants in raw units.'''
        try:
            return self._physical_constants_raw
        except AttributeError:
            return self.populate_physical_constants_raw()

    # # # DISPLAY # # #
    display_precision = 2  # precision for displaying numbers in repr(self)

    def _repr_show_factors(self):
        '''returns dict of name and conversion factor to si, to include in repr(self).
        Here, include l, t, M, and q. Also include K if it is not 1.
        '''
        factors = {key: self(key, 'si', 'raw') for key in ('l', 't', 'M', 'q', 'K')}
        if factors['K'] == 1:
            del factors['K']
        return factors

    def __repr__(self):
        prec = self.display_precision
        factors = self._repr_show_factors()
        factors = [f"{key}={value:.{prec}e}" for key, value in factors.items()]
        return f'{type(self).__name__}(units={self.units!r}, {", ".join(factors)})'
