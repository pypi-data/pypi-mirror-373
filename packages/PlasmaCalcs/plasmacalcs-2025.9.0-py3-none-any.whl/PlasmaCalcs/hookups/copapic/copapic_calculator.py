"""
File Purpose: CopapicCalculator
"""

import numpy as np
import xarray as xr

from .copapic_bases import CopapicBasesLoader
from .copapic_direct_loader import CopapicDirectLoader
from .copapic_input_deck import CopapicInputDeck
from .copapic_io_tools import read_copapic_snaps_info
from ...dimensions import SnapList, INPUT_SNAP
from ...errors import DimensionError, FluidValueError
from ...plasma_calculator import MultifluidPlasmaCalculator
from ...tools import (
    alias, alias_child,
    UNSET,
)
from ...defaults import DEFAULTS

class CopapicCalculator(CopapicBasesLoader, CopapicDirectLoader, MultifluidPlasmaCalculator):
    '''PlasmaCalculator for Copapic outputs.
    To initialize from an copapic.json file, use CopapicCalculator.from_here(fname).
    
    Use CopapicCalculator.help() for more help.

    input_deck: CopapicInputDeck
        the CopapicInputDeck which is being used by this calculator.
    u: None or UnitsManager
        if provided, set self.u = u, and ignore u_l, u_t, u_n, and ne_si.
    u_l, u_t, u_n, ne_si: None or value
        must provide one of these values in order to fully determine the units.
        u_l: length [si] = u_l * length [raw]
        u_t: time [si] = u_t * time [raw]
        u_n: number density [si] = u_n * number density [raw]
        ne_si: electron number density [si]. (ne [raw] will be loaded from input_deck)
    kw_units: dict
        any additional values used to determine the units.
        can also provide u_l, u_t, u_n, or ne_si, here, instead of as direct kwarg.
        See help(UnitsManagerPIC.from_pic) for more details.
    quasineutral: None or bool
        if provided, set self.quasineutral.
        otherwise, infer it from self.input_deck.is_quasineutral().
        in quasineutral mode, distribution 0 is assumed to be electrons,
            and different routines are used to calculate its density & other parameters.
    _more_init_checks: bool, default False
        if True, perform additional checks during initialization.
        False by default for slight efficiency improvement,
            and to avoid possibility of init checks failing but object still being usable.

    other kwargs are passed to super().__init__.
    '''
    # # # DEFAULTS # # #
    _quasineutral = False

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, input_deck, *, 
                 u=None, u_l=None, u_t=None, u_n=None, ne_si=None, kw_units=dict(),
                 quasineutral=None,
                 _more_init_checks=False,
                 **kw_super):
        self.input_deck = input_deck
        kwu = kw_units.copy()
        self.init_units_manager(u=u, u_l=kwu.pop('u_l', u_l), u_t=kwu.pop('u_t', u_t),
                                u_n=kwu.pop('u_n', u_n), ne_si=kwu.pop('ne_si', ne_si), **kwu)
        self.init_maindims()
        self.init_fluids()
        self.init_snaps()
        # kw_super.setdefault('jfluid', 0)
        if quasineutral is None: quasineutral = self.input_deck.is_quasineutral()
        super().__init__(input_deck, quasineutral=quasineutral, **kw_super)
        if _more_init_checks:
            self._check_files_readable()
        if self.input_deck['ndim'] != 3:
            self.components = self.components[:2]

    @classmethod
    def from_here(cls, filename, **kw):
        '''create CopapicCalculator from input deck file found here (at filename).
        dist_names: None or dict
            {N: name for distribution N} for any number of distributions in filename.
            E.g.: {0: 'e', 1: 'H+', 2: 'C+'}
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return cls(CopapicInputDeck.from_file(filename), **kw)

    # # # INFO # # #
    dirname = alias_child('input_deck', 'dirname')
    filename = alias_child('input_deck', 'filename')

    # # # UNITS # # #
    def init_units_manager(self, *, u=None, u_l=None, u_t=None, u_n=None, ne_si=None, **kw_get_units_manager):
        '''set units manager self.u, based on input_deck.
        must provide one of these values in order to fully determine the units.
            u: UnitsManager object. if provided, set self.u = u.
            u_l: length [si] = u_l * length [raw]
            u_t: time [si] = u_t * time [raw]
            u_n: number density [si] = u_n * number density [raw]
            ne_si: electron number density [si]. (ne [raw] will be loaded from input_deck)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if u is None:
            u = self.input_deck.get_units_manager(u_l=u_l, u_t=u_t, u_n=u_n, ne_si=ne_si, **kw_get_units_manager)
        self.u = u

    # # # DIMENSIONS SETUP -- MAINDIMS # # #
    def init_maindims(self):
        '''set self.maindims based on input_deck.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.maindims = self.input_deck.maindims()

    def get_maindims_coords(self, units=None):
        '''return dict of {'x': xcoords, 'y': ycoords}. Possibly also 'z': zcoords.
        units: None or str
            result will be in this unit system. if None, use self.coords_units (default: self.units).
        coords will also be sliced according to self.slices.
        '''
        result = self.input_deck.get_space_coords()
        u_l = self.u('l', self.coords_units_explicit if units is None else units)
        result = {key: u_l * value for key, value in result.items()}
        return self._apply_maindims_slices_to_dict(result)

    get_space_coords = alias('get_maindims_coords')

    # # # DIMENSIONS SETUP -- OTHERS # # #
    def init_snaps(self):
        '''set self.snaps based on input_deck AND reading files.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        dt = self.input_deck["dt"]
        dir_ = self.input_deck.dirname
        output_dir = self.input_deck.output_dir
        names, times = read_copapic_snaps_info(output_dir, dt, dir_)
        self.snaps = SnapList.from_lists(s=names, t=times)

    def init_fluids(self):
        '''set self.fluids and self.jfluids based on input_deck.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.fluids = self.input_deck.dists
        self.jfluids = self.input_deck.neutrals

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''return list of strings to use inside self.__repr__'''
        contents = super()._repr_contents()
        contents = [f'input_deck={self.input_deck!r}'] + list(contents)
        return contents