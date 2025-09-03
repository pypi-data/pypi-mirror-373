"""
File Purpose: EppicInputDeck - values from eppic.i file.
"""
import os

import numpy as np

from .eppic_dimensions import (
    EppicDist, EppicDistList,
    EppicNeutral, EppicNeutralList,
)
from .eppic_io_tools import read_eppic_i_file, infer_eppic_dist_names
from ...units import UnitsManagerPIC
from ...tools import (
    alias,
    DictlikeFromKeysAndGetitem,
)
from ...defaults import DEFAULTS


### --------------------- EppicInputDeck --------------------- ###

class EppicInputDeck(DictlikeFromKeysAndGetitem):
    '''info from eppic.i file, in a class.
    Use EppicInputDeck.from_file() to create an instance from a file.
    units are "raw". Numerical values equal those from the eppic.i file.

    params: dict
        values of params
    distributions: dict or EppicDistList
        dict of {distribution number: EppicDist}, or an already-created EppicDistList.
        if dict, will be internally stored as EppicDistList.from_dict(distributions), instead.
    filename: None or str
        path to eppic.i file this came from. E.g. 'path/to/eppic.i'
        str will be internally stored as os.path.abspath(filename), instead.

    Examples:
        eid = EppicInputDeck.from_file('eppic.i')
        eid[1]          # EppicDist for distribution 1
        eid['nz']       # number of grid points in z direction
        eid.params      # dict of all global params
        eid.dists       # EppicDistList of all the distributions
        eid.dists.get('e')    # get EppicDist with name 'e'
        eid.dists.get(0)      # get EppicDist number 0 from this list
        eid[2]['m']           # mass parameter for distribution 2
        eid[0]['coll_rate']   # collision rate parameter for distribution 0
        eid.keys()      # available keys
        eid.items()     # available (key, value) pairs
        eid[0].keys()   # available keys for distribution 0
        eid.get('k', 7) # eid['k'] if it exists, else 7.
    '''
    dist_type = EppicDist  # type for distributions
    dlist_type = EppicDistList  # type for list of distributions
    neutral_type = EppicNeutral  # type for neutral fluid
    nlist_type = EppicNeutralList  # type for list of neutral fluids

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, params, distributions, *, filename=None, **kw_super):
        self.params = params
        self.distributions = distributions if isinstance(distributions, self.dlist_type) \
                                else self.dlist_type.from_dict(distributions)
        self._init_neutral_fluid()
        self.filename = None if filename is None else os.path.abspath(filename)
        super().__init__(**kw_super)

    dists = alias('distributions')

    @classmethod
    def from_file(cls, filename='eppic.i', *, dist_names=None, **kw__init):
        '''return EppicInputDeck from eppic.i file.
        filename: str
            path to eppic.i file.
            abspath(filename) will be saved to result, for easier bookkeeping.
        dist_names: None or dict
            {N: name for distribution N} for any number of distributions in filename.
            None --> infer from file.
        '''
        params, dists = read_eppic_i_file(filename)
        if dist_names is None:
            dist_names = infer_eppic_dist_names(filename)
        if dist_names is not None:
            for N, name in dist_names.items():
                if name is not None:
                    dists[N][f'name{N}'] = name    # (the {N} in the key is required, then removed, by EppicDist.from_dict)
        dist_dict = cls.dist_type.dists_from_dict(dists)
        return cls(params, dist_dict, filename=filename, **kw__init)

    def _init_neutral_fluid(self):
        '''sets self.neutral and self.neutrals based on params of self.
        Particularly, uses params['m_neutral'].
        '''
        m = self.params['m_neutral']
        vth = self.params.get('vth_neutral', None)
        self.neutral = self.neutral_type(m, vth=vth)
        self.neutrals = self.nlist_type([self.neutral])

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'with {len(self.dists)} distributions']
        if self.filename is not None:
            contents.append(f'filename={self.filename!r}')
        contents_str = ', '.join(contents)
        return f'{type(self).__name__}({contents_str})'

    # # # GETTING VALUES & ITERATING # # #
    def __getitem__(self, key):
        '''return self.params[key] if key in self.params, else self.dists[key].'''
        try:
            return self.params[key]
        except KeyError:
            pass  # handled below, to make clearer error message if failing.
        try:
            return self.dists[key]
        except (KeyError, IndexError, ValueError):
            errmsg = f'key {key!r} not in {type(self).__name__}.params or .dists'
            raise KeyError(errmsg) from None

    def keys(self):
        '''return tuple of keys to access self.dists or self.params'''
        return tuple(key for key in (*range(len(self.dists)), *self.params.keys()))

    # # # FILE PATH # # #
    @property
    def dirname(self):
        '''os.path.dirname(self.filename).
        if self.filename is None, raise FileNotFoundError.
        '''
        filename = self.filename
        if filename is None:
            raise FileNotFoundError('self.filename is None; cannot determine dirname.')
        return os.path.dirname(filename)

    # # # DIMENSIONS # # #
    def maindims(self):
        '''returns tuple of main dimensions in this input deck.
        inferred from self['nx'], 'ny', 'nz', and 'ndim_space'
        '''
        ndim_space = self['ndim_space']
        if ndim_space == 3:
            return ('x', 'y', 'z')
        elif ndim_space == 2:
            nx = self.get('nx', None)
            if nx is None: return ('y', 'z')
            ny = self.get('ny', None)
            if ny is None: return ('x', 'z')
            nz = self.get('nz', None)
            if nz is None: return ('x', 'y')
            # provided nx, ny, and nz...
            if nz == 1: return ('x', 'y')
            elif ny == 1: return ('x', 'z')
            elif nx == 1: return ('y', 'z')
            # nx, ny, and nz were all provided, and not 1.
            if getattr(self, 'verbose', True) and not getattr(self, 'warned_ndim2', False):
                print("warning, ndim_space=2 but input deck contains 'nx', 'ny', and 'nz', all != 1.")
                print("assuming space dims ('x', 'y').")
                self.warned_ndim2 = True  # only print the warning once per input_deck.
            return ('x', 'y')  # by default, return ('x', 'y').
        else:
            raise NotImplementedError(f'{type(self).__name__}.maindims() when ndim_space={ndim_space}')

    def _get_nspace_simple(self, xstr):
        '''get "simple" number of cells in {x} dimension. == n{x} // nout_avg
        xstr should be 'x', 'y', or 'z'.
        Note that for x='x', actual number of cells may be affected by nsubdomains.
        See also: self._get_nspace.
        '''
        return self.get(f'n{xstr}', 1) // self.get('nout_avg', 1)

    def _get_velocity_nspace_simple(self, xstr, N):
        '''get "simple" number of cells in {vx} dimension. == pn{vx}{N}
        xstr should be 'vx', 'vy', or 'vz'.
        N is the distribution number.
        Note that for x='x', actual number of cells may be affected by nsubdomains.
        See also: self.get_nspace.
        '''
        N = str(N)
        return self.get(f'pn{xstr}{N}', 1)

    def get_nspace(self, xstr):
        '''get number of cells in {x} dimension, accounting for nout_avg and nsubdomains.
        See also: Nx, Ny, Nz.
        '''
        result = self._get_nspace_simple(xstr)
        if xstr == 'x':
            result = result * self.get('nsubdomains', 1)
        return result

    Nx = property(lambda self: self.get_nspace('x'),
                  doc='''actual total number of grid cells in the x dimension.''')
    Ny = property(lambda self: self.get_nspace('y'),
                  doc='''actual total number of grid cells in the y dimension.''')
    Nz = property(lambda self: self.get_nspace('z'),
                  doc='''actual total number of grid cells in the z dimension.''')

    def get_velocity_nspace(self, xstr, N):
        '''get number of cells in {vx} dimension.
        N is the distribution number.
        See also: Nvx, Nvy, Nvz.
        '''
        result = self._get_velocity_nspace_simple(xstr, N)
        return result

    Nvx = property(lambda self: [self.get_velocity_nspace('x', N) for N in range(len(self.dists))],
                  doc='''list of actual total numbers of grid cells in the vx dimension (ordered by distribution).''')
    Nvy = property(lambda self: [self.get_velocity_nspace('x', N) for N in range(len(self.dists))],
                  doc='''list of actual total numbers of grid cells in the vy dimension (ordered by distribution).''')
    Nvz = property(lambda self: [self.get_velocity_nspace('x', N) for N in range(len(self.dists))],
                  doc='''list of actual total numbers of grid cells in the vz dimension (ordered by distribution).''')

    def get_dspace(self, xstr):
        '''get d{x} [raw units] between output cells.
        accounts for nout_avg; see also: Dx, Dy, Dz.
        if {x} not provided in self (e.g. 2D in x & y, xstr='z'), returns 1 * nout_avg.
        '''
        return self.get(f'd{xstr}', 1) * self.get('nout_avg', 1)

    Dx = property(lambda self: self.get_dspace('x'),
                    doc='''dx between adjacent output cells [raw units]''')
    Dy = property(lambda self: self.get_dspace('y'),
                    doc='''dy between adjacent output cells [raw units]''')
    Dz = property(lambda self: self.get_dspace('z'),
                    doc='''dz between adjacent output cells [raw units]''')

    def _get_velocity_extents(self, xstr, N):
        '''get (p{vx}min{N}, p{vx}max{N}) [raw units].
        N is the distribution number.
        See also: Dvx, Dvy, Dvz.
        '''
        return (self.get(f'p{xstr}min{N}', 1), self.get(f'p{xstr}max{N}', 1))

    def get_coord(self, xstr):
        '''get coordinate array [raw units] for this dimension.
        xstr: str
            dimension name. 'x', 'y', or 'z'.
        '''
        dx = self.get_dspace(xstr)
        Nx = self.get_nspace(xstr)
        return np.arange(Nx) * dx

    def get_space_coords(self):
        '''return dict of {x: xcoord array} for x in self.maindims(), a subset of ('x', 'y', 'z').'''
        return {x: self.get_coord(x) for x in self.maindims()}

    def get_dspace_min(self):
        '''return min of self.Dx, self.Dy, self.Dz.'''
        return min(self.Dx, self.Dy, self.Dz)

    def get_dspace_max(self):
        '''return max of self.Dx, self.Dy, self.Dz.'''
        return max(self.Dx, self.Dy, self.Dz)

    # # # UNITS # # #
    def get_units_manager(self, *, u_l=None, u_t=None, u_n=None, ne_si=None, **kw_u_from_pic):
        '''return UnitsManagerPIC for this input deck. Assumes distribution 0 is electrons.
        Must provide u_l, u_t, u_n, or ne_si.
        Will read ne, qe, me, and eps0 from the input deck, unless they are provided in kw_u_from_pic.
        See help(UnitsManagerPIC.pic_ambiguous_unit) for details.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if 'ne' not in kw_u_from_pic: kw_u_from_pic['ne'] = self[0]['n0']
        if 'qe' not in kw_u_from_pic: kw_u_from_pic['qe'] = abs(self[0]['q'])
        if 'me' not in kw_u_from_pic: kw_u_from_pic['me'] = self[0]['m']
        if 'eps0' not in kw_u_from_pic: kw_u_from_pic['eps0'] = self['eps']
        return UnitsManagerPIC.from_pic(u_l=u_l, u_t=u_t, u_n=u_n, ne_si=ne_si, **kw_u_from_pic)

    # # # QUASINEUTRAL? # # #
    def is_quasineutral(self):
        '''return whether this input deck is in quasineutral mode.
        as a proxy, guessing quasineutral iff any dist.is_hybrid() for dist in self.dists.
        '''
        return any(dist.is_hybrid() for dist in self.dists)

