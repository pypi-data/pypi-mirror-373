"""
File Purpose: CopapicInputDeck - values from copapic.json file.
"""
import os

import numpy as np

from .copapic_dimensions import (
    CopapicDist, CopapicDistList,
    CopapicNeutral, CopapicNeutralList,
)
from .copapic_io_tools import read_copapic_json_file
from ...units import UnitsManagerPIC
from ...tools import (
    alias,
    DictlikeFromKeysAndGetitem,
)
from ...defaults import DEFAULTS


### --------------------- CopapicInputDeck --------------------- ###

class CopapicInputDeck(DictlikeFromKeysAndGetitem):
    '''info from copapic.json file, in a class.
    Use CopapicInputDeck.from_file() to create an instance from a file.
    Units are "SI". 

    params: dict
        values of params
    distributions: dict or CopapicDistList
        dict of {distribution number: CopapicDist}, or an already-created CopapicDistList.
        if dict, will be internally stored as CopapicDistList.from_dict(distributions), instead.
    filename: str
        path to copapic.json file
        str will be internally stored as os.path.abspath(filename), instead.

    Examples:
        cpid = CopapicInputDeck.from_file('copapic.json')
        cpid[1]          # CopapicDist for distribution 1
        cpid['nz']       # number of grid points in z direction
        cpid.params      # dict of all global params
        cpid.dists       # CopapicDistList of all the distributions
        cpid.dists.get('e')    # get CopapicDist with name 'e'
        cpid.dists.get(0)      # get CopapicDist number 0 from this list
        cpid[2]['m']           # mass parameter for distribution 2
        cpid[0]['coll_rate']   # collision rate parameter for distribution 0
        cpid.keys()      # available keys
        cpid.items()     # available (key, value) pairs
        cpid[0].keys()   # available keys for distribution 0
        cpid.get('k', 7) # eid['k'] if it exists, else 7.
    '''
    dist_type = CopapicDist  # type for distributions
    dlist_type = CopapicDistList  # type for list of distributions
    neutral_type = CopapicNeutral  # type for neutral fluid
    nlist_type = CopapicNeutralList  # type for list of neutral fluids

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, params, distributions, *, filename=None, **kw_super):
        self.params = params
        self.distributions = distributions if isinstance(distributions, self.dlist_type) \
                                else self.dlist_type.from_dict(distributions)
        self._init_neutral_fluid(self.distributions)
        self.filename = None if filename is None else os.path.abspath(filename)
        super().__init__(**kw_super)

    dists = alias('distributions')

    def _init_neutral_fluid(self, dists):
        '''sets self.neutral and self.neutrals based on each distribution.
        dists: CopapicDistList
            list of distributions.
        '''
        ns = []
        if not isinstance(dists, self.dlist_type):
            raise TypeError(f'dists must be {self.dlist_type}, not {type(dists)}')
        if len(dists) == 0:
            raise ValueError('dists must have at least one distribution')
        for i, dist in enumerate(dists):
            if not isinstance(dist, self.dist_type):
                raise TypeError(f'dist must be {self.dist_type}, not {type(dist)}')
            pms = dist.params
            n = self.neutral_type(m=pms['neutralmass'], vth=pms['vneutralth'], 
                name=f'neutral_{i}', v0=pms['vneutral0'])
            ns.append(n)
        self.neutrals = self.nlist_type(ns)
        # self.neutral = self.neutral_type(m=-1, vth=[-1,-1,-1])
        # self.neutrals = self.nlist_type([self.neutral])

    @classmethod
    def from_file(cls, filename, *, dist_names=None, **kw__init):
        '''return CopapicInputDeck from copapic.json file.
        filename: str
            path to copapic.json file.
            abspath(filename) will be saved to result, for easier bookkeeping.
        dist_names: None or dict
            {N: name for distribution N} for any number of distributions in filename.
            None --> infer from file.
        '''
        deck = read_copapic_json_file(filename)
        if dist_names is None:
            dist_names = [n["name"] for n in deck["distributions"]]
            dist_names = {N: name for N, name in enumerate(dist_names)}
            dists = {N: n for N, n in enumerate(deck["distributions"])}
            for N, name in dist_names.items():
                if name is not None:
                    dists[N][f'name{N}'] = name 
        dist_dict = cls.dist_type.dists_from_dict(dists)
        params = {key: value for key, value in deck.items() if key != 'distributions'}
        return cls(params, dist_dict, filename=filename, **kw__init)

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
    
    @property
    def output_dir(self):
        '''return directory where output files are stored.
        '''
        title = self['title']
        if title is None:
            raise ValueError('title is None; cannot determine output_dir.')
        title = title.replace(' ', '')
        return os.path.join(self.dirname, title)

    # # # DIMENSIONS # # #
    def maindims(self):
        '''returns tuple of main dimensions in this input deck.
        inferred from self['nx'], 'ny', 'nz', and 'ndim_space'
        '''
        ndim = self['ndim']
        if ndim == 3:
            return ('x', 'y', 'z')
        elif ndim == 2:
            return ('x', 'y')  # by default, return ('x', 'y').
        else:
            raise NotImplementedError(f'{type(self).__name__}.maindims() when ndim_space={ndim}')

    def _get_nspace_simple(self, xstr):
        '''get "simple" number of cells in {x} dimension. == n{x} // nout_avg
        xstr should be 'x', 'y', or 'z'.
        See also: self._get_nspace.
        '''
        return self.get(f'n{xstr}', 1)

    def get_nspace(self, xstr):
        '''get number of cells in {x} dimension, accounting for nout_avg and nsubdomains.
        See also: Nx, Ny, Nz.
        '''
        result = self._get_nspace_simple(xstr)
        return result

    Nx = property(lambda self: self.get_nspace('x'),
                  doc='''actual total number of grid cells in the x dimension.''')
    Ny = property(lambda self: self.get_nspace('y'),
                  doc='''actual total number of grid cells in the y dimension.''')
    Nz = property(lambda self: self.get_nspace('z'),
                  doc='''actual total number of grid cells in the z dimension.''')

    def get_dspace(self, xstr):
        '''get d{x} [raw units] between output cells.
        '''
        return self.get(f'd{xstr}', 1)

    Dx = property(lambda self: self.get_dspace('x'),
                    doc='''dx between adjacent output cells [raw units]''')
    Dy = property(lambda self: self.get_dspace('y'),
                    doc='''dy between adjacent output cells [raw units]''')
    Dz = property(lambda self: self.get_dspace('z'),
                    doc='''dz between adjacent output cells [raw units]''')

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
        '''return UnitsManagerPIC for this input deck
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return UnitsManagerPIC.from_pic(u_l=1.0)

    # # # QUASINEUTRAL? # # #
    def is_quasineutral(self):
        '''return whether this input deck is in quasineutral mode.
        as a proxy, guessing quasineutral iff any dist.is_hybrid() for dist in self.dists.
        '''
        return any(dist.is_hybrid() for dist in self.dists)