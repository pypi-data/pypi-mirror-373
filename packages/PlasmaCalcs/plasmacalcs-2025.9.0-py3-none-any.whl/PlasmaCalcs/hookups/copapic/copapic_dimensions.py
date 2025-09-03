"""
File Purpose: Dimension values & lists for Copapic
"""
import numpy as np

from ...dimensions import Fluid, FluidList
from ...errors import InputError, InputMissingError, FluidKeyError
from ...tools import (
    alias, value_from_aliases,
    DictlikeFromKeysAndGetitem,
    format_docstring,
    UNSET,
)


### --------------------- CopapicDist and CopapicDistList --------------------- ###

class CopapicDist(DictlikeFromKeysAndGetitem, Fluid):
    '''info about a single distribution.
    see cls.from_dict() to create an instance from a dict of values from an Copapic.json file.
    units are "raw". Numerical values equal those from the Copapic.json file.

    m: real number
        mass of a single "real" particle in the distribution
    q: real number
        charge of a single "real" particle in the distribution
    n0: real number
        background "physical" number density of this distribution of particles.
    params: None or dict
        additional parameters.
    name: None or str
        name of this distribution.
        Optional, and probably not found in Copapic.json files.
        Provide to improve human-readability.
    '''
    precision = 2  # precision when converting values to human-readable string

    # attrs "defining" this DimensionValue, & which can be provided as kwargs in __init__
    _kw_def = {'name', 'm', 'q', 'n0', 'params'}

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, m, q, n0, name, i, *, params=None):
        params = dict() if params is None else params
        super().__init__(name=name, i=int(i), m=m, q=q)
        self.n0 = n0
        self.N = int(i)
        self.params = params

    @classmethod
    def from_dict_and_N(cls, d, N):
        '''return CopapicDist from dict and N.
        d: dict
            result of copapic_io_tools.read_copapic_json_file()[N].
        N: None, str or int
            distribution number. if int, will be converted to str.
        '''
        N = str(N)
        params = {key : value for key, value in d.items()}
        return cls(m=params['mass'], q=params['charge'], n0=params['n0'], name=params['name'], i = N, params=params)

    @classmethod
    def dists_from_dict(cls, d):
        '''return dict of distributions, given a dict of {N: dict of distribution values}.'''
        return {N: cls.from_dict_and_N(d, N) for N, d in d.items()}

    # # # DISPLAY # # #
    def __repr__(self):
        fmt = f'{{:.{self.precision}e}}'
        contents = []
        if self.N is not None:
            contents.append(f'N={self.N}')
        if self.name is not None:
            contents.append(f'name={self.name!r}')
        contents.extend([f'{a_}={fmt.format(getattr(self, a_))}' for a_ in ('m', 'q', 'n0')])
        content_str = ', '.join(contents)
        return f'{type(self).__name__}({content_str})'

    # # # GETTING VALUES / ITERATING # # #
    SPECIAL = ('m', 'q', 'n0', 'N', 'name')

    @format_docstring(special=SPECIAL)
    def __getitem__(self, key):
        '''usually return self.params[key]; if key is special return self.key instead.
        special keys are determined by self.SPECIAL; default {special}.
            else, return self.params[key].
        '''
        if key in self.SPECIAL:
            return getattr(self, key)
        try:
            return self.params[key]
        except KeyError:
            errmsg = f'key {key!r} not in {type(self).__name__}.params, and not special {self.SPECIAL}'
            raise KeyError(errmsg) from None

    def keys(self):
        '''return tuple of keys which are special or in self.params'''
        return tuple(key for key in (*self.SPECIAL, *self.params.keys()))

    # # # QUASINEUTRAL? # # #
    def is_hybrid(self):
        '''return whether this distribution is "hybrid", i.e. fluid model instead of PIC.
        as a proxy, guessing hybrid iff self.get('method', 0) != 0.
        '''
        return self.get('method', 0) != 0

    # # # GETTING SOME PARAMETERS # # #
    def get_n0(self):
        '''returns background (mean) density of this distribution. Equivalent: self['n0']'''
        return self['n0']

    def get_v0(self, x=None):
        '''returns original (t=0) velocity, as a tuple of (vx, vy, xz) values,
        or the x component if x provided (x should be a string if provided).
        '''
        if x is None:
            return (self.get_v0('x'), self.get_v0('y'), self.get_v0('z'))
        else:
            key = f'v{x}0d'
            return self[key]

    def get_vth0(self, x=None):
        '''returns original (t=0) thermal velocity, as a tuple of (vx, vy, xz) values,
        or the x component if x provided (x should be a string if provided).

        if x is Ellipsis (i.e., x=...), assert all three components are the same,
            and return the one value which they all equal.
        '''
        if x is None:
            return (self.get_vth0('x'), self.get_vth0('y'), self.get_vth0('z'))
        elif x is ...:
            vx, vy, vz = self.get_vth0('x'), self.get_vth0('y'), self.get_vth0('z')
            assert vx == vy == vz, f'Expected all equal, but got: vth0x={vx}, vth0y={vy}, vth0z={vz}'
            return vx
        else:
            key = f'v{x}thd'
            return self[key]

    def get_velocity_coords(self, units):
        '''
        Returns a dictionary of vdist coordinates (vx, vy, vz) for this CopapicDist.
        For example, "vx": np.linspace(self["pvxmin"], self["pvxmax"], num=self["pnvx"]).
        '''
        coords = {
            "vx": np.linspace(self["pvxmin"], self["pvxmax"], num=self["pnvx"]) * units,
            "vy": np.linspace(self["pvymin"], self["pvymax"], num=self["pnvy"]) * units,
            "vz": np.linspace(self["pvzmin"], self["pvzmax"], num=self["pnvz"]) * units
        }
        return coords

    def get_npd(self, *, default=UNSET):
        '''return number of PIC particles for this distribution in each processor.
        If that is not possible (due to using alternate option for npd), raise FluidKeyError
        Alternate options include: nptotd, npcelld, nptotcelld;
            those options tell npd info but scaled by number of cells and/or processors.
            number of cells & processors are global parameters not known by CopapicDist,
            so CopapicDist cannot calculate npd from those options.

        default: UNSET or any value
            return default instead of error when npd not found, if default provided (not UNSET).
        '''
        npd = self.get('npd', None)
        if npd is None:
            if default is not UNSET:
                return default
            # else, raise FluidKeyError; error message depends on which alternative option in self.keys().
            keys = self.keys()
            errmsg = "'npd' not provided, and CopapicDist cannot determine 'npd' from "
            if 'nptotd' in keys:
                errmsg += "'nptotd', because CopapicDist doesn't know number of processors."
            elif 'npcelld' in keys:
                errmsg += "'npcelld', because CopapicDist doesn't know number of cells."
            elif 'nptotcelld' in keys:
                errmsg += "'nptotcelld', because CopapicDist doesn't know number of cells and processors."
            else:
                errmsg = "No indication of 'npd' was provided to CopapicDist."
            raise FluidKeyError(errmsg)
        # else:
        return npd


