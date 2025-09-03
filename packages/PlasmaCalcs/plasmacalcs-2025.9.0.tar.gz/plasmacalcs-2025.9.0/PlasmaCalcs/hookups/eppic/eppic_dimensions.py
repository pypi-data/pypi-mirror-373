"""
File Purpose: Dimension values & lists for Eppic
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


### --------------------- EppicDist and EppicDistList --------------------- ###

class EppicDist(DictlikeFromKeysAndGetitem, Fluid):
    '''info about a single distribution.
    see cls.from_dict() to create an instance from a dict of values from an eppic.i file.
    units are "raw". Numerical values equal those from the eppic.i file.

    m: real number
        mass of a single "real" particle in the distribution
    q: real number
        charge of a single "real" particle in the distribution
    n0: real number
        background "physical" number density of this distribution of particles.
    N: None, int, or str
        distribution number; will be internally stored as int (or None).
        Optional because distribution number doesn't affect distribution physics,
        however all distributions from eppic.i files will have a number.
    i: None or int
        index of this distribution in a DistributionList.
        raise NotImplementedError if i and N are incompatible
        (i.e. both non-None and representing different values).
    params: None or dict
        additional parameters.
        Provide dict with keys with trailing distN removed,
        e.g. "coll_rate" not "coll_rate1" (if dist='1')
    name: None or str
        name of this distribution.
        Optional, and probably not found in eppic.i files.
        Provide to improve human-readability.
    '''
    precision = 2  # precision when converting values to human-readable string

    # attrs "defining" this DimensionValue, & which can be provided as kwargs in __init__
    _kw_def = {'name', 'i', 'm', 'q', 'n0', 'N', 'params'}

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, m, q, n0, *, N=None, name=None, i=None, params=None):
        N = N if N is None else int(N)
        params = dict() if params is None else params
        try:
            i_use = value_from_aliases(i=i, N=N)
        except InputError:
            # maybe eventually we will handle this case, but for now we didn't implement it.
            raise NotImplementedError(f'distribution N not equal to index in list; N={N}, i={i}')
        super().__init__(name=name, i=i_use, m=m, q=q)
        self.n0 = n0
        self.N = N
        self.params = params

    @classmethod
    def from_dict_and_N(cls, d, N):
        '''return EppicDist from dict and N.
        d: dict
            result of eppic_io_tools.read_eppic_i_file()[N].
            must have keys mdN, qdN, n0dN. E.g. "md1" for N='1'
            other keys must end in N, and one N will be removed from end of each.
                e.g. "coll_rate1" --> "coll_rate".
                raise ValueError if any key doesn't end with N.
            if 'nameN' appears in d, it will be used as name.
        N: None, str or int
            distribution number. if int, will be converted to str.
        '''
        N = str(N)
        lN = len(N)
        for key in d:
            if not key.endswith(N):
                raise ValueError(f'key {key!r} does not end with {N!r}')
        params = {key[:-lN]: value for key, value in d.items()}
        return cls(m=params['md'], q=params['qd'], n0=params['n0d'],
                   N=N, name=params.get('name', None), params=params)

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
        or the `x` component if `x` = 'x', 'y', or 'z'.

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

    def get_nvsqr0(self, x=None):
        '''returns original (t=0) nvsqr, as a tuple of (vx^2, vy^2, vz^2) values,
        or the `x` component if `x` = 'x', 'y', or 'z'.

        The result should be comparable to eppic nvsqr output.
        To convert from known values to nvsqr...:
            Ta_x = m * (vsqr_x - u_x^2) / kB   # copied from EppicCalculator.help('Ta')
            --> vsqr_x = u_x^2 + kB * Ta_x / m.
            we know vth0_x == kB * Ta_x / m,
            and we know v0_x == u_x.
            --> nvsqr_x == n0 * (v0_x^2 + vth0_x^2)
        '''
        if x is None:
            return (self.get_nvsqr0('x'), self.get_nvsqr0('y'), self.get_nvsqr0('z'))
        else:
            return self.get_n0() * (self.get_v0(x)**2 + self.get_vth0(x)**2)

    def get_velocity_coords(self, units):
        '''
        Returns a dictionary of vdist coordinates (vx, vy, vz) for this EppicDist.
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
            number of cells & processors are global parameters not known by EppicDist,
            so EppicDist cannot calculate npd from those options.

        default: UNSET or any value
            return default instead of error when npd not found, if default provided (not UNSET).
        '''
        npd = self.get('npd', None)
        if npd is None:
            if default is not UNSET:
                return default
            # else, raise FluidKeyError; error message depends on which alternative option in self.keys().
            keys = self.keys()
            errmsg = "'npd' not provided, and EppicDist cannot determine 'npd' from "
            if 'nptotd' in keys:
                errmsg += "'nptotd', because EppicDist doesn't know number of processors."
            elif 'npcelld' in keys:
                errmsg += "'npcelld', because EppicDist doesn't know number of cells."
            elif 'nptotcelld' in keys:
                errmsg += "'nptotcelld', because EppicDist doesn't know number of cells and processors."
            else:
                errmsg = "No indication of 'npd' was provided to EppicDist."
            raise FluidKeyError(errmsg)
        # else:
        return npd


class EppicDistList(FluidList):
    '''list of EppicDist objects'''
    value_type = EppicDist


### --------------------- EppicNeutral and EppicNeutralList --------------------- ###

class EppicNeutral(Fluid):
    '''info about the neutral fluid, in eppic.
    [raw] units system; numerical values match input deck.

    m: number
        mass of neutral fluid particle.
    name: str, default 'neutral'
        name of the neutral fluid.
    i: int, default 0
        integer associated with the neutral fluid.
    vth: None or number
        thermal velocity of the neutral fluid. None --> unknown.
        (Note: the implementation here assumes neutral vth is isotropic.)
    '''
    precision = 2  # precision when converting values to human-readable string

    # attrs "defining" this DimensionValue, & which can be provided as kwargs in __init__
    _kw_def = {'m', 'name', 'i', 'vth'}

    def __init__(self, m, *, name='neutral', i=0, vth=None):
        self.vth = vth
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

    get_vth0 = alias('get_vth',
            doc='''alias to self.get_vth. Provides interface consistency with EppicDist.get_vth0.
            note: neutral vth is the same for all 3 components, and doesn't vary with time.''')

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(m={self.m:.{self.precision}e})'

    # # # COMPARISON # # # 
    # sometimes it's convenient to have an ordering for the values...
    # and, let's make sure EppicNeutral always compares as "less than" any EppicDist.
    # [TODO] better code encapsulation (some of this is repeated from DimensionValue class)?
    def __lt__(self, other):
        if isinstance(other, EppicDist): return True
        elif isinstance(other, type(self)): return (self.i, self.s) < (other.i, other.s)
        else: return NotImplemented
    def __le__(self, other):
        if isinstance(other, EppicDist): return True
        if isinstance(other, type(self)): return (self.i, self.s) <= (other.i, other.s)
        else: return NotImplemented
    def __gt__(self, other):
        if isinstance(other, EppicDist): return False
        if isinstance(other, type(self)): return (self.i, self.s) > (other.i, other.s)
        else: return NotImplemented
    def __ge__(self, other):
        if isinstance(other, EppicDist): return False
        if isinstance(other, type(self)): return (self.i, self.s) >= (other.i, other.s)
        else: return NotImplemented


class EppicNeutralList(FluidList):
    '''list of EppicNeutral objects.'''
    value_type = EppicNeutral

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if len(self) > 1:
            raise NotImplementedError('EppicNeutralList with more than 1 fluid...')