class CopapicDistList(FluidList):
    '''list of CopapicDist objects'''
    value_type = CopapicDist


### --------------------- CopapicNeutral and CopapicNeutralList --------------------- ###

class CopapicNeutral(Fluid):
    '''info about the neutral fluids, in Copapic.
    [raw] units system; numerical values match input deck.

    m: number
        mass of neutral fluid particle.
    name: str, default 'neutral'
        name of the neutral fluid.
    i: int, default 0
        Copapic dist that this neutral fluid is associated with.
    vth: None or number
        thermal velocity of the neutral fluid. None --> unknown.
    v0: None or number
        drift velocity of the neutral fluid. None --> unknown.
    '''
    precision = 2  # precision when converting values to human-readable string

    # attrs "defining" this DimensionValue, & which can be provided as kwargs in __init__
    _kw_def = {'m', 'name', 'i', 'vth'}

    def __init__(self, m, *, name='neutral', i=0, vth=None, v0=None):
        self.vth = vth
        self.v0 = v0
        super().__init__(name, m=m, q=0, i=i)

    # # # GETTING SOME PARAMETERS # # #
    def get_vth(self, x=None):
        '''returns thermal velocity, as a tuple of (vx, vy, xz) values,
        or the x component if x provided (x should be a string if provided).
        (Note that for neutrals, vth is the same for all 3 components.)
        if self.vth is None, raise InputMissingError.
        '''
        if self.vth is None:
            raise InputMissingError(f'cannot get_vth when {type(self).__name__}.vth is None')
        if x is None:
            return (self.vth, self.vth, self.vth)
        else:
            return self.vth
    
    def get_v0(self, x=None):
        '''returns drift velocity, as a tuple of (vx, vy, xz) values,
        or the x component if x provided (x should be a string if provided).
        if self.v0 is None, raise InputMissingError.
        '''
        if self.v0 is None:
            raise InputMissingError(f'cannot get_v0 when {type(self).__name__}.v0 is None')
        if x is None:
            return tuple(self.v0)
        else:
            if x == 'x':
                return self.v0[0]
            elif x == 'y':
                return self.v0[1]
            elif x == 'z':
                return self.v0[2]
            else:
                raise InputError(f'get_v0: x={x} not in {{x,y,z}}')
            
    # # # ALIASES # # #
    get_vth0 = alias('get_vth',
            doc='''alias to self.get_vth. Provides interface consistency with CopapicDist.get_vth0.
            note: neutral vth is the same for all 3 components, and doesn't vary with time.''')
    get_v0d = alias('get_v0',
            doc='''alias to self.get_v0. Provides interface consistency with CopapicDist.get_v0d.
            note: neutral v0 doesn't vary with time.''')

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(m={self.m:.{self.precision}e}, vth={self.vth[0]:.{self.precision}e}, v0=({self.v0[0]:.{self.precision}e}, {self.v0[1]:.{self.precision}e}, {self.v0[2]:.{self.precision}e}))'

    # # # COMPARISON # # # 
    # sometimes it's convenient to have an ordering for the values...
    # and, let's make sure CopapicNeutral always compares as "less than" any CopapicDist.
    # [TODO] better code encapsulation (some of this is repeated from DimensionValue class)?
    def __lt__(self, other):
        if isinstance(other, CopapicDist): return True
        elif isinstance(other, type(self)): return (self.i, self.s) < (other.i, other.s)
        else: return NotImplemented
    def __le__(self, other):
        if isinstance(other, CopapicDist): return True
        if isinstance(other, type(self)): return (self.i, self.s) <= (other.i, other.s)
        else: return NotImplemented
    def __gt__(self, other):
        if isinstance(other, CopapicDist): return False
        if isinstance(other, type(self)): return (self.i, self.s) > (other.i, other.s)
        else: return NotImplemented
    def __ge__(self, other):
        if isinstance(other, CopapicDist): return False
        if isinstance(other, type(self)): return (self.i, self.s) >= (other.i, other.s)
        else: return NotImplemented


class CopapicNeutralList(FluidList):
    '''list of CopapicNeutral objects.'''
    value_type = CopapicNeutral

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
